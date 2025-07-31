# -*- coding: utf-8 -*-
"""
事件系統
管理遊戲事件的觸發、處理和執行
"""

import json
import random
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class EventType(Enum):
    """事件類型枚舉"""

    DIALOGUE = "dialogue"  # 對話事件
    AFFECTION = "affection"  # 好感度事件
    TIME = "time"  # 時間事件
    INTERACTION = "interaction"  # 互動事件
    SPECIAL = "special"  # 特殊事件
    RANDOM = "random"  # 隨機事件


class EventPriority(Enum):
    """事件優先級枚舉"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventCondition:
    """事件條件類別"""

    def __init__(self, data: Dict[str, Any]):
        """初始化事件條件"""
        self.affection_min = data.get("affection_min", 0)
        self.affection_max = data.get("affection_max", 100)
        self.time_period = data.get("time_period", "")
        self.weekday = data.get("weekday", [])
        self.flags_required = data.get("flags_required", {})
        self.flags_forbidden = data.get("flags_forbidden", {})
        self.probability = data.get("probability", 1.0)
        self.cooldown_hours = data.get("cooldown_hours", 0)
        self.max_triggers = data.get("max_triggers", -1)  # -1 表示無限制

    def check_conditions(self, game_state: Dict[str, Any]) -> bool:
        """檢查條件是否滿足"""
        # 檢查好感度條件
        nyanko_affection = game_state.get("nyanko_affection", 0)
        if not (self.affection_min <= nyanko_affection <= self.affection_max):
            return False

        # 檢查時間段條件
        if (
            self.time_period
            and game_state.get("current_time_period", "") != self.time_period
        ):
            return False

        # 檢查星期條件
        if self.weekday and game_state.get("current_weekday", "") not in self.weekday:
            return False

        # 檢查必需旗標
        game_flags = game_state.get("flags", {})
        for flag, required_value in self.flags_required.items():
            if game_flags.get(flag) != required_value:
                return False

        # 檢查禁止旗標
        for flag, forbidden_value in self.flags_forbidden.items():
            if game_flags.get(flag) == forbidden_value:
                return False

        # 檢查概率
        if random.random() > self.probability:
            return False

        return True


class GameEvent:
    """遊戲事件類別"""

    def __init__(self, data: Dict[str, Any]):
        """初始化遊戲事件"""
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.event_type = EventType(data.get("event_type", "dialogue"))
        self.priority = EventPriority(data.get("priority", 2))  # 使用數字而非字串

        # 觸發條件
        self.conditions = EventCondition(data.get("conditions", {}))

        # 事件內容
        self.dialogue_id = data.get("dialogue_id", "")
        self.actions = data.get("actions", [])
        self.effects = data.get("effects", {})

        # 執行狀態
        self.trigger_count = 0
        self.last_triggered = None
        self.is_active = data.get("is_active", True)

        # 回調函數
        self.callback_function = data.get("callback_function", "")


class EventSystem:
    """事件系統主類別"""

    def __init__(self, game_engine):
        """初始化事件系統"""
        self.game_engine = game_engine

        # 事件資料
        self.events: Dict[str, GameEvent] = {}
        self.active_events: List[str] = []
        self.event_queue: List[Dict[str, Any]] = []

        # 事件歷史
        self.event_history: List[Dict[str, Any]] = []
        self.triggered_events: Dict[str, int] = {}  # 事件ID -> 觸發次數

        # 隨機事件池
        self.random_event_pool: List[str] = []

        # 回調函數
        self.on_event_triggered: Optional[Callable] = None
        self.on_event_completed: Optional[Callable] = None

        # 系統設定
        self.max_queue_size = 10
        self.auto_process_events = True

        # 載入預設事件
        self._load_default_events()

        print("事件系統初始化完成")

    def _load_default_events(self):
        """載入預設事件"""
        default_events = {
            "morning_surprise": {
                "id": "morning_surprise",
                "name": "早晨驚喜",
                "description": "にゃんこ為你準備了特別的早餐",
                "event_type": "interaction",
                "priority": 2,  # NORMAL
                "conditions": {
                    "time_period": "morning",
                    "affection_min": 30,
                    "probability": 0.3,
                    "cooldown_hours": 24,
                },
                "dialogue_id": "morning_surprise_01",
                "effects": {
                    "affection_change": 3,
                    "flags": {"special_breakfast": True},
                },
            },
            "afternoon_nap": {
                "id": "afternoon_nap",
                "name": "午後小憩",
                "description": "和にゃんこ一起午睡",
                "event_type": "interaction",
                "priority": 2,  # NORMAL
                "conditions": {
                    "time_period": "afternoon",
                    "affection_min": 40,
                    "probability": 0.2,
                    "weekday": ["saturday", "sunday"],
                },
                "dialogue_id": "afternoon_nap_01",
                "effects": {"affection_change": 5, "flags": {"nap_together": True}},
            },
            "evening_confession": {
                "id": "evening_confession",
                "name": "傍晚告白",
                "description": "にゃんこ在傍晚時分表達愛意",
                "event_type": "special",
                "priority": 3,  # HIGH
                "conditions": {
                    "time_period": "evening",
                    "affection_min": 75,
                    "flags_required": {"confession_unlocked": True},
                    "max_triggers": 1,
                },
                "dialogue_id": "evening_confession_01",
                "effects": {
                    "affection_change": 10,
                    "flags": {"confession_completed": True},
                },
            },
            "random_headpat": {
                "id": "random_headpat",
                "name": "隨機摸頭",
                "description": "にゃんこ突然要求摸頭",
                "event_type": "random",
                "priority": 1,  # LOW
                "conditions": {
                    "affection_min": 20,
                    "probability": 0.15,
                    "cooldown_hours": 6,
                },
                "dialogue_id": "random_headpat_01",
                "effects": {"affection_change": 2},
            },
            "birthday_celebration": {
                "id": "birthday_celebration",
                "name": "生日慶祝",
                "description": "にゃんこ為你準備生日驚喜",
                "event_type": "special",
                "priority": 4,  # CRITICAL
                "conditions": {
                    "flags_required": {"is_birthday": True},
                    "max_triggers": 1,
                },
                "dialogue_id": "birthday_celebration_01",
                "effects": {
                    "affection_change": 15,
                    "flags": {"birthday_celebrated": True},
                },
            },
        }

        for event_id, event_data in default_events.items():
            self.events[event_id] = GameEvent(event_data)

        # 設定隨機事件池
        self.random_event_pool = ["random_headpat", "morning_surprise"]

        print(f"載入了 {len(self.events)} 個預設事件")

    def update(self, dt: float, game_state: Dict[str, Any]):
        """
        更新事件系統

        Args:
            dt: 時間差
            game_state: 遊戲狀態
        """
        if not self.auto_process_events:
            return

        # 檢查事件觸發條件
        self._check_event_triggers(game_state)

        # 處理事件佇列
        self._process_event_queue(game_state)

        # 隨機事件檢查
        self._check_random_events(game_state)

    def _check_event_triggers(self, game_state: Dict[str, Any]):
        """檢查事件觸發條件"""
        for event_id, event in self.events.items():
            if not event.is_active:
                continue

            # 檢查冷卻時間
            if not self._check_cooldown(event_id, event):
                continue

            # 檢查最大觸發次數
            if not self._check_max_triggers(event_id, event):
                continue

            # 檢查觸發條件
            if event.conditions.check_conditions(game_state):
                self.queue_event(event_id, game_state)

    def _check_cooldown(self, event_id: str, event: GameEvent) -> bool:
        """檢查事件冷卻時間"""
        if event.conditions.cooldown_hours <= 0:
            return True

        if event.last_triggered is None:
            return True

        # 這裡需要與時間系統整合來計算時間差
        # 暫時簡化處理
        return True

    def _check_max_triggers(self, event_id: str, event: GameEvent) -> bool:
        """檢查最大觸發次數"""
        if event.conditions.max_triggers == -1:
            return True

        return event.trigger_count < event.conditions.max_triggers

    def _check_random_events(self, game_state: Dict[str, Any]):
        """檢查隨機事件"""
        if not self.random_event_pool:
            return

        # 隨機事件觸發機率較低
        if random.random() > 0.05:  # 5% 基礎概率
            return

        # 隨機選擇一個事件
        event_id = random.choice(self.random_event_pool)
        event = self.events.get(event_id)

        if event and event.is_active and event.conditions.check_conditions(game_state):
            self.queue_event(event_id, game_state)

    def queue_event(
        self,
        event_id: str,
        game_state: Dict[str, Any],
        priority_override: Optional[EventPriority] = None,
    ):
        """
        將事件加入佇列

        Args:
            event_id: 事件ID
            game_state: 遊戲狀態
            priority_override: 優先級覆蓋
        """
        if event_id not in self.events:
            print(f"警告: 未找到事件 {event_id}")
            return

        event = self.events[event_id]

        # 檢查佇列大小限制
        if len(self.event_queue) >= self.max_queue_size:
            print("事件佇列已滿，移除最舊的低優先級事件")
            self._remove_lowest_priority_event()

        # 創建事件項目
        event_item = {
            "event_id": event_id,
            "priority": priority_override or event.priority,
            "timestamp": game_state.get("current_time", ""),
            "game_state": game_state.copy(),
        }

        # 插入佇列並排序
        self.event_queue.append(event_item)
        self.event_queue.sort(key=lambda x: x["priority"].value, reverse=True)

        print(f"事件 '{event.name}' 已加入佇列")

    def _remove_lowest_priority_event(self):
        """移除最低優先級的事件"""
        if not self.event_queue:
            return

        # 找到最低優先級的事件
        lowest_priority = min(self.event_queue, key=lambda x: x["priority"].value)
        self.event_queue.remove(lowest_priority)

    def _process_event_queue(self, game_state: Dict[str, Any]):
        """處理事件佇列"""
        if not self.event_queue:
            return

        # 取出最高優先級的事件
        event_item = self.event_queue.pop(0)
        event_id = event_item["event_id"]

        self.trigger_event(event_id, game_state)

    def trigger_event(self, event_id: str, game_state: Dict[str, Any]) -> bool:
        """
        觸發事件

        Args:
            event_id: 事件ID
            game_state: 遊戲狀態

        Returns:
            bool: 是否成功觸發
        """
        if event_id not in self.events:
            print(f"錯誤: 未找到事件 {event_id}")
            return False

        event = self.events[event_id]

        print(f"觸發事件: {event.name}")

        # 更新觸發狀態
        event.trigger_count += 1
        event.last_triggered = game_state.get("current_time")

        # 記錄到歷史
        self._record_event_history(event_id, event, game_state)

        # 執行事件動作
        self._execute_event_actions(event, game_state)

        # 應用事件效果
        self._apply_event_effects(event, game_state)

        # 觸發對話
        if event.dialogue_id:
            self._trigger_event_dialogue(event.dialogue_id, game_state)

        # 執行回調函數
        if event.callback_function:
            self._execute_callback(event.callback_function, event, game_state)

        # 觸發回調
        if self.on_event_triggered:
            self.on_event_triggered(event_id, event, game_state)

        return True

    def _record_event_history(
        self, event_id: str, event: GameEvent, game_state: Dict[str, Any]
    ):
        """記錄事件歷史"""
        history_entry = {
            "event_id": event_id,
            "event_name": event.name,
            "timestamp": game_state.get("current_time", ""),
            "trigger_count": event.trigger_count,
        }

        self.event_history.append(history_entry)
        self.triggered_events[event_id] = self.triggered_events.get(event_id, 0) + 1

        # 保持歷史記錄大小
        if len(self.event_history) > 100:
            self.event_history.pop(0)

    def _execute_event_actions(self, event: GameEvent, game_state: Dict[str, Any]):
        """執行事件動作"""
        for action in event.actions:
            action_type = action.get("type", "")

            if action_type == "show_message":
                message = action.get("message", "")
                print(f"事件訊息: {message}")

            elif action_type == "play_sound":
                sound_file = action.get("sound_file", "")
                print(f"播放音效: {sound_file}")

            elif action_type == "change_scene":
                scene_name = action.get("scene_name", "")
                print(f"切換場景: {scene_name}")

    def _apply_event_effects(self, event: GameEvent, game_state: Dict[str, Any]):
        """應用事件效果"""
        effects = event.effects

        # 好感度變化
        affection_change = effects.get("affection_change", 0)
        if affection_change != 0:
            current_affection = game_state.get("nyanko_affection", 0)
            new_affection = max(0, min(100, current_affection + affection_change))
            game_state["nyanko_affection"] = new_affection
            print(f"好感度變化: {affection_change:+d} (當前: {new_affection})")

        # 設定旗標
        flags = effects.get("flags", {})
        if flags:
            if "flags" not in game_state:
                game_state["flags"] = {}
            game_state["flags"].update(flags)
            print(f"設定旗標: {flags}")

        # 物品獎勵
        items = effects.get("items", {})
        if items:
            if "items" not in game_state:
                game_state["items"] = {}
            for item_id, quantity in items.items():
                current_quantity = game_state["items"].get(item_id, 0)
                game_state["items"][item_id] = current_quantity + quantity
                print(f"獲得物品: {item_id} x{quantity}")

    def _trigger_event_dialogue(self, dialogue_id: str, game_state: Dict[str, Any]):
        """觸發事件對話"""
        # 這裡需要與對話系統整合
        dialogue_system = getattr(self.game_engine, "dialogue_system", None)
        if dialogue_system:
            dialogue_system.start_dialogue(dialogue_id, game_state)
        else:
            print(f"觸發對話: {dialogue_id}")

    def _execute_callback(
        self, callback_name: str, event: GameEvent, game_state: Dict[str, Any]
    ):
        """執行回調函數"""
        print(f"執行回調函數: {callback_name}")

        # 根據回調名稱執行相應邏輯
        if callback_name == "morning_routine":
            self._handle_morning_routine(game_state)
        elif callback_name == "confession_accepted":
            self._handle_confession_accepted(game_state)
        elif callback_name == "birthday_celebration":
            self._handle_birthday_celebration(game_state)

    def _handle_morning_routine(self, game_state: Dict[str, Any]):
        """處理早晨例行程序"""
        print("執行早晨例行程序")

    def _handle_confession_accepted(self, game_state: Dict[str, Any]):
        """處理告白被接受"""
        print("告白被接受！")
        game_state.setdefault("flags", {})["relationship_established"] = True

    def _handle_birthday_celebration(self, game_state: Dict[str, Any]):
        """處理生日慶祝"""
        print("生日慶祝活動！")

    def force_trigger_event(self, event_id: str, game_state: Dict[str, Any]) -> bool:
        """
        強制觸發事件（忽略條件檢查）

        Args:
            event_id: 事件ID
            game_state: 遊戲狀態

        Returns:
            bool: 是否成功觸發
        """
        if event_id not in self.events:
            return False

        print(f"強制觸發事件: {self.events[event_id].name}")
        return self.trigger_event(event_id, game_state)

    def add_event(self, event_data: Dict[str, Any]) -> bool:
        """
        添加新事件

        Args:
            event_data: 事件資料

        Returns:
            bool: 是否成功添加
        """
        try:
            event = GameEvent(event_data)
            self.events[event.id] = event
            print(f"添加事件: {event.name}")
            return True
        except Exception as e:
            print(f"添加事件失敗: {e}")
            return False

    def remove_event(self, event_id: str) -> bool:
        """
        移除事件

        Args:
            event_id: 事件ID

        Returns:
            bool: 是否成功移除
        """
        if event_id in self.events:
            event_name = self.events[event_id].name
            del self.events[event_id]
            print(f"移除事件: {event_name}")
            return True
        return False

    def enable_event(self, event_id: str):
        """啟用事件"""
        if event_id in self.events:
            self.events[event_id].is_active = True
            print(f"啟用事件: {self.events[event_id].name}")

    def disable_event(self, event_id: str):
        """停用事件"""
        if event_id in self.events:
            self.events[event_id].is_active = False
            print(f"停用事件: {self.events[event_id].name}")

    def clear_event_queue(self):
        """清空事件佇列"""
        self.event_queue.clear()
        print("事件佇列已清空")

    def get_event_statistics(self) -> Dict[str, Any]:
        """獲取事件統計資訊"""
        total_events = len(self.events)
        active_events = sum(1 for event in self.events.values() if event.is_active)
        total_triggers = sum(self.triggered_events.values())

        return {
            "total_events": total_events,
            "active_events": active_events,
            "queue_size": len(self.event_queue),
            "total_triggers": total_triggers,
            "history_size": len(self.event_history),
            "triggered_events": self.triggered_events.copy(),
        }

    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的事件記錄"""
        return self.event_history[-count:] if self.event_history else []

    def save_data(self) -> Dict[str, Any]:
        """儲存事件系統資料"""
        return {
            "triggered_events": self.triggered_events.copy(),
            "event_history": self.event_history.copy(),
            "event_states": {
                event_id: {
                    "trigger_count": event.trigger_count,
                    "last_triggered": event.last_triggered,
                    "is_active": event.is_active,
                }
                for event_id, event in self.events.items()
            },
        }

    def load_data(self, data: Dict[str, Any]) -> bool:
        """載入事件系統資料"""
        try:
            self.triggered_events = data.get("triggered_events", {})
            self.event_history = data.get("event_history", [])

            # 載入事件狀態
            event_states = data.get("event_states", {})
            for event_id, state in event_states.items():
                if event_id in self.events:
                    event = self.events[event_id]
                    event.trigger_count = state.get("trigger_count", 0)
                    event.last_triggered = state.get("last_triggered")
                    event.is_active = state.get("is_active", True)

            print("事件系統資料載入成功")
            return True

        except Exception as e:
            print(f"載入事件系統資料失敗: {e}")
            return False

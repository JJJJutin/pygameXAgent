# -*- coding: utf-8 -*-
"""
日常事件系統
管理遊戲中的日常事件、特殊活動和隨機事件
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class EventType(Enum):
    """事件類型"""

    DAILY = "daily"  # 日常事件
    SPECIAL = "special"  # 特殊事件
    RANDOM = "random"  # 隨機事件
    SEASONAL = "seasonal"  # 季節事件
    MILESTONE = "milestone"  # 里程碑事件


class EventPriority(Enum):
    """事件優先級"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class DailyEvent:
    """日常事件類別"""

    def __init__(
        self,
        event_id: str,
        name: str,
        description: str,
        event_type: EventType,
        priority: EventPriority = EventPriority.NORMAL,
    ):
        self.event_id = event_id
        self.name = name
        self.description = description
        self.event_type = event_type
        self.priority = priority

        # 觸發條件
        self.conditions = {}
        self.time_period = None
        self.required_affection = 0
        self.required_day = 0
        self.weather_condition = None
        self.location_condition = None

        # 事件結果
        self.dialogue_id = None
        self.affection_change = 0
        self.unlocks = []  # 解鎖的內容
        self.rewards = []  # 獎勵

        # 執行狀態
        self.is_executed = False
        self.execution_count = 0
        self.max_executions = -1  # -1 表示無限制

    def can_trigger(self, game_state: dict) -> bool:
        """檢查事件是否可以觸發"""
        # 檢查執行次數限制
        if self.max_executions > 0 and self.execution_count >= self.max_executions:
            return False

        # 檢查好感度要求
        if self.required_affection > 0:
            if game_state.get("nyanko_affection", 0) < self.required_affection:
                return False

        # 檢查日期要求
        if self.required_day > 0:
            if game_state.get("day_count", 0) < self.required_day:
                return False

        # 檢查時間段
        if self.time_period:
            if game_state.get("current_time_period") != self.time_period:
                return False

        # 檢查天氣條件
        if self.weather_condition:
            if game_state.get("weather") != self.weather_condition:
                return False

        # 檢查位置條件
        if self.location_condition:
            if game_state.get("current_location") != self.location_condition:
                return False

        # 檢查其他自定義條件
        for condition_key, condition_value in self.conditions.items():
            if game_state.get(condition_key) != condition_value:
                return False

        return True

    def execute(self, game_state: dict) -> dict:
        """執行事件"""
        self.is_executed = True
        self.execution_count += 1

        result = {
            "event_id": self.event_id,
            "dialogue_id": self.dialogue_id,
            "affection_change": self.affection_change,
            "unlocks": self.unlocks.copy(),
            "rewards": self.rewards.copy(),
            "message": f"觸發事件: {self.name}",
        }

        return result


class DailyEventSystem:
    """日常事件系統"""

    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.events: Dict[str, DailyEvent] = {}
        self.active_events: List[str] = []
        self.event_history: List[Dict] = []

        # 事件觸發概率
        self.random_event_chance = 0.3  # 30% 機會觸發隨機事件

        # 初始化事件
        self._initialize_events()

    def _initialize_events(self):
        """初始化所有事件"""
        self._create_daily_events()
        self._create_special_events()
        self._create_random_events()
        self._create_seasonal_events()
        self._create_milestone_events()

    def _create_daily_events(self):
        """創建日常事件"""
        # 早晨事件
        morning_greeting = DailyEvent(
            "morning_greeting",
            "早晨問候",
            "にゃんこ的早晨問候",
            EventType.DAILY,
            EventPriority.NORMAL,
        )
        morning_greeting.time_period = "morning"
        morning_greeting.dialogue_id = "greeting_morning_01"
        morning_greeting.affection_change = 1
        self.events[morning_greeting.event_id] = morning_greeting

        # 午後茶時間
        afternoon_tea = DailyEvent(
            "afternoon_tea",
            "午後茶時間",
            "和にゃんこ一起享受下午茶",
            EventType.DAILY,
            EventPriority.LOW,
        )
        afternoon_tea.time_period = "afternoon"
        afternoon_tea.dialogue_id = "afternoon_tea_time"
        afternoon_tea.affection_change = 2
        afternoon_tea.required_affection = 10
        self.events[afternoon_tea.event_id] = afternoon_tea

        # 晚餐準備
        dinner_prep = DailyEvent(
            "dinner_preparation",
            "晚餐準備",
            "和にゃんこ一起準備晚餐",
            EventType.DAILY,
            EventPriority.NORMAL,
        )
        dinner_prep.time_period = "evening"
        dinner_prep.dialogue_id = "cooking_together_01"
        dinner_prep.affection_change = 3
        self.events[dinner_prep.event_id] = dinner_prep

        # 睡前聊天
        bedtime_chat = DailyEvent(
            "bedtime_chat",
            "睡前聊天",
            "和にゃんこ的睡前溫馨時光",
            EventType.DAILY,
            EventPriority.NORMAL,
        )
        bedtime_chat.time_period = "night"
        bedtime_chat.dialogue_id = "night_sleep_together"
        bedtime_chat.affection_change = 2
        bedtime_chat.required_affection = 20
        self.events[bedtime_chat.event_id] = bedtime_chat

    def _create_special_events(self):
        """創建特殊事件"""
        # にゃんこ生日
        nyanko_birthday = DailyEvent(
            "nyanko_birthday",
            "にゃんこ的生日",
            "為にゃんこ慶祝生日",
            EventType.SPECIAL,
            EventPriority.HIGH,
        )
        nyanko_birthday.conditions = {"special_date": "nyanko_birthday"}
        nyanko_birthday.dialogue_id = "nyanko_birthday_01"
        nyanko_birthday.affection_change = 10
        nyanko_birthday.unlocks = ["birthday_memories"]
        nyanko_birthday.max_executions = 1
        self.events[nyanko_birthday.event_id] = nyanko_birthday

        # 情人節
        valentines_day = DailyEvent(
            "valentines_day",
            "情人節",
            "和にゃんこ的情人節",
            EventType.SPECIAL,
            EventPriority.HIGH,
        )
        valentines_day.conditions = {"special_date": "valentines_day"}
        valentines_day.dialogue_id = "valentines_day_01"
        valentines_day.affection_change = 8
        valentines_day.required_affection = 30
        valentines_day.unlocks = ["valentine_chocolate"]
        self.events[valentines_day.event_id] = valentines_day

        # 聖誕節
        christmas = DailyEvent(
            "christmas",
            "聖誕節",
            "和にゃんこ的聖誕節",
            EventType.SPECIAL,
            EventPriority.HIGH,
        )
        christmas.conditions = {"special_date": "christmas"}
        christmas.dialogue_id = "christmas_eve_01"
        christmas.affection_change = 7
        christmas.unlocks = ["christmas_decorations"]
        self.events[christmas.event_id] = christmas

    def _create_random_events(self):
        """創建隨機事件"""
        # にゃんこ撒嬌
        nyanko_spoiled = DailyEvent(
            "nyanko_spoiled",
            "にゃんこ撒嬌",
            "にゃんこ突然想要撒嬌",
            EventType.RANDOM,
            EventPriority.NORMAL,
        )
        nyanko_spoiled.dialogue_id = "cuddling_request_01"
        nyanko_spoiled.affection_change = 3
        nyanko_spoiled.required_affection = 25
        self.events[nyanko_spoiled.event_id] = nyanko_spoiled

        # 貓咪調皮
        nyanko_mischief = DailyEvent(
            "nyanko_mischief",
            "にゃんこ調皮",
            "にゃんこ做了調皮的事情",
            EventType.RANDOM,
            EventPriority.LOW,
        )
        nyanko_mischief.dialogue_id = "casual_chat_01"
        nyanko_mischief.affection_change = 1
        self.events[nyanko_mischief.event_id] = nyanko_mischief

        # 突然告白
        sudden_confession = DailyEvent(
            "sudden_confession",
            "突然告白",
            "にゃんこ突然想要告白",
            EventType.RANDOM,
            EventPriority.URGENT,
        )
        sudden_confession.dialogue_id = "confession_preparation"
        sudden_confession.affection_change = 15
        sudden_confession.required_affection = 80
        sudden_confession.required_day = 14
        sudden_confession.max_executions = 1
        self.events[sudden_confession.event_id] = sudden_confession

    def _create_seasonal_events(self):
        """創建季節事件"""
        # 雨天事件
        rainy_day = DailyEvent(
            "rainy_day_comfort",
            "雨天安慰",
            "雨天にゃんこ需要安慰",
            EventType.SEASONAL,
            EventPriority.NORMAL,
        )
        rainy_day.weather_condition = "rainy"
        rainy_day.dialogue_id = "rainy_day_01"
        rainy_day.affection_change = 4
        self.events[rainy_day.event_id] = rainy_day

        # 雪天事件
        snowy_day = DailyEvent(
            "snowy_day_play",
            "雪天玩耍",
            "和にゃんこ一起玩雪",
            EventType.SEASONAL,
            EventPriority.NORMAL,
        )
        snowy_day.weather_condition = "snowy"
        snowy_day.dialogue_id = "snow_day_01"
        snowy_day.affection_change = 5
        self.events[snowy_day.event_id] = snowy_day

    def _create_milestone_events(self):
        """創建里程碑事件"""
        # 第一週紀念
        first_week = DailyEvent(
            "first_week_milestone",
            "同居一週紀念",
            "和にゃんこ同居滿一週",
            EventType.MILESTONE,
            EventPriority.HIGH,
        )
        first_week.required_day = 7
        first_week.dialogue_id = "first_week_01"
        first_week.affection_change = 5
        first_week.unlocks = ["first_week_memory"]
        first_week.max_executions = 1
        self.events[first_week.event_id] = first_week

        # 好感度里程碑
        high_affection = DailyEvent(
            "high_affection_milestone",
            "深厚感情",
            "和にゃんこ的感情越來越深",
            EventType.MILESTONE,
            EventPriority.NORMAL,
        )
        high_affection.required_affection = 60
        high_affection.dialogue_id = "confession_preparation"
        high_affection.affection_change = 8
        high_affection.max_executions = 1
        self.events[high_affection.event_id] = high_affection

    def update(self, dt: float, game_state: dict):
        """更新事件系統"""
        # 檢查和觸發日常事件
        self._check_daily_events(game_state)

        # 檢查和觸發特殊事件
        self._check_special_events(game_state)

        # 檢查和觸發隨機事件
        if random.random() < self.random_event_chance * dt:
            self._check_random_events(game_state)

        # 檢查和觸發季節事件
        self._check_seasonal_events(game_state)

        # 檢查和觸發里程碑事件
        self._check_milestone_events(game_state)

    def _check_daily_events(self, game_state: dict):
        """檢查日常事件"""
        for event in self.events.values():
            if event.event_type == EventType.DAILY and event.can_trigger(game_state):
                if event.event_id not in self.active_events:
                    self._trigger_event(event, game_state)

    def _check_special_events(self, game_state: dict):
        """檢查特殊事件"""
        for event in self.events.values():
            if event.event_type == EventType.SPECIAL and event.can_trigger(game_state):
                if event.event_id not in self.active_events:
                    self._trigger_event(event, game_state)

    def _check_random_events(self, game_state: dict):
        """檢查隨機事件"""
        random_events = [
            e
            for e in self.events.values()
            if e.event_type == EventType.RANDOM and e.can_trigger(game_state)
        ]

        if random_events:
            # 根據優先級選擇事件
            random_events.sort(key=lambda x: x.priority.value, reverse=True)
            selected_event = random.choice(
                random_events[:3]
            )  # 從前3個最高優先級中隨機選擇

            if selected_event.event_id not in self.active_events:
                self._trigger_event(selected_event, game_state)

    def _check_seasonal_events(self, game_state: dict):
        """檢查季節事件"""
        for event in self.events.values():
            if event.event_type == EventType.SEASONAL and event.can_trigger(game_state):
                if event.event_id not in self.active_events:
                    self._trigger_event(event, game_state)

    def _check_milestone_events(self, game_state: dict):
        """檢查里程碑事件"""
        for event in self.events.values():
            if event.event_type == EventType.MILESTONE and event.can_trigger(
                game_state
            ):
                if event.event_id not in self.active_events:
                    self._trigger_event(event, game_state)

    def _trigger_event(self, event: DailyEvent, game_state: dict):
        """觸發事件"""
        result = event.execute(game_state)
        self.active_events.append(event.event_id)
        self.event_history.append(
            {
                "event": event,
                "result": result,
                "timestamp": datetime.now(),
                "game_state": game_state.copy(),
            }
        )

        # 通知遊戲引擎
        if self.game_engine and hasattr(self.game_engine, "dialogue_system"):
            if result["dialogue_id"]:
                # 檢查是否已有對話在進行中
                if self.game_engine.dialogue_system.is_active:
                    print(f"對話進行中，跳過日常事件對話: {result['dialogue_id']}")
                else:
                    self.game_engine.dialogue_system.start_dialogue(
                        result["dialogue_id"], game_state
                    )

        # 修改好感度
        if result["affection_change"] != 0 and hasattr(
            self.game_engine, "affection_system"
        ):
            self.game_engine.affection_system.change_affection(
                result["affection_change"], "nyanko", f"事件: {event.name}"
            )

        print(f"觸發事件: {event.name} ({event.event_id})")
        if result["affection_change"] != 0:
            print(f"好感度變化: {result['affection_change']:+d}")

    def get_available_events(self, game_state: dict) -> List[DailyEvent]:
        """獲取可用的事件列表"""
        available = []
        for event in self.events.values():
            if event.can_trigger(game_state):
                available.append(event)
        return available

    def get_random_event(self, game_state: dict = None) -> Optional[Dict[str, Any]]:
        """
        獲取隨機事件

        Args:
            game_state: 遊戲狀態

        Returns:
            Optional[Dict]: 隨機事件資料，如果沒有可用事件則返回None
        """
        if game_state is None:
            game_state = {}

        # 獲取隨機類型的事件
        random_events = [
            event
            for event in self.events.values()
            if event.event_type == EventType.RANDOM and event.can_trigger(game_state)
        ]

        if not random_events:
            return None

        # 隨機選擇一個事件
        selected_event = random.choice(random_events)

        return {
            "id": selected_event.event_id,
            "name": selected_event.name,
            "description": selected_event.description,
            "type": selected_event.event_type.value,
            "priority": selected_event.priority.value,
        }

    def get_event_history(self) -> List[Dict]:
        """獲取事件歷史"""
        return self.event_history.copy()

    def clear_active_events(self):
        """清空活躍事件列表（用於新的一天）"""
        self.active_events.clear()

    def set_special_date(self, date_type: str, game_state: dict):
        """設置特殊日期"""
        game_state["special_date"] = date_type

    def set_weather(self, weather: str, game_state: dict):
        """設置天氣"""
        game_state["weather"] = weather

    def add_custom_event(self, event: DailyEvent):
        """添加自定義事件"""
        self.events[event.event_id] = event

    def remove_event(self, event_id: str):
        """移除事件"""
        if event_id in self.events:
            del self.events[event_id]
        if event_id in self.active_events:
            self.active_events.remove(event_id)

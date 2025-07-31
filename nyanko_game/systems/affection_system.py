# -*- coding: utf-8 -*-
"""
好感度系統
管理角色好感度、關係等級、特殊事件觸發
"""

import json
import os
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from config.character_data import RELATIONSHIP_LEVELS, AFFECTION_MODIFIERS


class RelationshipLevel(Enum):
    """關係等級枚舉"""

    STRANGER = "stranger"  # 陌生人 (0-9)
    ACQUAINTANCE = "acquaintance"  # 認識 (10-24)
    FRIEND = "friend"  # 朋友 (25-49)
    CLOSE_FRIEND = "close_friend"  # 好朋友 (50-74)
    LOVE_INTEREST = "love_interest"  # 戀人 (75-89)
    BELOVED = "beloved"  # 摯愛 (90-100)


class AffectionEvent:
    """好感度事件類別"""

    def __init__(self, data: Dict[str, Any]):
        """初始化好感度事件"""
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.affection_threshold = data.get("affection_threshold", 0)
        self.relationship_level = data.get("relationship_level", "")
        self.trigger_once = data.get("trigger_once", True)
        self.dialogue_id = data.get("dialogue_id", "")
        self.rewards = data.get("rewards", {})
        self.unlock_flags = data.get("unlock_flags", {})
        self.conditions = data.get("conditions", {})


class AffectionSystem:
    """好感度系統主類別"""

    def __init__(self, game_engine):
        """初始化好感度系統"""
        self.game_engine = game_engine

        # 角色好感度數據
        self.character_affection: Dict[str, int] = {"nyanko": 0}

        # 關係等級
        self.character_relationships: Dict[str, RelationshipLevel] = {
            "nyanko": RelationshipLevel.STRANGER
        }

        # 好感度事件
        self.affection_events: Dict[str, AffectionEvent] = {}
        self.triggered_events: List[str] = []

        # 每日互動記錄
        self.daily_interactions: Dict[str, int] = {}
        self.max_daily_gain = 20  # 每日最大好感度增益

        # 特殊狀態
        self.confession_available = False
        self.special_flags: Dict[str, bool] = {}

        # 回調函數
        self.on_affection_change: Optional[Callable] = None
        self.on_relationship_change: Optional[Callable] = None
        self.on_special_event: Optional[Callable] = None

        # 載入事件資料
        self._load_affection_events()

    def _load_affection_events(self):
        """載入好感度事件資料"""
        events_data = {
            "first_meeting": {
                "id": "first_meeting",
                "name": "初次見面",
                "description": "與にゃんこ的第一次相遇",
                "affection_threshold": 0,
                "relationship_level": "stranger",
                "trigger_once": True,
                "dialogue_id": "first_meeting_01",
                "rewards": {"unlock_morning_greeting": True},
            },
            "friend_level": {
                "id": "friend_level",
                "name": "成為朋友",
                "description": "與にゃんこ建立了友誼",
                "affection_threshold": 25,
                "relationship_level": "friend",
                "trigger_once": True,
                "dialogue_id": "friend_milestone_01",
                "rewards": {"unlock_casual_topics": True},
            },
            "close_friend_level": {
                "id": "close_friend_level",
                "name": "親密朋友",
                "description": "與にゃんこ變成了親密朋友",
                "affection_threshold": 50,
                "relationship_level": "close_friend",
                "trigger_once": True,
                "dialogue_id": "close_friend_milestone_01",
                "rewards": {"unlock_intimate_conversations": True},
            },
            "confession": {
                "id": "confession",
                "name": "愛的告白",
                "description": "にゃんこ向你告白了",
                "affection_threshold": 75,
                "relationship_level": "love_interest",
                "trigger_once": True,
                "dialogue_id": "affection_50",
                "rewards": {"unlock_romantic_options": True},
                "unlock_flags": {"confession_unlocked": True},
            },
            "true_love": {
                "id": "true_love",
                "name": "真愛",
                "description": "與にゃんこ達成了真愛",
                "affection_threshold": 90,
                "relationship_level": "beloved",
                "trigger_once": True,
                "dialogue_id": "true_love_01",
                "rewards": {"unlock_special_endings": True},
            },
        }

        for event_id, event_data in events_data.items():
            self.affection_events[event_id] = AffectionEvent(event_data)

    def get_affection(self, character: str = "nyanko") -> int:
        """
        獲取角色好感度

        Args:
            character: 角色名稱

        Returns:
            int: 好感度值 (0-100)
        """
        return self.character_affection.get(character, 0)

    def set_affection(self, affection: int, character: str = "nyanko") -> bool:
        """
        設定角色好感度

        Args:
            affection: 好感度值
            character: 角色名稱

        Returns:
            bool: 是否成功設定
        """
        # 限制好感度範圍
        affection = max(0, min(100, affection))
        old_affection = self.character_affection.get(character, 0)

        if affection == old_affection:
            return False

        self.character_affection[character] = affection

        # 檢查關係等級變化
        old_level = self.character_relationships.get(
            character, RelationshipLevel.STRANGER
        )
        new_level = self._calculate_relationship_level(affection)

        if new_level != old_level:
            self.character_relationships[character] = new_level
            self._on_relationship_level_change(character, old_level, new_level)

        # 觸發回調
        if self.on_affection_change:
            self.on_affection_change(character, old_affection, affection)

        # 檢查事件觸發
        self._check_affection_events(character, affection)

        print(f"{character}好感度變化: {old_affection} → {affection}")
        print(f"關係等級: {new_level.value}")

        return True

    def change_affection(
        self, change: int, character: str = "nyanko", reason: str = ""
    ) -> int:
        """
        改變角色好感度

        Args:
            change: 好感度變化量
            character: 角色名稱
            reason: 變化原因

        Returns:
            int: 實際變化量
        """
        if change == 0:
            return 0

        current_affection = self.get_affection(character)

        # 檢查每日限制
        if change > 0:
            daily_total = self.daily_interactions.get(character, 0)
            if daily_total >= self.max_daily_gain:
                print(f"今日與{character}的互動已達上限")
                return 0

            # 限制增益量
            available_gain = self.max_daily_gain - daily_total
            change = min(change, available_gain)

        # 應用好感度修正
        adjusted_change = self._apply_affection_modifiers(change, current_affection)

        # 計算新好感度
        new_affection = max(0, min(100, current_affection + adjusted_change))
        actual_change = new_affection - current_affection

        # 更新好感度
        if actual_change != 0:
            self.set_affection(new_affection, character)

            # 記錄每日互動
            if actual_change > 0:
                self.daily_interactions[character] = (
                    self.daily_interactions.get(character, 0) + actual_change
                )

            # 記錄變化原因
            if reason:
                print(f"好感度變化原因: {reason}")

        return actual_change

    def _apply_affection_modifiers(self, change: int, current_affection: int) -> int:
        """應用好感度修正因子"""
        if change <= 0:
            return change

        # 根據當前好感度等級調整增益
        if current_affection < 25:
            # 低好感度階段，增益正常
            modifier = 1.0
        elif current_affection < 50:
            # 中等好感度階段，增益稍微減少
            modifier = 0.9
        elif current_affection < 75:
            # 高好感度階段，增益明顯減少
            modifier = 0.7
        else:
            # 最高好感度階段，增益大幅減少
            modifier = 0.5

        return int(change * modifier)

    def _calculate_relationship_level(self, affection: int) -> RelationshipLevel:
        """根據好感度計算關係等級"""
        if affection >= 90:
            return RelationshipLevel.BELOVED
        elif affection >= 75:
            return RelationshipLevel.LOVE_INTEREST
        elif affection >= 50:
            return RelationshipLevel.CLOSE_FRIEND
        elif affection >= 25:
            return RelationshipLevel.FRIEND
        elif affection >= 10:
            return RelationshipLevel.ACQUAINTANCE
        else:
            return RelationshipLevel.STRANGER

    def get_relationship_level(self, character: str = "nyanko") -> RelationshipLevel:
        """獲取角色關係等級"""
        return self.character_relationships.get(character, RelationshipLevel.STRANGER)

    def get_relationship_name(self, character: str = "nyanko") -> str:
        """獲取關係等級的中文名稱"""
        level = self.get_relationship_level(character)
        level_names = {
            RelationshipLevel.STRANGER: "陌生人",
            RelationshipLevel.ACQUAINTANCE: "認識",
            RelationshipLevel.FRIEND: "朋友",
            RelationshipLevel.CLOSE_FRIEND: "好朋友",
            RelationshipLevel.LOVE_INTEREST: "戀人",
            RelationshipLevel.BELOVED: "摯愛",
        }
        return level_names.get(level, "未知")

    def _on_relationship_level_change(
        self, character: str, old_level: RelationshipLevel, new_level: RelationshipLevel
    ):
        """處理關係等級變化"""
        print(f"{character}關係等級提升: {old_level.value} → {new_level.value}")

        if self.on_relationship_change:
            self.on_relationship_change(character, old_level, new_level)

    def _check_affection_events(self, character: str, affection: int):
        """檢查是否觸發好感度事件"""
        for event_id, event in self.affection_events.items():
            # 檢查是否已觸發
            if event.trigger_once and event_id in self.triggered_events:
                continue

            # 檢查好感度門檻
            if affection < event.affection_threshold:
                continue

            # 檢查其他條件
            if not self._check_event_conditions(event):
                continue

            # 觸發事件
            self._trigger_affection_event(event_id, event)

    def _check_event_conditions(self, event: AffectionEvent) -> bool:
        """檢查事件觸發條件"""
        # 檢查特殊旗標
        for flag, required_value in event.conditions.get("flags", {}).items():
            if self.special_flags.get(flag) != required_value:
                return False

        return True

    def _trigger_affection_event(self, event_id: str, event: AffectionEvent):
        """觸發好感度事件"""
        print(f"觸發好感度事件: {event.name}")

        # 標記為已觸發
        if event.trigger_once:
            self.triggered_events.append(event_id)

        # 應用獎勵
        for reward_type, reward_value in event.rewards.items():
            self._apply_event_reward(reward_type, reward_value)

        # 設定解鎖旗標
        for flag, value in event.unlock_flags.items():
            self.special_flags[flag] = value

        # 觸發特殊事件對話
        if event.dialogue_id and self.on_special_event:
            self.on_special_event(event_id, event.dialogue_id)

    def _apply_event_reward(self, reward_type: str, reward_value: Any):
        """應用事件獎勵"""
        if reward_type == "unlock_morning_greeting":
            self.special_flags["morning_greeting_unlocked"] = reward_value
        elif reward_type == "unlock_casual_topics":
            self.special_flags["casual_topics_unlocked"] = reward_value
        elif reward_type == "unlock_intimate_conversations":
            self.special_flags["intimate_conversations_unlocked"] = reward_value
        elif reward_type == "unlock_romantic_options":
            self.special_flags["romantic_options_unlocked"] = reward_value
        elif reward_type == "unlock_special_endings":
            self.special_flags["special_endings_unlocked"] = reward_value

        print(f"解鎖獎勵: {reward_type}")

    def reset_daily_interactions(self):
        """重置每日互動記錄"""
        self.daily_interactions.clear()
        print("每日互動記錄已重置")

    def get_daily_interaction_count(self, character: str = "nyanko") -> int:
        """獲取今日互動次數"""
        return self.daily_interactions.get(character, 0)

    def get_remaining_daily_gain(self, character: str = "nyanko") -> int:
        """獲取今日剩餘可獲得好感度"""
        used = self.daily_interactions.get(character, 0)
        return max(0, self.max_daily_gain - used)

    def is_flag_unlocked(self, flag: str) -> bool:
        """檢查特殊旗標是否解鎖"""
        return self.special_flags.get(flag, False)

    def set_flag(self, flag: str, value: bool):
        """設定特殊旗標"""
        self.special_flags[flag] = value

    def can_confess(self, character: str = "nyanko") -> bool:
        """檢查是否可以告白"""
        affection = self.get_affection(character)
        confession_unlocked = self.is_flag_unlocked("confession_unlocked")
        return affection >= 75 and confession_unlocked

    def get_affection_status_text(self, character: str = "nyanko") -> str:
        """獲取好感度狀態文字"""
        affection = self.get_affection(character)
        relationship = self.get_relationship_name(character)
        daily_used = self.get_daily_interaction_count(character)
        daily_remaining = self.get_remaining_daily_gain(character)

        status_text = f"好感度: {affection}/100\n"
        status_text += f"關係: {relationship}\n"
        status_text += f"今日互動: {daily_used}/{self.max_daily_gain}\n"
        status_text += f"剩餘增益: {daily_remaining}"

        return status_text

    def save_data(self) -> Dict[str, Any]:
        """儲存好感度系統資料"""
        save_data = {
            "character_affection": self.character_affection.copy(),
            "character_relationships": {
                k: v.value for k, v in self.character_relationships.items()
            },
            "triggered_events": self.triggered_events.copy(),
            "daily_interactions": self.daily_interactions.copy(),
            "special_flags": self.special_flags.copy(),
        }
        return save_data

    def load_data(self, data: Dict[str, Any]) -> bool:
        """載入好感度系統資料"""
        try:
            self.character_affection = data.get("character_affection", {"nyanko": 0})

            # 載入關係等級
            relationships_data = data.get("character_relationships", {})
            self.character_relationships = {}
            for char, level_str in relationships_data.items():
                try:
                    self.character_relationships[char] = RelationshipLevel(level_str)
                except ValueError:
                    self.character_relationships[char] = RelationshipLevel.STRANGER

            self.triggered_events = data.get("triggered_events", [])
            self.daily_interactions = data.get("daily_interactions", {})
            self.special_flags = data.get("special_flags", {})

            print("好感度系統資料載入成功")
            return True

        except Exception as e:
            print(f"載入好感度系統資料失敗: {e}")
            return False

    def get_progress_to_next_level(self, character: str = "nyanko") -> tuple:
        """
        獲取到下一關係等級的進度

        Returns:
            tuple: (當前進度, 總需求, 百分比)
        """
        affection = self.get_affection(character)
        current_level = self.get_relationship_level(character)

        # 定義等級門檻
        level_thresholds = {
            RelationshipLevel.STRANGER: (0, 10),
            RelationshipLevel.ACQUAINTANCE: (10, 25),
            RelationshipLevel.FRIEND: (25, 50),
            RelationshipLevel.CLOSE_FRIEND: (50, 75),
            RelationshipLevel.LOVE_INTEREST: (75, 90),
            RelationshipLevel.BELOVED: (90, 100),
        }

        if current_level == RelationshipLevel.BELOVED:
            return (100, 100, 100.0)

        current_min, next_threshold = level_thresholds[current_level]
        progress = affection - current_min
        total_needed = next_threshold - current_min
        percentage = (progress / total_needed) * 100 if total_needed > 0 else 100

        return (progress, total_needed, percentage)

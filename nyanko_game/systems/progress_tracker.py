# -*- coding: utf-8 -*-
"""
遊戲進度追蹤系統
負責追蹤玩家的遊戲進度、解鎖內容、成就等
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class ProgressType(Enum):
    """進度類型"""

    STORY = "story"  # 劇情進度
    RELATIONSHIP = "relationship"  # 關係進度
    ACHIEVEMENT = "achievement"  # 成就
    UNLOCK = "unlock"  # 解鎖內容
    COLLECTION = "collection"  # 收集品


class Achievement:
    """成就類別"""

    def __init__(
        self,
        achievement_id: str,
        name: str,
        description: str,
        unlock_condition: Dict[str, Any],
        reward: Dict[str, Any] = None,
    ):
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.unlock_condition = unlock_condition
        self.reward = reward or {}
        self.is_unlocked = False
        self.unlock_date = None

    def check_unlock(self, game_state: dict) -> bool:
        """檢查成就是否解鎖"""
        if self.is_unlocked:
            return False

        # 檢查解鎖條件
        for key, value in self.unlock_condition.items():
            if key == "affection_min":
                if game_state.get("nyanko_affection", 0) < value:
                    return False
            elif key == "day_count_min":
                if game_state.get("day_count", 0) < value:
                    return False
            elif key == "dialogue_count_min":
                if game_state.get("dialogue_count", 0) < value:
                    return False
            elif key == "special_events":
                completed_events = game_state.get("completed_special_events", [])
                for required_event in value:
                    if required_event not in completed_events:
                        return False
            elif key == "flags":
                flags = game_state.get("flags", {})
                for flag_key, flag_value in value.items():
                    if flags.get(flag_key) != flag_value:
                        return False
            else:
                # 通用條件檢查
                if game_state.get(key) != value:
                    return False

        return True

    def unlock(self):
        """解鎖成就"""
        self.is_unlocked = True
        self.unlock_date = datetime.now()


class ProgressTracker:
    """遊戲進度追蹤器"""

    def __init__(self, game_engine):
        self.game_engine = game_engine

        # 進度資料
        self.story_progress = {}
        self.relationship_milestones = []
        self.achievements = {}
        self.unlocked_content = set()
        self.collections = {}

        # 統計資料
        self.stats = {
            "play_time": 0.0,  # 遊玩時間（秒）
            "dialogue_count": 0,  # 對話次數
            "choice_count": 0,  # 選擇次數
            "scene_visits": {},  # 場景訪問次數
            "affection_history": [],  # 好感度變化歷史
            "special_events_completed": [],  # 完成的特殊事件
            "daily_activities": {},  # 日常活動統計
        }

        # 遊戲狀態
        self.current_save_slot = None
        self.last_save_time = None

        # 初始化成就系統
        self._initialize_achievements()

    def _initialize_achievements(self):
        """初始化成就系統"""
        # 關係成就
        self.achievements["first_meeting"] = Achievement(
            "first_meeting",
            "初次相遇",
            "第一次與にゃんこ對話",
            {"dialogue_count_min": 1},
            {"affection_bonus": 2},
        )

        self.achievements["friend_level"] = Achievement(
            "friend_level",
            "朋友關係",
            "與にゃんこ達到朋友關係",
            {"affection_min": 20},
            {"unlock_content": "friend_activities"},
        )

        self.achievements["close_friend"] = Achievement(
            "close_friend",
            "親密朋友",
            "與にゃんこ達到親密朋友關係",
            {"affection_min": 40},
            {"unlock_content": "intimate_conversations"},
        )

        self.achievements["lover_level"] = Achievement(
            "lover_level",
            "戀人關係",
            "與にゃんこ達到戀人關係",
            {"affection_min": 60},
            {"unlock_content": "romantic_activities"},
        )

        self.achievements["true_love"] = Achievement(
            "true_love",
            "真愛",
            "與にゃんこ達到真愛關係",
            {"affection_min": 80},
            {"unlock_content": "special_endings"},
        )

        # 時間成就
        self.achievements["first_week"] = Achievement(
            "first_week",
            "第一週",
            "與にゃんこ同居滿一週",
            {"day_count_min": 7},
            {"affection_bonus": 5},
        )

        self.achievements["one_month"] = Achievement(
            "one_month",
            "一個月",
            "與にゃんこ同居滿一個月",
            {"day_count_min": 30},
            {"unlock_content": "monthly_special"},
        )

        # 活動成就
        self.achievements["cook_master"] = Achievement(
            "cook_master",
            "料理達人",
            "與にゃんこ一起料理10次",
            {"cooking_count": 10},
            {"unlock_content": "special_recipes"},
        )

        self.achievements["entertainment_lover"] = Achievement(
            "entertainment_lover",
            "娛樂愛好者",
            "與にゃんこ一起娛樂20次",
            {"entertainment_count": 20},
            {"unlock_content": "special_games"},
        )

        # 特殊事件成就
        self.achievements["birthday_celebration"] = Achievement(
            "birthday_celebration",
            "生日慶祝",
            "為にゃんこ慶祝生日",
            {"special_events": ["nyanko_birthday"]},
            {"unlock_content": "birthday_memories"},
        )

        self.achievements["valentine_romance"] = Achievement(
            "valentine_romance",
            "情人節浪漫",
            "與にゃんこ度過情人節",
            {"special_events": ["valentines_day"]},
            {"unlock_content": "valentine_special"},
        )

        self.achievements["confession_success"] = Achievement(
            "confession_success",
            "告白成功",
            "成功向にゃんこ告白",
            {"flags": {"confession_success": True}},
            {"unlock_content": "confession_ending"},
        )

        # 對話成就
        self.achievements["chatterbox"] = Achievement(
            "chatterbox",
            "話匣子",
            "進行100次對話",
            {"dialogue_count_min": 100},
            {"affection_bonus": 10},
        )

        self.achievements["deep_conversation"] = Achievement(
            "deep_conversation",
            "深度對話",
            "進行50次深度對話",
            {"deep_dialogue_count": 50},
            {"unlock_content": "philosophical_talks"},
        )

        # 探索成就
        self.achievements["home_explorer"] = Achievement(
            "home_explorer",
            "家庭探索者",
            "訪問所有房間",
            {"visited_scenes": ["living_room", "kitchen", "bedroom", "bathroom"]},
            {"unlock_content": "secret_areas"},
        )

    def update_progress(self, progress_type: ProgressType, key: str, value: Any):
        """更新進度"""
        if progress_type == ProgressType.STORY:
            self.story_progress[key] = value
        elif progress_type == ProgressType.RELATIONSHIP:
            if value not in self.relationship_milestones:
                self.relationship_milestones.append(value)
        elif progress_type == ProgressType.UNLOCK:
            self.unlocked_content.add(value)
        elif progress_type == ProgressType.COLLECTION:
            if key not in self.collections:
                self.collections[key] = []
            if value not in self.collections[key]:
                self.collections[key].append(value)

    def update_stats(self, stat_key: str, value: Any, increment: bool = False):
        """更新統計資料"""
        if increment:
            if stat_key in self.stats:
                if isinstance(self.stats[stat_key], (int, float)):
                    self.stats[stat_key] += value
                elif isinstance(self.stats[stat_key], list):
                    self.stats[stat_key].append(value)
                elif isinstance(self.stats[stat_key], dict):
                    for k, v in value.items():
                        self.stats[stat_key][k] = self.stats[stat_key].get(k, 0) + v
            else:
                self.stats[stat_key] = value
        else:
            self.stats[stat_key] = value

    def track_dialogue(self, dialogue_id: str, choices_made: List[str] = None):
        """追蹤對話"""
        self.update_stats("dialogue_count", 1, increment=True)

        if choices_made:
            self.update_stats("choice_count", len(choices_made), increment=True)

        # 檢查是否為深度對話
        if self._is_deep_dialogue(dialogue_id):
            self.update_stats("deep_dialogue_count", 1, increment=True)

    def track_scene_visit(self, scene_name: str):
        """追蹤場景訪問"""
        scene_visits = self.stats.get("scene_visits", {})
        scene_visits[scene_name] = scene_visits.get(scene_name, 0) + 1
        self.stats["scene_visits"] = scene_visits

        # 更新訪問過的場景列表
        visited_scenes = self.stats.get("visited_scenes", [])
        if scene_name not in visited_scenes:
            visited_scenes.append(scene_name)
            self.stats["visited_scenes"] = visited_scenes

    def track_activity(self, activity_type: str, activity_name: str):
        """追蹤活動"""
        activities = self.stats.get("daily_activities", {})
        if activity_type not in activities:
            activities[activity_type] = {}
        activities[activity_type][activity_name] = (
            activities[activity_type].get(activity_name, 0) + 1
        )
        self.stats["daily_activities"] = activities

        # 更新特定活動計數
        if activity_type == "cooking":
            self.update_stats("cooking_count", 1, increment=True)
        elif activity_type == "entertainment":
            self.update_stats("entertainment_count", 1, increment=True)

    def track_affection_change(self, old_value: int, new_value: int, reason: str):
        """追蹤好感度變化"""
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "old_value": old_value,
            "new_value": new_value,
            "change": new_value - old_value,
            "reason": reason,
        }

        affection_history = self.stats.get("affection_history", [])
        affection_history.append(change_record)
        self.stats["affection_history"] = affection_history

    def track_special_event(self, event_id: str):
        """追蹤特殊事件"""
        completed_events = self.stats.get("special_events_completed", [])
        if event_id not in completed_events:
            completed_events.append(event_id)
            self.stats["special_events_completed"] = completed_events

    def set_flag(self, flag_name: str, value: Any, game_state: dict):
        """設置遊戲標誌"""
        if "flags" not in game_state:
            game_state["flags"] = {}
        game_state["flags"][flag_name] = value

    def check_achievements(self, game_state: dict) -> List[Achievement]:
        """檢查並解鎖成就"""
        newly_unlocked = []

        # 更新遊戲狀態中的統計資料
        for key, value in self.stats.items():
            game_state[key] = value

        for achievement in self.achievements.values():
            if achievement.check_unlock(game_state):
                achievement.unlock()
                newly_unlocked.append(achievement)

                # 應用成就獎勵
                if achievement.reward:
                    self._apply_achievement_reward(achievement.reward, game_state)

                print(f"成就解鎖: {achievement.name} - {achievement.description}")

        return newly_unlocked

    def _apply_achievement_reward(self, reward: Dict[str, Any], game_state: dict):
        """應用成就獎勵"""
        if "affection_bonus" in reward:
            if (
                hasattr(self.game_engine, "affection_system")
                and self.game_engine.affection_system
            ):
                self.game_engine.affection_system.change_affection(
                    reward["affection_bonus"], "nyanko", "成就獎勵"
                )

        if "unlock_content" in reward:
            self.unlocked_content.add(reward["unlock_content"])

    def _is_deep_dialogue(self, dialogue_id: str) -> bool:
        """判斷是否為深度對話"""
        deep_dialogue_keywords = [
            "confession",
            "heart_to_heart",
            "intimate",
            "romantic",
            "future",
            "feelings",
            "love",
            "relationship",
        ]

        for keyword in deep_dialogue_keywords:
            if keyword in dialogue_id.lower():
                return True
        return False

    def get_progress_summary(self) -> Dict[str, Any]:
        """獲取進度總結"""
        unlocked_achievements = [a for a in self.achievements.values() if a.is_unlocked]

        return {
            "story_progress": self.story_progress,
            "relationship_milestones": self.relationship_milestones,
            "unlocked_achievements": len(unlocked_achievements),
            "total_achievements": len(self.achievements),
            "unlocked_content": list(self.unlocked_content),
            "statistics": self.stats,
            "achievement_completion": len(unlocked_achievements)
            / len(self.achievements)
            * 100,
        }

    def get_achievement_list(self) -> List[Dict[str, Any]]:
        """獲取成就列表"""
        achievement_list = []

        for achievement in self.achievements.values():
            achievement_data = {
                "id": achievement.achievement_id,
                "name": achievement.name,
                "description": achievement.description,
                "is_unlocked": achievement.is_unlocked,
                "unlock_date": (
                    achievement.unlock_date.isoformat()
                    if achievement.unlock_date
                    else None
                ),
            }
            achievement_list.append(achievement_data)

        return achievement_list

    def is_content_unlocked(self, content_id: str) -> bool:
        """檢查內容是否已解鎖"""
        return content_id in self.unlocked_content

    def save_progress(self, save_path: str):
        """保存進度"""
        progress_data = {
            "story_progress": self.story_progress,
            "relationship_milestones": self.relationship_milestones,
            "unlocked_content": list(self.unlocked_content),
            "collections": self.collections,
            "statistics": self.stats,
            "achievements": {
                aid: {
                    "is_unlocked": achievement.is_unlocked,
                    "unlock_date": (
                        achievement.unlock_date.isoformat()
                        if achievement.unlock_date
                        else None
                    ),
                }
                for aid, achievement in self.achievements.items()
            },
            "save_timestamp": datetime.now().isoformat(),
        }

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
            self.last_save_time = datetime.now()
            print(f"進度已保存至: {save_path}")
        except Exception as e:
            print(f"保存進度失敗: {e}")

    def load_progress(self, save_path: str) -> bool:
        """載入進度"""
        if not os.path.exists(save_path):
            print(f"存檔文件不存在: {save_path}")
            return False

        try:
            with open(save_path, "r", encoding="utf-8") as f:
                progress_data = json.load(f)

            self.story_progress = progress_data.get("story_progress", {})
            self.relationship_milestones = progress_data.get(
                "relationship_milestones", []
            )
            self.unlocked_content = set(progress_data.get("unlocked_content", []))
            self.collections = progress_data.get("collections", {})
            self.stats = progress_data.get("statistics", {})

            # 載入成就狀態
            achievements_data = progress_data.get("achievements", {})
            for aid, achievement_state in achievements_data.items():
                if aid in self.achievements:
                    achievement = self.achievements[aid]
                    achievement.is_unlocked = achievement_state.get(
                        "is_unlocked", False
                    )
                    unlock_date_str = achievement_state.get("unlock_date")
                    if unlock_date_str:
                        achievement.unlock_date = datetime.fromisoformat(
                            unlock_date_str
                        )

            print(f"進度已載入: {save_path}")
            return True

        except Exception as e:
            print(f"載入進度失敗: {e}")
            return False

    def reset_progress(self):
        """重置進度"""
        self.story_progress.clear()
        self.relationship_milestones.clear()
        self.unlocked_content.clear()
        self.collections.clear()

        # 重置統計資料
        self.stats = {
            "play_time": 0.0,
            "dialogue_count": 0,
            "choice_count": 0,
            "scene_visits": {},
            "affection_history": [],
            "special_events_completed": [],
            "daily_activities": {},
        }

        # 重置成就
        for achievement in self.achievements.values():
            achievement.is_unlocked = False
            achievement.unlock_date = None

        print("進度已重置")

    def update_play_time(self, dt: float):
        """更新遊玩時間"""
        self.update_stats("play_time", dt, increment=True)

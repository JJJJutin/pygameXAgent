"""
事件驅動時間系統 (Event-Driven Time System)
===========================================

設計理念：
- 時間推進完全由玩家行動觸發
- 每個時間段都對應具體的活動/事件
- 強調玩家選擇的意義和後果
- 參考培養遊戲和戀愛模擬遊戲的設計

作者：GitHub Copilot
日期：2025年8月1日
"""

from enum import Enum
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json


class TimePeriod(Enum):
    """時間段枚舉"""

    EARLY_MORNING = "early_morning"  # 清晨 (6:00-8:00)
    MORNING = "morning"  # 上午 (8:00-12:00)
    AFTERNOON = "afternoon"  # 下午 (12:00-18:00)
    EVENING = "evening"  # 傍晚 (18:00-21:00)
    NIGHT = "night"  # 夜晚 (21:00-24:00)
    LATE_NIGHT = "late_night"  # 深夜 (0:00-6:00)


class ActivityType(Enum):
    """活動類型"""

    DAILY_ROUTINE = "daily_routine"  # 日常活動 (起床、洗漱、用餐)
    INTERACTION = "interaction"  # 互動活動 (對話、遊戲)
    CARE = "care"  # 照顧活動 (餵食、清潔)
    ENTERTAINMENT = "entertainment"  # 娛樂活動 (看電視、聽音樂)
    REST = "rest"  # 休息活動 (小憩、睡覺)
    SPECIAL = "special"  # 特殊活動 (約會、事件)


@dataclass
class ActivityChoice:
    """活動選擇"""

    id: str
    name: str
    description: str
    activity_type: ActivityType
    time_cost: int  # 消耗的時間點數 (1-3)
    energy_change: int  # 體力變化
    affection_change: int  # 好感度變化
    mood_change: int  # 心情變化
    requirements: Dict[str, Any]  # 前置條件
    consequences: Dict[str, Any]  # 後果/效果
    available_periods: List[TimePeriod]  # 可執行的時間段


@dataclass
class GameTime:
    """遊戲時間狀態"""

    current_day: int = 1
    current_period: TimePeriod = TimePeriod.EARLY_MORNING
    time_points: int = 6  # 每日時間點數 (對應6個時間段)
    week_day: int = 1  # 星期幾 (1-7)


class TimeEvent:
    """時間事件基類"""

    def __init__(self, event_id: str, name: str, description: str):
        self.event_id = event_id
        self.name = name
        self.description = description
        self.is_completed = False

    @abstractmethod
    def can_trigger(self, context: Dict[str, Any]) -> bool:
        """檢查是否可以觸發"""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """執行事件"""
        pass


class DailyEvent(TimeEvent):
    """日常事件"""

    def __init__(
        self,
        event_id: str,
        name: str,
        description: str,
        trigger_period: TimePeriod,
        required_day: Optional[int] = None,
    ):
        super().__init__(event_id, name, description)
        self.trigger_period = trigger_period
        self.required_day = required_day

    def can_trigger(self, context: Dict[str, Any]) -> bool:
        game_time = context.get("game_time")
        if not game_time:
            return False

        # 檢查時間段
        if game_time.current_period != self.trigger_period:
            return False

        # 檢查日期（如果有要求）
        if self.required_day and game_time.current_day != self.required_day:
            return False

        return not self.is_completed

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.is_completed = True
        return {"message": f"觸發了日常事件: {self.name}", "type": "daily_event"}


class SpecialEvent(TimeEvent):
    """特殊事件"""

    def __init__(
        self, event_id: str, name: str, description: str, conditions: Dict[str, Any]
    ):
        super().__init__(event_id, name, description)
        self.conditions = conditions

    def can_trigger(self, context: Dict[str, Any]) -> bool:
        if self.is_completed:
            return False

        # 檢查觸發條件
        for key, required_value in self.conditions.items():
            if context.get(key) != required_value:
                return False

        return True

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.is_completed = True
        return {"message": f"觸發了特殊事件: {self.name}", "type": "special_event"}


class EventDrivenTimeSystem:
    """事件驅動時間系統"""

    def __init__(self):
        self.game_time = GameTime()
        self.activities: Dict[str, ActivityChoice] = {}
        self.events: Dict[str, TimeEvent] = {}
        self.activity_history: List[Dict[str, Any]] = []
        self.game_state = {
            "nyanko_energy": 100,
            "nyanko_affection": 50,
            "nyanko_mood": 50,
            "player_money": 1000,
            "unlocked_activities": [],
            "completed_events": [],
        }

        # 時間段對應的基礎時間
        self.period_times = {
            TimePeriod.EARLY_MORNING: "6:00",
            TimePeriod.MORNING: "8:00",
            TimePeriod.AFTERNOON: "12:00",
            TimePeriod.EVENING: "18:00",
            TimePeriod.NIGHT: "21:00",
            TimePeriod.LATE_NIGHT: "0:00",
        }

        # 時間段中文名稱
        self.period_names = {
            TimePeriod.EARLY_MORNING: "清晨",
            TimePeriod.MORNING: "上午",
            TimePeriod.AFTERNOON: "中午",
            TimePeriod.EVENING: "傍晚",
            TimePeriod.NIGHT: "夜晚",
            TimePeriod.LATE_NIGHT: "深夜",
        }

        # 初始化基礎活動和事件
        self._init_default_activities()
        self._init_default_events()

        # 回調函數
        self.on_time_advance: Optional[Callable] = None
        self.on_activity_complete: Optional[Callable] = None
        self.on_event_trigger: Optional[Callable] = None
        self.on_day_change: Optional[Callable] = None

    def _init_default_activities(self):
        """初始化預設活動"""
        activities = [
            # 清晨活動
            ActivityChoice(
                id="wake_up",
                name="起床",
                description="開始新的一天，與にゃんこ一起起床",
                activity_type=ActivityType.DAILY_ROUTINE,
                time_cost=1,
                energy_change=10,
                affection_change=2,
                mood_change=5,
                requirements={},
                consequences={"unlocks": ["morning_routine"]},
                available_periods=[TimePeriod.EARLY_MORNING],
            ),
            # 上午活動
            ActivityChoice(
                id="breakfast",
                name="一起吃早餐",
                description="與にゃんこ享用溫馨的早餐時光",
                activity_type=ActivityType.DAILY_ROUTINE,
                time_cost=1,
                energy_change=15,
                affection_change=5,
                mood_change=10,
                requirements={"unlocked_activities": "morning_routine"},
                consequences={},
                available_periods=[TimePeriod.MORNING],
            ),
            ActivityChoice(
                id="play_games",
                name="一起玩遊戲",
                description="與にゃんこ玩一些有趣的小遊戲",
                activity_type=ActivityType.ENTERTAINMENT,
                time_cost=2,
                energy_change=-10,
                affection_change=8,
                mood_change=15,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.MORNING, TimePeriod.AFTERNOON],
            ),
            # 下午活動
            ActivityChoice(
                id="lunch",
                name="午餐時光",
                description="準備午餐，與にゃんこ一起用餐",
                activity_type=ActivityType.DAILY_ROUTINE,
                time_cost=1,
                energy_change=20,
                affection_change=3,
                mood_change=8,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.AFTERNOON],
            ),
            ActivityChoice(
                id="afternoon_nap",
                name="午休小憩",
                description="與にゃんこ一起享受舒適的午後小憩",
                activity_type=ActivityType.REST,
                time_cost=1,
                energy_change=25,
                affection_change=4,
                mood_change=10,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.AFTERNOON],
            ),
            # 傍晚活動
            ActivityChoice(
                id="dinner",
                name="晚餐時光",
                description="準備豐盛的晚餐，與にゃんこ共度",
                activity_type=ActivityType.DAILY_ROUTINE,
                time_cost=1,
                energy_change=25,
                affection_change=5,
                mood_change=12,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.EVENING],
            ),
            ActivityChoice(
                id="evening_chat",
                name="傍晚談心",
                description="與にゃんこ坐在一起聊天談心",
                activity_type=ActivityType.INTERACTION,
                time_cost=2,
                energy_change=-5,
                affection_change=12,
                mood_change=15,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.EVENING],
            ),
            # 夜晚活動
            ActivityChoice(
                id="watch_movie",
                name="一起看電影",
                description="選一部電影與にゃんこ一起觀看",
                activity_type=ActivityType.ENTERTAINMENT,
                time_cost=2,
                energy_change=-8,
                affection_change=10,
                mood_change=18,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.NIGHT],
            ),
            ActivityChoice(
                id="bedtime",
                name="準備就寢",
                description="與にゃんこ一起準備睡覺",
                activity_type=ActivityType.DAILY_ROUTINE,
                time_cost=1,
                energy_change=5,
                affection_change=6,
                mood_change=8,
                requirements={},
                consequences={"advances_day": True},
                available_periods=[TimePeriod.NIGHT, TimePeriod.LATE_NIGHT],
            ),
            # 額外的客廳活動
            ActivityChoice(
                id="chat",
                name="愉快聊天",
                description="與にゃんこ進行輕鬆的對話",
                activity_type=ActivityType.INTERACTION,
                time_cost=1,
                energy_change=0,
                affection_change=4,
                mood_change=8,
                requirements={},
                consequences={},
                available_periods=[
                    TimePeriod.MORNING,
                    TimePeriod.AFTERNOON,
                    TimePeriod.EVENING,
                ],
            ),
            ActivityChoice(
                id="cuddle",
                name="親密擁抱",
                description="與にゃんこ來個溫馨的擁抱",
                activity_type=ActivityType.INTERACTION,
                time_cost=1,
                energy_change=5,
                affection_change=8,
                mood_change=12,
                requirements={"affection_min": 30},
                consequences={},
                available_periods=[
                    TimePeriod.AFTERNOON,
                    TimePeriod.EVENING,
                    TimePeriod.NIGHT,
                ],
            ),
            ActivityChoice(
                id="read_together",
                name="一起看書",
                description="與にゃんこ一起閱讀有趣的書籍",
                activity_type=ActivityType.ENTERTAINMENT,
                time_cost=2,
                energy_change=-5,
                affection_change=5,
                mood_change=6,
                requirements={},
                consequences={},
                available_periods=[TimePeriod.AFTERNOON, TimePeriod.EVENING],
            ),
        ]

        for activity in activities:
            self.activities[activity.id] = activity

    def _init_default_events(self):
        """初始化預設事件"""
        # 日常事件
        morning_greeting = DailyEvent(
            "morning_greeting",
            "早安問候",
            "にゃんこ給你一個溫暖的早安問候",
            TimePeriod.EARLY_MORNING,
        )

        # 特殊事件
        first_week_end = SpecialEvent(
            "first_week_end",
            "第一週結束",
            "與にゃんこ度過了第一週，她似乎更信任你了",
            {"current_day": 7},
        )

        self.events["morning_greeting"] = morning_greeting
        self.events["first_week_end"] = first_week_end

    def get_available_activities(self) -> List[ActivityChoice]:
        """獲取當前時間段可執行的活動"""
        available = []

        for activity in self.activities.values():
            # 檢查時間段
            if self.game_time.current_period not in activity.available_periods:
                continue

            # 檢查前置條件
            if not self._check_requirements(activity.requirements):
                continue

            # 檢查是否有足夠時間點數
            if self.game_time.time_points < activity.time_cost:
                continue

            available.append(activity)

        return available

    def _check_requirements(self, requirements: Dict[str, Any]) -> bool:
        """檢查活動前置條件"""
        for key, value in requirements.items():
            if key == "unlocked_activities":
                if value not in self.game_state.get("unlocked_activities", []):
                    return False
            elif key in self.game_state:
                if self.game_state[key] < value:
                    return False
        return True

    def execute_activity(self, activity_id: str) -> Dict[str, Any]:
        """執行活動"""
        if activity_id not in self.activities:
            return {"success": False, "message": "活動不存在"}

        activity = self.activities[activity_id]

        # 檢查是否可執行
        if activity not in self.get_available_activities():
            return {"success": False, "message": "當前無法執行此活動"}

        # 執行活動
        result = self._perform_activity(activity)

        # 推進時間
        self._advance_time(activity.time_cost)

        # 記錄歷史
        self.activity_history.append(
            {
                "day": self.game_time.current_day,
                "period": self.game_time.current_period.value,
                "activity": activity_id,
                "result": result,
            }
        )

        # 觸發回調
        if self.on_activity_complete:
            self.on_activity_complete(activity, result)

        return result

    def _perform_activity(self, activity: ActivityChoice) -> Dict[str, Any]:
        """執行活動邏輯"""
        # 應用狀態變化
        self.game_state["nyanko_energy"] = max(
            0, min(100, self.game_state["nyanko_energy"] + activity.energy_change)
        )
        self.game_state["nyanko_affection"] = max(
            0, min(100, self.game_state["nyanko_affection"] + activity.affection_change)
        )
        self.game_state["nyanko_mood"] = max(
            0, min(100, self.game_state["nyanko_mood"] + activity.mood_change)
        )

        # 應用後果
        self._apply_consequences(activity.consequences)

        return {
            "success": True,
            "message": f"完成了活動: {activity.name}",
            "energy_change": activity.energy_change,
            "affection_change": activity.affection_change,
            "mood_change": activity.mood_change,
            "current_state": self.game_state.copy(),
        }

    def _apply_consequences(self, consequences: Dict[str, Any]):
        """應用活動後果"""
        for key, value in consequences.items():
            if key == "unlocks":
                if isinstance(value, list):
                    self.game_state["unlocked_activities"].update(value)
                else:
                    self.game_state["unlocked_activities"].add(value)
            elif key == "advances_day":
                if value:
                    self._advance_to_next_day()

    def _advance_time(self, time_cost: int):
        """推進時間"""
        self.game_time.time_points -= time_cost

        # 如果時間點數用完，自動推進到下個時間段
        if self.game_time.time_points <= 0:
            self._advance_to_next_period()

        # 檢查並觸發事件
        self._check_and_trigger_events()

        # 觸發時間推進回調
        if self.on_time_advance:
            self.on_time_advance(self.game_time)

    def _advance_to_next_period(self):
        """推進到下個時間段"""
        periods = list(TimePeriod)
        current_index = periods.index(self.game_time.current_period)

        if current_index >= len(periods) - 1:
            # 到了深夜，推進到下一天
            self._advance_to_next_day()
        else:
            # 推進到下個時間段
            self.game_time.current_period = periods[current_index + 1]
            self.game_time.time_points = 2  # 每個時間段給2個時間點數

    def _advance_to_next_day(self):
        """推進到下一天"""
        self.game_time.current_day += 1
        self.game_time.current_period = TimePeriod.EARLY_MORNING
        self.game_time.time_points = 6  # 新的一天開始
        self.game_time.week_day = (self.game_time.week_day % 7) + 1

        # 重置每日事件
        self._reset_daily_events()

        # 觸發新一天回調
        if self.on_day_change:
            self.on_day_change(self.game_time.current_day)

    def _reset_daily_events(self):
        """重置每日事件"""
        for event in self.events.values():
            if isinstance(event, DailyEvent):
                event.is_completed = False

    def _check_and_trigger_events(self):
        """檢查並觸發事件"""
        context = {
            "game_time": self.game_time,
            "game_state": self.game_state,
            "current_day": self.game_time.current_day,
        }

        for event in self.events.values():
            if event.can_trigger(context):
                result = event.execute(context)

                # 觸發事件回調
                if self.on_event_trigger:
                    self.on_event_trigger(event, result)

    def get_current_time_info(self) -> Dict[str, Any]:
        """獲取當前時間資訊"""
        return {
            "day": self.game_time.current_day,
            "period": self.period_names[self.game_time.current_period],
            "period_id": self.game_time.current_period.value,
            "time": self.period_times[self.game_time.current_period],
            "time_points": self.game_time.time_points,
            "week_day": self.game_time.week_day,
        }

    def get_game_state(self) -> Dict[str, Any]:
        """獲取遊戲狀態"""
        return self.game_state.copy()

    def force_advance_period(self):
        """強制推進時間段（跳過當前時間段）"""
        self._advance_to_next_period()
        print(f"時間推進到: {self.period_names[self.game_time.current_period]}")

    def add_custom_activity(self, activity: ActivityChoice):
        """添加自定義活動"""
        self.activities[activity.id] = activity

    def add_custom_event(self, event: TimeEvent):
        """添加自定義事件"""
        self.events[event.event_id] = event

    def save_state(self, filepath: str):
        """保存遊戲狀態"""
        import json
        import os

        # 確保目錄存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        state_data = {
            "game_time": {
                "current_day": self.game_time.current_day,
                "current_period": self.game_time.current_period.value,
                "time_points": self.game_time.time_points,
                "week_day": self.game_time.week_day,
            },
            "game_state": self.game_state.copy(),
            "activity_history": self.activity_history,  # 已經是list，不需要轉換
            "completed_events": [
                event.event_id for event in self.events.values() if event.is_completed
            ],
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存失敗: {e}")
            return False

    def load_state(self, filepath: str):
        """加載遊戲狀態"""
        import json
        import os

        try:
            if not os.path.exists(filepath):
                print(f"文件不存在: {filepath}")
                return False

            with open(filepath, "r", encoding="utf-8") as f:
                state_data = json.load(f)

            # 恢復遊戲時間
            time_data = state_data["game_time"]
            self.game_time.current_day = time_data["current_day"]
            self.game_time.current_period = TimePeriod(time_data["current_period"])
            self.game_time.time_points = time_data["time_points"]
            self.game_time.week_day = time_data["week_day"]

            # 恢復遊戲狀態
            self.game_state = state_data["game_state"]
            self.activity_history = state_data["activity_history"]  # 已經是list

            # 恢復事件完成狀態
            completed_events = state_data.get("completed_events", [])
            for event_id in completed_events:
                if event_id in self.events:
                    self.events[event_id].is_completed = True

            return True
        except Exception as e:
            print(f"加載狀態失敗: {e}")
            return False

    def load_state_from_dict(self, save_data: dict) -> bool:
        """從字典加載時間系統狀態"""
        try:
            # 恢復遊戲時間
            if "current_day" in save_data:
                self.game_time.current_day = save_data["current_day"]
            if "current_period" in save_data:
                self.game_time.current_period = TimePeriod(save_data["current_period"])
            if "time_points" in save_data:
                self.game_time.time_points = save_data["time_points"]

            # 恢復遊戲狀態
            for key in ["nyanko_energy", "nyanko_affection", "nyanko_mood"]:
                if key in save_data:
                    self.game_state[key] = save_data[key]

            # 恢復活動歷史
            if "activity_history" in save_data:
                self.activity_history = save_data["activity_history"]

            return True
        except Exception as e:
            print(f"從字典加載狀態失敗: {e}")
            return False

    def get_activity_by_id(self, activity_id: str) -> Optional[ActivityChoice]:
        """根據ID獲取活動"""
        return self.activities.get(activity_id)

    def force_next_period(self):
        """強制推進到下個時間段"""
        # 將時間點數設為0，觸發時間推進
        self.game_time.time_points = 0
        self._advance_time()

    def set_time_period(self, period: str):
        """設置當前時間段"""
        try:
            if isinstance(period, str):
                self.game_time.current_period = TimePeriod(period.upper())
            else:
                self.game_time.current_period = period
        except ValueError:
            print(f"無效的時間段: {period}")

    def get_current_time_period(self):
        """獲取當前時間段對象"""
        return self.game_time.current_period


# 使用示例和測試
if __name__ == "__main__":
    # 創建事件驅動時間系統
    time_system = EventDrivenTimeSystem()

    # 設置回調函數
    def on_time_advance(game_time):
        print(
            f"⏰ 時間推進到: 第{game_time.current_day}天 {time_system.period_names[game_time.current_period]}"
        )

    def on_activity_complete(activity, result):
        print(f"✅ 完成活動: {activity.name}")
        print(
            f"   效果: 體力{result['energy_change']:+d}, 好感{result['affection_change']:+d}, 心情{result['mood_change']:+d}"
        )

    def on_event_trigger(event, result):
        print(f"🎉 {result['message']}")

    def on_day_change(day):
        print(f"🌅 新的一天開始了！第{day}天")

    time_system.on_time_advance = on_time_advance
    time_system.on_activity_complete = on_activity_complete
    time_system.on_event_trigger = on_event_trigger
    time_system.on_day_change = on_day_change

    print("=== 事件驅動時間系統演示 ===\n")

    # 模擬一天的活動
    demo_activities = [
        "wake_up",  # 清晨：起床
        "breakfast",  # 上午：早餐
        "play_games",  # 上午：玩遊戲
        "lunch",  # 下午：午餐
        "afternoon_nap",  # 下午：午休
        "dinner",  # 傍晚：晚餐
        "evening_chat",  # 傍晚：談心
        "watch_movie",  # 夜晚：看電影
        "bedtime",  # 夜晚：睡覺
    ]

    for activity_id in demo_activities:
        print(f"\n--- 當前時間: {time_system.get_current_time_info()['period']} ---")
        print(f"時間點數: {time_system.game_time.time_points}")

        # 顯示可用活動
        available = time_system.get_available_activities()
        print(f"可用活動: {[a.name for a in available]}")

        # 執行指定活動
        if activity_id in [a.id for a in available]:
            result = time_system.execute_activity(activity_id)
            if not result["success"]:
                print(f"❌ {result['message']}")
        else:
            print(f"⚠️  活動 {activity_id} 當前不可執行")
            # 強制推進時間段
            time_system.force_advance_period()

    print(f"\n=== 最終狀態 ===")
    print(f"遊戲時間: {time_system.get_current_time_info()}")
    print(f"にゃんこ狀態: {time_system.get_game_state()}")

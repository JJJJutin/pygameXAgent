# -*- coding: utf-8 -*-
"""
時間系統
管理遊戲內時間、日期、時間段和時間相關事件
"""

import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class TimePeriod(Enum):
    """時間段枚舉"""

    EARLY_MORNING = "early_morning"  # 早晨 (6:00-8:00)
    MORNING = "morning"  # 上午 (8:00-12:00)
    AFTERNOON = "afternoon"  # 下午 (12:00-18:00)
    EVENING = "evening"  # 傍晚 (18:00-21:00)
    NIGHT = "night"  # 夜晚 (21:00-24:00)
    LATE_NIGHT = "late_night"  # 深夜 (0:00-6:00)


class WeekDay(Enum):
    """星期枚舉"""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Season(Enum):
    """季節枚舉"""

    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class TimeEvent:
    """時間事件類別"""

    def __init__(self, data: Dict[str, Any]):
        """初始化時間事件"""
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.event_type = data.get(
            "event_type", "daily"
        )  # daily, weekly, monthly, once
        self.trigger_time = data.get("trigger_time", {})  # 觸發時間條件
        self.callback_function = data.get("callback_function", "")
        self.conditions = data.get("conditions", {})
        self.active = data.get("active", True)


class GameTime:
    """遊戲時間類別"""

    def __init__(
        self,
        year: int = 2024,
        month: int = 1,
        day: int = 1,
        hour: int = 8,
        minute: int = 0,
    ):
        """初始化遊戲時間"""
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = 0

    def to_datetime(self) -> datetime.datetime:
        """轉換為datetime物件"""
        return datetime.datetime(
            self.year, self.month, self.day, self.hour, self.minute, self.second
        )

    def get_weekday(self) -> WeekDay:
        """獲取星期"""
        dt = self.to_datetime()
        return WeekDay(dt.weekday())

    def get_season(self) -> Season:
        """獲取季節"""
        if self.month in [3, 4, 5]:
            return Season.SPRING
        elif self.month in [6, 7, 8]:
            return Season.SUMMER
        elif self.month in [9, 10, 11]:
            return Season.AUTUMN
        else:
            return Season.WINTER

    def get_time_period(self) -> TimePeriod:
        """獲取時間段"""
        if 6 <= self.hour < 8:
            return TimePeriod.EARLY_MORNING
        elif 8 <= self.hour < 12:
            return TimePeriod.MORNING
        elif 12 <= self.hour < 18:
            return TimePeriod.AFTERNOON
        elif 18 <= self.hour < 21:
            return TimePeriod.EVENING
        elif 21 <= self.hour < 24:
            return TimePeriod.NIGHT
        else:  # 0 <= hour < 6
            return TimePeriod.LATE_NIGHT

    def add_minutes(self, minutes: int):
        """增加分鐘數"""
        dt = self.to_datetime()
        dt += datetime.timedelta(minutes=minutes)
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hour = dt.hour
        self.minute = dt.minute
        self.second = dt.second

    def add_hours(self, hours: int):
        """增加小時數"""
        self.add_minutes(hours * 60)

    def add_days(self, days: int):
        """增加天數"""
        self.add_hours(days * 24)

    def format_time(self) -> str:
        """格式化時間顯示"""
        return f"{self.hour:02d}:{self.minute:02d}"

    def format_date(self) -> str:
        """格式化日期顯示"""
        return f"{self.year}年{self.month}月{self.day}日"

    def format_full(self) -> str:
        """格式化完整時間顯示"""
        weekday_names = {
            WeekDay.MONDAY: "星期一",
            WeekDay.TUESDAY: "星期二",
            WeekDay.WEDNESDAY: "星期三",
            WeekDay.THURSDAY: "星期四",
            WeekDay.FRIDAY: "星期五",
            WeekDay.SATURDAY: "星期六",
            WeekDay.SUNDAY: "星期日",
        }
        weekday = weekday_names[self.get_weekday()]
        return f"{self.format_date()} {weekday} {self.format_time()}"


class TimeSystem:
    """時間系統主類別"""

    def __init__(self, game_engine):
        """初始化時間系統"""
        self.game_engine = game_engine

        # 遊戲時間
        self.game_time = GameTime()
        self.start_time = GameTime()

        # 時間流逝設定
        self.time_scale = 1.0  # 時間流逝倍率
        self.is_paused = False
        self.auto_advance = True  # 自動時間推進

        # 時間事件
        self.time_events: Dict[str, TimeEvent] = {}
        self.scheduled_events: List[Dict[str, Any]] = []

        # 時間相關統計
        self.total_game_days = 0
        self.current_day = 1
        self.time_period_changed = False
        self.day_changed = False

        # 時間段記錄
        self.previous_time_period = self.game_time.get_time_period()
        self.current_time_period = self.game_time.get_time_period()

        # 事件觸發記錄（避免重複觸發）
        self.last_triggered_events = {}  # event_id -> (day, hour, minute)

        # 回調函數
        self.on_time_change: Optional[Callable] = None
        self.on_day_change: Optional[Callable] = None
        self.on_time_period_change: Optional[Callable] = None
        self.on_hour_change: Optional[Callable] = None

        # 初始化預設事件
        self._initialize_default_events()

        print(f"時間系統初始化完成")
        print(f"遊戲開始時間: {self.game_time.format_full()}")

    def _initialize_default_events(self):
        """初始化預設時間事件"""
        default_events = {
            "new_day": {
                "id": "new_day",
                "name": "新的一天",
                "description": "每天開始時觸發",
                "event_type": "daily",
                "trigger_time": {"hour": 6, "minute": 0},
                "callback_function": "on_new_day",
            },
            "morning_greeting": {
                "id": "morning_greeting",
                "name": "早晨問候",
                "description": "早上問候時間",
                "event_type": "daily",
                "trigger_time": {"hour": 8, "minute": 0},
                "callback_function": "on_morning_greeting",
            },
            "afternoon_check": {
                "id": "afternoon_check",
                "name": "下午時光",
                "description": "下午時間檢查",
                "event_type": "daily",
                "trigger_time": {"hour": 14, "minute": 0},
                "callback_function": "on_afternoon_check",
            },
            "evening_time": {
                "id": "evening_time",
                "name": "傍晚時光",
                "description": "傍晚休息時間",
                "event_type": "daily",
                "trigger_time": {"hour": 19, "minute": 0},
                "callback_function": "on_evening_time",
            },
            "bedtime": {
                "id": "bedtime",
                "name": "就寢時間",
                "description": "該睡覺了",
                "event_type": "daily",
                "trigger_time": {"hour": 22, "minute": 0},
                "callback_function": "on_bedtime",
            },
        }

        for event_id, event_data in default_events.items():
            self.time_events[event_id] = TimeEvent(event_data)

    def update(self, dt: float):
        """
        更新時間系統

        Args:
            dt: 時間差(秒)
        """
        if self.is_paused or not self.auto_advance:
            return

        # 保存舊時間資訊
        old_hour = self.game_time.hour
        old_day = self.game_time.day
        old_time_period = self.current_time_period

        # 推進時間
        minutes_to_add = dt * self.time_scale
        self.game_time.add_minutes(int(minutes_to_add))

        # 檢查變化
        new_time_period = self.game_time.get_time_period()

        # 檢查小時變化
        if self.game_time.hour != old_hour:
            self._on_hour_change()

        # 檢查日期變化
        if self.game_time.day != old_day:
            self.day_changed = True
            self.current_day += 1
            self.total_game_days += 1
            self._on_day_change()

        # 檢查時間段變化
        if new_time_period != old_time_period:
            self.time_period_changed = True
            self.previous_time_period = old_time_period
            self.current_time_period = new_time_period
            self._on_time_period_change()

        # 檢查時間事件
        self._check_time_events()

        # 觸發回調
        if self.on_time_change:
            self.on_time_change(self.game_time)

    def _on_hour_change(self):
        """處理小時變化"""
        if self.on_hour_change:
            self.on_hour_change(self.game_time.hour)

    def _on_day_change(self):
        """處理日期變化"""
        print(f"新的一天: {self.game_time.format_date()}")

        if self.on_day_change:
            self.on_day_change(self.current_day, self.game_time)

    def _on_time_period_change(self):
        """處理時間段變化"""
        period_names = {
            TimePeriod.EARLY_MORNING: "清晨",
            TimePeriod.MORNING: "上午",
            TimePeriod.AFTERNOON: "下午",
            TimePeriod.EVENING: "傍晚",
            TimePeriod.NIGHT: "夜晚",
            TimePeriod.LATE_NIGHT: "深夜",
        }

        old_name = period_names.get(self.previous_time_period, "未知")
        new_name = period_names.get(self.current_time_period, "未知")

        print(f"時間段變化: {old_name} → {new_name}")

        if self.on_time_period_change:
            self.on_time_period_change(
                self.previous_time_period, self.current_time_period
            )

    def _check_time_events(self):
        """檢查並觸發時間事件"""
        current_hour = self.game_time.hour
        current_minute = self.game_time.minute
        current_day = self.current_day

        for event_id, event in self.time_events.items():
            if not event.active:
                continue

            trigger_time = event.trigger_time
            trigger_hour = trigger_time.get("hour", -1)
            trigger_minute = trigger_time.get("minute", 0)

            # 檢查是否到達觸發時間
            if trigger_hour == current_hour and trigger_minute == current_minute:

                # 檢查是否今天已經觸發過
                last_trigger = self.last_triggered_events.get(event_id)
                if last_trigger and last_trigger == (
                    current_day,
                    current_hour,
                    current_minute,
                ):
                    continue  # 今天這個時間已經觸發過了

                # 記錄觸發時間
                self.last_triggered_events[event_id] = (
                    current_day,
                    current_hour,
                    current_minute,
                )

                self._trigger_time_event(event_id, event)

    def _trigger_time_event(self, event_id: str, event: TimeEvent):
        """觸發時間事件"""
        print(f"觸發時間事件: {event.name}")

        # 根據回調函數執行相應動作
        callback = event.callback_function

        if callback == "on_new_day":
            self._handle_new_day_event()
        elif callback == "on_morning_greeting":
            self._handle_morning_greeting_event()
        elif callback == "on_afternoon_check":
            self._handle_afternoon_check_event()
        elif callback == "on_evening_time":
            self._handle_evening_time_event()
        elif callback == "on_bedtime":
            self._handle_bedtime_event()

    def _handle_new_day_event(self):
        """處理新一天事件"""
        print("新的一天開始了！")
        # 這裡可以重置每日數據、觸發特殊事件等

    def _handle_morning_greeting_event(self):
        """處理早晨問候事件"""
        print("早晨問候時間到了")
        # 可以觸發にゃんこ的早晨問候對話

    def _handle_afternoon_check_event(self):
        """處理下午檢查事件"""
        print("下午時光")

    def _handle_evening_time_event(self):
        """處理傍晚時光事件"""
        print("傍晚時光到了")

    def _handle_bedtime_event(self):
        """處理就寢時間事件"""
        print("該準備睡覺了")

    def advance_time(self, hours: int = 0, minutes: int = 0):
        """
        手動推進時間

        Args:
            hours: 推進的小時數
            minutes: 推進的分鐘數
        """
        if hours > 0:
            self.game_time.add_hours(hours)
        if minutes > 0:
            self.game_time.add_minutes(minutes)

        print(f"時間推進: {self.game_time.format_full()}")

    def set_time(self, hour: int, minute: int = 0):
        """
        設定時間

        Args:
            hour: 小時 (0-23)
            minute: 分鐘 (0-59)
        """
        self.game_time.hour = max(0, min(23, hour))
        self.game_time.minute = max(0, min(59, minute))

        print(f"時間設定為: {self.game_time.format_time()}")

    def set_date(self, year: int, month: int, day: int):
        """
        設定日期

        Args:
            year: 年份
            month: 月份 (1-12)
            day: 日期 (1-31)
        """
        self.game_time.year = year
        self.game_time.month = max(1, min(12, month))
        self.game_time.day = max(1, min(31, day))

        print(f"日期設定為: {self.game_time.format_date()}")

    def pause_time(self):
        """暫停時間"""
        self.is_paused = True
        print("時間系統已暫停")

    def resume_time(self):
        """恢復時間"""
        self.is_paused = False
        print("時間系統已恢復")

    def set_time_scale(self, scale: float):
        """
        設定時間流逝倍率

        Args:
            scale: 時間倍率 (1.0 = 正常速度)
        """
        self.time_scale = max(0.1, min(10.0, scale))
        print(f"時間倍率設定為: {self.time_scale:.1f}x")

    def get_current_time(self) -> GameTime:
        """獲取當前遊戲時間"""
        return self.game_time

    def get_current_time_period(self) -> TimePeriod:
        """獲取當前時間段"""
        return self.game_time.get_time_period()

    def get_current_time_period_name(self) -> str:
        """獲取當前時間段名稱"""
        period_names = {
            TimePeriod.EARLY_MORNING: "清晨",
            TimePeriod.MORNING: "上午",
            TimePeriod.AFTERNOON: "下午",
            TimePeriod.EVENING: "傍晚",
            TimePeriod.NIGHT: "夜晚",
            TimePeriod.LATE_NIGHT: "深夜",
        }
        return period_names.get(self.get_current_time_period(), "未知")

    def get_season(self) -> Season:
        """獲取當前季節"""
        return self.game_time.get_season()

    def get_season_name(self) -> str:
        """獲取當前季節名稱"""
        season_names = {
            Season.SPRING: "春天",
            Season.SUMMER: "夏天",
            Season.AUTUMN: "秋天",
            Season.WINTER: "冬天",
        }
        return season_names.get(self.get_season(), "未知")

    def get_weekday(self) -> WeekDay:
        """獲取星期"""
        return self.game_time.get_weekday()

    def get_weekday_name(self) -> str:
        """獲取星期名稱"""
        weekday_names = {
            WeekDay.MONDAY: "星期一",
            WeekDay.TUESDAY: "星期二",
            WeekDay.WEDNESDAY: "星期三",
            WeekDay.THURSDAY: "星期四",
            WeekDay.FRIDAY: "星期五",
            WeekDay.SATURDAY: "星期六",
            WeekDay.SUNDAY: "星期日",
        }
        return weekday_names.get(self.get_weekday(), "未知")

    def is_weekend(self) -> bool:
        """檢查是否為週末"""
        weekday = self.get_weekday()
        return weekday in [WeekDay.SATURDAY, WeekDay.SUNDAY]

    def get_time_until_next_period(self) -> int:
        """獲取到下一時間段的分鐘數"""
        current_hour = self.game_time.hour
        current_minute = self.game_time.minute

        # 定義時間段邊界
        period_boundaries = [6, 8, 12, 18, 21, 24]

        # 找到下一個邊界
        next_boundary = None
        for boundary in period_boundaries:
            if current_hour < boundary:
                next_boundary = boundary
                break

        if next_boundary is None:
            next_boundary = 6 + 24  # 次日清晨

        # 計算分鐘差
        current_total_minutes = current_hour * 60 + current_minute
        next_total_minutes = next_boundary * 60

        return next_total_minutes - current_total_minutes

    def add_time_event(self, event_data: Dict[str, Any]):
        """添加時間事件"""
        event = TimeEvent(event_data)
        self.time_events[event.id] = event
        print(f"添加時間事件: {event.name}")

    def remove_time_event(self, event_id: str):
        """移除時間事件"""
        if event_id in self.time_events:
            event_name = self.time_events[event_id].name
            del self.time_events[event_id]
            print(f"移除時間事件: {event_name}")

    def toggle_time_event(self, event_id: str, active: bool):
        """切換時間事件的啟用狀態"""
        if event_id in self.time_events:
            self.time_events[event_id].active = active
            status = "啟用" if active else "停用"
            print(f"時間事件 {self.time_events[event_id].name} 已{status}")

    def get_game_statistics(self) -> Dict[str, Any]:
        """獲取遊戲時間統計"""
        return {
            "total_days": self.total_game_days,
            "current_day": self.current_day,
            "current_time": self.game_time.format_full(),
            "time_period": self.get_current_time_period_name(),
            "season": self.get_season_name(),
            "weekday": self.get_weekday_name(),
            "is_weekend": self.is_weekend(),
            "time_scale": self.time_scale,
            "is_paused": self.is_paused,
        }

    def save_data(self) -> Dict[str, Any]:
        """儲存時間系統資料"""
        return {
            "game_time": {
                "year": self.game_time.year,
                "month": self.game_time.month,
                "day": self.game_time.day,
                "hour": self.game_time.hour,
                "minute": self.game_time.minute,
            },
            "total_game_days": self.total_game_days,
            "current_day": self.current_day,
            "time_scale": self.time_scale,
        }

    def load_data(self, data: Dict[str, Any]) -> bool:
        """載入時間系統資料"""
        try:
            time_data = data.get("game_time", {})
            self.game_time = GameTime(
                year=time_data.get("year", 2024),
                month=time_data.get("month", 1),
                day=time_data.get("day", 1),
                hour=time_data.get("hour", 8),
                minute=time_data.get("minute", 0),
            )

            self.total_game_days = data.get("total_game_days", 0)
            self.current_day = data.get("current_day", 1)
            self.time_scale = data.get("time_scale", 1.0)

            # 更新時間段
            self.current_time_period = self.game_time.get_time_period()
            self.previous_time_period = self.current_time_period

            print("時間系統資料載入成功")
            return True

        except Exception as e:
            print(f"載入時間系統資料失敗: {e}")
            return False

# -*- coding: utf-8 -*-
"""
基本時間系統
提供最基本的時間功能，確保遊戲不會因為時間系統而崩潰
"""

from enum import Enum


class TimePeriod(Enum):
    """時間段枚舉"""

    EARLY_MORNING = "early_morning"
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    LATE_NIGHT = "late_night"


class BasicTimeSystem:
    """基本時間系統"""

    def __init__(self):
        """初始化基本時間系統"""
        self.current_day = 1
        self.current_hour = 8
        self.current_minute = 0
        self.current_period = TimePeriod.MORNING

    def get_current_day(self):
        """獲取當前天數"""
        return self.current_day

    def get_current_time(self):
        """獲取當前時間（返回格式化字符串）"""
        return f"{self.current_hour:02d}:{self.current_minute:02d}"

    def get_current_time_period(self):
        """獲取當前時間段"""
        return self.current_period

    def get_current_period(self):
        """獲取當前時間段（別名方法）"""
        return self.current_period

    def get_time_points(self):
        """獲取當前時間點數"""
        return 6

    def get_max_time_points(self):
        """獲取最大時間點數"""
        return 6

    def get_current_time_period_name(self):
        """獲取當前時間段名稱"""
        period_names = {
            TimePeriod.EARLY_MORNING: "清晨",
            TimePeriod.MORNING: "上午",
            TimePeriod.AFTERNOON: "下午",
            TimePeriod.EVENING: "傍晚",
            TimePeriod.NIGHT: "夜晚",
            TimePeriod.LATE_NIGHT: "深夜",
        }
        return period_names.get(self.current_period, "上午")

    def get_season_name(self):
        """獲取季節名稱"""
        return "春天"

    def get_weekday_name(self):
        """獲取星期名稱"""
        weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        return f"星期{weekday_names[(self.current_day - 1) % 7]}"

    def get_weekday(self):
        """獲取星期對象（為了兼容性）"""

        class WeekdayStub:
            def __init__(self, name):
                self.name = name

        weekday_names = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        return WeekdayStub(weekday_names[(self.current_day - 1) % 7])

    def update(self, dt):
        """更新時間系統"""
        # 基本版本不需要實時更新
        pass

    def advance_time(self):
        """推進時間"""
        periods = [
            TimePeriod.EARLY_MORNING,
            TimePeriod.MORNING,
            TimePeriod.AFTERNOON,
            TimePeriod.EVENING,
            TimePeriod.NIGHT,
            TimePeriod.LATE_NIGHT,
        ]

        current_index = periods.index(self.current_period)
        if current_index < len(periods) - 1:
            self.current_period = periods[current_index + 1]
            self.current_hour += 3  # 每個時間段大約3小時
        else:
            # 新的一天
            self.current_day += 1
            self.current_period = TimePeriod.EARLY_MORNING
            self.current_hour = 6
            self.current_minute = 0

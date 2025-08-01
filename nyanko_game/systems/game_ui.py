# -*- coding: utf-8 -*-
"""
遊戲UI系統 - 時間和狀態顯示
提供美觀的時間、體力、好感度等狀態顯示UI
"""

import pygame
from typing import Dict, Any, Optional
from config.settings import Colors, FontSettings


class GameStatusUI:
    """遊戲狀態UI類別 - 負責顯示時間、體力等資訊"""

    def __init__(self, screen_width: int, screen_height: int):
        """初始化UI系統"""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 字體設置
        self.fonts = {}
        self._setup_fonts()

        # UI配色方案
        self.colors = {
            "background": (50, 50, 50, 180),  # 半透明深灰背景
            "border": (100, 150, 200),  # 藍色邊框
            "text_primary": (255, 255, 255),  # 主文字白色
            "text_secondary": (200, 200, 200),  # 次文字淺灰
            "time_text": (255, 223, 0),  # 時間文字金色
            "energy_high": (46, 204, 113),  # 體力高綠色
            "energy_mid": (241, 196, 15),  # 體力中黃色
            "energy_low": (231, 76, 60),  # 體力低紅色
            "affection_color": (231, 84, 128),  # 好感度粉色
            "mood_color": (155, 89, 182),  # 心情紫色
            "points_color": (52, 152, 219),  # 時間點數藍色
        }

        # UI佈局設置
        self.layout = {
            "panel_margin": 10,
            "panel_padding": 15,
            "bar_height": 8,
            "bar_width": 120,
            "icon_size": 24,
        }

        # 動畫效果
        self.animations = {"time_glow": 0, "energy_pulse": 0, "affection_sparkle": 0}

    def _setup_fonts(self):
        """設置字體"""
        try:
            self.fonts = {
                "title": pygame.font.Font(FontSettings.DEFAULT_FONT, 28),
                "large": pygame.font.Font(FontSettings.DEFAULT_FONT, 24),
                "medium": pygame.font.Font(FontSettings.DEFAULT_FONT, 20),
                "small": pygame.font.Font(FontSettings.DEFAULT_FONT, 16),
                "tiny": pygame.font.Font(FontSettings.DEFAULT_FONT, 14),
            }
        except (FileNotFoundError, OSError):
            # 使用系統預設字體
            self.fonts = {
                "title": pygame.font.Font(None, 32),
                "large": pygame.font.Font(None, 28),
                "medium": pygame.font.Font(None, 24),
                "small": pygame.font.Font(None, 20),
                "tiny": pygame.font.Font(None, 18),
            }

    def update(self, dt: float):
        """更新動畫效果"""
        import math

        # 時間發光效果
        self.animations["time_glow"] += dt * 2
        if self.animations["time_glow"] > 2 * math.pi:
            self.animations["time_glow"] = 0

        # 體力脈動效果
        self.animations["energy_pulse"] += dt * 3
        if self.animations["energy_pulse"] > 2 * math.pi:
            self.animations["energy_pulse"] = 0

        # 好感度閃爍效果
        self.animations["affection_sparkle"] += dt * 4
        if self.animations["affection_sparkle"] > 2 * math.pi:
            self.animations["affection_sparkle"] = 0

    def draw_main_status_panel(
        self, screen: pygame.Surface, time_info: Dict, game_state: Dict
    ):
        """繪製主狀態面板 - 顯示時間和核心狀態"""
        panel_width = 300
        panel_height = 160
        panel_x = self.layout["panel_margin"]
        panel_y = self.layout["panel_margin"]

        # 繪製背景面板
        self._draw_panel_background(screen, panel_x, panel_y, panel_width, panel_height)

        # 內容區域
        content_x = panel_x + self.layout["panel_padding"]
        content_y = panel_y + self.layout["panel_padding"]
        content_width = panel_width - 2 * self.layout["panel_padding"]

        y_offset = content_y

        # 繪製時間資訊
        y_offset = self._draw_time_section(
            screen, content_x, y_offset, content_width, time_info
        )

        # 分隔線
        y_offset += 5
        pygame.draw.line(
            screen,
            self.colors["border"],
            (content_x, y_offset),
            (content_x + content_width, y_offset),
            2,
        )
        y_offset += 10

        # 繪製にゃんこ狀態
        self._draw_nyanko_status(screen, content_x, y_offset, content_width, game_state)

    def draw_detailed_status_panel(self, screen: pygame.Surface, game_state: Dict):
        """繪製詳細狀態面板 - 右側顯示詳細數值"""
        panel_width = 200
        panel_height = 120
        panel_x = self.screen_width - panel_width - self.layout["panel_margin"]
        panel_y = self.layout["panel_margin"]

        # 繪製背景面板
        self._draw_panel_background(screen, panel_x, panel_y, panel_width, panel_height)

        # 內容區域
        content_x = panel_x + self.layout["panel_padding"]
        content_y = panel_y + self.layout["panel_padding"]

        # 標題
        title_text = self.fonts["medium"].render(
            "にゃんこ狀態", True, self.colors["text_primary"]
        )
        screen.blit(title_text, (content_x, content_y))

        y_offset = content_y + 30

        # 詳細數值
        stats = [
            ("體力", game_state.get("nyanko_energy", 100), self.colors["energy_high"]),
            (
                "好感度",
                game_state.get("nyanko_affection", 50),
                self.colors["affection_color"],
            ),
            ("心情", game_state.get("nyanko_mood", 70), self.colors["mood_color"]),
        ]

        for stat_name, value, color in stats:
            self._draw_detailed_stat(
                screen, content_x, y_offset, stat_name, value, color
            )
            y_offset += 25

    def draw_time_points_indicator(self, screen: pygame.Surface, time_info: Dict):
        """繪製時間點數指示器 - 底部中央顯示"""
        time_points = time_info.get("time_points", 0)
        max_points = 8  # 假設最大時間點數

        # 計算位置
        indicator_width = 300
        indicator_height = 40
        indicator_x = (self.screen_width - indicator_width) // 2
        indicator_y = self.screen_height - indicator_height - 20

        # 背景
        bg_rect = pygame.Rect(
            indicator_x, indicator_y, indicator_width, indicator_height
        )
        pygame.draw.rect(screen, (*self.colors["background"][:3], 150), bg_rect)
        pygame.draw.rect(screen, self.colors["border"], bg_rect, 2)

        # 標題
        title_text = self.fonts["small"].render(
            "時間點數", True, self.colors["text_primary"]
        )
        title_rect = title_text.get_rect()
        title_rect.centerx = indicator_x + indicator_width // 2
        title_rect.y = indicator_y + 5
        screen.blit(title_text, title_rect)

        # 點數顯示
        points_text = f"{time_points} / {max_points}"
        points_surface = self.fonts["medium"].render(
            points_text, True, self.colors["points_color"]
        )
        points_rect = points_surface.get_rect()
        points_rect.centerx = indicator_x + indicator_width // 2
        points_rect.y = indicator_y + 20
        screen.blit(points_surface, points_rect)

        # 點數條
        bar_width = 200
        bar_height = 6
        bar_x = indicator_x + (indicator_width - bar_width) // 2
        bar_y = indicator_y + indicator_height - 10

        # 背景條
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # 進度條
        if max_points > 0:
            progress_width = int(bar_width * (time_points / max_points))
            if progress_width > 0:
                color = self._get_points_color(time_points, max_points)
                pygame.draw.rect(
                    screen, color, (bar_x, bar_y, progress_width, bar_height)
                )

    def draw_activity_hint(self, screen: pygame.Surface, available_activities: int):
        """繪製活動提示 - 右下角"""
        hint_width = 180
        hint_height = 60
        hint_x = self.screen_width - hint_width - self.layout["panel_margin"]
        hint_y = self.screen_height - hint_height - 20

        # 背景
        bg_rect = pygame.Rect(hint_x, hint_y, hint_width, hint_height)
        pygame.draw.rect(screen, (*self.colors["background"][:3], 120), bg_rect)
        pygame.draw.rect(screen, self.colors["border"], bg_rect, 1)

        # 內容
        content_x = hint_x + 10
        content_y = hint_y + 8

        if available_activities > 0:
            hint_text = f"可用活動: {available_activities}個"
            color = self.colors["text_primary"]
            action_text = "按 SPACE 選擇"
        else:
            hint_text = "無可用活動"
            color = self.colors["energy_low"]
            action_text = "按 T 跳過時間"

        # 主文字
        main_surface = self.fonts["small"].render(hint_text, True, color)
        screen.blit(main_surface, (content_x, content_y))

        # 操作提示
        action_surface = self.fonts["tiny"].render(
            action_text, True, self.colors["text_secondary"]
        )
        screen.blit(action_surface, (content_x, content_y + 20))

    def _draw_panel_background(
        self, screen: pygame.Surface, x: int, y: int, width: int, height: int
    ):
        """繪製面板背景"""
        # 主背景
        bg_rect = pygame.Rect(x, y, width, height)
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill(self.colors["background"])
        screen.blit(bg_surface, (x, y))

        # 邊框
        pygame.draw.rect(screen, self.colors["border"], bg_rect, 2)

        # 內發光效果
        inner_rect = pygame.Rect(x + 2, y + 2, width - 4, height - 4)
        pygame.draw.rect(screen, (*self.colors["border"], 50), inner_rect, 1)

    def _draw_time_section(
        self, screen: pygame.Surface, x: int, y: int, width: int, time_info: Dict
    ) -> int:
        """繪製時間區塊"""
        # 天數
        day_text = f"第 {time_info.get('day', 1)} 天"
        day_surface = self.fonts["large"].render(
            day_text, True, self.colors["time_text"]
        )
        screen.blit(day_surface, (x, y))

        # 時間段和具體時間
        period = self._get_period_display(time_info.get("period", "MORNING"))
        time_str = time_info.get("time", "08:00")
        time_text = f"{period} ({time_str})"

        # 添加發光效果
        import math

        glow_alpha = int(30 + 20 * math.sin(self.animations["time_glow"]))

        time_surface = self.fonts["medium"].render(
            time_text, True, self.colors["text_primary"]
        )
        screen.blit(time_surface, (x, y + 30))

        return y + 55

    def _draw_nyanko_status(
        self, screen: pygame.Surface, x: int, y: int, width: int, game_state: Dict
    ):
        """繪製にゃんこ狀態條"""
        energy = game_state.get("nyanko_energy", 100)
        affection = game_state.get("nyanko_affection", 50)
        mood = game_state.get("nyanko_mood", 70)

        # 體力條
        self._draw_status_bar(
            screen, x, y, "體力", energy, self._get_energy_color(energy)
        )

        # 好感度條
        self._draw_status_bar(
            screen, x, y + 25, "好感", affection, self.colors["affection_color"]
        )

        # 心情條
        self._draw_status_bar(
            screen, x, y + 50, "心情", mood, self.colors["mood_color"]
        )

    def _draw_status_bar(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        label: str,
        value: int,
        color: tuple,
    ):
        """繪製單個狀態條"""
        # 標籤
        label_surface = self.fonts["small"].render(
            f"{label}:", True, self.colors["text_secondary"]
        )
        screen.blit(label_surface, (x, y))

        # 數值
        value_text = f"{value}/100"
        value_surface = self.fonts["small"].render(
            value_text, True, self.colors["text_primary"]
        )
        screen.blit(value_surface, (x + 200, y))

        # 狀態條
        bar_x = x + 45
        bar_y = y + 2
        bar_width = self.layout["bar_width"]
        bar_height = self.layout["bar_height"]

        # 背景條
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # 進度條
        progress_width = int(bar_width * (value / 100))
        if progress_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, progress_width, bar_height))

        # 邊框
        pygame.draw.rect(
            screen, (120, 120, 120), (bar_x, bar_y, bar_width, bar_height), 1
        )

    def _draw_detailed_stat(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        name: str,
        value: int,
        color: tuple,
    ):
        """繪製詳細狀態項目"""
        # 名稱
        name_surface = self.fonts["small"].render(
            f"{name}:", True, self.colors["text_secondary"]
        )
        screen.blit(name_surface, (x, y))

        # 數值
        value_surface = self.fonts["small"].render(str(value), True, color)
        screen.blit(value_surface, (x + 80, y))

        # 小型狀態條
        bar_x = x + 120
        bar_y = y + 5
        bar_width = 50
        bar_height = 4

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        progress_width = int(bar_width * (value / 100))
        if progress_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, progress_width, bar_height))

    def _get_period_display(self, period: str) -> str:
        """獲取時間段顯示文字"""
        period_names = {
            "EARLY_MORNING": "清晨",
            "MORNING": "上午",
            "AFTERNOON": "下午",
            "EVENING": "傍晚",
            "NIGHT": "夜晚",
            "LATE_NIGHT": "深夜",
        }
        return period_names.get(period, "未知")

    def _get_energy_color(self, energy: int) -> tuple:
        """根據體力值獲取顏色"""
        if energy >= 70:
            return self.colors["energy_high"]
        elif energy >= 40:
            return self.colors["energy_mid"]
        else:
            return self.colors["energy_low"]

    def _get_points_color(self, current: int, max_val: int) -> tuple:
        """根據點數比例獲取顏色"""
        ratio = current / max_val if max_val > 0 else 0
        if ratio >= 0.6:
            return self.colors["energy_high"]
        elif ratio >= 0.3:
            return self.colors["energy_mid"]
        else:
            return self.colors["energy_low"]


class MinimalStatusUI:
    """精簡狀態UI - 適合小螢幕或簡潔模式"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        try:
            self.font = pygame.font.Font(FontSettings.DEFAULT_FONT, 18)
        except (FileNotFoundError, OSError):
            self.font = pygame.font.Font(None, 22)

    def draw(self, screen: pygame.Surface, time_info: Dict, game_state: Dict):
        """繪製精簡UI"""
        # 頂部狀態條
        bg_height = 40
        bg_rect = pygame.Rect(0, 0, self.screen_width, bg_height)
        bg_surface = pygame.Surface((self.screen_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, (0, 0))

        # 時間資訊 (左側)
        day = time_info.get("day", 1)
        period = self._get_period_display(time_info.get("period", "MORNING"))
        time_str = time_info.get("time", "08:00")
        points = time_info.get("time_points", 0)

        time_text = f"第{day}天 {period} {time_str} | 點數:{points}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        screen.blit(time_surface, (10, 10))

        # 狀態資訊 (右側)
        energy = game_state.get("nyanko_energy", 100)
        affection = game_state.get("nyanko_affection", 50)
        mood = game_state.get("nyanko_mood", 70)

        status_text = f"體力:{energy} 好感:{affection} 心情:{mood}"
        status_surface = self.font.render(status_text, True, (200, 200, 200))
        status_rect = status_surface.get_rect()
        status_rect.right = self.screen_width - 10
        status_rect.y = 10
        screen.blit(status_surface, status_rect)

    def _get_period_display(self, period: str) -> str:
        """獲取時間段顯示文字"""
        period_names = {
            "EARLY_MORNING": "清晨",
            "MORNING": "上午",
            "AFTERNOON": "下午",
            "EVENING": "傍晚",
            "NIGHT": "夜晚",
            "LATE_NIGHT": "深夜",
        }
        return period_names.get(period, "未知")

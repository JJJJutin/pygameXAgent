# -*- coding: utf-8 -*-
"""
臥室場景
休息和親密互動的場景
"""

import pygame
from scenes.base_scene import BaseScene
from config.settings import *


class BedroomScene(BaseScene):
    """臥室場景類別"""

    def __init__(self, game_engine, scene_manager):
        """初始化臥室場景"""
        self.background = None
        self.ui_font = None

        super().__init__(game_engine, scene_manager)

    def load_resources(self):
        """載入場景資源"""
        # 建立字體（使用中文字體）
        try:
            self.ui_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.FONT_SIZE_MEDIUM
            )
        except (FileNotFoundError, OSError):
            print("警告: 無法載入指定字體，使用系統預設字體")
            self.ui_font = pygame.font.Font(None, FontSettings.FONT_SIZE_MEDIUM)

        # 建立背景
        screen_width, screen_height = self.get_screen_size()
        self.background = pygame.Surface((screen_width, screen_height))
        self.background.fill(Colors.LIGHT_PINK)

        # 簡單的臥室佈局
        self._create_bedroom_layout()

    def _create_bedroom_layout(self):
        """建立臥室佈局"""
        screen_width, screen_height = self.get_screen_size()

        # 床
        bed_color = (255, 228, 225)
        bed_rect = pygame.Rect(screen_width // 2 - 150, screen_height - 250, 300, 150)
        pygame.draw.rect(self.background, bed_color, bed_rect)

        # 衣櫃
        wardrobe_color = (139, 69, 19)
        wardrobe_rect = pygame.Rect(50, 150, 80, 250)
        pygame.draw.rect(self.background, wardrobe_color, wardrobe_rect)

    def setup_ui(self):
        """設置UI元素"""
        pass

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        screen.blit(self.background, (0, 0))

        # 場景標題
        title_text = self.ui_font.render("臥室", True, Colors.DARK_GRAY)
        screen.blit(title_text, (20, 20))

        # 操作提示
        screen_width, screen_height = self.get_screen_size()
        hint_text = self.ui_font.render("ESC: 返回客廳", True, Colors.GRAY)
        screen.blit(hint_text, (20, screen_height - 30))

    def handle_event(self, event: pygame.event.Event):
        """處理事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_scene("living_room")

    def handle_escape(self):
        """處理ESC鍵"""
        self.change_scene("living_room")

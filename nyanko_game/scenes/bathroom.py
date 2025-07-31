# -*- coding: utf-8 -*-
"""
浴室場景
清潔和放鬆相關的場景
"""

import pygame
from scenes.base_scene import BaseScene
from config.settings import *


class BathroomScene(BaseScene):
    """浴室場景類別"""

    def __init__(self, game_engine, scene_manager):
        """初始化浴室場景"""
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
        self.background.fill(Colors.LIGHT_BLUE)

        # 簡單的浴室佈局
        self._create_bathroom_layout()

    def _create_bathroom_layout(self):
        """建立浴室佈局"""
        screen_width, screen_height = self.get_screen_size()

        # 浴缸
        bathtub_color = (255, 255, 255)
        bathtub_rect = pygame.Rect(screen_width - 300, screen_height - 200, 250, 150)
        pygame.draw.rect(self.background, bathtub_color, bathtub_rect)

        # 洗手台
        sink_color = (240, 240, 240)
        sink_rect = pygame.Rect(50, screen_height - 180, 150, 80)
        pygame.draw.rect(self.background, sink_color, sink_rect)

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
        title_text = self.ui_font.render("浴室", True, Colors.DARK_GRAY)
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

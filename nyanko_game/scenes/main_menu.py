# -*- coding: utf-8 -*-
"""
主選單場景
遊戲的主要選單界面，包含開始遊戲、載入遊戲、設定等選項
"""

import pygame
from scenes.base_scene import BaseScene
from config.settings import *


class MainMenuScene(BaseScene):
    """主選單場景類別"""

    def __init__(self, game_engine, scene_manager):
        """初始化主選單場景"""
        self.background = None
        self.title_font = None
        self.menu_font = None
        self.menu_items = []
        self.selected_index = 0
        self.button_hover_color = Colors.LIGHT_PINK
        self.button_normal_color = Colors.WHITE

        super().__init__(game_engine, scene_manager)

    def load_resources(self):
        """載入場景資源"""
        # 建立字體（使用中文字體）
        try:
            self.title_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.FONT_SIZE_TITLE * 2
            )
            self.menu_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.FONT_SIZE_LARGE
            )
        except (FileNotFoundError, OSError):
            # 如果找不到指定字體，使用系統預設字體
            print("警告: 無法載入指定字體，使用系統預設字體")
            self.title_font = pygame.font.Font(None, FontSettings.FONT_SIZE_TITLE * 2)
            self.menu_font = pygame.font.Font(None, FontSettings.FONT_SIZE_LARGE)

        # 建立背景
        screen_width, screen_height = self.get_screen_size()
        self.background = pygame.Surface((screen_width, screen_height))
        self.background.fill(Colors.LIGHT_PINK)

        # 添加簡單的背景圖案
        for i in range(0, screen_width, 100):
            for j in range(0, screen_height, 100):
                pygame.draw.circle(
                    self.background, Colors.WHITE, (i + 50, j + 50), 30, 2
                )

    def setup_ui(self):
        """設置UI元素"""
        # 選單項目
        self.menu_items = [
            {"text": "開始遊戲", "action": self._start_new_game, "enabled": True},
            {
                "text": "載入遊戲",
                "action": self._load_game,
                "enabled": False,  # 暫時禁用
            },
            {
                "text": "遊戲設定",
                "action": self._show_settings,
                "enabled": False,  # 暫時禁用
            },
            {"text": "離開遊戲", "action": self._quit_game, "enabled": True},
        ]

        self.selected_index = 0

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

        # 這裡可以添加動畫效果或其他更新邏輯
        pass

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        # 繪製背景
        screen.blit(self.background, (0, 0))

        # 繪製標題
        self._render_title(screen)

        # 繪製選單
        self._render_menu(screen)

        # 繪製版本資訊
        self._render_version_info(screen)

    def _render_title(self, screen: pygame.Surface):
        """繪製遊戲標題"""
        screen_width, screen_height = self.get_screen_size()

        # 主標題
        title_text = self.title_font.render("にゃんこと一緒", True, Colors.DARK_GRAY)
        title_rect = title_text.get_rect()
        title_rect.centerx = screen_width // 2
        title_rect.y = screen_height // 6
        screen.blit(title_text, title_rect)

        # 副標題
        subtitle_text = self.menu_font.render(
            "～貓娘女僕的同居日常～", True, Colors.GRAY
        )
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.centerx = screen_width // 2
        subtitle_rect.y = title_rect.bottom + 20
        screen.blit(subtitle_text, subtitle_rect)

    def _render_menu(self, screen: pygame.Surface):
        """繪製選單項目"""
        screen_width, screen_height = self.get_screen_size()

        # 計算選單位置
        menu_start_y = screen_height // 2
        button_height = UISettings.BUTTON_HEIGHT
        button_spacing = button_height + UISettings.BUTTON_MARGIN

        for i, item in enumerate(self.menu_items):
            # 計算按鈕位置
            button_y = menu_start_y + i * button_spacing
            button_rect = pygame.Rect(
                screen_width // 2 - UISettings.BUTTON_WIDTH // 2,
                button_y,
                UISettings.BUTTON_WIDTH,
                button_height,
            )

            # 選擇按鈕顏色
            if not item["enabled"]:
                button_color = Colors.GRAY
                text_color = Colors.LIGHT_GRAY
            elif i == self.selected_index:
                button_color = self.button_hover_color
                text_color = Colors.DARK_GRAY
            else:
                button_color = self.button_normal_color
                text_color = Colors.DARK_GRAY

            # 繪製按鈕
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, Colors.DARK_GRAY, button_rect, 2)

            # 繪製文字
            text_surface = self.menu_font.render(item["text"], True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.center = button_rect.center
            screen.blit(text_surface, text_rect)

    def _render_version_info(self, screen: pygame.Surface):
        """繪製版本資訊"""
        screen_width, screen_height = self.get_screen_size()

        version_font = pygame.font.Font(None, FontSettings.FONT_SIZE_SMALL)
        version_text = version_font.render(f"版本 {GAME_VERSION}", True, Colors.GRAY)
        screen.blit(version_text, (10, screen_height - 30))

    def handle_event(self, event: pygame.event.Event):
        """處理事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._navigate_menu(-1)
            elif event.key == pygame.K_DOWN:
                self._navigate_menu(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_menu_item()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵點擊
                mouse_pos = pygame.mouse.get_pos()
                self._handle_mouse_click(mouse_pos)

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self._handle_mouse_hover(mouse_pos)

    def _navigate_menu(self, direction: int):
        """
        選單導航

        Args:
            direction: 方向 (-1: 上, 1: 下)
        """
        enabled_indices = [
            i for i, item in enumerate(self.menu_items) if item["enabled"]
        ]

        if not enabled_indices:
            return

        current_pos = (
            enabled_indices.index(self.selected_index)
            if self.selected_index in enabled_indices
            else 0
        )
        new_pos = (current_pos + direction) % len(enabled_indices)
        self.selected_index = enabled_indices[new_pos]

    def _select_menu_item(self):
        """選擇選單項目"""
        if 0 <= self.selected_index < len(self.menu_items):
            item = self.menu_items[self.selected_index]
            if item["enabled"] and item["action"]:
                item["action"]()

    def _handle_mouse_click(self, mouse_pos: tuple):
        """處理滑鼠點擊"""
        screen_width, screen_height = self.get_screen_size()
        menu_start_y = screen_height // 2
        button_height = UISettings.BUTTON_HEIGHT
        button_spacing = button_height + UISettings.BUTTON_MARGIN

        for i, item in enumerate(self.menu_items):
            if not item["enabled"]:
                continue

            button_rect = pygame.Rect(
                screen_width // 2 - UISettings.BUTTON_WIDTH // 2,
                menu_start_y + i * button_spacing,
                UISettings.BUTTON_WIDTH,
                button_height,
            )

            if button_rect.collidepoint(mouse_pos):
                self.selected_index = i
                item["action"]()
                break

    def _handle_mouse_hover(self, mouse_pos: tuple):
        """處理滑鼠懸停"""
        screen_width, screen_height = self.get_screen_size()
        menu_start_y = screen_height // 2
        button_height = UISettings.BUTTON_HEIGHT
        button_spacing = button_height + UISettings.BUTTON_MARGIN

        for i, item in enumerate(self.menu_items):
            if not item["enabled"]:
                continue

            button_rect = pygame.Rect(
                screen_width // 2 - UISettings.BUTTON_WIDTH // 2,
                menu_start_y + i * button_spacing,
                UISettings.BUTTON_WIDTH,
                button_height,
            )

            if button_rect.collidepoint(mouse_pos):
                self.selected_index = i
                break

    def _start_new_game(self):
        """開始新遊戲"""
        print("開始新遊戲...")
        # 切換到客廳場景開始遊戲
        self.change_scene("living_room", {"new_game": True})

    def _load_game(self):
        """載入遊戲"""
        print("載入遊戲...")
        # TODO: 實作載入遊戲功能
        pass

    def _show_settings(self):
        """顯示設定"""
        print("顯示設定...")
        # TODO: 實作設定介面
        pass

    def _quit_game(self):
        """退出遊戲"""
        print("退出遊戲...")
        self.quit_game()

    def handle_escape(self):
        """處理ESC鍵"""
        # 在主選單中ESC鍵直接退出遊戲
        self._quit_game()

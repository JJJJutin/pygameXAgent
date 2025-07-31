# -*- coding: utf-8 -*-
"""
廚房場景
烹飪和用餐相關的互動場景
"""

import pygame
from scenes.base_scene import BaseScene
from config.settings import *


class KitchenScene(BaseScene):
    """廚房場景類別"""

    def __init__(self, game_engine, scene_manager):
        """初始化廚房場景"""
        self.background = None
        self.ui_font = None
        self.cooking_options = [
            {
                "text": "和にゃんこ一起做早餐",
                "action": "breakfast_cooking",
                "dialogue": "cooking_breakfast_01",
            },
            {
                "text": "準備豐盛的晚餐",
                "action": "dinner_cooking",
                "dialogue": "cooking_dinner_01",
            },
            {
                "text": "學習新的菜色",
                "action": "new_recipe",
                "dialogue": "new_recipe_learning",
            },
            {
                "text": "陪にゃんこ聊天",
                "action": "kitchen_chat",
                "dialogue": "kitchen_casual_chat",
            },
            {"text": "返回客廳", "action": "leave_kitchen", "dialogue": None},
        ]
        self.selected_option = 0
        self.show_menu = True
        self.nyanko_messages = [
            "主人想在廚房做什麼呢？人家來幫忙喵～",
            "一起做料理最開心了喵❤",
            "人家新學了很多好吃的菜色喵～",
            "和主人一起在廚房的時光真幸福喵！",
        ]
        self.current_message = 0

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
        self.background.fill((255, 248, 220))  # 溫暖的米色背景

        # 簡單的廚房佈局
        self._create_kitchen_layout()

    def _create_kitchen_layout(self):
        """建立廚房佈局"""
        screen_width, screen_height = self.get_screen_size()

        # 流理台
        counter_color = (139, 69, 19)
        counter_rect = pygame.Rect(50, screen_height - 200, screen_width - 100, 80)
        pygame.draw.rect(self.background, counter_color, counter_rect)

        # 流理台檯面
        surface_color = (222, 184, 135)
        surface_rect = pygame.Rect(50, screen_height - 200, screen_width - 100, 20)
        pygame.draw.rect(self.background, surface_color, surface_rect)

        # 冰箱
        fridge_color = (192, 192, 192)
        fridge_rect = pygame.Rect(50, 200, 100, 300)
        pygame.draw.rect(self.background, fridge_color, fridge_rect)

        # 冰箱門把
        handle_color = (128, 128, 128)
        handle_rect = pygame.Rect(130, 320, 15, 60)
        pygame.draw.rect(self.background, handle_color, handle_rect)

        # 瓦斯爐
        stove_color = (105, 105, 105)
        stove_rect = pygame.Rect(200, screen_height - 180, 150, 60)
        pygame.draw.rect(self.background, stove_color, stove_rect)

        # 爐火位置
        for i in range(2):
            fire_x = 220 + i * 60
            fire_y = screen_height - 160
            pygame.draw.circle(self.background, (64, 64, 64), (fire_x, fire_y), 15)

    def setup_ui(self):
        """設置UI元素"""
        pass

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

        # 根據遊戲狀態更新可用選項
        if game_state:
            current_time = game_state.get("current_time_period", "morning")
            affection = game_state.get("affection", 0)

            # 根據時間調整選項可見性
            self._update_options_by_time(current_time)

            # 根據好感度調整對話
            self._update_message_by_affection(affection)

    def _update_options_by_time(self, time_period):
        """根據時間段更新選項"""
        # 早上突出早餐選項
        if time_period == "morning":
            if self.cooking_options[0]["text"] != "和にゃんこ一起做早餐 ★":
                self.cooking_options[0]["text"] = "和にゃんこ一起做早餐 ★"
        # 晚上突出晚餐選項
        elif time_period == "evening":
            if self.cooking_options[1]["text"] != "準備豐盛的晚餐 ★":
                self.cooking_options[1]["text"] = "準備豐盛的晚餐 ★"

    def _update_message_by_affection(self, affection):
        """根據好感度更新にゃんこ的訊息"""
        if affection >= 75:
            self.current_message = 3  # 最愛的訊息
        elif affection >= 50:
            self.current_message = 2  # 開心的訊息
        elif affection >= 25:
            self.current_message = 1  # 友善的訊息
        else:
            self.current_message = 0  # 普通的訊息

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        screen.blit(self.background, (0, 0))

        # 場景標題
        title_text = self.ui_font.render("廚房 🍳", True, (139, 69, 19))
        screen.blit(title_text, (20, 20))

        # にゃんこ的訊息
        message_text = self.ui_font.render(
            self.nyanko_messages[self.current_message], True, (255, 105, 180)
        )
        screen.blit(message_text, (20, 70))

        # 繪制選項選單
        if self.show_menu:
            self._render_cooking_menu(screen)

        # 操作提示
        screen_width, screen_height = self.get_screen_size()
        hint_text = self.ui_font.render(
            "↑↓: 選擇  Enter: 確認  ESC: 返回客廳", True, Colors.GRAY
        )
        screen.blit(hint_text, (20, screen_height - 30))

    def _render_cooking_menu(self, screen):
        """渲染料理選單"""
        screen_width, screen_height = self.get_screen_size()
        menu_start_y = 150

        # 選單背景
        menu_rect = pygame.Rect(
            100,
            menu_start_y - 20,
            screen_width - 200,
            len(self.cooking_options) * 40 + 40,
        )
        pygame.draw.rect(screen, (255, 255, 255, 200), menu_rect)
        pygame.draw.rect(screen, (139, 69, 19), menu_rect, 3)

        # 選項列表
        for i, option in enumerate(self.cooking_options):
            y_pos = menu_start_y + i * 40

            # 選中效果
            if i == self.selected_option:
                highlight_rect = pygame.Rect(110, y_pos - 5, screen_width - 220, 30)
                pygame.draw.rect(screen, (255, 192, 203), highlight_rect)

            # 選項文字
            color = (139, 69, 19) if i == self.selected_option else (105, 105, 105)
            option_text = self.ui_font.render(f"→ {option['text']}", True, color)
            screen.blit(option_text, (120, y_pos))

    def handle_event(self, event: pygame.event.Event):
        """處理事件"""
        if event.type == pygame.KEYDOWN:
            if self.show_menu:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(
                        self.cooking_options
                    )
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.cooking_options
                    )
                elif event.key == pygame.K_RETURN:
                    self._handle_option_selection()
                elif event.key == pygame.K_ESCAPE:
                    self.change_scene("living_room")
            elif event.key == pygame.K_ESCAPE:
                self.change_scene("living_room")

    def _handle_option_selection(self):
        """處理選項選擇"""
        selected_option = self.cooking_options[self.selected_option]
        action = selected_option["action"]
        dialogue_id = selected_option["dialogue"]

        if action == "leave_kitchen":
            self.change_scene("living_room")
        elif dialogue_id:
            # 觸發對話系統
            if hasattr(self.game_engine, "dialogue_system"):
                self.game_engine.dialogue_system.start_dialogue(dialogue_id)

            # 根據動作類型給予好感度獎勵
            affection_bonus = self._get_affection_bonus(action)
            if affection_bonus > 0 and hasattr(self.game_engine, "affection_system"):
                self.game_engine.affection_system.add_affection(
                    affection_bonus, f"在廚房{action}"
                )

    def _get_affection_bonus(self, action):
        """根據動作獲取好感度獎勵"""
        action_bonuses = {
            "breakfast_cooking": 3,
            "dinner_cooking": 4,
            "new_recipe": 2,
            "kitchen_chat": 1,
        }
        return action_bonuses.get(action, 0)

    def handle_escape(self):
        """處理ESC鍵"""
        self.change_scene("living_room")

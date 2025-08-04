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
        self.interaction_options = []
        self.selected_option = 0
        self.nyanko_position = None
        self.nyanko_mood = "normal"
        self.interaction_areas = {}

        super().__init__(game_engine, scene_manager)

        # 使用遊戲引擎的統一選擇系統
        self.unified_choice_system = self.game_engine.unified_choice_system

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
        self.interaction_areas["bathtub"] = bathtub_rect

        # 洗手台
        sink_color = (240, 240, 240)
        sink_rect = pygame.Rect(50, screen_height - 180, 150, 80)
        pygame.draw.rect(self.background, sink_color, sink_rect)
        self.interaction_areas["sink"] = sink_rect

        # 鏡子
        mirror_color = (200, 200, 255)
        mirror_rect = pygame.Rect(60, 150, 130, 100)
        pygame.draw.rect(self.background, mirror_color, mirror_rect)
        self.interaction_areas["mirror"] = mirror_rect

        # にゃんこ初始位置（洗手台旁）
        self.nyanko_position = (150, screen_height - 220)

    def setup_ui(self):
        """設置UI元素"""
        self.interaction_options = [
            {"text": "與にゃんこ聊天", "action": "chat_with_nyanko"},
            {"text": "洗手", "action": "wash_hands"},
            {"text": "照鏡子", "action": "look_mirror"},
            {"text": "洗澡", "action": "take_bath"},
            {"text": "返回客廳", "action": "go_living_room"},
        ]

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

        # 根據遊戲狀態更新可用選項
        if game_state:
            self.current_game_state = game_state
            current_time = game_state.get("current_time_period", "morning")
            affection = game_state.get("affection", 0)

            # 根據好感度調整互動選項
            if affection >= 60:
                if not any(
                    opt["action"] == "bath_together" for opt in self.interaction_options
                ):
                    # 在洗澡選項後插入一起洗澡選項
                    bath_index = next(
                        (
                            i
                            for i, opt in enumerate(self.interaction_options)
                            if opt["action"] == "take_bath"
                        ),
                        3,
                    )
                    self.interaction_options.insert(
                        bath_index + 1,
                        {"text": "一起洗澡 ❤", "action": "bath_together"},
                    )
        else:
            # 如果沒有提供遊戲狀態，從遊戲引擎獲取
            if hasattr(self.game_engine, "game_state"):
                self.current_game_state = self.game_engine.game_state
            else:
                self.current_game_state = {}

        # 更新對話系統
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.dialogue_system.update(dt, self.current_game_state)

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        screen.blit(self.background, (0, 0))

        # 場景標題
        title_text = self.ui_font.render("浴室", True, Colors.DARK_GRAY)
        screen.blit(title_text, (20, 20))

        # 繪製にゃんこ
        if self.nyanko_position:
            self._render_nyanko(screen)

        # 繪製互動選項
        self._render_interaction_options(screen)

        # 操作提示
        screen_width, screen_height = self.get_screen_size()
        hint_text = self.ui_font.render(
            "方向鍵選擇，空白鍵確認，ESC返回", True, Colors.GRAY
        )
        screen.blit(hint_text, (20, screen_height - 30))

        # 繪製對話框（如果需要）
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.dialogue_system.render(screen)

    def _render_nyanko(self, screen: pygame.Surface):
        """繪製にゃんこ"""
        nyanko_color = Colors.PINK if self.nyanko_mood == "happy" else Colors.LIGHT_PINK
        if self.nyanko_mood == "shy":
            nyanko_color = Colors.LIGHT_BLUE

        # 簡單的にゃんこ表示（圓形）
        pygame.draw.circle(screen, nyanko_color, self.nyanko_position, 30)

        # 貓耳
        ear_left = (self.nyanko_position[0] - 15, self.nyanko_position[1] - 20)
        ear_right = (self.nyanko_position[0] + 15, self.nyanko_position[1] - 20)
        pygame.draw.circle(screen, nyanko_color, ear_left, 8)
        pygame.draw.circle(screen, nyanko_color, ear_right, 8)

        # 心情文字顯示
        mood_text = {"happy": "😊", "shy": "😳", "normal": "😺"}.get(
            self.nyanko_mood, "😺"
        )

        mood_surface = self.ui_font.render(mood_text, True, Colors.BLACK)
        text_pos = (self.nyanko_position[0] - 10, self.nyanko_position[1] + 40)
        screen.blit(mood_surface, text_pos)

    def _render_interaction_options(self, screen: pygame.Surface):
        """繪製互動選項"""
        screen_width, screen_height = self.get_screen_size()
        option_x = 20
        option_y = 100

        for i, option in enumerate(self.interaction_options):
            color = Colors.BLUE if i == self.selected_option else Colors.DARK_GRAY
            option_text = self.ui_font.render(f"{i+1}. {option['text']}", True, color)
            screen.blit(option_text, (option_x, option_y + i * 35))

    def handle_event(self, event: pygame.event.Event):
        """處理事件"""
        # 首先讓對話系統處理事件
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            # 獲取當前遊戲狀態
            game_state = getattr(
                self,
                "current_game_state",
                (
                    self.game_engine.game_state
                    if hasattr(self.game_engine, "game_state")
                    else {}
                ),
            )

            # 如果對話系統處理了事件，就不再繼續處理其他事件
            if self.game_engine.dialogue_system.handle_event(event, game_state):
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_scene("living_room")
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(
                    self.interaction_options
                )
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(
                    self.interaction_options
                )
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self._execute_interaction()
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                option_index = event.key - pygame.K_1
                if option_index < len(self.interaction_options):
                    self.selected_option = option_index
                    self._execute_interaction()

    def _execute_interaction(self):
        """執行選中的互動"""
        if not self.interaction_options:
            return

        action = self.interaction_options[self.selected_option]["action"]

        if action == "chat_with_nyanko":
            self._chat_with_nyanko()
        elif action == "wash_hands":
            self._wash_hands()
        elif action == "look_mirror":
            self._look_mirror()
        elif action == "take_bath":
            self._take_bath()
        elif action == "bath_together":
            self._bath_together()
        elif action == "go_living_room":
            self.change_scene("living_room")

    def _chat_with_nyanko(self):
        """與にゃんこ聊天"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bathroom_chat_01")
        self.nyanko_mood = "happy"

    def _wash_hands(self):
        """洗手"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bathroom_wash_hands_01")

    def _look_mirror(self):
        """照鏡子"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bathroom_mirror_01")

    def _take_bath(self):
        """洗澡"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bathroom_bath_01")

    def _bath_together(self):
        """一起洗澡"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bathing_together_01")  # 使用已存在的對話
        self.nyanko_mood = "shy"

    def handle_escape(self):
        """處理ESC鍵"""
        self.change_scene("living_room")

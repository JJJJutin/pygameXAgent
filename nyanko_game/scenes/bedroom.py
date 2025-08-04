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
        self.interaction_areas["bed"] = bed_rect

        # 衣櫃
        wardrobe_color = (139, 69, 19)
        wardrobe_rect = pygame.Rect(50, 150, 80, 250)
        pygame.draw.rect(self.background, wardrobe_color, wardrobe_rect)
        self.interaction_areas["wardrobe"] = wardrobe_rect

        # 梳妝台
        dresser_color = (160, 82, 45)
        dresser_rect = pygame.Rect(screen_width - 200, 200, 120, 80)
        pygame.draw.rect(self.background, dresser_color, dresser_rect)
        self.interaction_areas["dresser"] = dresser_rect

        # にゃんこ初始位置（床邊）
        self.nyanko_position = (screen_width // 2, screen_height - 280)

    def setup_ui(self):
        """設置UI元素"""
        self.interaction_options = [
            {"text": "與にゃんこ聊天", "action": "chat_with_nyanko"},
            {"text": "整理床鋪", "action": "make_bed"},
            {"text": "檢查衣櫃", "action": "check_wardrobe"},
            {"text": "在梳妝台前整理儀容", "action": "use_dresser"},
            {"text": "休息一下", "action": "rest"},
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

            # 根據時間調整にゃんこ的行為和對話
            self._update_nyanko_behavior(current_time, affection)
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

    def _update_nyanko_behavior(self, time_period: str, affection: int):
        """根據時間和好感度更新にゃんこ行為"""
        if time_period == "night" or time_period == "late_night":
            # 夜晚時にゃんこ可能已經在床上
            screen_width, screen_height = self.get_screen_size()
            self.nyanko_position = (screen_width // 2, screen_height - 200)
            self.nyanko_mood = "sleepy"
        elif time_period == "morning":
            # 早晨時にゃんこ在整理房間
            self.nyanko_mood = "energetic"
        else:
            self.nyanko_mood = "normal"

        # 根據好感度調整互動選項
        if affection >= 60:
            if not any(
                opt["action"] == "intimate_chat" for opt in self.interaction_options
            ):
                self.interaction_options.insert(
                    1, {"text": "親密聊天 ❤", "action": "intimate_chat"}
                )

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        screen.blit(self.background, (0, 0))

        # 場景標題
        title_text = self.ui_font.render("臥室", True, Colors.DARK_GRAY)
        screen.blit(title_text, (20, 20))

        # 繪製にゃんこ
        if self.nyanko_position:
            self._render_nyanko(screen)

        # 不再顯示互動選項，因為已經整合到對話選擇中
        # self._render_interaction_options(screen)

        # 操作提示
        screen_width, screen_height = self.get_screen_size()
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system.is_active
        ):
            # 對話進行中
            hint_text = self.ui_font.render("對話進行中...", True, Colors.GRAY)
        else:
            # 提示點擊にゃんこ互動
            hint_text = self.ui_font.render(
                "點擊にゃんこ互動 | ESC: 返回客廳", True, Colors.GRAY
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
        if self.nyanko_mood == "sleepy":
            nyanko_color = Colors.LIGHT_GRAY

        # 簡單的にゃんこ表示（圓形）
        pygame.draw.circle(screen, nyanko_color, self.nyanko_position, 30)

        # 貓耳
        ear_left = (self.nyanko_position[0] - 15, self.nyanko_position[1] - 20)
        ear_right = (self.nyanko_position[0] + 15, self.nyanko_position[1] - 20)
        pygame.draw.circle(screen, nyanko_color, ear_left, 8)
        pygame.draw.circle(screen, nyanko_color, ear_right, 8)

        # 心情文字顯示
        mood_text = {
            "happy": "😊",
            "sleepy": "😴",
            "energetic": "✨",
            "normal": "😺",
        }.get(self.nyanko_mood, "😺")

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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                # 使用事件中已轉換的座標或獲取轉換後的滑鼠位置
                mouse_pos = getattr(event, "pos", self.get_mouse_pos())
                self._handle_mouse_click(mouse_pos)

    def _handle_mouse_click(self, mouse_pos: tuple):
        """處理滑鼠點擊"""
        # 檢查是否點擊了にゃんこ
        if self.nyanko_position:
            nyanko_rect = pygame.Rect(
                self.nyanko_position[0] - 35, self.nyanko_position[1] - 35, 70, 70
            )
            if nyanko_rect.collidepoint(mouse_pos):
                self._interact_with_nyanko()

    def _interact_with_nyanko(self):
        """與にゃんこ互動"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system.is_active
        ):
            print("對話進行中，請稍候...")
            return

        # 設定心情並觸發對話
        self.nyanko_mood = "happy"

        # 播放音效
        if (
            hasattr(self.game_engine, "audio_manager")
            and self.game_engine.audio_manager is not None
        ):
            self.game_engine.audio_manager.play_sfx("nyanko_interact", 0.7)

        # 根據時間段選擇適當的對話
        time_info = self._get_current_time_info()
        time_period = time_info.get("period_id", "morning")

        # 使用臥室專用的對話ID
        dialogue_id = f"bedroom_greeting_{time_period}_01"

        # 如果找不到特定對話，使用通用臥室對話
        if (
            not hasattr(self.game_engine, "dialogue_system")
            or dialogue_id not in self.game_engine.dialogue_system.dialogue_data
        ):
            dialogue_id = "bedroom_chat_01"

        self.game_engine.start_dialogue(dialogue_id)

    def _get_current_time_info(self):
        """獲取當前時間資訊"""
        if hasattr(self.game_engine, "get_current_time_info"):
            time_info = self.game_engine.get_current_time_info()
            if not time_info:
                return {
                    "period": "MORNING",
                    "period_id": "morning",
                    "day": 1,
                    "time": "08:00",
                    "time_points": 8,
                }
            return time_info
        return {
            "period": "MORNING",
            "period_id": "morning",
            "day": 1,
            "time": "08:00",
            "time_points": 8,
        }

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

        if game_state:
            self.current_game_state = game_state
        else:
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

        # 獲取時間資訊並更新にゃんこ狀態
        time_info = self._get_current_time_info()
        time_period = time_info.get("period_id", "morning")

        # 根據時間段設定にゃんこ位置和心情
        self._update_nyanko_by_time(time_period)

    def _update_nyanko_by_time(self, time_period):
        """根據時間段更新にゃんこ位置和心情"""
        screen_width, screen_height = self.get_screen_size()

        if time_period in ["night", "late_night"]:
            # 晚上在床上
            self.nyanko_position = (screen_width // 2, screen_height - 200)
            self.nyanko_mood = "sleepy"
        elif time_period == "morning":
            # 早上在梳妝台附近
            self.nyanko_position = (screen_width - 150, screen_height - 200)
            self.nyanko_mood = "energetic"
        else:
            # 其他時間在房間中央
            self.nyanko_position = (screen_width // 2 - 50, screen_height - 250)
            self.nyanko_mood = "normal"

    def _execute_interaction(self):
        """執行選中的互動"""
        if not self.interaction_options:
            return

        action = self.interaction_options[self.selected_option]["action"]

        if action == "chat_with_nyanko":
            self._chat_with_nyanko()
        elif action == "intimate_chat":
            self._intimate_chat()
        elif action == "make_bed":
            self._make_bed()
        elif action == "check_wardrobe":
            self._check_wardrobe()
        elif action == "use_dresser":
            self._use_dresser()
        elif action == "rest":
            self._rest()
        elif action == "go_living_room":
            self.change_scene("living_room")

    def _chat_with_nyanko(self):
        """與にゃんこ聊天"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            # 根據時間段選擇不同的對話
            time_period = getattr(
                self.game_engine.time_system, "get_current_time_period", lambda: None
            )()
            if time_period:
                period_name = (
                    time_period.value
                    if hasattr(time_period, "value")
                    else str(time_period)
                )
                dialogue_id = f"bedroom_chat_{period_name}_01"
                self.game_engine.start_dialogue(dialogue_id)
            else:
                self.game_engine.start_dialogue("bedroom_chat_general_01")

        self.nyanko_mood = "happy"

    def _intimate_chat(self):
        """親密聊天"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bedroom_intimate_chat_01")
        self.nyanko_mood = "happy"

    def _make_bed(self):
        """整理床鋪"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bedroom_make_bed_01")

        # 增加少量好感度
        if (
            hasattr(self.game_engine, "affection_system")
            and self.game_engine.affection_system
        ):
            self.game_engine.affection_system.modify_affection(1, "幫忙整理床鋪")

    def _check_wardrobe(self):
        """檢查衣櫃"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bedroom_wardrobe_01")

    def _use_dresser(self):
        """使用梳妝台"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.start_dialogue("bedroom_dresser_01")

    def _rest(self):
        """休息"""
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            # 根據時間決定休息類型
            time_period = getattr(
                self.game_engine.time_system, "get_current_time_period", lambda: None
            )()
            if time_period and (
                time_period.value == "night" or time_period.value == "late_night"
            ):
                self.game_engine.start_dialogue("bedroom_sleep_01")
            else:
                self.game_engine.start_dialogue("bedroom_nap_01")

    def handle_escape(self):
        """處理ESC鍵"""
        self.change_scene("living_room")

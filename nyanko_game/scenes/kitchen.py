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
                "dialogue": "cooking_together_01",
            },
            {
                "text": "準備豐盛的晚餐",
                "action": "dinner_cooking",
                "dialogue": "cooking_dinner_01",
            },
            {
                "text": "學習新的菜色",
                "action": "new_recipe",
                "dialogue": "new_recipe_learning_01",
            },
            {
                "text": "陪にゃんこ聊天",
                "action": "kitchen_chat",
                "dialogue": "kitchen_chat_01",
            },
            {
                "text": "幫忙清洗碗盤",
                "action": "wash_dishes",
                "dialogue": "kitchen_washing_01",
            },
            {
                "text": "檢查冰箱",
                "action": "check_fridge",
                "dialogue": "kitchen_fridge_01",
            },
            {"text": "返回客廳", "action": "leave_kitchen", "dialogue": None},
        ]
        self.selected_option = 0
        self.show_menu = False  # 改為False，整合到對話選擇中
        self.nyanko_position = None
        self.nyanko_mood = "normal"
        self.cooking_state = "idle"  # idle, cooking, cleaning
        self.interaction_areas = {}
        self.nyanko_messages = [
            "主人想在廚房做什麼呢？人家來幫忙喵～",
            "一起做料理最開心了喵❤",
            "人家新學了很多好吃的菜色喵～",
            "和主人一起在廚房的時光真幸福喵！",
        ]
        self.current_message = 0

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
        self.interaction_areas["counter"] = counter_rect

        # 流理台檯面
        surface_color = (222, 184, 135)
        surface_rect = pygame.Rect(50, screen_height - 200, screen_width - 100, 20)
        pygame.draw.rect(self.background, surface_color, surface_rect)

        # 冰箱
        fridge_color = (192, 192, 192)
        fridge_rect = pygame.Rect(50, 200, 100, 300)
        pygame.draw.rect(self.background, fridge_color, fridge_rect)
        self.interaction_areas["fridge"] = fridge_rect

        # 冰箱門把
        handle_color = (128, 128, 128)
        handle_rect = pygame.Rect(130, 320, 15, 60)
        pygame.draw.rect(self.background, handle_color, handle_rect)

        # 瓦斯爐
        stove_color = (105, 105, 105)
        stove_rect = pygame.Rect(200, screen_height - 180, 150, 60)
        pygame.draw.rect(self.background, stove_color, stove_rect)
        self.interaction_areas["stove"] = stove_rect

        # 爐火位置
        for i in range(2):
            fire_x = 220 + i * 60
            fire_y = screen_height - 160
            pygame.draw.circle(self.background, (64, 64, 64), (fire_x, fire_y), 15)

        # 水槽
        sink_color = (240, 240, 240)
        sink_rect = pygame.Rect(screen_width - 200, screen_height - 180, 120, 60)
        pygame.draw.rect(self.background, sink_color, sink_rect)
        self.interaction_areas["sink"] = sink_rect

        # にゃんこ初始位置（流理台旁）
        self.nyanko_position = (screen_width // 2, screen_height - 250)

    def setup_ui(self):
        """設置UI元素"""
        pass

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

        # 根據遊戲狀態更新可用選項
        if game_state:
            self.current_game_state = game_state
            current_time = game_state.get("current_time_period", "morning")
            affection = game_state.get("affection", 0)

            # 根據時間調整選項可見性
            self._update_options_by_time(current_time)

            # 根據好感度調整對話
            self._update_message_by_affection(affection)

            # 更新にゃんこ行為
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
        screen_width, screen_height = self.get_screen_size()

        if time_period == "morning":
            # 早晨在準備早餐
            self.nyanko_position = (280, screen_height - 250)  # 靠近爐子
            self.nyanko_mood = "energetic"
            self.cooking_state = "cooking"
        elif time_period == "afternoon":
            # 下午在整理廚房
            self.nyanko_position = (screen_width - 150, screen_height - 250)  # 靠近水槽
            self.nyanko_mood = "normal"
            self.cooking_state = "cleaning"
        elif time_period == "evening":
            # 傍晚準備晚餐
            self.nyanko_position = (200, screen_height - 250)  # 在流理台
            self.nyanko_mood = "happy"
            self.cooking_state = "cooking"
        else:
            # 其他時間一般位置
            self.nyanko_position = (screen_width // 2, screen_height - 250)
            self.nyanko_mood = "normal"
            self.cooking_state = "idle"

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

        # 繪製にゃんこ
        if self.nyanko_position:
            self._render_nyanko(screen)

        # 不再顯示舊的選項選單，因為已經整合到對話選擇中
        # if self.show_menu:
        #     self._render_cooking_menu(screen)

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
        if self.nyanko_mood == "energetic":
            nyanko_color = Colors.YELLOW

        # 簡單的にゃんこ表示（圓形）
        pygame.draw.circle(screen, nyanko_color, self.nyanko_position, 25)

        # 貓耳
        ear_left = (self.nyanko_position[0] - 12, self.nyanko_position[1] - 18)
        ear_right = (self.nyanko_position[0] + 12, self.nyanko_position[1] - 18)
        pygame.draw.circle(screen, nyanko_color, ear_left, 6)
        pygame.draw.circle(screen, nyanko_color, ear_right, 6)

        # 活動狀態顯示
        activity_text = {"cooking": "🍳", "cleaning": "🧽", "idle": "😺"}.get(
            self.cooking_state, "😺"
        )

        activity_surface = self.ui_font.render(activity_text, True, Colors.BLACK)
        text_pos = (self.nyanko_position[0] - 10, self.nyanko_position[1] + 35)
        screen.blit(activity_surface, text_pos)

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

    def handle_event(self, event: pygame.event.Event) -> bool:
        """處理事件"""
        # 首先讓對話系統處理事件（包含統一選擇系統）
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
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_scene("living_room")
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                # 使用事件中已轉換的座標或獲取轉換後的滑鼠位置
                mouse_pos = getattr(event, "pos", self.get_mouse_pos())
                self._handle_mouse_click(mouse_pos)
                return True

        return False

    def _handle_mouse_click(self, mouse_pos: tuple):
        """處理滑鼠點擊"""
        # 檢查是否點擊了にゃんこ
        if self.nyanko_position:
            nyanko_rect = pygame.Rect(
                self.nyanko_position[0] - 30, self.nyanko_position[1] - 30, 60, 60
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

        # 使用廚房專用的對話ID
        dialogue_id = f"kitchen_greeting_{time_period}_01"

        # 如果找不到特定對話，使用通用廚房對話
        if (
            not hasattr(self.game_engine, "dialogue_system")
            or dialogue_id not in self.game_engine.dialogue_system.dialogue_data
        ):
            dialogue_id = "kitchen_chat_01"

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

        # 獲取時間資訊
        time_info = self._get_current_time_info()
        time_period = time_info.get("period_id", "morning")

        # 根據時間段更新にゃんこ位置和狀態
        self._update_nyanko_by_time(time_period)

        # 根據好感度更新訊息
        affection = self.current_game_state.get("nyanko_affection", 50)
        self._update_message_by_affection(affection)

    def _handle_option_selection(self):
        """處理選項選擇"""
        selected_option = self.cooking_options[self.selected_option]
        action = selected_option["action"]
        dialogue_id = selected_option["dialogue"]

        if action == "leave_kitchen":
            self.change_scene("living_room")
        elif dialogue_id:
            # 檢查是否已有對話在進行中
            if (
                hasattr(self.game_engine, "dialogue_system")
                and self.game_engine.dialogue_system.is_active
            ):
                print("對話進行中，請稍候...")
                return

            # 觸發對話系統
            if hasattr(self.game_engine, "dialogue_system"):
                self.game_engine.dialogue_system.start_dialogue(dialogue_id)

            # 根據動作類型給予好感度獎勵
            affection_bonus = self._get_affection_bonus(action)
            if affection_bonus > 0 and hasattr(self.game_engine, "affection_system"):
                self.game_engine.affection_system.change_affection(
                    affection_bonus, reason=f"在廚房{action}"
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

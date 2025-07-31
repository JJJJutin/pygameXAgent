# -*- coding: utf-8 -*-
"""
客廳場景
主要的遊戲場景，玩家與にゃんこ的日常互動場所
"""

import pygame
from scenes.base_scene import BaseScene
from config.settings import *
from systems.image_manager import image_manager


class LivingRoomScene(BaseScene):
    """客廳場景類別"""

    def __init__(self, game_engine, scene_manager):
        """初始化客廳場景"""
        self.background = None
        self.ui_font = None
        self.dialogue_font = None

        # 場景狀態
        self.current_time = "morning"
        self.day_count = 1

        # にゃんこ狀態
        self.nyanko_present = True
        self.nyanko_mood = "normal"
        self.nyanko_position = (600, 400)  # 初始位置，會在渲染時動態更新
        self.nyanko_rect = None  # 點擊檢測區域，會在渲染時動態更新

        # 新增的互動選項
        self.activity_options = [
            {
                "text": "和にゃんこ一起看電視",
                "action": "watch_tv",
                "dialogue": "tv_together_01",
            },
            {
                "text": "玩遊戲",
                "action": "play_games",
                "dialogue": "gaming_together_01",
            },
            {
                "text": "聊天談心",
                "action": "heart_to_heart",
                "dialogue": "casual_chat_01",
            },
            {"text": "放鬆休息", "action": "relax_together", "dialogue": "relaxing_01"},
            {"text": "前往廚房", "action": "go_kitchen", "dialogue": None},
            {"text": "前往臥室", "action": "go_bedroom", "dialogue": None},
            {"text": "前往浴室", "action": "go_bathroom", "dialogue": None},
        ]
        self.selected_option = 0
        self.show_menu = False
        self.weather_state = "normal"  # normal, rainy, sunny

        super().__init__(game_engine, scene_manager)

    def load_resources(self):
        """載入場景資源"""
        # 確保圖片管理器已載入
        image_manager.load_all_images()

        # 建立字體（使用中文字體）
        try:
            self.ui_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.FONT_SIZE_MEDIUM
            )
            self.dialogue_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.DIALOGUE_FONT_SIZE
            )
        except (FileNotFoundError, OSError):
            # 如果找不到指定字體，使用系統預設字體
            print("警告: 無法載入指定字體，使用系統預設字體")
            self.ui_font = pygame.font.Font(None, FontSettings.FONT_SIZE_MEDIUM)
            self.dialogue_font = pygame.font.Font(None, FontSettings.DIALOGUE_FONT_SIZE)

        # 載入背景圖片
        self.background_morning = image_manager.get_image("bg_livingroom_morning")
        self.background_evening = image_manager.get_image("bg_livingroom_evening")

        # 如果圖片載入失敗，創建替代背景
        if not self.background_morning or not self.background_evening:
            self._create_fallback_background()

    def _create_fallback_background(self):
        """創建備用背景（如果圖片載入失敗）"""
        screen_width, screen_height = self.get_screen_size()

        # 早上背景
        self.background_morning = pygame.Surface((screen_width, screen_height))
        self.background_morning.fill((255, 255, 200))  # 淡黃色
        self._create_background_layout(self.background_morning, "morning")

        # 晚上背景
        self.background_evening = pygame.Surface((screen_width, screen_height))
        self.background_evening.fill((100, 100, 200))  # 深藍色
        self._create_background_layout(self.background_evening, "evening")

    def _create_background_layout(self, surface, time_of_day):
        """建立背景佈局"""
        screen_width, screen_height = self.get_screen_size()

        # 根據時間選擇顏色
        if time_of_day == "morning":
            floor_color = (240, 220, 180)  # 溫暖的淺褐色
            furniture_color = (160, 120, 80)  # 明亮的木色
        else:
            floor_color = (180, 160, 140)  # 較暗的褐色
            furniture_color = (120, 90, 60)  # 較暗的木色

        # 繪製地板
        floor_rect = pygame.Rect(0, screen_height - 200, screen_width, 200)
        pygame.draw.rect(surface, floor_color, floor_rect)

        # 繪製沙發
        sofa_rect = pygame.Rect(100, screen_height - 300, 200, 100)
        pygame.draw.rect(surface, furniture_color, sofa_rect)

        # 繪製桌子
        table_rect = pygame.Rect(400, screen_height - 250, 150, 50)
        pygame.draw.rect(surface, furniture_color, table_rect)

        # 繪製窗戶（根據時間變化）
        if time_of_day == "morning":
            window_color = (255, 255, 200)  # 明亮的黃色
        else:
            window_color = (50, 50, 100)  # 深藍色夜空

        window_rect = pygame.Rect(screen_width - 250, 100, 200, 150)
        pygame.draw.rect(surface, window_color, window_rect)
        pygame.draw.rect(surface, Colors.DARK_GRAY, window_rect, 3)

    def setup_ui(self):
        """設置UI元素"""
        # 初始化UI狀態
        pass

    def update(self, dt: float, game_state: dict = None):
        """更新場景邏輯"""
        if self.paused:
            return

        # 更新遊戲邏輯
        # 如果需要，可以在這裡檢查遊戲狀態並觸發事件
        if game_state:
            self.current_game_state = None

        # nyanko_rect 會在 _render_nyanko() 中動態更新

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        # 根據時間選擇背景
        if self.current_time in ["morning", "afternoon"]:
            current_bg = self.background_morning
        else:
            current_bg = self.background_evening

        # 縮放背景到螢幕大小
        screen_size = self.get_screen_size()
        if current_bg:
            scaled_bg = pygame.transform.scale(current_bg, screen_size)
            screen.blit(scaled_bg, (0, 0))
        else:
            # 備用背景色
            screen.fill(Colors.LIGHT_PINK)

        # 繪製にゃんこ
        if self.nyanko_present:
            self._render_nyanko(screen)

        # 繪製UI
        self._render_ui(screen)

        # 繪製對話框（如果需要）
        # self._render_dialogue(screen)

    def _render_nyanko(self, screen: pygame.Surface):
        """繪製にゃんこ角色"""
        # 根據心情選擇圖片
        if self.nyanko_mood == "happy":
            emotion = "happy"
        else:
            emotion = "normal"

        # 獲取螢幕尺寸
        screen_width, screen_height = self.get_screen_size()

        # 計算適合的人物立繪尺寸（根據螢幕大小自動調整）
        char_width, char_height = image_manager.get_adaptive_character_size(
            screen_width, screen_height
        )

        # 獲取縮放後的角色圖片
        nyanko_image = image_manager.get_scaled_character_image(
            "nyanko", emotion, "default", (char_width, char_height)
        )

        if nyanko_image:
            # 計算最佳位置（自動根據螢幕大小調整）
            char_x, char_y = image_manager.get_adaptive_character_position(
                screen_width, screen_height, char_width, char_height
            )

            # 繪製角色
            screen.blit(nyanko_image, (char_x, char_y))

            # 更新 nyanko_position 以供點擊檢測使用
            self.nyanko_position = (char_x + char_width // 2, char_y + char_height // 2)

            # 更新 nyanko_rect 以供點擊檢測使用
            self.nyanko_rect = pygame.Rect(char_x, char_y, char_width, char_height)
        else:
            # 備用：使用簡單圖形代表にゃんこ
            nyanko_color = Colors.PINK
            nyanko_radius = max(30, int(screen_width * 0.025))  # 根據螢幕大小調整

            # 使用固定位置的備用顯示
            backup_x = screen_width - 150
            backup_y = screen_height - 150
            self.nyanko_position = (backup_x, backup_y)

            # 繪製身體
            pygame.draw.circle(
                screen, nyanko_color, self.nyanko_position, nyanko_radius
            )

            # 繪製貓耳
            ear_offset = int(nyanko_radius * 0.7)
            ear_size = int(nyanko_radius * 0.3)
            left_ear = (backup_x - ear_offset, backup_y - ear_offset)
            right_ear = (backup_x + ear_offset, backup_y - ear_offset)
            pygame.draw.circle(screen, nyanko_color, left_ear, ear_size)
            pygame.draw.circle(screen, nyanko_color, right_ear, ear_size)

            # 更新點擊區域
            self.nyanko_rect = pygame.Rect(
                backup_x - nyanko_radius,
                backup_y - nyanko_radius,
                nyanko_radius * 2,
                nyanko_radius * 2,
            )

        # 繪製名字標籤
        name_text = self.ui_font.render("にゃんこ", True, Colors.DARK_GRAY)
        name_rect = name_text.get_rect()
        name_rect.centerx = self.nyanko_position[0]
        name_rect.y = self.nyanko_position[1] + (
            char_height // 4 if nyanko_image else 60
        )
        screen.blit(name_text, name_rect)

    def _render_ui(self, screen: pygame.Surface):
        """繪製UI介面"""
        screen_width, screen_height = self.get_screen_size()

        # 繪製遊戲資訊
        info_y = 20

        # 天數
        day_text = self.ui_font.render(
            f"第 {self.day_count} 天", True, Colors.DARK_GRAY
        )
        screen.blit(day_text, (20, info_y))

        # 時間
        time_text = self.ui_font.render(
            f"時間: {self._get_time_display()}", True, Colors.DARK_GRAY
        )
        screen.blit(time_text, (20, info_y + 30))

        # 場景名稱
        scene_text = self.ui_font.render("客廳", True, Colors.DARK_GRAY)
        scene_rect = scene_text.get_rect()
        scene_rect.right = screen_width - 20
        scene_rect.y = info_y
        screen.blit(scene_text, scene_rect)

        # 繪制活動選單
        if self.show_menu:
            self._render_activity_menu(screen)
        else:
            # 操作提示
            hint_text = self.ui_font.render(
                "SPACE: 與にゃんこ互動  TAB: 活動選單", True, Colors.GRAY
            )
            hint_rect = hint_text.get_rect()
            hint_rect.centerx = screen_width // 2
            hint_rect.y = screen_height - 50
            screen.blit(hint_text, hint_rect)

        # ESC 提示
        esc_text = self.ui_font.render(
            "ESC: 返回主選單  1:廚房 2:臥室 3:浴室", True, Colors.GRAY
        )
        screen.blit(esc_text, (20, screen_height - 30))

    def _get_time_display(self) -> str:
        """
        獲取時間顯示文字

        Returns:
            str: 時間顯示文字
        """
        time_names = {
            "early_morning": "清晨",
            "morning": "上午",
            "afternoon": "下午",
            "evening": "傍晚",
            "night": "夜晚",
            "late_night": "深夜",
        }
        return time_names.get(self.current_time, "未知")

    def handle_event(self, event: pygame.event.Event):
        """處理事件"""
        # 處理表情重置事件
        if event.type == pygame.USEREVENT + 1:
            self.nyanko_mood = "normal"
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # 停止計時器

        elif event.type == pygame.KEYDOWN:
            if self.show_menu:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(
                        self.activity_options
                    )
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.activity_options
                    )
                elif event.key == pygame.K_RETURN:
                    self._handle_option_selection()
                elif event.key == pygame.K_ESCAPE:
                    self.show_menu = False
            else:
                if event.key == pygame.K_SPACE:
                    self._interact_with_nyanko()
                elif event.key == pygame.K_TAB:
                    self.show_menu = True
                elif event.key == pygame.K_1:
                    self.change_scene("kitchen")
                elif event.key == pygame.K_2:
                    self.change_scene("bedroom")
                elif event.key == pygame.K_3:
                    self.change_scene("bathroom")
                elif event.key == pygame.K_ESCAPE:
                    self.change_scene("main_menu")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵點擊
                mouse_pos = pygame.mouse.get_pos()
                self._handle_mouse_click(mouse_pos)

    def _interact_with_nyanko(self):
        """與にゃんこ互動"""
        if self.nyanko_present:
            # 互動時讓にゃんこ變開心
            self.nyanko_mood = "happy"

            print("與にゃんこ開始對話...")
            # 使用遊戲引擎的對話系統
            if (
                hasattr(self.game_engine, "time_system")
                and self.game_engine.time_system
            ):
                time_period = (
                    self.game_engine.time_system.get_current_time_period().value
                )
                dialogue_id = f"greeting_{time_period}_01"
                self.game_engine.start_dialogue(dialogue_id)
            else:
                # 後備對話
                self.game_engine.start_dialogue("greeting_morning_01")

        # 一段時間後恢復正常表情
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # 3秒後

    def _show_menu(self):
        """顯示遊戲選單"""
        self.show_menu = True

    def _render_activity_menu(self, screen):
        """渲染活動選單"""
        screen_width, screen_height = self.get_screen_size()
        menu_start_y = 180

        # 選單背景
        menu_rect = pygame.Rect(
            100,
            menu_start_y - 20,
            screen_width - 200,
            len(self.activity_options) * 35 + 40,
        )
        pygame.draw.rect(screen, (255, 255, 255, 220), menu_rect)
        pygame.draw.rect(screen, (70, 130, 180), menu_rect, 3)

        # 選項列表
        for i, option in enumerate(self.activity_options):
            y_pos = menu_start_y + i * 35

            # 選中效果
            if i == self.selected_option:
                highlight_rect = pygame.Rect(110, y_pos - 5, screen_width - 220, 25)
                pygame.draw.rect(screen, (173, 216, 230), highlight_rect)

            # 選項文字
            color = (70, 130, 180) if i == self.selected_option else (105, 105, 105)
            option_text = self.ui_font.render(f"→ {option['text']}", True, color)
            screen.blit(option_text, (120, y_pos))

    def _handle_option_selection(self):
        """處理選項選擇"""
        selected_option = self.activity_options[self.selected_option]
        action = selected_option["action"]
        dialogue_id = selected_option["dialogue"]

        self.show_menu = False  # 關閉選單

        # 場景切換
        scene_actions = {
            "go_kitchen": "kitchen",
            "go_bedroom": "bedroom",
            "go_bathroom": "bathroom",
        }

        if action in scene_actions:
            self.change_scene(scene_actions[action])
        elif dialogue_id:
            # 觸發對話系統
            if hasattr(self.game_engine, "dialogue_system"):
                self.game_engine.dialogue_system.start_dialogue(dialogue_id)

            # 根據動作類型給予好感度獎勵
            affection_bonus = self._get_affection_bonus(action)
            if affection_bonus > 0 and hasattr(self.game_engine, "affection_system"):
                self.game_engine.affection_system.add_affection(
                    affection_bonus, f"在客廳{action}"
                )

    def _get_affection_bonus(self, action):
        """根據動作獲取好感度獎勵"""
        action_bonuses = {
            "watch_tv": 3,
            "play_games": 2,
            "heart_to_heart": 4,
            "relax_together": 2,
        }
        return action_bonuses.get(action, 0)

    def _handle_mouse_click(self, mouse_pos: tuple):
        """處理滑鼠點擊"""
        # 檢查是否點擊了にゃんこ（使用動態更新的區域）
        if self.nyanko_present and hasattr(self, "nyanko_rect"):
            if self.nyanko_rect.collidepoint(mouse_pos):
                self._interact_with_nyanko()

    def on_enter(self, transition_data=None):
        """場景進入時的回調"""
        super().on_enter(transition_data)

        if transition_data and transition_data.get("new_game"):
            # 新遊戲初始化
            self.day_count = 1
            self.current_time = "morning"
            print("開始新的一天...")

    def handle_escape(self):
        """處理ESC鍵"""
        # 返回主選單並確認
        print("確定要返回主選單嗎？")
        # TODO: 添加確認對話框
        self.change_scene("main_menu")

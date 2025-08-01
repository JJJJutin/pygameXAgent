# -*- coding: utf-8 -*-
"""
客廳場景 - 事件驅動版本
主要的遊戲場景，支持事件驅動時間系統的玩家與にゃんこ的日常互動場所
"""

import pygame
from scenes.base_scene import BaseScene
from config.settings import *
from systems.image_manager import image_manager
from systems.game_ui import GameStatusUI


class EnhancedLivingRoomScene(BaseScene):
    """客廳場景類別 - 事件驅動版本"""

    def __init__(self, game_engine, scene_manager):
        """初始化客廳場景"""
        self.background = None
        self.ui_font = None
        self.dialogue_font = None

        # にゃんこ狀態
        self.nyanko_present = True
        self.nyanko_mood = "normal"
        self.nyanko_position = (600, 400)
        self.nyanko_rect = None

        # 事件驅動活動系統
        self.activity_menu_visible = False
        self.selected_activity = 0
        self.available_activities = []
        self.activity_result_display = False
        self.activity_result = {}
        self.result_timer = 0

        # 場景相關設置
        self.weather_state = "normal"

        super().__init__(game_engine, scene_manager)

        # 初始化UI系統 - 只使用GameStatusUI作為唯一UI面板
        screen_width, screen_height = self.get_screen_size()
        self.status_ui = GameStatusUI(screen_width, screen_height)

        # 設置活動結果回調
        if hasattr(self.game_engine, "set_activity_result_callback"):
            self.game_engine.set_activity_result_callback(self._on_activity_complete)

    def load_resources(self):
        """載入場景資源"""
        image_manager.load_all_images()

        try:
            self.ui_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.FONT_SIZE_MEDIUM
            )
            self.dialogue_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.DIALOGUE_FONT_SIZE
            )
        except (FileNotFoundError, OSError):
            print("警告: 無法載入指定字體，使用系統預設字體")
            self.ui_font = pygame.font.Font(None, FontSettings.FONT_SIZE_MEDIUM)
            self.dialogue_font = pygame.font.Font(None, FontSettings.DIALOGUE_FONT_SIZE)

        # 載入背景圖片
        self.background_morning = image_manager.get_image("bg_livingroom_morning")
        self.background_evening = image_manager.get_image("bg_livingroom_evening")

        if not self.background_morning or not self.background_evening:
            self._create_fallback_background()

    def _create_fallback_background(self):
        """創建備用背景"""
        screen_width, screen_height = self.get_screen_size()

        self.background_morning = pygame.Surface((screen_width, screen_height))
        self.background_morning.fill((255, 255, 200))
        self._create_background_layout(self.background_morning, "morning")

        self.background_evening = pygame.Surface((screen_width, screen_height))
        self.background_evening.fill((100, 100, 200))
        self._create_background_layout(self.background_evening, "evening")

    def _create_background_layout(self, surface, time_of_day):
        """建立背景佈局"""
        screen_width, screen_height = self.get_screen_size()

        if time_of_day == "morning":
            floor_color = (240, 220, 180)
            furniture_color = (160, 120, 80)
            window_color = (255, 255, 200)
        else:
            floor_color = (180, 160, 140)
            furniture_color = (120, 90, 60)
            window_color = (50, 50, 100)

        # 繪製地板
        floor_rect = pygame.Rect(0, screen_height - 200, screen_width, 200)
        pygame.draw.rect(surface, floor_color, floor_rect)

        # 繪製沙發
        sofa_rect = pygame.Rect(100, screen_height - 300, 200, 100)
        pygame.draw.rect(surface, furniture_color, sofa_rect)

        # 繪製桌子
        table_rect = pygame.Rect(400, screen_height - 250, 150, 50)
        pygame.draw.rect(surface, furniture_color, table_rect)

        # 繪製窗戶
        window_rect = pygame.Rect(screen_width - 250, 100, 200, 150)
        pygame.draw.rect(surface, window_color, window_rect)
        pygame.draw.rect(surface, Colors.DARK_GRAY, window_rect, 3)

    def setup_ui(self):
        """設置UI元素"""
        pass

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

        # 更新可用活動列表
        if hasattr(self.game_engine, "get_scene_activities"):
            self.available_activities = self.game_engine.get_scene_activities(
                "living_room"
            )

        # 更新UI系統動畫
        self.status_ui.update(dt)

        # 更新對話系統
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.dialogue_system.update(dt, self.current_game_state)

        # 自動隱藏活動結果
        if self.activity_result_display:
            if pygame.time.get_ticks() - self.result_timer > 3000:
                self.activity_result_display = False

    def render(self, screen: pygame.Surface):
        """渲染場景"""
        # 獲取當前時間資訊來選擇背景
        time_info = self._get_current_time_info()
        time_period = time_info.get("period", "MORNING")

        if time_period in ["MORNING", "AFTERNOON"]:
            current_bg = self.background_morning
        else:
            current_bg = self.background_evening

        # 縮放背景到螢幕大小 - 使用像素完整縮放
        screen_size = self.get_screen_size()
        if current_bg:
            from config.settings import ImageScaling

            scaled_bg = ImageScaling.pixel_perfect_scale(current_bg, screen_size)
            screen.blit(scaled_bg, (0, 0))
        else:
            screen.fill(Colors.LIGHT_PINK)

        # 繪製にゃんこ
        if self.nyanko_present:
            self._render_nyanko(screen)

        # 繪製新的UI系統
        self._render_new_ui(screen)

        # 繪製活動選單
        if self.activity_menu_visible:
            self._render_activity_menu(screen)

        # 繪製活動結果
        if self.activity_result_display:
            self._render_activity_result(screen)

        # 繪製對話框
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            self.game_engine.dialogue_system.render(screen)

    def _get_current_time_info(self):
        """獲取當前時間資訊"""
        if hasattr(self.game_engine, "get_current_time_info"):
            time_info = self.game_engine.get_current_time_info()
            # 如果時間系統沒有初始化，提供預設值
            if not time_info:
                return {
                    "period": "MORNING",
                    "day": 1,
                    "time": "08:00",
                    "time_points": 8,
                }
            return time_info
        return {"period": "MORNING", "day": 1, "time": "08:00", "time_points": 8}

    def _render_nyanko(self, screen: pygame.Surface):
        """繪製にゃんこ角色"""
        if self.nyanko_mood == "happy":
            emotion = "happy"
        else:
            emotion = "normal"

        screen_width, screen_height = self.get_screen_size()
        char_width, char_height = image_manager.get_adaptive_character_size(
            screen_width, screen_height
        )

        nyanko_image = image_manager.get_scaled_character_image(
            "nyanko", emotion, "default", (char_width, char_height)
        )

        if nyanko_image:
            char_x, char_y = image_manager.get_adaptive_character_position(
                screen_width, screen_height, char_width, char_height
            )
            screen.blit(nyanko_image, (char_x, char_y))
            self.nyanko_position = (char_x + char_width // 2, char_y + char_height // 2)
            self.nyanko_rect = pygame.Rect(char_x, char_y, char_width, char_height)
        else:
            # 備用顯示
            nyanko_color = Colors.PINK
            nyanko_radius = max(30, int(screen_width * 0.025))
            backup_x = screen_width - 150
            backup_y = screen_height - 150
            self.nyanko_position = (backup_x, backup_y)

            pygame.draw.circle(
                screen, nyanko_color, self.nyanko_position, nyanko_radius
            )

            # 貓耳
            ear_offset = int(nyanko_radius * 0.7)
            ear_size = int(nyanko_radius * 0.3)
            left_ear = (backup_x - ear_offset, backup_y - ear_offset)
            right_ear = (backup_x + ear_offset, backup_y - ear_offset)
            pygame.draw.circle(screen, nyanko_color, left_ear, ear_size)
            pygame.draw.circle(screen, nyanko_color, right_ear, ear_size)

            self.nyanko_rect = pygame.Rect(
                backup_x - nyanko_radius,
                backup_y - nyanko_radius,
                nyanko_radius * 2,
                nyanko_radius * 2,
            )

        # 名字標籤
        name_text = self.ui_font.render("にゃんこ", True, Colors.DARK_GRAY)
        name_rect = name_text.get_rect()
        name_rect.centerx = self.nyanko_position[0]
        name_rect.y = self.nyanko_position[1] + (
            char_height // 4 if nyanko_image else 60
        )
        screen.blit(name_text, name_rect)

    def _render_new_ui(self, screen):
        """使用新的UI系統渲染狀態顯示"""
        # 準備時間資訊
        if (
            hasattr(self.game_engine, "event_driven_time_system")
            and self.game_engine.event_driven_time_system
        ):
            # 使用事件驅動時間系統
            time_info = (
                self.game_engine.event_driven_time_system.get_current_time_info()
            )
        else:
            # 使用基本時間系統或回退到默認值
            time_system = self.game_engine.time_system
            if time_system:
                time_info = {
                    "day": time_system.get_current_day(),
                    "time": time_system.get_current_time(),
                    "period": time_system.get_current_time_period().value,
                    "time_points": time_system.get_time_points(),
                    "max_time_points": time_system.get_max_time_points(),
                }
            else:
                time_info = {
                    "day": 1,
                    "time": "08:00",
                    "period": "morning",
                    "time_points": 6,
                    "max_time_points": 6,
                }

        # 準備遊戲狀態
        if (
            hasattr(self.game_engine, "event_driven_time_system")
            and self.game_engine.event_driven_time_system
        ):
            game_state = self.game_engine.event_driven_time_system.get_game_state()
        else:
            game_state = {
                "health": getattr(self.game_engine, "character_stats", {}).get(
                    "health", 100
                ),
                "nyanko_affection": getattr(
                    self.game_engine, "character_stats", {}
                ).get("nyanko_affection", 50),
                "nyanko_mood": getattr(self.game_engine, "character_stats", {}).get(
                    "nyanko_mood", 75
                ),
                "nyanko_energy": 100,  # 默認值
            }

        # 更新動畫和顯示GameStatusUI
        dt = 1 / 60  # 假設60fps
        self.status_ui.update(dt)
        self.status_ui.draw_main_status_panel(screen, time_info, game_state)
        self.status_ui.draw_detailed_status_panel(screen, game_state)
        self.status_ui.draw_time_points_indicator(screen, time_info)

    def _render_ui(self, screen: pygame.Surface):
        """繪製UI介面"""
        screen_width, screen_height = self.get_screen_size()
        info_y = 20

        # 時間資訊
        time_info = self._get_current_time_info()

        # 天數和時間段
        day_text = self.ui_font.render(
            f"第 {time_info['day']} 天", True, Colors.DARK_GRAY
        )
        screen.blit(day_text, (20, info_y))

        time_text = self.ui_font.render(
            f"{self._get_period_display(time_info['period'])} ({time_info['time']})",
            True,
            Colors.DARK_GRAY,
        )
        screen.blit(time_text, (20, info_y + 30))

        # 時間點數
        points_text = self.ui_font.render(
            f"時間點數: {time_info['time_points']}", True, Colors.BLUE
        )
        screen.blit(points_text, (20, info_y + 60))

        # にゃんこ狀態
        if hasattr(self.game_engine, "event_driven_time_system"):
            game_state = self.game_engine.event_driven_time_system.get_game_state()

            state_title = self.ui_font.render("にゃんこ狀態:", True, Colors.DARK_GRAY)
            screen.blit(state_title, (20, info_y + 100))

            state_items = [
                f"體力: {game_state['nyanko_energy']}/100",
                f"好感度: {game_state['nyanko_affection']}/100",
                f"心情: {game_state['nyanko_mood']}/100",
            ]

            for i, item in enumerate(state_items):
                item_surface = self.ui_font.render(item, True, Colors.DARK_GRAY)
                screen.blit(item_surface, (40, info_y + 125 + i * 25))

        # 場景名稱
        scene_text = self.ui_font.render("客廳", True, Colors.DARK_GRAY)
        scene_rect = scene_text.get_rect()
        scene_rect.right = screen_width - 20
        scene_rect.y = info_y
        screen.blit(scene_text, scene_rect)

        # 操作提示
        if not self.activity_menu_visible:
            if self.available_activities:
                hint_text = self.ui_font.render(
                    "SPACE: 活動選單  CLICK: 與にゃんこ互動", True, Colors.GRAY
                )
            else:
                hint_text = self.ui_font.render(
                    "此時間段沒有可用活動 - 按T跳過時間", True, Colors.RED
                )

            hint_rect = hint_text.get_rect()
            hint_rect.centerx = screen_width // 2
            hint_rect.y = screen_height - 80
            screen.blit(hint_text, hint_rect)

        # 場景切換提示
        nav_text = self.ui_font.render(
            "1:廚房 2:臥室 3:浴室 ESC:主選單", True, Colors.GRAY
        )
        screen.blit(nav_text, (20, screen_height - 50))

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

    def _render_activity_menu(self, screen: pygame.Surface):
        """渲染活動選單"""
        if not self.available_activities:
            return

        screen_width, screen_height = self.get_screen_size()

        # 計算選單尺寸
        menu_width = 500
        menu_height = len(self.available_activities) * 80 + 60
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2

        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # 選單背景
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill((255, 255, 255))
        pygame.draw.rect(menu_surface, (70, 130, 180), menu_surface.get_rect(), 3)

        # 標題
        title_text = self.ui_font.render("選擇活動", True, (50, 50, 50))
        title_rect = title_text.get_rect()
        title_rect.centerx = menu_width // 2
        title_rect.y = 10
        menu_surface.blit(title_text, title_rect)

        # 活動選項
        y_offset = 50
        for i, activity in enumerate(self.available_activities):
            # 選中高亮
            if i == self.selected_activity:
                highlight_rect = pygame.Rect(10, y_offset - 5, menu_width - 20, 70)
                pygame.draw.rect(menu_surface, (173, 216, 230), highlight_rect)

            # 活動名稱
            color = (0, 100, 200) if i == self.selected_activity else (50, 50, 50)
            name_text = self.ui_font.render(activity.name, True, color)
            menu_surface.blit(name_text, (20, y_offset))

            # 活動描述
            desc_color = (100, 100, 100)
            try:
                desc_font = pygame.font.Font(FontSettings.DEFAULT_FONT, 20)
            except (FileNotFoundError, OSError):
                desc_font = self.ui_font
            desc_text = desc_font.render(activity.description, True, desc_color)
            menu_surface.blit(desc_text, (20, y_offset + 25))

            # 效果資訊
            effects_text = f"消耗{activity.time_cost}點 | 體力{activity.energy_change:+d} 好感{activity.affection_change:+d} 心情{activity.mood_change:+d}"
            try:
                effects_font = pygame.font.Font(FontSettings.DEFAULT_FONT, 18)
            except (FileNotFoundError, OSError):
                effects_font = self.ui_font
            effects_surface = effects_font.render(effects_text, True, (80, 80, 80))
            menu_surface.blit(effects_surface, (20, y_offset + 45))

            y_offset += 80

        # 操作提示
        try:
            hint_font = pygame.font.Font(FontSettings.DEFAULT_FONT, 20)
        except (FileNotFoundError, OSError):
            hint_font = self.ui_font
        hint_text = hint_font.render(
            "↑↓ 選擇  Enter 確認  ESC 取消", True, (100, 100, 100)
        )
        hint_rect = hint_text.get_rect()
        hint_rect.centerx = menu_width // 2
        hint_rect.y = menu_height - 25
        menu_surface.blit(hint_text, hint_rect)

        screen.blit(menu_surface, (menu_x, menu_y))

    def _render_activity_result(self, screen: pygame.Surface):
        """渲染活動結果"""
        screen_width, screen_height = self.get_screen_size()

        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # 結果框
        result_width = 400
        result_height = 200
        result_x = (screen_width - result_width) // 2
        result_y = (screen_height - result_height) // 2

        result_surface = pygame.Surface((result_width, result_height))
        result_surface.fill((255, 255, 255))
        pygame.draw.rect(result_surface, (0, 150, 0), result_surface.get_rect(), 3)

        # 結果內容
        y_offset = 20

        title_text = self.ui_font.render("活動完成！", True, (0, 150, 0))
        title_rect = title_text.get_rect()
        title_rect.centerx = result_width // 2
        title_rect.y = y_offset
        result_surface.blit(title_text, title_rect)

        if self.activity_result:
            y_offset += 50
            activity_text = self.ui_font.render(
                f"完成: {self.activity_result.get('name', '未知活動')}",
                True,
                (50, 50, 50),
            )
            activity_rect = activity_text.get_rect()
            activity_rect.centerx = result_width // 2
            activity_rect.y = y_offset
            result_surface.blit(activity_text, activity_rect)

            # 效果顯示
            changes = self.activity_result.get("changes", {})
            y_offset += 40
            for stat, value in changes.items():
                if value != 0:
                    color = (0, 150, 0) if value > 0 else (200, 0, 0)
                    change_text = f"{stat}: {value:+d}"
                    try:
                        change_font = pygame.font.Font(FontSettings.DEFAULT_FONT, 24)
                    except (FileNotFoundError, OSError):
                        change_font = self.ui_font
                    change_surface = change_font.render(change_text, True, color)
                    change_rect = change_surface.get_rect()
                    change_rect.centerx = result_width // 2
                    change_rect.y = y_offset
                    result_surface.blit(change_surface, change_rect)
                    y_offset += 25

        # 提示
        try:
            hint_font = pygame.font.Font(FontSettings.DEFAULT_FONT, 20)
        except (FileNotFoundError, OSError):
            hint_font = self.ui_font
        hint_text = hint_font.render("按任意鍵繼續...", True, (150, 150, 150))
        hint_rect = hint_text.get_rect()
        hint_rect.centerx = result_width // 2
        hint_rect.y = result_height - 30
        result_surface.blit(hint_text, hint_rect)

        screen.blit(result_surface, (result_x, result_y))

    def handle_event(self, event: pygame.event.Event):
        """處理事件"""
        # 對話系統優先處理
        if (
            hasattr(self.game_engine, "dialogue_system")
            and self.game_engine.dialogue_system
        ):
            game_state = getattr(
                self, "current_game_state", getattr(self.game_engine, "game_state", {})
            )
            if self.game_engine.dialogue_system.handle_event(event, game_state):
                return

        # 活動結果顯示中
        if self.activity_result_display:
            if event.type == pygame.KEYDOWN:
                self.activity_result_display = False
            return

        # 處理表情重置
        if event.type == pygame.USEREVENT + 1:
            self.nyanko_mood = "normal"
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)

        elif event.type == pygame.KEYDOWN:
            if self.activity_menu_visible:
                if event.key == pygame.K_UP:
                    self.selected_activity = (self.selected_activity - 1) % len(
                        self.available_activities
                    )
                elif event.key == pygame.K_DOWN:
                    self.selected_activity = (self.selected_activity + 1) % len(
                        self.available_activities
                    )
                elif event.key == pygame.K_RETURN:
                    self._execute_selected_activity()
                elif event.key == pygame.K_ESCAPE:
                    self.activity_menu_visible = False
            else:
                if event.key == pygame.K_SPACE:
                    if self.available_activities:
                        self.activity_menu_visible = True
                        self.selected_activity = 0
                    else:
                        self._show_no_activities_message()
                elif event.key == pygame.K_t:
                    # 跳過時間段
                    if hasattr(self.game_engine, "skip_time_period"):
                        self.game_engine.skip_time_period()
                elif event.key == pygame.K_1:
                    self.change_scene("kitchen")
                elif event.key == pygame.K_2:
                    self.change_scene("bedroom")
                elif event.key == pygame.K_3:
                    self.change_scene("bathroom")
                elif event.key == pygame.K_ESCAPE:
                    self.change_scene("main_menu")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 使用事件中已轉換的座標或獲取轉換後的滑鼠位置
                mouse_pos = getattr(event, "pos", self.get_mouse_pos())
                self._handle_mouse_click(mouse_pos)

    def _execute_selected_activity(self):
        """執行選中的活動"""
        if not self.available_activities or self.selected_activity >= len(
            self.available_activities
        ):
            return

        activity = self.available_activities[self.selected_activity]

        if hasattr(self.game_engine, "execute_activity"):
            success = self.game_engine.execute_activity(activity.id)
            if success:
                self.activity_menu_visible = False
                self.nyanko_mood = "happy"
                pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # 3秒後恢復表情
            else:
                print(f"無法執行活動: {activity.name}")

    def _show_no_activities_message(self):
        """顯示沒有可用活動的訊息"""
        print("當前時間段沒有可執行的活動，按 T 鍵跳過時間")

    def _handle_mouse_click(self, mouse_pos: tuple):
        """處理滑鼠點擊"""
        if self.nyanko_present and hasattr(self, "nyanko_rect") and self.nyanko_rect:
            if self.nyanko_rect.collidepoint(mouse_pos):
                self._interact_with_nyanko()

    def _interact_with_nyanko(self):
        """與にゃんこ互動"""
        if self.nyanko_present:
            if (
                hasattr(self.game_engine, "dialogue_system")
                and self.game_engine.dialogue_system.is_active
            ):
                print("對話進行中，請稍候...")
                return

            self.nyanko_mood = "happy"

            if (
                hasattr(self.game_engine, "audio_manager")
                and self.game_engine.audio_manager is not None
            ):
                self.game_engine.audio_manager.play_sfx("nyanko_interact", 0.7)

            # 觸發簡單對話
            time_info = self._get_current_time_info()
            # 使用英文時間段ID而不是中文名稱
            time_period = time_info.get("period_id", "morning")
            dialogue_id = f"greeting_{time_period}_01"
            self.game_engine.start_dialogue(dialogue_id)

            pygame.time.set_timer(pygame.USEREVENT + 1, 3000)

    def _on_activity_complete(self, activity, result):
        """活動完成回調"""
        self.activity_result = {
            "name": activity.name,
            "description": activity.description,
            "changes": {
                "體力": result["energy_change"],
                "好感度": result["affection_change"],
                "心情": result["mood_change"],
            },
        }
        self.activity_result_display = True
        self.result_timer = pygame.time.get_ticks()

    def on_enter(self, transition_data=None):
        """場景進入時的回調"""
        super().on_enter(transition_data)

        if transition_data and transition_data.get("new_game"):
            print("開始新的一天...")

    def handle_escape(self):
        """處理ESC鍵"""
        if self.activity_menu_visible:
            self.activity_menu_visible = False
        else:
            self.change_scene("main_menu")

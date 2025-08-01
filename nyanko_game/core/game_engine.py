# -*- coding: utf-8 -*-
"""
主要遊戲引擎
負責遊戲的初始化、主循環、事件處理和渲染
"""

import pygame
import sys
from typing import Optional
from config.settings import *
from core.scene_manager import SceneManager
from systems import DialogueSystem, AffectionSystem, EventSystem
from systems.image_manager import image_manager
from systems.daily_event_system import DailyEventSystem
from systems.daily_event_system import DailyEventSystem
from systems.progress_tracker import ProgressTracker
from systems.audio_system import audio_manager


class GameEngine:
    """遊戲引擎主類別"""

    def __init__(self):
        """初始化遊戲引擎"""
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.scene_manager: Optional[SceneManager] = None
        self.running = False
        self.dt = 0  # Delta time (時間差)

        # 顯示相關
        self.fullscreen_mode = FULLSCREEN_MODE

        # 滑鼠座標轉換相關（用於全螢幕縮放模式）
        self.mouse_scale_factor = 1.0
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0
        self.needs_mouse_transform = False

        # 遊戲狀態
        self.paused = False
        self.debug_mode = DebugSettings.DEBUG_MODE

        # 核心系統
        self.dialogue_system: Optional[DialogueSystem] = None
        self.affection_system: Optional[AffectionSystem] = None
        self.time_system = None
        self.event_system: Optional[EventSystem] = None

        # 新增的系統
        self.daily_event_system = None
        self.daily_event_system = None
        self.progress_tracker = None
        self.audio_manager = None

        # 遊戲狀態資料
        self.game_state = {
            "nyanko_affection": 0,
            "current_time_period": "",
            "current_weekday": "",
            "flags": {},
            "items": {},
        }

    def initialize(self) -> bool:
        """
        初始化pygame和遊戲系統

        Returns:
            bool: 初始化是否成功
        """
        try:
            # 初始化pygame
            pygame.init()
            pygame.mixer.init()

            # 設置顯示模式
            self._setup_display()

            # 設置視窗標題和圖示
            pygame.display.set_caption(GAME_TITLE)

            # 建立時鐘物件
            self.clock = pygame.time.Clock()

            # 初始化場景管理器
            self.scene_manager = SceneManager(self)

            # 初始化核心系統
            self._initialize_systems()

            # 載入初始場景
            self.scene_manager.change_scene("main_menu")

            self.running = True

            if self.debug_mode:
                print(f"遊戲引擎初始化完成")
                print(f"遊戲解析度: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
                display_size = self.screen.get_size()
                print(f"實際顯示解析度: {display_size[0]}x{display_size[1]}")
                print(f"FPS目標: {FPS}")
                mode_name = "全螢幕" if self.fullscreen_mode else "視窗"
                print(f"顯示模式: {mode_name}")

            return True

        except Exception as e:
            print(f"遊戲引擎初始化失敗: {e}")
            return False

    def _get_screen_resolution(self):
        """
        獲取系統螢幕的真實解析度

        Returns:
            tuple: (width, height) 螢幕解析度
        """
        try:
            # 方法1: 使用 tkinter（最可靠）
            try:
                import tkinter as tk

                root = tk.Tk()
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()
                root.destroy()
                return (width, height)
            except ImportError:
                pass

            # 方法2: Windows 特定方法
            if sys.platform == "win32":
                try:
                    import ctypes

                    user32 = ctypes.windll.user32
                    width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                    height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
                    return (width, height)
                except:
                    pass

            # 方法3: pygame 方法（作為備用）
            info = pygame.display.Info()
            width = info.current_w
            height = info.current_h
            return (width, height)

        except Exception as e:
            if self.debug_mode:
                print(f"無法獲取螢幕解析度: {e}")
            # 返回遊戲預設解析度
            return (SCREEN_WIDTH, SCREEN_HEIGHT)

    def _setup_display(self):
        """改進的顯示設置 - 正確獲取原生解析度"""
        if self.fullscreen_mode:
            # 獲取真實螢幕解析度
            native_width, native_height = self._get_screen_resolution()

            # 檢查螢幕解析度是否與遊戲解析度相同
            if native_width == SCREEN_WIDTH and native_height == SCREEN_HEIGHT:
                # 解析度相同，直接使用全螢幕
                self.screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
                )
                if self.debug_mode:
                    print(f"全螢幕模式: {SCREEN_WIDTH}x{SCREEN_HEIGHT} (完美匹配)")
            else:
                # 解析度不同，使用原生解析度並後續縮放
                self.screen = pygame.display.set_mode(
                    (native_width, native_height), pygame.FULLSCREEN
                )
                if self.debug_mode:
                    print(
                        f"全螢幕模式: {native_width}x{native_height} (原生解析度，需要縮放)"
                    )
        else:
            # 視窗模式
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            if self.debug_mode:
                print(f"視窗模式: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

        # 更新滑鼠轉換參數
        self._update_mouse_transform_params()

    def _update_mouse_transform_params(self):
        """更新滑鼠座標轉換參數"""
        if self.fullscreen_mode:
            screen_width, screen_height = self.screen.get_size()

            if screen_width == SCREEN_WIDTH and screen_height == SCREEN_HEIGHT:
                # 解析度匹配，無需轉換
                self.needs_mouse_transform = False
                self.mouse_scale_factor = 1.0
                self.mouse_offset_x = 0
                self.mouse_offset_y = 0
            else:
                # 需要縮放轉換
                scale_x = screen_width / SCREEN_WIDTH
                scale_y = screen_height / SCREEN_HEIGHT
                scale = min(scale_x, scale_y)

                scaled_width = int(SCREEN_WIDTH * scale)
                scaled_height = int(SCREEN_HEIGHT * scale)

                self.needs_mouse_transform = True
                self.mouse_scale_factor = scale
                self.mouse_offset_x = (screen_width - scaled_width) // 2
                self.mouse_offset_y = (screen_height - scaled_height) // 2
        else:
            # 視窗模式，無需轉換
            self.needs_mouse_transform = False
            self.mouse_scale_factor = 1.0
            self.mouse_offset_x = 0
            self.mouse_offset_y = 0

    def _calculate_scaling(self, display_width: int, display_height: int):
        """計算縮放比例和渲染偏移 - 已簡化，保留以維持相容性"""
        # 這個方法保留以維持相容性
        if self.debug_mode:
            print(f"顯示解析度: {display_width}x{display_height}")
            print(f"遊戲解析度: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
            print("使用簡化的顯示處理")

    def _initialize_systems(self):
        """初始化核心系統"""
        try:
            # 初始化圖片管理器
            image_manager.load_all_images()

            # 初始化對話系統
            self.dialogue_system = DialogueSystem(self)
            dialogue_data_path = "assets/dialogue_data.json"
            self.dialogue_system.load_dialogue_data(dialogue_data_path)

            # 初始化好感度系統
            self.affection_system = AffectionSystem(self)

            # 初始化基本時間系統，確保遊戲正常運行
            from systems.basic_time_system import BasicTimeSystem

            self.time_system = BasicTimeSystem()

            # 初始化事件系統
            self.event_system = EventSystem(self)

            # 初始化日常事件系統
            self.daily_event_system = DailyEventSystem(self)

            # 初始化進度追蹤系統
            self.progress_tracker = ProgressTracker(self)

            # 初始化音效系統
            self.audio_manager = audio_manager

            # 設定系統間的回調關聯
            self.affection_system.on_affection_change = self._on_affection_change
            self.affection_system.on_special_event = self._on_special_event
            # 基本時間系統暫時不需要回調
            # self.time_system.on_day_change = self._on_day_change
            # self.time_system.on_time_period_change = self._on_time_period_change

            # 播放主選單背景音樂
            self.audio_manager.play_bgm("main_menu", loop=True, fade_in=2.0)

            print("所有核心系統初始化完成")

        except Exception as e:
            print(f"系統初始化失敗: {e}")
            raise e

    def _on_affection_change(self, character: str, old_value: int, new_value: int):
        """好感度變化回調"""
        if self.debug_mode:
            print(f"{character}好感度變化: {old_value} → {new_value}")

        # 追蹤好感度變化
        if self.progress_tracker:
            self.progress_tracker.track_affection_change(
                old_value, new_value, f"{character}好感度變化"
            )

        # 播放音效
        if new_value > old_value:
            if self.audio_manager:
                self.audio_manager.play_sfx("affection_up", 0.7)
        elif new_value < old_value:
            if self.audio_manager:
                self.audio_manager.play_sfx("affection_down", 0.5)

    def _on_special_event(self, event_id: str, dialogue_id: str):
        """特殊事件觸發回調"""
        if self.dialogue_system:
            self.dialogue_system.start_dialogue(dialogue_id, self.game_state)

    def _on_day_change(self, day: int, game_time):
        """日期變化回調"""
        if self.affection_system:
            self.affection_system.reset_daily_interactions()
        if self.debug_mode:
            print(f"新的一天: 第{day}天 - {game_time.format_date()}")

        # 清空日常事件
        if self.daily_event_system:
            self.daily_event_system.clear_active_events()

        # 檢查成就
        if self.progress_tracker:
            self.progress_tracker.check_achievements(self.game_state)

        # 播放新一天音效
        if self.audio_manager:
            self.audio_manager.play_sfx("new_day", 0.6)

    def _on_time_period_change(self, old_period, new_period):
        """時間段變化回調"""
        if self.debug_mode:
            print(f"時間段變化: {old_period.value} → {new_period.value}")

        # 根據時間段播放合適的BGM
        self._update_bgm_for_time_period(new_period.value)

        # 播放時間變化音效
        if self.audio_manager:
            self.audio_manager.play_sfx("time_change", 0.4)

    def _update_bgm_for_time_period(self, time_period: str):
        """根據時間段更新BGM"""
        bgm_mapping = {
            "morning": "morning_theme",
            "afternoon": "afternoon_theme",
            "evening": "evening_theme",
            "night": "night_theme",
            "late_night": "late_night_theme",
        }

        bgm_name = bgm_mapping.get(time_period, "default_theme")

        # 如果當前場景是遊戲場景（非主選單），則切換BGM
        current_scene = getattr(self.scene_manager, "current_scene_name", None)
        if current_scene and current_scene != "main_menu":
            self.audio_manager.play_bgm(bgm_name, loop=True, fade_in=1.5)

    def run(self):
        """主遊戲循環"""
        if not self.running:
            print("遊戲引擎未正確初始化！")
            return

        print("開始遊戲主循環...")

        while self.running:
            # 計算時間差
            self.dt = self.clock.tick(FPS) / 1000.0

            # 處理事件
            self.handle_events()

            # 更新遊戲邏輯
            if not self.paused:
                self.update()

            # 渲染畫面
            self.render()

        # 清理資源
        self.cleanup()

    def transform_mouse_pos(self, mouse_pos: tuple) -> tuple:
        """
        轉換滑鼠座標從實際螢幕座標到遊戲虛擬座標

        Args:
            mouse_pos: 實際螢幕滑鼠位置 (x, y)

        Returns:
            tuple: 轉換後的遊戲座標 (x, y)，如果點擊在遊戲區域外則返回 None
        """
        if not self.needs_mouse_transform:
            return mouse_pos

        # 將滑鼠座標轉換為遊戲座標
        screen_x, screen_y = mouse_pos

        # 減去偏移量
        game_x = screen_x - self.mouse_offset_x
        game_y = screen_y - self.mouse_offset_y

        # 縮放到遊戲座標
        if self.mouse_scale_factor > 0:
            game_x = int(game_x / self.mouse_scale_factor)
            game_y = int(game_y / self.mouse_scale_factor)

        # 檢查是否在遊戲區域內
        if (
            game_x < 0
            or game_x >= SCREEN_WIDTH
            or game_y < 0
            or game_y >= SCREEN_HEIGHT
        ):
            return None  # 點擊在遊戲區域外

        return (game_x, game_y)

    def is_mouse_in_game_area(self, mouse_pos: tuple) -> bool:
        """
        檢查滑鼠是否在遊戲區域內

        Args:
            mouse_pos: 滑鼠位置 (x, y)

        Returns:
            bool: 是否在遊戲區域內
        """
        transformed_pos = self.transform_mouse_pos(mouse_pos)
        return transformed_pos is not None

    def handle_events(self):
        """處理輸入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # 處理滑鼠事件，進行座標轉換
            elif event.type in (
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION,
            ):
                # 轉換滑鼠座標
                transformed_pos = self.transform_mouse_pos(event.pos)
                if transformed_pos is not None:
                    # 創建新的事件對象，使用轉換後的座標
                    transformed_event = pygame.event.Event(
                        event.type, {**event.dict, "pos": transformed_pos}
                    )

                    # 優先讓對話系統處理事件
                    if (
                        self.dialogue_system
                        and self.dialogue_system.is_dialogue_active()
                    ):
                        if self.dialogue_system.handle_event(
                            transformed_event, self.game_state
                        ):
                            continue  # 對話系統處理了事件，跳過其他處理

                    # 將轉換後的事件傳遞給場景管理器
                    if self.scene_manager:
                        self.scene_manager.handle_event(transformed_event)
                # 如果點擊在遊戲區域外，忽略事件
                continue

            # 優先讓對話系統處理事件
            if self.dialogue_system and self.dialogue_system.is_dialogue_active():
                if self.dialogue_system.handle_event(event, self.game_state):
                    continue  # 對話系統處理了事件，跳過其他處理

            elif event.type == pygame.KEYDOWN:
                # 處理全域按鍵
                if event.key == pygame.K_F11:
                    # 切換全螢幕
                    self.toggle_fullscreen()
                elif event.key == pygame.K_F1 and self.debug_mode:
                    # 切換除錯資訊顯示
                    DebugSettings.SHOW_FPS = not DebugSettings.SHOW_FPS
                elif event.key == pygame.K_F2 and self.debug_mode:
                    # 切換像素完整縮放模式
                    from config.settings import ImageScaling

                    ImageScaling.USE_PIXEL_PERFECT_SCALING = (
                        not ImageScaling.USE_PIXEL_PERFECT_SCALING
                    )
                    mode_text = (
                        "開啟" if ImageScaling.USE_PIXEL_PERFECT_SCALING else "關閉"
                    )
                    print(f"像素完整縮放: {mode_text}")
                elif event.key == pygame.K_ESCAPE:
                    # ESC鍵處理
                    if self.scene_manager.current_scene:
                        # 讓當前場景處理ESC鍵
                        if hasattr(self.scene_manager.current_scene, "handle_escape"):
                            self.scene_manager.current_scene.handle_escape()
                        else:
                            # 預設行為：暫停或返回主選單
                            self.toggle_pause()

            # 將事件傳遞給場景管理器
            if self.scene_manager:
                self.scene_manager.handle_event(event)

    def update(self):
        """更新遊戲邏輯"""
        # 更新核心系統
        # 只在遊戲場景中更新時間系統，不在主選單中
        current_scene = self.scene_manager.current_scene if self.scene_manager else None
        if current_scene and current_scene.__class__.__name__ != "MainMenuScene":
            if self.time_system:
                self.time_system.update(self.dt)
                # 更新遊戲狀態中的時間相關資訊
                self.game_state["current_time_period"] = (
                    self.time_system.get_current_time_period().value
                )
                self.game_state["current_weekday"] = (
                    self.time_system.get_weekday().name.lower()
                )
                self.game_state["current_time"] = self.time_system.get_current_time()

        if self.affection_system:
            # 好感度系統的更新（主要在對話和事件中觸發）
            self.game_state["nyanko_affection"] = self.affection_system.get_affection()

        if self.dialogue_system:
            self.dialogue_system.update(self.dt, self.game_state)

        # 只在遊戲場景中更新事件系統，不在主選單中
        current_scene = self.scene_manager.current_scene if self.scene_manager else None
        if current_scene and current_scene.__class__.__name__ != "MainMenuScene":
            if self.event_system:
                self.event_system.update(self.dt, self.game_state)

            # 更新日常事件系統
            # 更新日常事件系統
            if self.daily_event_system:
                self.daily_event_system.update(self.dt, self.game_state)

        # 更新進度追蹤
        if self.progress_tracker:
            self.progress_tracker.update_play_time(self.dt)
            # 定期檢查成就（每5秒檢查一次）
            if hasattr(self, "_achievement_check_timer"):
                self._achievement_check_timer += self.dt
                if self._achievement_check_timer >= 5.0:
                    self.progress_tracker.check_achievements(self.game_state)
                    self._achievement_check_timer = 0.0
            else:
                self._achievement_check_timer = 0.0

        # 更新場景管理器
        if self.scene_manager:
            self.scene_manager.update(self.dt, self.game_state)

    def render(self):
        """智能渲染畫面 - 根據解析度匹配情況選擇最佳渲染方式"""
        if self.fullscreen_mode:
            screen_width, screen_height = self.screen.get_size()

            # 檢查是否需要縮放
            if screen_width == SCREEN_WIDTH and screen_height == SCREEN_HEIGHT:
                # 解析度完全匹配，直接渲染（最高效率）
                self.needs_mouse_transform = False
                self.mouse_scale_factor = 1.0
                self.mouse_offset_x = 0
                self.mouse_offset_y = 0

                self.screen.fill(Colors.BACKGROUND_COLOR)

                if self.scene_manager:
                    self.scene_manager.render(self.screen)

                if self.dialogue_system:
                    self.dialogue_system.render(self.screen)

                if self.debug_mode:
                    self.render_debug_info()

            else:
                # 需要縮放渲染
                virtual_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                virtual_surface.fill(Colors.BACKGROUND_COLOR)

                # 在虛擬表面上渲染
                if self.scene_manager:
                    self.scene_manager.render(virtual_surface)

                if self.dialogue_system:
                    self.dialogue_system.render(virtual_surface)

                if self.debug_mode:
                    self._render_debug_info_on_surface(virtual_surface)

                # 計算縮放比例和位置
                scale_x = screen_width / SCREEN_WIDTH
                scale_y = screen_height / SCREEN_HEIGHT
                scale = min(scale_x, scale_y)  # 保持比例

                scaled_width = int(SCREEN_WIDTH * scale)
                scaled_height = int(SCREEN_HEIGHT * scale)

                # 縮放虛擬表面 - 使用像素完整縮放
                from config.settings import ImageScaling

                scaled_surface = ImageScaling.pixel_perfect_scale(
                    virtual_surface, (scaled_width, scaled_height)
                )

                # 居中顯示
                x = (screen_width - scaled_width) // 2
                y = (screen_height - scaled_height) // 2

                # 設置滑鼠座標轉換參數
                self.needs_mouse_transform = True
                self.mouse_scale_factor = scale
                self.mouse_offset_x = x
                self.mouse_offset_y = y

                # 清空實際螢幕並繪製縮放後的內容
                self.screen.fill(Colors.BLACK)  # 黑色邊框
                self.screen.blit(scaled_surface, (x, y))

        else:
            # 視窗模式：直接渲染
            self.needs_mouse_transform = False
            self.mouse_scale_factor = 1.0
            self.mouse_offset_x = 0
            self.mouse_offset_y = 0

            self.screen.fill(Colors.BACKGROUND_COLOR)

            if self.scene_manager:
                self.scene_manager.render(self.screen)

            if self.dialogue_system:
                self.dialogue_system.render(self.screen)

            if self.debug_mode:
                self.render_debug_info()

        # 更新顯示
        pygame.display.flip()

    def _render_debug_info_on_surface(self, surface):
        """在指定表面上渲染除錯資訊"""
        if DebugSettings.SHOW_FPS:
            fps = self.clock.get_fps()
            try:
                font = pygame.font.Font(FontSettings.DEFAULT_FONT, 20)
            except (FileNotFoundError, OSError):
                font = pygame.font.Font(None, 24)

            # FPS資訊
            fps_text = font.render(f"FPS: {fps:.1f}", True, Colors.BLACK)
            surface.blit(fps_text, (10, 10))

            # 場景資訊
            if self.scene_manager and self.scene_manager.current_scene:
                scene_name = self.scene_manager.current_scene.__class__.__name__
                scene_text = font.render(f"Scene: {scene_name}", True, Colors.BLACK)
                surface.blit(scene_text, (10, 35))

            # 顯示模式和解析度資訊
            mode_name = "全螢幕" if self.fullscreen_mode else "視窗"
            mode_text = font.render(f"Mode: {mode_name}", True, Colors.BLACK)
            surface.blit(mode_text, (10, 60))

            if self.fullscreen_mode:
                screen_size = self.screen.get_size()
                native_text = font.render(
                    f"Native: {screen_size[0]}x{screen_size[1]}", True, Colors.BLACK
                )
                surface.blit(native_text, (10, 85))

                game_text = font.render(
                    f"Game: {SCREEN_WIDTH}x{SCREEN_HEIGHT}", True, Colors.BLACK
                )
                surface.blit(game_text, (10, 110))

                scale_text = font.render("Status: Scaling Active", True, Colors.BLACK)
                surface.blit(scale_text, (10, 135))

            # 像素完整縮放狀態
            from config.settings import ImageScaling

            pixel_mode = "ON" if ImageScaling.USE_PIXEL_PERFECT_SCALING else "OFF"
            pixel_text = font.render(f"Pixel Perfect: {pixel_mode}", True, Colors.BLACK)
            surface.blit(pixel_text, (10, 160))

            # 滑鼠座標轉換狀態
            if self.needs_mouse_transform:
                transform_text = font.render("Mouse Transform: ON", True, Colors.BLACK)
                surface.blit(transform_text, (10, 185))

                # 顯示滑鼠座標
                raw_mouse = pygame.mouse.get_pos()
                game_mouse = self.get_mouse_pos()
                mouse_info = font.render(
                    f"Mouse: {raw_mouse} -> {game_mouse}", True, Colors.BLACK
                )
                surface.blit(mouse_info, (10, 210))
            else:
                transform_text = font.render("Mouse Transform: OFF", True, Colors.BLACK)
                surface.blit(transform_text, (10, 185))

            # 控制提示
            controls_text = font.render("F2: Toggle Pixel Perfect", True, Colors.GRAY)
            surface.blit(controls_text, (10, 235))

    def render_debug_info(self):
        """簡化的除錯資訊渲染"""
        if DebugSettings.SHOW_FPS:
            # 顯示FPS
            fps = self.clock.get_fps()
            try:
                font = pygame.font.Font(FontSettings.DEFAULT_FONT, 20)
            except (FileNotFoundError, OSError):
                font = pygame.font.Font(None, 24)

            # FPS資訊
            fps_text = font.render(f"FPS: {fps:.1f}", True, Colors.BLACK)
            self.screen.blit(fps_text, (10, 10))

            # 場景資訊
            if self.scene_manager and self.scene_manager.current_scene:
                scene_name = self.scene_manager.current_scene.__class__.__name__
                scene_text = font.render(f"Scene: {scene_name}", True, Colors.BLACK)
                self.screen.blit(scene_text, (10, 35))

            # 顯示模式資訊
            mode_name = "全螢幕" if self.fullscreen_mode else "視窗"
            mode_text = font.render(f"Mode: {mode_name}", True, Colors.BLACK)
            self.screen.blit(mode_text, (10, 60))

            # 解析度資訊（全螢幕時）
            if self.fullscreen_mode:
                screen_size = self.screen.get_size()
                native_text = font.render(
                    f"Native: {screen_size[0]}x{screen_size[1]}", True, Colors.BLACK
                )
                self.screen.blit(native_text, (10, 85))

                game_text = font.render(
                    f"Game: {SCREEN_WIDTH}x{SCREEN_HEIGHT}", True, Colors.BLACK
                )
                self.screen.blit(game_text, (10, 110))

                # 顯示是否需要縮放
                if screen_size[0] == SCREEN_WIDTH and screen_size[1] == SCREEN_HEIGHT:
                    match_text = font.render(
                        "Status: Perfect Match", True, Colors.BLACK
                    )
                else:
                    match_text = font.render(
                        "Status: Scaling Required", True, Colors.BLACK
                    )
                self.screen.blit(match_text, (10, 135))

            # 像素完整縮放狀態
            from config.settings import ImageScaling

            pixel_mode = "ON" if ImageScaling.USE_PIXEL_PERFECT_SCALING else "OFF"
            pixel_text = font.render(f"Pixel Perfect: {pixel_mode}", True, Colors.BLACK)
            self.screen.blit(pixel_text, (10, 160))

            # 滑鼠座標轉換狀態
            if self.needs_mouse_transform:
                transform_text = font.render("Mouse Transform: ON", True, Colors.BLACK)
                self.screen.blit(transform_text, (10, 185))

                # 顯示滑鼠座標
                raw_mouse = pygame.mouse.get_pos()
                game_mouse = self.get_mouse_pos()
                mouse_info = font.render(
                    f"Mouse: {raw_mouse} -> {game_mouse}", True, Colors.BLACK
                )
                self.screen.blit(mouse_info, (10, 210))
            else:
                transform_text = font.render("Mouse Transform: OFF", True, Colors.BLACK)
                self.screen.blit(transform_text, (10, 185))

            # 控制提示
            controls_text = font.render("F2: Toggle Pixel Perfect", True, Colors.GRAY)
            self.screen.blit(controls_text, (10, 235))

    def get_mouse_pos(self) -> tuple:
        """
        獲取正確轉換後的滑鼠位置

        Returns:
            tuple: 遊戲座標系中的滑鼠位置 (x, y)，如果滑鼠不在遊戲區域則返回 (-1, -1)
        """
        raw_mouse_pos = pygame.mouse.get_pos()
        transformed_pos = self.transform_mouse_pos(raw_mouse_pos)

        if transformed_pos is None:
            return (-1, -1)  # 滑鼠不在遊戲區域

        return transformed_pos

    def get_mouse_buttons(self) -> tuple:
        """
        獲取滑鼠按鈕狀態

        Returns:
            tuple: (left, middle, right) 按鈕狀態
        """
        return pygame.mouse.get_pressed()

    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        檢查滑鼠按鈕是否被按下

        Args:
            button: 按鈕編號 (1=左鍵, 2=中鍵, 3=右鍵)

        Returns:
            bool: 按鈕是否被按下
        """
        pressed = pygame.mouse.get_pressed()
        if button == 1:
            return pressed[0]  # 左鍵
        elif button == 2:
            return pressed[1]  # 中鍵
        elif button == 3:
            return pressed[2]  # 右鍵
        return False

    def toggle_fullscreen(self):
        """簡化的全螢幕切換"""
        self.fullscreen_mode = not self.fullscreen_mode
        self._setup_display()

        if self.debug_mode:
            mode_name = "全螢幕" if self.fullscreen_mode else "視窗"
            transform_status = "ON" if self.needs_mouse_transform else "OFF"
            print(f"切換到{mode_name}模式，滑鼠轉換: {transform_status}")
            if self.needs_mouse_transform:
                print(
                    f"縮放比例: {self.mouse_scale_factor:.3f}, 偏移: ({self.mouse_offset_x}, {self.mouse_offset_y})"
                )

    def toggle_pause(self):
        """切換暫停狀態"""
        self.paused = not self.paused
        if self.debug_mode:
            print(f"遊戲{'暫停' if self.paused else '繼續'}")

    def quit_game(self):
        """退出遊戲"""
        if self.debug_mode:
            print("準備退出遊戲...")
        self.running = False

    def cleanup(self):
        """清理資源"""
        if self.debug_mode:
            print("清理遊戲資源...")

        # 保存進度
        if self.progress_tracker:
            save_path = "data/progress.json"
            self.progress_tracker.save_progress(save_path)

        # 清理音效系統
        if self.audio_manager:
            self.audio_manager.cleanup()

        # 停止音效（如果初始化的話）
        try:
            pygame.mixer.stop()
        except pygame.error:
            pass  # mixer未初始化或已關閉

        # 退出pygame
        pygame.quit()

        if self.debug_mode:
            print("遊戲引擎已關閉")

    def start_dialogue(self, dialogue_id: str):
        """
        開始對話

        Args:
            dialogue_id: 對話ID
        """
        if self.dialogue_system:
            self.dialogue_system.start_dialogue(dialogue_id, self.game_state)

        # 追蹤對話
        if self.progress_tracker:
            self.progress_tracker.track_dialogue(dialogue_id)

        # 播放對話開始音效
        if self.audio_manager:
            self.audio_manager.play_sfx("dialogue_start", 0.5)

    def change_affection(self, change: int, reason: str = ""):
        """
        改變好感度

        Args:
            change: 好感度變化量
            reason: 變化原因
        """
        if self.affection_system:
            return self.affection_system.change_affection(change, "nyanko", reason)
        return 0

    def get_affection(self) -> int:
        """獲取當前好感度"""
        if self.affection_system:
            return self.affection_system.get_affection()
        return 0

    def get_current_time_info(self) -> dict:
        """獲取當前時間資訊"""
        if self.time_system:
            return {
                "time": self.time_system.get_current_time(),
                "period": self.time_system.get_current_time_period().value,
                "day": self.time_system.get_current_day(),
                "time_points": 6,  # 假設固定值
                "period_name": self.time_system.get_current_time_period_name(),
                "season": self.time_system.get_season_name(),
                "weekday": self.time_system.get_weekday_name(),
            }
        return {
            "time": "08:00",
            "period": "morning",
            "day": 1,
            "time_points": 6,
            "period_name": "上午",
            "season": "春天",
            "weekday": "星期一",
        }

    def get_screen_size(self) -> tuple:
        """
        獲取螢幕尺寸

        Returns:
            tuple: (寬度, 高度)
        """
        return (SCREEN_WIDTH, SCREEN_HEIGHT)

    def get_fps(self) -> float:
        """
        獲取當前FPS

        Returns:
            float: 當前FPS值
        """
        return self.clock.get_fps() if self.clock else 0.0

    def save_game(self, slot: int = 0) -> bool:
        """
        儲存遊戲

        Args:
            slot: 存檔槽位

        Returns:
            bool: 儲存是否成功
        """
        try:
            import json
            import os
            from datetime import datetime

            # 創建存檔目錄
            save_dir = "data"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # 收集遊戲狀態資料
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "game_state": self.game_state.copy(),
                "current_scene": getattr(
                    self.scene_manager, "current_scene_name", "main_menu"
                ),
            }

            # 收集各系統的資料
            if self.affection_system:
                save_data["affection_data"] = self.affection_system.save_data()

            if self.time_system:
                save_data["time_data"] = {
                    "day": getattr(self.time_system, "current_day", 1),
                    "hour": getattr(self.time_system, "current_hour", 8),
                    "minute": getattr(self.time_system, "current_minute", 0),
                }

            # 寫入存檔檔案
            save_file = os.path.join(save_dir, f"save_slot_{slot}.json")
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"遊戲已儲存到槽位 {slot}")
            return True

        except Exception as e:
            print(f"儲存遊戲失敗: {e}")
            return False

    def load_game(self, slot: int = 0) -> bool:
        """
        載入遊戲

        Args:
            slot: 存檔槽位

        Returns:
            bool: 載入是否成功
        """
        try:
            import json
            import os

            save_file = os.path.join("data", f"save_slot_{slot}.json")
            if not os.path.exists(save_file):
                print(f"存檔槽位 {slot} 不存在")
                return False

            # 讀取存檔檔案
            with open(save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # 恢復遊戲狀態
            self.game_state = save_data.get("game_state", {})

            # 恢復各系統的資料
            if self.affection_system and "affection_data" in save_data:
                self.affection_system.load_data(save_data["affection_data"])

            if self.time_system and "time_data" in save_data:
                time_data = save_data["time_data"]
                # 這裡可以恢復時間系統的狀態
                pass

            # 切換到存檔時的場景
            if self.scene_manager and "current_scene" in save_data:
                scene_name = save_data["current_scene"]
                self.scene_manager.change_scene(scene_name)

            print(f"遊戲已從槽位 {slot} 載入")
            return True

        except Exception as e:
            print(f"載入遊戲失敗: {e}")
            return False

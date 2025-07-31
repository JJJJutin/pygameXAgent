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
from systems import DialogueSystem, AffectionSystem, TimeSystem, EventSystem


class GameEngine:
    """遊戲引擎主類別"""

    def __init__(self):
        """初始化遊戲引擎"""
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.scene_manager: Optional[SceneManager] = None
        self.running = False
        self.dt = 0  # Delta time (時間差)

        # 遊戲狀態
        self.paused = False
        self.debug_mode = DebugSettings.DEBUG_MODE

        # 核心系統
        self.dialogue_system: Optional[DialogueSystem] = None
        self.affection_system: Optional[AffectionSystem] = None
        self.time_system: Optional[TimeSystem] = None
        self.event_system: Optional[EventSystem] = None

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

            # 設置視窗
            if FULLSCREEN:
                self.screen = pygame.display.set_mode(
                    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
                )
            else:
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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
                print(f"解析度: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
                print(f"FPS目標: {FPS}")

            return True

        except Exception as e:
            print(f"遊戲引擎初始化失敗: {e}")
            return False

    def _initialize_systems(self):
        """初始化核心系統"""
        try:
            # 初始化對話系統
            self.dialogue_system = DialogueSystem(self)
            dialogue_data_path = "assets/dialogue_data.json"
            self.dialogue_system.load_dialogue_data(dialogue_data_path)

            # 初始化好感度系統
            self.affection_system = AffectionSystem(self)

            # 初始化時間系統
            self.time_system = TimeSystem(self)

            # 初始化事件系統
            self.event_system = EventSystem(self)

            # 設定系統間的回調關聯
            self.affection_system.on_affection_change = self._on_affection_change
            self.affection_system.on_special_event = self._on_special_event
            self.time_system.on_day_change = self._on_day_change
            self.time_system.on_time_period_change = self._on_time_period_change

            print("所有核心系統初始化完成")

        except Exception as e:
            print(f"系統初始化失敗: {e}")
            raise e

    def _on_affection_change(self, character: str, old_value: int, new_value: int):
        """好感度變化回調"""
        if self.debug_mode:
            print(f"{character}好感度變化: {old_value} → {new_value}")

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

    def _on_time_period_change(self, old_period, new_period):
        """時間段變化回調"""
        if self.debug_mode:
            print(f"時間段變化: {old_period.value} → {new_period.value}")

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

    def handle_events(self):
        """處理輸入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

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
        if self.time_system:
            self.time_system.update(self.dt)
            # 更新遊戲狀態中的時間相關資訊
            self.game_state["current_time_period"] = (
                self.time_system.get_current_time_period().value
            )
            self.game_state["current_weekday"] = (
                self.time_system.get_weekday().name.lower()
            )
            self.game_state["current_time"] = (
                self.time_system.get_current_time().format_full()
            )

        if self.affection_system:
            # 好感度系統的更新（主要在對話和事件中觸發）
            self.game_state["nyanko_affection"] = self.affection_system.get_affection()

        if self.dialogue_system:
            self.dialogue_system.update(self.dt, self.game_state)

        if self.event_system:
            self.event_system.update(self.dt, self.game_state)

        # 更新場景管理器
        if self.scene_manager:
            self.scene_manager.update(self.dt, self.game_state)

    def render(self):
        """渲染畫面"""
        # 清空螢幕
        self.screen.fill(Colors.BACKGROUND_COLOR)

        # 渲染當前場景
        if self.scene_manager:
            self.scene_manager.render(self.screen)

        # 渲染對話系統（在最上層）
        if self.dialogue_system:
            self.dialogue_system.render(self.screen)

        # 渲染除錯資訊
        if self.debug_mode:
            self.render_debug_info()

        # 更新顯示
        pygame.display.flip()

    def render_debug_info(self):
        """渲染除錯資訊"""
        if DebugSettings.SHOW_FPS:
            # 顯示FPS
            fps = self.clock.get_fps()
            try:
                font = pygame.font.Font(FontSettings.DEFAULT_FONT, 20)
            except (FileNotFoundError, OSError):
                font = pygame.font.Font(None, 24)
            fps_text = font.render(f"FPS: {fps:.1f}", True, Colors.BLACK)
            self.screen.blit(fps_text, (10, 10))

            # 顯示場景資訊
            if self.scene_manager and self.scene_manager.current_scene:
                scene_name = self.scene_manager.current_scene.__class__.__name__
                scene_text = font.render(f"Scene: {scene_name}", True, Colors.BLACK)
                self.screen.blit(scene_text, (10, 35))

    def toggle_fullscreen(self):
        """切換全螢幕模式"""
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN

        if FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.debug_mode:
            print(f"切換全螢幕模式: {'開啟' if FULLSCREEN else '關閉'}")

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

        # 停止音效
        pygame.mixer.stop()

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
                "time": self.time_system.get_current_time().format_full(),
                "period": self.time_system.get_current_time_period_name(),
                "season": self.time_system.get_season_name(),
                "weekday": self.time_system.get_weekday_name(),
            }
        return {}

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

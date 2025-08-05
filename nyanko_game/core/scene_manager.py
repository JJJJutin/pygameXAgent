# -*- coding: utf-8 -*-
"""
場景切換管理
負責管理遊戲中不同場景的切換和狀態維護
"""

import pygame
from typing import Dict, Optional, Any
from scenes.base_scene import BaseScene


class SceneManager:
    """場景管理器類別"""

    def __init__(self, game_engine):
        """
        初始化場景管理器

        Args:
            game_engine: 遊戲引擎實例
        """
        self.game_engine = game_engine
        self.scenes: Dict[str, BaseScene] = {}
        self.current_scene: Optional[BaseScene] = None
        self.current_scene_name: Optional[str] = None
        self.next_scene: Optional[str] = None
        self.transitioning = False
        self.transition_data: Dict[str, Any] = {}

        # 註冊所有場景
        self._register_scenes()

    def _register_scenes(self):
        """註冊所有可用的場景"""
        # 導入所有場景類別
        from scenes.main_menu import MainMenuScene
        from scenes.enhanced_living_room import (
            EnhancedLivingRoomScene,
        )  # 使用增強版客廳
        from scenes.kitchen import KitchenScene
        from scenes.bedroom import BedroomScene
        from scenes.bathroom import BathroomScene

        # 註冊場景
        self.register_scene("main_menu", MainMenuScene)
        self.register_scene("living_room", EnhancedLivingRoomScene)  # 使用增強版
        self.register_scene("kitchen", KitchenScene)
        self.register_scene("bedroom", BedroomScene)
        self.register_scene("bathroom", BathroomScene)

    def register_scene(self, scene_name: str, scene_class):
        """
        註冊場景

        Args:
            scene_name (str): 場景名稱
            scene_class: 場景類別
        """
        if scene_name not in self.scenes:
            self.scenes[scene_name] = scene_class(self.game_engine, self)
            print(f"場景已註冊: {scene_name}")

    def change_scene(self, scene_name: str, transition_data: Dict[str, Any] = None):
        """
        切換到指定場景

        Args:
            scene_name (str): 目標場景名稱
            transition_data (dict): 場景轉換時傳遞的資料
        """
        if scene_name not in self.scenes:
            print(f"警告: 場景 '{scene_name}' 不存在！")
            return

        self.next_scene = scene_name
        self.transition_data = transition_data or {}

        # 如果當前有場景，呼叫其退出方法
        if self.current_scene:
            self.current_scene.on_exit()

        # 追蹤場景訪問
        if (
            hasattr(self.game_engine, "progress_tracker")
            and self.game_engine.progress_tracker
        ):
            self.game_engine.progress_tracker.track_scene_visit(scene_name)

        # 播放場景切換音效
        if (
            hasattr(self.game_engine, "audio_manager")
            and self.game_engine.audio_manager
        ):
            self.game_engine.audio_manager.play_sfx("scene_transition", 0.6)

        print(f"準備切換到場景: {scene_name}")

    def update(self, dt: float, game_state: dict = None):
        """
        更新場景管理器

        Args:
            dt (float): 時間差
            game_state (dict): 遊戲狀態
        """
        # 處理場景切換
        if self.next_scene:
            self._perform_scene_transition()

        # 更新當前場景
        if self.current_scene:
            self.current_scene.update(dt, game_state)

    def _perform_scene_transition(self):
        """執行場景切換"""
        if self.next_scene in self.scenes:
            self.current_scene = self.scenes[self.next_scene]
            self.current_scene_name = self.next_scene  # 儲存場景名稱
            self.current_scene.on_enter(self.transition_data)
            print(f"已切換到場景: {self.next_scene}")

        self.next_scene = None
        self.transition_data = {}

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        處理事件

        Args:
            event: pygame事件

        Returns:
            bool: 如果事件被處理則返回 True，否則返回 False
        """
        if self.current_scene:
            # 如果場景的 handle_event 有返回值，使用它；否則假設已處理
            result = self.current_scene.handle_event(event)
            if result is not None:
                return result
            return True  # 假設場景處理了事件
        return False  # 沒有當前場景，事件未被處理

    def render(self, screen: pygame.Surface):
        """
        渲染當前場景

        Args:
            screen: pygame螢幕表面
        """
        if self.current_scene:
            self.current_scene.render(screen)

    def get_current_scene_name(self) -> str:
        """
        獲取當前場景名稱

        Returns:
            str: 當前場景名稱
        """
        return self.current_scene_name or "unknown"

    def pause_current_scene(self):
        """暫停當前場景"""
        if self.current_scene:
            self.current_scene.pause()

    def resume_current_scene(self):
        """恢復當前場景"""
        if self.current_scene:
            self.current_scene.resume()

    def get_scene_data(self, scene_name: str) -> Any:
        """
        獲取指定場景的資料

        Args:
            scene_name (str): 場景名稱

        Returns:
            Any: 場景資料
        """
        if scene_name in self.scenes:
            return self.scenes[scene_name].get_scene_data()
        return None

    def cleanup(self):
        """清理所有場景資源"""
        for scene in self.scenes.values():
            if hasattr(scene, "cleanup"):
                scene.cleanup()

        self.scenes.clear()
        self.current_scene = None
        print("場景管理器已清理")

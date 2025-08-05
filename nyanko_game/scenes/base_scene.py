# -*- coding: utf-8 -*-
"""
場景基礎類別
所有遊戲場景的父類別，定義場景的基本介面和行為
"""

import pygame
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseScene(ABC):
    """場景基礎抽象類別"""

    def __init__(self, game_engine, scene_manager):
        """
        初始化場景

        Args:
            game_engine: 遊戲引擎實例
            scene_manager: 場景管理器實例
        """
        self.game_engine = game_engine
        self.scene_manager = scene_manager
        self.paused = False
        self.scene_data = {}

        # 場景狀態
        self.is_active = False
        self.is_loaded = False

        # 初始化場景
        self._initialize()

    def _initialize(self):
        """內部初始化方法"""
        self.load_resources()
        self.setup_ui()
        self.is_loaded = True

    @abstractmethod
    def load_resources(self):
        """載入場景資源（子類別必須實作）"""
        pass

    @abstractmethod
    def setup_ui(self):
        """設置UI元素（子類別必須實作）"""
        pass

    def on_enter(self, transition_data: Dict[str, Any] = None):
        """
        場景進入時的回調函數

        Args:
            transition_data: 場景轉換時傳遞的資料
        """
        self.is_active = True
        self.paused = False

        if transition_data:
            self.scene_data.update(transition_data)

        print(f"進入場景: {self.__class__.__name__}")

    def on_exit(self):
        """場景退出時的回調函數"""
        self.is_active = False
        print(f"離開場景: {self.__class__.__name__}")

    @abstractmethod
    def update(self, dt: float, game_state: Dict[str, Any] = None):
        """
        更新場景邏輯（子類別必須實作）

        Args:
            dt: 時間差
            game_state: 遊戲狀態字典
        """
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """
        渲染場景（子類別必須實作）

        Args:
            screen: pygame螢幕表面
        """
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        處理事件（子類別必須實作）

        Args:
            event: pygame事件

        Returns:
            bool: 如果事件被處理則返回 True，否則返回 False
        """
        pass

    def pause(self):
        """暫停場景"""
        self.paused = True

    def resume(self):
        """恢復場景"""
        self.paused = False

    def handle_escape(self):
        """處理ESC鍵（可選實作）"""
        # 預設行為：返回主選單
        self.scene_manager.change_scene("main_menu")

    def get_scene_data(self) -> Dict[str, Any]:
        """
        獲取場景資料

        Returns:
            dict: 場景資料
        """
        return self.scene_data.copy()

    def set_scene_data(self, key: str, value: Any):
        """
        設置場景資料

        Args:
            key: 資料鍵
            value: 資料值
        """
        self.scene_data[key] = value

    def cleanup(self):
        """清理場景資源"""
        self.scene_data.clear()
        self.is_loaded = False
        self.is_active = False
        print(f"場景資源已清理: {self.__class__.__name__}")

    def change_scene(self, scene_name: str, data: Dict[str, Any] = None):
        """
        切換場景的便利方法

        Args:
            scene_name: 目標場景名稱
            data: 傳遞的資料
        """
        self.scene_manager.change_scene(scene_name, data)

    def quit_game(self):
        """退出遊戲的便利方法"""
        self.game_engine.quit_game()

    def get_mouse_pos(self) -> tuple:
        """
        獲取正確轉換後的滑鼠位置

        Returns:
            tuple: 遊戲座標系中的滑鼠位置 (x, y)
        """
        return self.game_engine.get_mouse_pos()

    def get_mouse_buttons(self) -> tuple:
        """
        獲取滑鼠按鈕狀態

        Returns:
            tuple: (left, middle, right) 按鈕狀態
        """
        return self.game_engine.get_mouse_buttons()

    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        檢查滑鼠按鈕是否被按下

        Args:
            button: 按鈕編號 (1=左鍵, 2=中鍵, 3=右鍵)

        Returns:
            bool: 按鈕是否被按下
        """
        return self.game_engine.is_mouse_button_pressed(button)

    def is_mouse_in_game_area(self) -> bool:
        """
        檢查滑鼠是否在遊戲區域內

        Returns:
            bool: 是否在遊戲區域內
        """
        raw_mouse_pos = pygame.mouse.get_pos()
        return self.game_engine.is_mouse_in_game_area(raw_mouse_pos)

    def get_screen_size(self) -> tuple:
        """
        獲取螢幕尺寸

        Returns:
            tuple: (寬度, 高度)
        """
        return self.game_engine.get_screen_size()

    def is_scene_active(self) -> bool:
        """
        檢查場景是否活躍

        Returns:
            bool: 場景是否活躍
        """
        return self.is_active and not self.paused

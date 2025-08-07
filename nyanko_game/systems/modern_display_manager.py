# -*- coding: utf-8 -*-
"""
現代顯示管理器
處理多解析度支援、智能縮放和全螢幕最佳化
"""

import pygame
import sys
from typing import Tuple, Optional, List
from config.settings import *


class ModernDisplayManager:
    """現代顯示管理器 - 提供智能解析度處理和最佳化縮放"""

    def __init__(self, game_engine=None):
        self.game_engine = game_engine
        self.current_resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.native_resolution = None
        self.is_fullscreen = False

        # 縮放和轉換參數
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.needs_scaling = False

        # 虛擬表面用於縮放渲染
        self.virtual_surface = None

        # 顯示能力
        self.supported_resolutions = self._detect_supported_resolutions()
        self.optimal_resolution = self._find_optimal_resolution()

    def _detect_supported_resolutions(self) -> List[Tuple[int, int]]:
        """偵測系統支援的解析度"""
        try:
            # 獲取系統支援的所有解析度
            modes = pygame.display.list_modes()
            if modes == -1:  # 支援所有解析度
                return DisplayModes.SUPPORTED_RESOLUTIONS

            # 過濾並排序支援的解析度
            supported = []
            for mode in modes:
                if (
                    mode[0] >= DisplayModes.MIN_WIDTH
                    and mode[1] >= DisplayModes.MIN_HEIGHT
                ):
                    supported.append(mode)

            # 按解析度大小排序（降序）
            supported.sort(key=lambda x: x[0] * x[1], reverse=True)
            return supported

        except Exception as e:
            print(f"偵測解析度失敗，使用預設列表: {e}")
            return [(w, h) for w, h, _ in DisplayModes.SUPPORTED_RESOLUTIONS]

    def _find_optimal_resolution(self) -> Tuple[int, int]:
        """尋找最佳解析度"""
        try:
            # 獲取原生螢幕解析度
            native = self._get_native_resolution()
            self.native_resolution = native

            # 如果原生解析度就是遊戲解析度，直接使用
            if native == (SCREEN_WIDTH, SCREEN_HEIGHT):
                return native

            # 檢查原生解析度是否支援遊戲解析度
            native_w, native_h = native
            game_w, game_h = SCREEN_WIDTH, SCREEN_HEIGHT

            if native_w >= game_w and native_h >= game_h:
                # 原生解析度足夠大，可以使用遊戲解析度
                return (SCREEN_WIDTH, SCREEN_HEIGHT)

            # 尋找最接近且支援的解析度
            for res in DisplayModes.PREFERRED_RESOLUTIONS:
                if res in self.supported_resolutions:
                    if res[0] <= native_w and res[1] <= native_h:
                        return res

            # 使用最小支援解析度
            return (DisplayModes.MIN_WIDTH, DisplayModes.MIN_HEIGHT)

        except Exception as e:
            print(f"尋找最佳解析度失敗: {e}")
            return (SCREEN_WIDTH, SCREEN_HEIGHT)

    def _get_native_resolution(self) -> Tuple[int, int]:
        """獲取系統原生解析度"""
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
            return (info.current_w, info.current_h)

        except Exception as e:
            print(f"無法獲取原生解析度: {e}")
            return (1920, 1080)  # 預設為Full HD

    def initialize_display(self, fullscreen: bool = False) -> pygame.Surface:
        """初始化顯示器"""
        self.is_fullscreen = fullscreen

        if fullscreen:
            return self._setup_fullscreen_display()
        else:
            return self._setup_windowed_display()

    def _setup_windowed_display(self) -> pygame.Surface:
        """設置視窗模式顯示"""
        # 檢查視窗是否能完整顯示在螢幕上
        native_w, native_h = self.native_resolution or self._get_native_resolution()

        # 考慮工作列和視窗框架的空間
        available_w = native_w - 100  # 預留空間
        available_h = native_h - 150  # 預留工作列和標題列空間

        target_w, target_h = SCREEN_WIDTH, SCREEN_HEIGHT

        # 如果遊戲視窗太大，縮放到適合的大小
        if target_w > available_w or target_h > available_h:
            scale_x = available_w / target_w
            scale_y = available_h / target_h
            scale = min(scale_x, scale_y, 0.9)  # 最多縮放到90%

            target_w = int(target_w * scale)
            target_h = int(target_h * scale)

            print(f"視窗縮放: {scale:.2f}, 調整尺寸: {target_w}x{target_h}")

        self.current_resolution = (target_w, target_h)
        self.needs_scaling = target_w != SCREEN_WIDTH or target_h != SCREEN_HEIGHT

        if self.needs_scaling:
            self._setup_scaling_params(target_w, target_h)
            self.virtual_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        flags = pygame.DOUBLEBUF
        return pygame.display.set_mode(self.current_resolution, flags)

    def _setup_fullscreen_display(self) -> pygame.Surface:
        """設置全螢幕模式顯示"""
        native_w, native_h = self.native_resolution or self._get_native_resolution()

        # 檢查是否完美匹配
        if native_w == SCREEN_WIDTH and native_h == SCREEN_HEIGHT:
            # 完美匹配，無需縮放
            self.current_resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
            self.needs_scaling = False
            self.scale_factor = 1.0
            self.offset_x = 0
            self.offset_y = 0

            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
            print(f"全螢幕模式: {SCREEN_WIDTH}x{SCREEN_HEIGHT} (完美匹配)")

        else:
            # 需要縮放，使用原生解析度
            self.current_resolution = (native_w, native_h)
            self.needs_scaling = True
            self._setup_scaling_params(native_w, native_h)
            self.virtual_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
            print(f"全螢幕模式: {native_w}x{native_h} (需要縮放)")

        return pygame.display.set_mode(self.current_resolution, flags)

    def _setup_scaling_params(self, display_w: int, display_h: int):
        """設置縮放參數"""
        game_w, game_h = SCREEN_WIDTH, SCREEN_HEIGHT

        # 計算縮放比例（保持縱橫比）
        scale_x = display_w / game_w
        scale_y = display_h / game_h
        self.scale_factor = min(scale_x, scale_y)

        # 計算縮放後的尺寸
        scaled_w = int(game_w * self.scale_factor)
        scaled_h = int(game_h * self.scale_factor)

        # 計算居中偏移
        self.offset_x = (display_w - scaled_w) // 2
        self.offset_y = (display_h - scaled_h) // 2

        print(
            f"縮放設定: 比例={self.scale_factor:.3f}, 偏移=({self.offset_x}, {self.offset_y})"
        )

    def render_frame(self, screen: pygame.Surface, render_callback):
        """渲染一幀畫面"""
        if self.needs_scaling:
            # 使用虛擬表面渲染
            self.virtual_surface.fill(Colors.BACKGROUND_COLOR)
            render_callback(self.virtual_surface)

            # 縮放並繪製到實際螢幕
            scaled_w = int(SCREEN_WIDTH * self.scale_factor)
            scaled_h = int(SCREEN_HEIGHT * self.scale_factor)

            scaled_surface = ImageScaling.pixel_perfect_scale(
                self.virtual_surface, (scaled_w, scaled_h)
            )

            # 清空螢幕並居中繪製
            screen.fill(Colors.BLACK)
            screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        else:
            # 直接渲染
            screen.fill(Colors.BACKGROUND_COLOR)
            render_callback(screen)

    def transform_mouse_position(
        self, screen_pos: Tuple[int, int]
    ) -> Optional[Tuple[int, int]]:
        """轉換滑鼠座標從螢幕座標到遊戲座標"""
        if not self.needs_scaling:
            return screen_pos

        screen_x, screen_y = screen_pos

        # 減去偏移
        game_x = screen_x - self.offset_x
        game_y = screen_y - self.offset_y

        # 反向縮放
        if self.scale_factor > 0:
            game_x = int(game_x / self.scale_factor)
            game_y = int(game_y / self.scale_factor)

        # 檢查是否在遊戲區域內
        if (
            game_x < 0
            or game_x >= SCREEN_WIDTH
            or game_y < 0
            or game_y >= SCREEN_HEIGHT
        ):
            return None

        return (game_x, game_y)

    def is_position_in_game_area(self, screen_pos: Tuple[int, int]) -> bool:
        """檢查位置是否在遊戲區域內"""
        return self.transform_mouse_position(screen_pos) is not None

    def toggle_fullscreen(self, screen: pygame.Surface) -> pygame.Surface:
        """切換全螢幕模式"""
        self.is_fullscreen = not self.is_fullscreen
        return self.initialize_display(self.is_fullscreen)

    def get_display_info(self) -> dict:
        """獲取顯示資訊"""
        return {
            "current_resolution": self.current_resolution,
            "game_resolution": (SCREEN_WIDTH, SCREEN_HEIGHT),
            "native_resolution": self.native_resolution,
            "is_fullscreen": self.is_fullscreen,
            "needs_scaling": self.needs_scaling,
            "scale_factor": self.scale_factor,
            "offset": (self.offset_x, self.offset_y),
            "supported_resolutions": self.supported_resolutions,
            "optimal_resolution": self.optimal_resolution,
        }

    def set_resolution(self, width: int, height: int) -> pygame.Surface:
        """設定自訂解析度（僅視窗模式）"""
        if self.is_fullscreen:
            print("全螢幕模式下無法變更解析度")
            return None

        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH = width
        SCREEN_HEIGHT = height

        # 重新初始化顯示
        return self.initialize_display(False)

    def get_recommended_resolution(self) -> Tuple[int, int]:
        """獲取建議的解析度"""
        native = self.native_resolution or self._get_native_resolution()

        # 如果原生解析度支援Full HD，建議使用Full HD
        if native[0] >= 1920 and native[1] >= 1080:
            return (1920, 1080)

        # 否則尋找最適合的解析度
        for res in DisplayModes.PREFERRED_RESOLUTIONS:
            if res[0] <= native[0] * 0.9 and res[1] <= native[1] * 0.9:
                return res

        return (1280, 720)  # 最低建議解析度

    def auto_adjust_resolution(self) -> Tuple[int, int]:
        """自動調整到最佳解析度"""
        recommended = self.get_recommended_resolution()

        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = recommended

        print(f"自動調整解析度到: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        return recommended

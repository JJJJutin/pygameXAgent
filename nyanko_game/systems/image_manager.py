# -*- coding: utf-8 -*-
"""
圖片管理系統
負責載入、管理和提供遊戲中的所有圖片資源
"""

import pygame
import os
from config.settings import Paths


class ImageManager:
    """圖片管理器"""

    def __init__(self):
        """初始化圖片管理器"""
        self.images = {}
        self.loaded = False

    def load_all_images(self):
        """載入所有遊戲圖片"""
        if self.loaded:
            return

        print("正在載入圖片資源...")

        # 載入背景圖片
        self._load_backgrounds()

        # 載入角色圖片
        self._load_characters()

        # 載入UI圖片
        self._load_ui()

        self.loaded = True
        print("圖片資源載入完成!")

    def _load_backgrounds(self):
        """載入背景圖片"""
        backgrounds_path = os.path.join(Paths.BACKGROUNDS_DIR)

        # 客廳背景
        self._load_image(
            "bg_livingroom_morning",
            os.path.join(backgrounds_path, "bg_livingroom-AM.png"),
        )
        self._load_image(
            "bg_livingroom_evening",
            os.path.join(backgrounds_path, "bg_livingroom-PM.png"),
        )

    def _load_characters(self):
        """載入角色圖片"""
        # にゃんこ角色圖片
        nyanko_path = os.path.join(Paths.CHARACTERS_DIR, "nyanko", "maid")

        self._load_image("nyanko_normal", os.path.join(nyanko_path, "nyanko.png"))
        self._load_image("nyanko_happy", os.path.join(nyanko_path, "nyanko-happy.png"))

    def _load_ui(self):
        """載入UI圖片"""
        ui_path = os.path.join(Paths.UI_DIR)
        # 預留UI圖片載入位置
        pass

    def _load_image(self, key, filepath):
        """
        載入單張圖片

        Args:
            key (str): 圖片的識別鍵
            filepath (str): 圖片檔案路徑
        """
        try:
            if os.path.exists(filepath):
                image = pygame.image.load(filepath).convert_alpha()
                self.images[key] = image
                print(f"已載入圖片: {key} ({filepath})")
            else:
                print(f"警告: 找不到圖片檔案: {filepath}")
                # 創建佔位圖片
                self.images[key] = self._create_placeholder_image(key)
        except pygame.error as e:
            print(f"錯誤: 無法載入圖片 {filepath}: {e}")
            self.images[key] = self._create_placeholder_image(key)

    def _create_placeholder_image(self, key):
        """
        創建佔位圖片

        Args:
            key (str): 圖片識別鍵

        Returns:
            pygame.Surface: 佔位圖片
        """
        if "bg_" in key:
            # 背景佔位圖片
            surface = pygame.Surface((1280, 720))
            if "morning" in key:
                surface.fill((255, 255, 200))  # 淡黃色代表早上
            else:
                surface.fill((100, 100, 200))  # 深藍色代表晚上
        else:
            # 角色佔位圖片
            surface = pygame.Surface((300, 400))
            surface.fill((255, 182, 193))  # 粉色

        return surface

    def get_image(self, key):
        """
        獲取圖片

        Args:
            key (str): 圖片識別鍵

        Returns:
            pygame.Surface: 圖片物件，如果不存在則返回None
        """
        if not self.loaded:
            self.load_all_images()

        return self.images.get(key)

    def get_scaled_image(self, key, size):
        """
        獲取縮放後的圖片 - 使用像素完整縮放

        Args:
            key (str): 圖片識別鍵
            size (tuple): 目標尺寸 (width, height)

        Returns:
            pygame.Surface: 縮放後的圖片
        """
        image = self.get_image(key)
        if image:
            from config.settings import ImageScaling

            return ImageScaling.pixel_perfect_scale(image, size)
        return None

    def get_background_for_time(self, location, time_period):
        """
        根據時間獲取背景圖片

        Args:
            location (str): 地點名稱
            time_period (str): 時間段

        Returns:
            pygame.Surface: 背景圖片
        """
        if location == "living_room":
            if time_period in ["morning", "afternoon"]:
                return self.get_image("bg_livingroom_morning")
            else:
                return self.get_image("bg_livingroom_evening")

        # 預設返回早上的客廳背景
        return self.get_image("bg_livingroom_morning")

    def get_character_image(self, character, emotion="normal", outfit="default"):
        """
        獲取角色圖片

        Args:
            character (str): 角色名稱
            emotion (str): 表情狀態
            outfit (str): 服裝類型

        Returns:
            pygame.Surface: 角色圖片
        """
        if character == "nyanko":
            if emotion == "happy":
                return self.get_image("nyanko_happy")
            else:
                return self.get_image("nyanko_normal")

        return None

    def get_scaled_character_image(
        self, character, emotion="normal", outfit="default", target_size=None
    ):
        """
        獲取按比例縮放的角色圖片 - 使用像素完整縮放

        Args:
            character (str): 角色名稱
            emotion (str): 表情狀態
            outfit (str): 服裝類型
            target_size (tuple): 目標尺寸 (width, height)，如果為None則使用原始尺寸

        Returns:
            pygame.Surface: 縮放後的角色圖片
        """
        # 獲取原始圖片
        original_image = self.get_character_image(character, emotion, outfit)

        if original_image is None:
            return None

        # 如果沒有指定目標尺寸，返回原始圖片
        if target_size is None:
            return original_image

        # 使用像素完整縮放圖片
        from config.settings import ImageScaling

        return ImageScaling.pixel_perfect_scale(original_image, target_size)

    def get_adaptive_character_size(self, screen_width, screen_height):
        """
        根據螢幕尺寸計算人物立繪的適合大小

        Args:
            screen_width (int): 螢幕寬度
            screen_height (int): 螢幕高度

        Returns:
            tuple: (character_width, character_height)
        """
        from config.settings import ImageScaling

        return ImageScaling.calculate_character_size(screen_width, screen_height)

    def get_adaptive_character_position(
        self, screen_width, screen_height, char_width, char_height
    ):
        """
        計算人物立繪的最佳位置

        Args:
            screen_width (int): 螢幕寬度
            screen_height (int): 螢幕高度
            char_width (int): 人物立繪寬度
            char_height (int): 人物立繪高度

        Returns:
            tuple: (x, y) 位置座標
        """
        from config.settings import ImageScaling

        return ImageScaling.calculate_character_position(
            screen_width, screen_height, char_width, char_height
        )

    def list_loaded_images(self):
        """列出所有已載入的圖片"""
        print("已載入的圖片:")
        for key in sorted(self.images.keys()):
            print(f"  - {key}")


# 全域圖片管理器實例
image_manager = ImageManager()

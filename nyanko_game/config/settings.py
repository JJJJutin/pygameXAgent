# -*- coding: utf-8 -*-
"""
遊戲設定常數
包含所有遊戲相關的設定值和常數定義
"""

import pygame

# 遊戲基本設定
GAME_TITLE = "にゃんこと一緒 ～貓娘女僕的同居日常～"
GAME_VERSION = "1.0.0"

# 視窗設定
SCREEN_WIDTH = 1280  # 視窗寬度
SCREEN_HEIGHT = 720  # 視窗高度
FPS = 60
FULLSCREEN_MODE = False  # 預設視窗模式


# 顏色定義 (RGB)
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    PINK = (255, 182, 193)
    LIGHT_PINK = (255, 218, 224)
    BLUE = (173, 216, 230)
    LIGHT_BLUE = (173, 216, 230)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (211, 211, 211)
    DARK_GRAY = (64, 64, 64)
    YELLOW = (255, 255, 0)
    LIGHT_YELLOW = (255, 255, 224)
    GREEN = (0, 255, 0)
    LIGHT_GREEN = (144, 238, 144)
    RED = (255, 0, 0)
    LIGHT_RED = (255, 182, 193)

    # 主題色彩
    PRIMARY_COLOR = PINK
    SECONDARY_COLOR = LIGHT_PINK
    ACCENT_COLOR = BLUE
    TEXT_COLOR = DARK_GRAY
    BACKGROUND_COLOR = WHITE


# 字體設定
class FontSettings:
    # 使用Microsoft JhengHei字體的絕對路徑
    DEFAULT_FONT = r"C:\Windows\Fonts\msjh.ttc"  # 微軟正黑體
    FALLBACK_FONT = r"C:\Windows\Fonts\msjhbd.ttc"  # 微軟正黑體粗體

    FONT_SIZE_SMALL = 14
    FONT_SIZE_MEDIUM = 18
    FONT_SIZE_LARGE = 24
    FONT_SIZE_TITLE = 32

    # 對話字體設定
    DIALOGUE_FONT_SIZE = 20
    SPEAKER_FONT_SIZE = 16

    @staticmethod
    def get_font(size, bold=False):
        """
        獲取字體的輔助函數

        Args:
            size (int): 字體大小
            bold (bool): 是否使用粗體

        Returns:
            pygame.font.Font: 字體物件
        """
        import pygame

        try:
            font_path = (
                FontSettings.FALLBACK_FONT if bold else FontSettings.DEFAULT_FONT
            )
            return pygame.font.Font(font_path, size)
        except (FileNotFoundError, OSError):
            print(f"警告: 無法載入指定字體，使用系統預設字體 (size: {size})")
            return pygame.font.Font(None, size)


# UI設定
class UISettings:
    # 對話框設定
    DIALOGUE_BOX_HEIGHT = 200
    DIALOGUE_BOX_MARGIN = 20
    DIALOGUE_TEXT_MARGIN = 15

    # 按鈕設定
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    BUTTON_MARGIN = 10

    # 動畫設定
    FADE_SPEED = 5
    TEXT_SPEED_SLOW = 30
    TEXT_SPEED_NORMAL = 50
    TEXT_SPEED_FAST = 100


# 遊戲邏輯設定
class GameSettings:
    # 時間系統
    MINUTES_PER_PERIOD = 30  # 每個時段的分鐘數
    AUTO_SAVE_INTERVAL = 300  # 自動存檔間隔（秒）

    # 好感度系統
    MAX_AFFECTION = 100
    MIN_AFFECTION = 0
    DAILY_AFFECTION_DECAY = 1  # 每日好感度自然衰減

    # 存檔設定
    MAX_SAVE_SLOTS = 10
    AUTO_SAVE_SLOT = 0


# 圖片縮放設定
class ImageScaling:
    # 背景圖片原始解析度
    BACKGROUND_ORIGINAL_WIDTH = 480
    BACKGROUND_ORIGINAL_HEIGHT = 270

    # 人物立繪原始解析度
    CHARACTER_ORIGINAL_WIDTH = 170
    CHARACTER_ORIGINAL_HEIGHT = 283

    # 相對於背景的人物立繪縮放比例
    CHARACTER_TO_BACKGROUND_RATIO = 1  # 人物立繪高度為背景高度的1.0倍

    # 像素完整縮放設定
    USE_PIXEL_PERFECT_SCALING = True  # 是否使用像素完整縮放
    PIXEL_PERFECT_FILTER = True  # 是否在像素完整縮放時使用最近鄰過濾

    @staticmethod
    def calculate_character_size(background_width, background_height):
        """
        根據背景尺寸計算人物立繪的適合尺寸

        Args:
            background_width (int): 背景寬度
            background_height (int): 背景高度

        Returns:
            tuple: (character_width, character_height)
        """
        # 計算目標高度（背景高度的一定比例）
        target_height = int(
            background_height * ImageScaling.CHARACTER_TO_BACKGROUND_RATIO
        )

        # 保持人物立繪的原始比例
        original_ratio = (
            ImageScaling.CHARACTER_ORIGINAL_WIDTH
            / ImageScaling.CHARACTER_ORIGINAL_HEIGHT
        )
        target_width = int(target_height * original_ratio)

        return (target_width, target_height)

    @staticmethod
    def calculate_character_position(
        screen_width, screen_height, char_width, char_height
    ):
        """
        計算人物立繪在螢幕上的最佳位置

        Args:
            screen_width (int): 螢幕寬度
            screen_height (int): 螢幕高度
            char_width (int): 人物立繪寬度
            char_height (int): 人物立繪高度

        Returns:
            tuple: (x, y) 人物立繪左上角座標
        """
        # 將人物放在螢幕右側，底部對齊
        x = screen_width - char_width - 50  # 距離右邊緣50像素
        y = screen_height - char_height - -20  # 距離底部20像素

        return (x, y)

    @staticmethod
    def pixel_perfect_scale(surface, target_size):
        """
        像素完整縮放函數 - 保持圖片的銳利度和像素完整性

        Args:
            surface (pygame.Surface): 要縮放的表面
            target_size (tuple): 目標尺寸 (width, height)

        Returns:
            pygame.Surface: 縮放後的表面
        """
        if not ImageScaling.USE_PIXEL_PERFECT_SCALING:
            # 如果不使用像素完整縮放，使用傳統方法
            return pygame.transform.scale(surface, target_size)

        original_size = surface.get_size()
        target_width, target_height = target_size
        original_width, original_height = original_size

        # 計算縮放倍數
        scale_x = target_width / original_width
        scale_y = target_height / original_height

        # 檢查是否可以使用整數倍縮放（允許小誤差）
        if (
            abs(scale_x - round(scale_x)) < 0.01
            and abs(scale_y - round(scale_y)) < 0.01
            and abs(scale_x - scale_y) < 0.01
            and scale_x >= 1
        ):
            # 使用整數倍縮放，保持像素銳利
            scale_factor = round(scale_x)

            if scale_factor == 1:
                # 沒有縮放，直接返回
                if target_size == original_size:
                    return surface.copy()
                else:
                    # 需要裁剪或填充
                    result = pygame.Surface(target_size, pygame.SRCALPHA)
                    x_offset = (target_width - original_width) // 2
                    y_offset = (target_height - original_height) // 2
                    result.blit(surface, (x_offset, y_offset))
                    return result

            # 對於整數倍縮放，使用快速的重複blit方法
            scaled_size = (
                original_width * scale_factor,
                original_height * scale_factor,
            )
            scaled_surface = pygame.Surface(scaled_size, pygame.SRCALPHA)

            # 使用pygame的transform.scale進行整數倍縮放，然後手動確保像素完整性
            temp_scaled = pygame.transform.scale(surface, scaled_size)
            scaled_surface.blit(temp_scaled, (0, 0))

            # 如果目標尺寸與縮放尺寸不同，居中顯示
            if scaled_size != target_size:
                final_surface = pygame.Surface(target_size, pygame.SRCALPHA)
                x_offset = (target_width - scaled_size[0]) // 2
                y_offset = (target_height - scaled_size[1]) // 2
                final_surface.blit(scaled_surface, (x_offset, y_offset))
                return final_surface

            return scaled_surface

        # 對於非整數倍縮放，根據設定選擇算法
        if ImageScaling.PIXEL_PERFECT_FILTER:
            # 使用最近鄰算法避免模糊，但保持原生性能
            # 這個方法比手動設置每個像素快得多
            # 暫時禁用平滑過濾以獲得最接近的像素效果
            result = pygame.transform.scale(surface, target_size)
            return result
        else:
            # 使用平滑縮放
            return pygame.transform.smoothscale(surface, target_size)

    @staticmethod
    def get_optimal_scale_factor(original_size, target_size):
        """
        獲取最優的整數縮放倍數

        Args:
            original_size (tuple): 原始尺寸 (width, height)
            target_size (tuple): 目標尺寸 (width, height)

        Returns:
            int: 最優縮放倍數
        """
        original_width, original_height = original_size
        target_width, target_height = target_size

        scale_x = target_width / original_width
        scale_y = target_height / original_height

        # 選擇較小的縮放倍數，保證圖片完整顯示
        scale = min(scale_x, scale_y)

        # 返回最大的不超過目標的整數倍數
        return max(1, int(scale))


# 檔案路徑設定
class Paths:
    # 資源路徑
    ASSETS_DIR = "assets"
    IMAGES_DIR = f"{ASSETS_DIR}/images"
    SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
    FONTS_DIR = f"{ASSETS_DIR}/fonts"

    # 圖片子目錄
    CHARACTERS_DIR = f"{IMAGES_DIR}/characters"
    BACKGROUNDS_DIR = f"{IMAGES_DIR}/backgrounds"
    UI_DIR = f"{IMAGES_DIR}/ui"

    # 資料檔案
    DATA_DIR = "data"
    SAVES_DIR = f"{DATA_DIR}/saves"
    DIALOGUE_DATA = f"{DATA_DIR}/dialogue.json"
    CHARACTER_DATA = f"{DATA_DIR}/characters.json"


# 音效設定
class AudioSettings:
    MASTER_VOLUME = 1.0
    BGM_VOLUME = 0.8
    SFX_VOLUME = 0.9
    VOICE_VOLUME = 1.0

    # 音效檔案格式
    AUDIO_FORMATS = [".ogg", ".wav", ".mp3"]


# 除錯設定
class DebugSettings:
    DEBUG_MODE = True
    SHOW_FPS = True
    SHOW_COLLISION_BOXES = True
    SHOW_SCENE_INFO = True
    SHOW_DIALOGUE_DEBUG = True
    SHOW_AFFECTION_DEBUG = True
    SHOW_TIME_DEBUG = True
    SHOW_EVENT_DEBUG = True
    LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
    VERBOSE_LOGGING = True


# 輸入設定
class InputSettings:
    # 鍵盤對應
    KEY_CONFIRM = "SPACE"
    KEY_CANCEL = "ESCAPE"
    KEY_SKIP = "CTRL"
    KEY_AUTO = "A"
    KEY_MENU = "TAB"

    # 滑鼠設定
    DOUBLE_CLICK_TIME = 500  # 毫秒

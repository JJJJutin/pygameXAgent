# -*- coding: utf-8 -*-
"""
遊戲設定常數
包含所有遊戲相關的設定值和常數定義
"""

# 遊戲基本設定
GAME_TITLE = "にゃんこと一緒 ～貓娘女僕的同居日常～"
GAME_VERSION = "1.0.0"

# 視窗設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = False

# 全螢幕縮放設定
SCALE_MODE_STRETCH = "stretch"  # 拉伸填滿
SCALE_MODE_KEEP_ASPECT = "keep_aspect"  # 保持長寬比
SCALE_MODE_PIXEL_PERFECT = "pixel_perfect"  # 像素完美縮放
DEFAULT_SCALE_MODE = SCALE_MODE_KEEP_ASPECT


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
    SHOW_COLLISION_BOXES = False
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR


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

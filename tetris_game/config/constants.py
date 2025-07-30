"""
遊戲常數定義模組
定義遊戲中所有使用的常數
"""

# ============================
# 視窗設定
# ============================
WINDOW_WIDTH = 800  # 視窗寬度（增加以容納 Hold 和 Next 區域）
WINDOW_HEIGHT = 680  # 視窗高度
FPS = 60  # 遊戲幀率

# ============================
# 遊戲區域參數
# ============================
GRID_WIDTH = 10  # 遊戲區域寬度（格數）
GRID_HEIGHT = 20  # 遊戲區域高度（格數）
CELL_SIZE = 30  # 每個格子的像素大小
FALL_SPEED = 500  # 方塊下落速度（毫秒）

# 遊戲區域位置
GRID_X = (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_Y = 20

# ============================
# 顏色常數
# ============================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
CYAN = (0, 255, 255)  # I 型：天藍色
YELLOW = (255, 255, 0)  # O 型：黃色
PURPLE = (128, 0, 128)  # T 型：紫色
GREEN = (0, 255, 0)  # S 型：綠色
RED = (255, 0, 0)  # Z 型：紅色
BLUE = (0, 0, 255)  # J 型：藍色
ORANGE = (255, 165, 0)  # L 型：橙色

# Tetromino 顏色清單
TETROMINO_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

# 網格線顏色
GRID_COLOR = GRAY

# ============================
# DAS (Delayed Auto Shift) 設定
# ============================
DAS_DELAY = 10  # DAS 延遲 (16.67ms * 10 ≈ 167ms)
ARR_RATE = 2  # ARR 重複率 (每2幀移動一次)

# ============================
# Lock Delay 設定
# ============================
LOCK_DELAY_MAX = 8  # Lock delay 時間 (約 0.13秒 @ 60fps)
MAX_LOCK_RESETS = 15  # 最大重置次數

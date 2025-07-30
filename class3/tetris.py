# pip install pygame
import pygame
import sys
import random

# ============================
# 遊戲常數定義區塊
# ============================

# 視窗設定
WINDOW_WIDTH = 800  # 視窗寬度（增加以容納 Hold 和 Next 區域）
WINDOW_HEIGHT = 680  # 視窗高度
FPS = 60  # 遊戲幀率

# 遊戲區域參數
GRID_WIDTH = 10  # 遊戲區域寬度（格數）
GRID_HEIGHT = 20  # 遊戲區域高度（格數）
CELL_SIZE = 30  # 每個格子的像素大小
FALL_SPEED = 500  # 方塊下落速度（毫秒）

# 遊戲區域位置
GRID_X = (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_Y = 20

# 顏色常數
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
# Tetromino 形狀定義區塊
# ============================

# 七種 Tetromino 形狀定義（SRS 標準）
TETROMINO_SHAPES = {
    "I": [  # I 型（直線）- 天藍色
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],  # 水平
        [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],  # 垂直
        [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],  # 水平
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],  # 垂直
    ],
    "O": [  # O 型（正方形）- 黃色
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # 只有一種狀態
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    ],
    "T": [  # T 型（T 字形）- 紫色
        [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # 0° 朝上
        [[0, 1, 0, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 90° 朝右
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 180° 朝下
        [[0, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 270° 朝左
    ],
    "S": [  # S 型（閃電形）- 綠色
        [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # 水平
        [[0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]],  # 垂直
        [[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]],  # 水平
        [[1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 垂直
    ],
    "Z": [  # Z 型（反閃電形）- 紅色
        [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # 水平
        [[0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 垂直
        [[0, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],  # 水平
        [[0, 1, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]],  # 垂直
    ],
    "J": [  # J 型（反 L 形）- 藍色
        [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # 0°
        [[0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 90°
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]],  # 180°
        [[0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0]],  # 270°
    ],
    "L": [  # L 型（L 形）- 橙色
        [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # 0°
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],  # 90°
        [[0, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0]],  # 180°
        [[1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],  # 270°
    ],
}

# 形狀類型對應顏色索引
SHAPE_COLORS = {"I": 0, "O": 1, "T": 2, "S": 3, "Z": 4, "J": 5, "L": 6}

# ============================
# 遊戲物件類別定義區塊
# ============================


class Tetromino:
    """四格方塊物件類別"""

    def __init__(self, shape_type):
        """
        初始化 Tetromino 物件
        參數：
        - shape_type: 方塊類型 (I, O, T, S, Z, J, L)
        """
        self.shape_type = shape_type
        self.shapes = TETROMINO_SHAPES[shape_type]
        self.color = TETROMINO_COLORS[SHAPE_COLORS[shape_type]]
        self.x = GRID_WIDTH // 2 - 2  # 方塊在遊戲區域中的 X 位置
        self.y = -1 if shape_type == "I" else 0  # I 方塊稍微高一點出現
        self.rotation = 0  # 當前旋轉狀態（0-3）

    def get_rotation_center(self):
        """
        獲取旋轉中心點（SRS 標準）
        返回：(center_x, center_y) 相對於形狀矩陣的中心點
        """
        if self.shape_type == "I":
            # I 方塊的旋轉中心在 (1.5, 1.5)
            return (1.5, 1.5)
        elif self.shape_type == "O":
            # O 方塊的旋轉中心在 (1.5, 0.5)
            return (1.5, 0.5)
        else:
            # 其他方塊 (T, S, Z, J, L) 的旋轉中心在 (1.5, 1.5)
            return (1.5, 1.5)

    def get_rotation_center(self):
        """
        獲取 SRS 標準旋轉中心點
        - I 和 O 型：網格線交點
        - J, L, S, T, Z 型：方塊中心
        """
        if self.shape_type in ["I", "O"]:
            # I 和 O 型的旋轉中心在網格線交點
            return (1.5, 1.5)
        else:
            # J, L, S, T, Z 型的旋轉中心在方塊中心
            return (1, 1)

    def rotate_clockwise(self):
        """順時針旋轉方塊（90 度）"""
        if len(self.shapes) > 1:  # O 型方塊不需要旋轉
            self.rotation = (self.rotation + 1) % len(self.shapes)

    def rotate_counterclockwise(self):
        """逆時針旋轉方塊（90 度）"""
        if len(self.shapes) > 1:  # O 型方塊不需要旋轉
            self.rotation = (self.rotation - 1) % len(self.shapes)

    def rotate(self, clockwise=True):
        """
        旋轉方塊（保持向後相容性）
        參數：
        - clockwise: True 為順時針，False 為逆時針
        """
        if clockwise:
            self.rotate_clockwise()
        else:
            self.rotate_counterclockwise()

    def move(self, dx, dy):
        """
        移動方塊位置
        參數：
        - dx: X 軸移動距離
        - dy: Y 軸移動距離
        """
        self.x += dx
        self.y += dy

    def get_current_shape(self):
        """獲取當前旋轉狀態的形狀"""
        return self.shapes[self.rotation]

    def get_rotated_shape(self, rotation):
        """獲取指定旋轉狀態的形狀（用於 Wall Kick 測試）"""
        return self.shapes[rotation]

    def get_blocks(self):
        """獲取方塊所佔據的所有格子位置"""
        blocks = []
        shape = self.get_current_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    blocks.append((self.x + col_idx, self.y + row_idx))
        return blocks

    def get_ghost_blocks(self, grid):
        """
        獲取幽靈方塊位置（預覽落點）
        參數：
        - grid: GameGrid 物件
        返回：幽靈方塊的所有格子位置
        """
        ghost_tetromino = Tetromino(self.shape_type)
        ghost_tetromino.x = self.x
        ghost_tetromino.y = self.y
        ghost_tetromino.rotation = self.rotation

        # 向下移動直到碰撞
        while grid.is_valid_position(ghost_tetromino, 0, 1):
            ghost_tetromino.move(0, 1)

        return ghost_tetromino.get_blocks()

    def copy(self):
        """創建方塊的副本"""
        new_tetromino = Tetromino(self.shape_type)
        new_tetromino.x = self.x
        new_tetromino.y = self.y
        new_tetromino.rotation = self.rotation
        return new_tetromino


class GameGrid:
    """遊戲區域物件類別"""

    def __init__(self, width, height):
        """
        初始化遊戲區域
        參數：
        - width: 遊戲區域寬度
        - height: 遊戲區域高度
        """
        self.width = width
        self.height = height
        self.grid = [[BLACK for _ in range(width)] for _ in range(height)]
        self.filled_rows = []

    def is_valid_position(self, tetromino, offset_x=0, offset_y=0):
        """
        檢查方塊位置是否合法
        參數：
        - tetromino: Tetromino 物件
        - offset_x: X 軸偏移量
        - offset_y: Y 軸偏移量
        返回：True 如果位置合法，False 如果不合法
        """
        shape = tetromino.get_current_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = tetromino.x + col_idx + offset_x
                    new_y = tetromino.y + row_idx + offset_y

                    # 檢查邊界
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False

                    # 檢查是否與已放置的方塊重疊
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return False

        return True

    def is_valid_position_at(self, shape, x, y):
        """
        檢查指定形狀在指定位置是否合法（用於 Wall Kick）
        參數：
        - shape: 方塊形狀（2D 陣列）
        - x: X 位置
        - y: Y 位置
        返回：True 如果位置合法，False 如果不合法
        """
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx

                    # 檢查邊界
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False

                    # 檢查是否與已放置的方塊重疊
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return False

        return True

    def place_tetromino(self, tetromino):
        """
        將方塊放置到遊戲區域
        參數：
        - tetromino: Tetromino 物件
        """
        blocks = tetromino.get_blocks()
        for x, y in blocks:
            if y >= 0:  # 只放置在可見區域內
                self.grid[y][x] = tetromino.color

    def check_lines(self):
        """檢查並消除填滿的行"""
        lines_cleared = 0
        y = self.height - 1

        while y >= 0:
            if all(cell != BLACK for cell in self.grid[y]):
                # 找到完整的行，清除它
                self.clear_line(y)
                lines_cleared += 1
            else:
                y -= 1

        return lines_cleared

    def is_perfect_clear(self):
        """檢查是否為 Perfect Clear (All Clear)"""
        return all(all(cell == BLACK for cell in row) for row in self.grid)

    def clear_line(self, row):
        """
        清除指定行
        參數：
        - row: 要清除的行索引
        """
        # 刪除指定行
        del self.grid[row]
        # 在頂部添加新的空白行
        self.grid.insert(0, [BLACK for _ in range(self.width)])

    def is_game_over(self):
        """檢查遊戲是否結束"""
        # 如果第一行有方塊，遊戲結束
        return any(cell != BLACK for cell in self.grid[0])

    def draw(self, screen):
        """
        繪製遊戲區域和已放置的方塊
        參數：
        - screen: pygame 螢幕物件
        """
        # 繪製已放置的方塊
        for row_idx, row in enumerate(self.grid):
            for col_idx, color in enumerate(row):
                if color != BLACK:
                    x = GRID_X + col_idx * CELL_SIZE
                    y = GRID_Y + row_idx * CELL_SIZE
                    pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE), 1)

        # 繪製網格線
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                screen,
                GRID_COLOR,
                (GRID_X + x * CELL_SIZE, GRID_Y),
                (GRID_X + x * CELL_SIZE, GRID_Y + GRID_HEIGHT * CELL_SIZE),
            )

        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                screen,
                GRID_COLOR,
                (GRID_X, GRID_Y + y * CELL_SIZE),
                (GRID_X + GRID_WIDTH * CELL_SIZE, GRID_Y + y * CELL_SIZE),
            )


class Game:
    """遊戲控制器物件類別"""

    def __init__(self):
        """初始化遊戲"""
        self.grid = GameGrid(GRID_WIDTH, GRID_HEIGHT)

        # 7-bag 隨機器系統
        self.piece_bag = []  # 當前的方塊袋
        self.fill_bag()  # 填充第一個袋子

        self.current_tetromino = self.spawn_tetromino()
        self.next_tetromino = self.spawn_tetromino()
        self.hold_tetromino = None  # Hold 功能的方塊
        self.can_hold = True  # 是否可以使用 Hold 功能
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_timer = 0
        self.game_over = False

        # DAS (Delayed Auto Shift) 系統
        self.das_timer_left = 0  # 左移計時器
        self.das_timer_right = 0  # 右移計時器
        self.das_delay = 10  # DAS 延遲 (16.67ms * 10 ≈ 167ms)
        self.arr_rate = 2  # ARR 重複率 (每2幀移動一次)
        self.das_active_left = False  # 左移是否在DAS狀態
        self.das_active_right = False  # 右移是否在DAS狀態

        # Lock Delay 系統（Tetris 99 標準）
        self.lock_delay_timer = 0  # Lock delay 計時器
        self.lock_delay_max = (
            8  # 大幅縮短 lock delay 時間 (約 0.13秒 @ 60fps，接近競技標準)
        )
        self.lock_delay_resets = 0  # Lock delay 重置次數
        self.max_lock_resets = 15  # 最大重置次數
        self.is_on_ground = False  # 方塊是否接觸地面

        # T-spin 檢測系統
        self.last_move_was_rotation = False  # 最後一個動作是否為旋轉
        self.t_spin_type = None  # T-spin 類型 ("tspin", "mini", None)

        # Back-to-back 系統
        self.back_to_back_count = 0  # 連續 back-to-back 次數
        self.last_clear_was_difficult = (
            False  # 上次消行是否為困難動作 (Tetris 或 T-spin)
        )

        # 顯示系統
        self.action_text = ""  # 動作文字顯示 ("T-SPIN!", "TETRIS!", "BACK-TO-BACK!")
        self.action_text_timer = 0  # 動作文字顯示計時器

        # Combo 系統
        self.combo_count = 0  # 連續消行次數

        # Perfect Clear (All Clear) 系統
        self.perfect_clear_count = 0  # Perfect Clear 次數

    def fill_bag(self):
        """填充 7-bag 系統的方塊袋"""
        shapes = list(TETROMINO_SHAPES.keys())
        random.shuffle(shapes)  # 隨機排列7種方塊
        self.piece_bag.extend(shapes)

    def spawn_tetromino(self):
        """使用 7-bag 系統生成新的 Tetromino"""
        if not self.piece_bag:  # 如果袋子空了，重新填充
            self.fill_bag()

        shape_type = self.piece_bag.pop(0)  # 取出袋子中的第一個方塊
        return Tetromino(shape_type)

    def hold_piece(self):
        """
        Hold 功能：儲存/交換當前方塊
        """
        if not self.can_hold:
            return False

        if self.hold_tetromino is None:
            # 第一次使用 Hold，儲存當前方塊並生成新方塊
            self.hold_tetromino = Tetromino(self.current_tetromino.shape_type)
            self.current_tetromino = self.next_tetromino
            self.next_tetromino = self.spawn_tetromino()
        else:
            # 交換 Hold 方塊與當前方塊
            temp = self.hold_tetromino
            self.hold_tetromino = Tetromino(self.current_tetromino.shape_type)
            self.current_tetromino = temp
            # 重置位置
            self.current_tetromino.x = GRID_WIDTH // 2 - 2
            self.current_tetromino.y = 0
            self.current_tetromino.rotation = 0

        # 使用 Hold 後需要等到方塊鎖定才能再次使用
        self.can_hold = False
        return True

    def update(self, dt):
        """
        更新遊戲狀態（支援 Lock Delay）
        參數：
        - dt: 時間差（毫秒）
        """
        if self.game_over:
            return

        # 更新動作文字顯示計時器
        if self.action_text_timer > 0:
            self.action_text_timer -= 1
            if self.action_text_timer <= 0:
                self.action_text = ""

        # 更新下落計時器
        self.fall_timer += dt

        # 檢查方塊是否接觸地面
        was_on_ground = self.is_on_ground
        self.is_on_ground = not self.grid.is_valid_position(
            self.current_tetromino, 0, 1
        )

        # 如果剛接觸地面，開始 lock delay
        if self.is_on_ground and not was_on_ground:
            self.lock_delay_timer = 0
            self.lock_delay_resets = 0

        # 檢查是否需要自動下落
        fall_speed = max(50, FALL_SPEED - self.level * 50)  # 隨等級提升速度
        if self.fall_timer >= fall_speed:
            self.fall_timer = 0

            # 嘗試向下移動
            if self.grid.is_valid_position(self.current_tetromino, 0, 1):
                self.current_tetromino.move(0, 1)
                # 自動下落不影響旋轉標記
            else:
                # 方塊接觸地面，開始或繼續 lock delay
                if self.is_on_ground:
                    self.lock_delay_timer += 1

                # 檢查是否應該鎖定方塊
                if (
                    self.lock_delay_timer >= self.lock_delay_max
                    or self.lock_delay_resets >= self.max_lock_resets
                ):
                    self.lock_piece()

    def lock_piece(self):
        """鎖定方塊並處理後續邏輯"""
        # 檢測 T-spin
        t_spin_type = self.check_t_spin()
        is_tspin = t_spin_type is not None

        # Debug: 顯示 T-spin 檢測結果
        if self.current_tetromino.shape_type == "T" and self.last_move_was_rotation:
            print(
                f"T-spin 檢測: {t_spin_type}, 最後動作是旋轉: {self.last_move_was_rotation}"
            )

        # 放置方塊
        self.grid.place_tetromino(self.current_tetromino)

        # 檢查行消除
        lines = self.grid.check_lines()

        # 檢查 Perfect Clear
        is_perfect_clear = self.grid.is_perfect_clear() if lines > 0 else False

        if lines > 0:
            self.lines_cleared += lines
            self.score += self.calculate_score(
                lines, is_tspin, t_spin_type, is_perfect_clear
            )
            self.increase_level()
        elif is_tspin:
            # T-spin 但沒有消行（T-spin 0 lines）
            self.score += self.calculate_score(0, is_tspin, t_spin_type, False)
        else:
            # 沒有消行，重置 combo
            self.combo_count = 0

        # 重置狀態
        self.is_on_ground = False
        self.lock_delay_timer = 0
        self.lock_delay_resets = 0
        self.last_move_was_rotation = False
        self.t_spin_type = None

        # 生成新方塊
        self.current_tetromino = self.next_tetromino
        self.next_tetromino = self.spawn_tetromino()

        # 方塊鎖定後可以再次使用 Hold
        self.can_hold = True

        # 檢查遊戲結束
        if not self.grid.is_valid_position(self.current_tetromino):
            self.game_over = True

    def reset_lock_delay(self):
        """重置 lock delay（在移動或旋轉時調用）"""
        if self.is_on_ground and self.lock_delay_resets < self.max_lock_resets:
            self.lock_delay_timer = 0
            self.lock_delay_resets += 1

    def restart_game(self):
        """重啟遊戲"""
        # 完全重新初始化
        self.__init__()

    def handle_input(self, keys_pressed, keys_just_pressed):
        """
        處理鍵盤輸入（支援 DAS 系統）
        參數：
        - keys_pressed: 當前按下的鍵
        - keys_just_pressed: 剛按下的鍵
        """
        if self.game_over:
            return

        # DAS 水平移動系統
        self.handle_horizontal_movement(keys_pressed, keys_just_pressed)

        # 加速下落
        if keys_pressed[pygame.K_DOWN]:
            if self.grid.is_valid_position(self.current_tetromino, 0, 1):
                self.current_tetromino.move(0, 1)
                self.last_move_was_rotation = False
                self.reset_lock_delay()
                self.score += 1  # 手動下落獲得額外分數

        # 重啟遊戲
        if keys_just_pressed.get(pygame.K_r, False):
            self.restart_game()

        # 順時針旋轉
        if keys_just_pressed.get(pygame.K_UP, False) or keys_just_pressed.get(
            pygame.K_x, False
        ):
            original_rotation = self.current_tetromino.rotation
            new_rotation = (original_rotation + 1) % 4

            # 嘗試直接旋轉
            if self.grid.is_valid_position_at(
                self.current_tetromino.get_rotated_shape(new_rotation),
                self.current_tetromino.x,
                self.current_tetromino.y,
            ):
                # 直接旋轉成功
                self.current_tetromino.rotation = new_rotation
                self.last_move_was_rotation = True
                self.reset_lock_delay()
            else:
                # 嘗試 SRS Wall Kick
                if self.try_wall_kick(original_rotation, new_rotation):
                    self.last_move_was_rotation = True
                    self.reset_lock_delay()
                else:
                    # 旋轉失敗，保持原狀態
                    self.last_move_was_rotation = False

        # 逆時針旋轉
        if keys_just_pressed.get(pygame.K_z, False):
            original_rotation = self.current_tetromino.rotation
            new_rotation = (original_rotation - 1) % 4

            # 嘗試直接旋轉
            if self.grid.is_valid_position_at(
                self.current_tetromino.get_rotated_shape(new_rotation),
                self.current_tetromino.x,
                self.current_tetromino.y,
            ):
                # 直接旋轉成功
                self.current_tetromino.rotation = new_rotation
                self.last_move_was_rotation = True
                self.reset_lock_delay()
            else:
                # 嘗試 SRS Wall Kick
                if self.try_wall_kick(original_rotation, new_rotation):
                    self.last_move_was_rotation = True
                    self.reset_lock_delay()
                else:
                    # 旋轉失敗，保持原狀態
                    self.last_move_was_rotation = False

        # Hold 功能
        if keys_just_pressed.get(pygame.K_c, False) or keys_just_pressed.get(
            pygame.K_LSHIFT, False
        ):
            self.hold_piece()

        # 硬降（Hard Drop）
        if keys_just_pressed.get(pygame.K_SPACE, False):
            drop_distance = 0
            while self.grid.is_valid_position(self.current_tetromino, 0, 1):
                self.current_tetromino.move(0, 1)
                drop_distance += 1

            # 硬降獲得額外分數
            self.score += drop_distance * 2

            # 硬降後立即鎖定方塊
            self.lock_piece()

    def handle_horizontal_movement(self, keys_pressed, keys_just_pressed):
        """
        處理 DAS 水平移動系統
        參數：
        - keys_pressed: 當前按下的鍵
        - keys_just_pressed: 剛按下的鍵
        """
        # 檢查按鍵狀態
        left_pressed = keys_pressed[pygame.K_LEFT]
        right_pressed = keys_pressed[pygame.K_RIGHT]
        left_just_pressed = keys_just_pressed.get(pygame.K_LEFT, False)
        right_just_pressed = keys_just_pressed.get(pygame.K_RIGHT, False)

        # 處理左移
        if left_pressed:
            if left_just_pressed:
                # 剛按下左鍵，立即移動一次
                if self.grid.is_valid_position(self.current_tetromino, -1, 0):
                    self.current_tetromino.move(-1, 0)
                    self.last_move_was_rotation = False
                    self.reset_lock_delay()
                self.das_timer_left = 0
                self.das_active_left = False
            else:
                # 持續按住左鍵
                self.das_timer_left += 1
                if not self.das_active_left:
                    if self.das_timer_left >= self.das_delay:
                        self.das_active_left = True
                        self.das_timer_left = 0
                else:
                    # DAS 已激活，按照 ARR 頻率移動
                    if self.das_timer_left >= self.arr_rate:
                        if self.grid.is_valid_position(self.current_tetromino, -1, 0):
                            self.current_tetromino.move(-1, 0)
                            self.last_move_was_rotation = False
                            self.reset_lock_delay()
                        self.das_timer_left = 0
        else:
            # 沒有按左鍵，重置狀態
            self.das_timer_left = 0
            self.das_active_left = False

        # 處理右移
        if right_pressed:
            if right_just_pressed:
                # 剛按下右鍵，立即移動一次
                if self.grid.is_valid_position(self.current_tetromino, 1, 0):
                    self.current_tetromino.move(1, 0)
                    self.last_move_was_rotation = False
                    self.reset_lock_delay()
                self.das_timer_right = 0
                self.das_active_right = False
            else:
                # 持續按住右鍵
                self.das_timer_right += 1
                if not self.das_active_right:
                    if self.das_timer_right >= self.das_delay:
                        self.das_active_right = True
                        self.das_timer_right = 0
                else:
                    # DAS 已激活，按照 ARR 頻率移動
                    if self.das_timer_right >= self.arr_rate:
                        if self.grid.is_valid_position(self.current_tetromino, 1, 0):
                            self.current_tetromino.move(1, 0)
                            self.last_move_was_rotation = False
                            self.reset_lock_delay()
                        self.das_timer_right = 0
        else:
            # 沒有按右鍵，重置狀態
            self.das_timer_right = 0
            self.das_active_right = False

    def try_wall_kick(self, old_rotation, new_rotation):
        """嘗試踢牆操作（完整 SRS Wall Kick 系統）"""
        # 根據方塊類型選擇對應的 Wall Kick 資料
        if self.current_tetromino.shape_type == "I":
            kick_data_type = "I"
        elif self.current_tetromino.shape_type in ["J", "L", "S", "T", "Z"]:
            kick_data_type = "JLSTZ"
        else:  # O 方塊不需要 Wall Kick
            return False

        # SRS Wall Kick 資料表
        wall_kick_data = {
            "JLSTZ": {
                (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0->R
                (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # R->0
                (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # R->2
                (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 2->R
                (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 2->L
                (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # L->2
                (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # L->0
                (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 0->L
            },
            "I": {
                (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],  # 0->R
                (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],  # R->0
                (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],  # R->2
                (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],  # 2->R
                (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],  # 2->L
                (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],  # L->2
                (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],  # L->0
                (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],  # 0->L
            },
        }

        # 獲取對應的踢牆測試序列
        kick_tests = wall_kick_data[kick_data_type].get(
            (old_rotation, new_rotation), []
        )

        # 嘗試每個踢牆位置
        for kick_x, kick_y in kick_tests:
            test_x = self.current_tetromino.x + kick_x
            test_y = self.current_tetromino.y + kick_y

            # 檢查這個位置是否有效
            if self.grid.is_valid_position_at(
                self.current_tetromino.get_rotated_shape(new_rotation), test_x, test_y
            ):
                # 移動到有效位置
                self.current_tetromino.x = test_x
                self.current_tetromino.y = test_y
                self.current_tetromino.rotation = new_rotation
                return True

        return False

    def check_t_spin(self):
        """
        檢測 T-spin 動作（使用標準 3-corner 規則）
        返回：T-spin 類型 ("tspin", "mini", None)
        """
        # 只有 T 方塊才能進行 T-spin
        if self.current_tetromino.shape_type != "T":
            return None

        # 最後動作必須是旋轉
        if not self.last_move_was_rotation:
            return None

        # 獲取 T 方塊在遊戲網格中的實際中心位置
        # 根據 SRS 標準，T 方塊的中心位置計算
        center_x = self.current_tetromino.x + 1  # T 方塊在 4x4 矩陣中的中心
        center_y = self.current_tetromino.y + 1

        # 檢查 T 方塊周圍的 4 個對角位置
        corners = [
            (center_x - 1, center_y - 1),  # 左上角
            (center_x + 1, center_y - 1),  # 右上角
            (center_x - 1, center_y + 1),  # 左下角
            (center_x + 1, center_y + 1),  # 右下角
        ]

        filled_corners = 0
        for corner_x, corner_y in corners:
            # 檢查是否為牆壁、地板或已放置的方塊
            # 根據標準規則：牆壁和地板也算作被佔用
            if (
                corner_x < 0  # 左牆壁
                or corner_x >= GRID_WIDTH  # 右牆壁
                or corner_y < 0  # 頂部（雖然通常不會發生）
                or corner_y >= GRID_HEIGHT  # 地板
                or (
                    corner_y >= 0
                    and corner_x >= 0
                    and corner_x < GRID_WIDTH
                    and self.grid.grid[corner_y][corner_x] != BLACK
                )  # 已放置的方塊
            ):
                filled_corners += 1

        # Debug 輸出
        print(
            f"T-spin 檢測: 中心位置=({center_x},{center_y}), 被填充的角落={filled_corners}/4, 旋轉={self.last_move_was_rotation}"
        )

        # 需要至少 3 個角落被填充才算 T-spin
        if filled_corners < 3:
            return None

        # 判斷是正常 T-spin 還是 Mini T-spin
        # 根據 T 方塊的朝向檢查前角（指向側）
        rotation = self.current_tetromino.rotation

        if rotation == 0:  # T 朝上
            front_corners = [
                (center_x - 1, center_y - 1),  # 左上
                (center_x + 1, center_y - 1),  # 右上
            ]
        elif rotation == 1:  # T 朝右
            front_corners = [
                (center_x + 1, center_y - 1),  # 右上
                (center_x + 1, center_y + 1),  # 右下
            ]
        elif rotation == 2:  # T 朝下
            front_corners = [
                (center_x - 1, center_y + 1),  # 左下
                (center_x + 1, center_y + 1),  # 右下
            ]
        else:  # rotation == 3, T 朝左
            front_corners = [
                (center_x - 1, center_y - 1),  # 左上
                (center_x - 1, center_y + 1),  # 左下
            ]

        # 檢查前角（指向側）的填充情況
        front_filled = 0
        for corner_x, corner_y in front_corners:
            if (
                corner_x < 0
                or corner_x >= GRID_WIDTH
                or corner_y < 0
                or corner_y >= GRID_HEIGHT
                or (
                    corner_y >= 0
                    and corner_x >= 0
                    and corner_x < GRID_WIDTH
                    and self.grid.grid[corner_y][corner_x] != BLACK
                )
            ):
                front_filled += 1

        # 如果前角（指向側）的兩個角都被填充，則為正常 T-spin
        # 否則為 Mini T-spin
        if front_filled == 2:
            print("檢測到正常 T-spin!")
            return "tspin"
        else:
            print("檢測到 Mini T-spin!")
            return "mini"

    def calculate_score(
        self, lines, is_tspin=False, tspin_type=None, is_perfect_clear=False
    ):
        """
        計算消除行數的分數（Tetris 99 完整算分系統）
        參數：
        - lines: 消除的行數
        - is_tspin: 是否為 T-spin
        - tspin_type: T-spin 類型 ("tspin", "mini")
        - is_perfect_clear: 是否為 Perfect Clear
        返回：分數
        """
        base_score = 0
        action_text = ""
        is_difficult = False  # 是否為困難動作 (Tetris 或 T-spin)

        # Perfect Clear 檢測和算分
        if is_perfect_clear:
            self.perfect_clear_count += 1
            if lines == 1:
                base_score = 800 * self.perfect_clear_count
                action_text = "PERFECT CLEAR SINGLE"
            elif lines == 2:
                base_score = 1200 * self.perfect_clear_count
                action_text = "PERFECT CLEAR DOUBLE"
            elif lines == 3:
                base_score = 1800 * self.perfect_clear_count
                action_text = "PERFECT CLEAR TRIPLE"
            elif lines == 4:
                base_score = 2000 * self.perfect_clear_count
                action_text = "PERFECT CLEAR TETRIS"
                is_difficult = True
            self.combo_count += 1
        elif is_tspin:
            # T-spin 算分
            if tspin_type == "mini":
                if lines == 0:
                    base_score = 100
                    action_text = "MINI T-SPIN"
                elif lines == 1:
                    base_score = 200
                    action_text = "MINI T-SPIN SINGLE"
                    is_difficult = True
                elif lines == 2:
                    base_score = 400
                    action_text = "MINI T-SPIN DOUBLE"
                    is_difficult = True
            else:  # 正常 T-spin
                if lines == 0:
                    base_score = 400
                    action_text = "T-SPIN"
                elif lines == 1:
                    base_score = 800
                    action_text = "T-SPIN SINGLE"
                    is_difficult = True
                elif lines == 2:
                    base_score = 1200
                    action_text = "T-SPIN DOUBLE"
                    is_difficult = True
                elif lines == 3:
                    base_score = 1600
                    action_text = "T-SPIN TRIPLE"
                    is_difficult = True
            self.combo_count += 1
        else:
            # 普通消行算分
            if lines == 1:
                base_score = 100
                action_text = "SINGLE"
                self.combo_count += 1
            elif lines == 2:
                base_score = 300
                action_text = "DOUBLE"
                self.combo_count += 1
            elif lines == 3:
                base_score = 500
                action_text = "TRIPLE"
                self.combo_count += 1
            elif lines == 4:
                base_score = 800
                action_text = "TETRIS"
                is_difficult = True
                self.combo_count += 1
            else:
                # 沒有消行，重置 combo
                self.combo_count = 0

        # Combo 加成
        if self.combo_count > 1:
            combo_bonus = (
                min(self.combo_count - 1, 12) * 50
            )  # Combo 每連續一次 +50 分，最多 12 連
            base_score += combo_bonus
            if lines > 0:
                action_text += f" COMBO x{self.combo_count}"

        # Back-to-back 加成
        multiplier = 1.0
        if is_difficult and self.last_clear_was_difficult:
            self.back_to_back_count += 1
            multiplier = 1.5  # Back-to-back 50% 加成
            action_text = f"BACK-TO-BACK {action_text}"
        elif is_difficult:
            self.back_to_back_count = 1
        else:
            self.back_to_back_count = 0

        # 更新困難動作狀態
        self.last_clear_was_difficult = is_difficult

        # 設定動作文字顯示
        self.action_text = action_text
        self.action_text_timer = 120  # 顯示 2 秒 (120 幀)

        # 計算最終分數
        final_score = int(base_score * multiplier * self.level)
        return final_score

    def increase_level(self):
        """提升遊戲等級和速度"""
        new_level = self.lines_cleared // 10 + 1
        if new_level > self.level:
            self.level = new_level

    def draw_current_tetromino(self, screen):
        """
        繪製當前下落方塊
        參數：
        - screen: pygame 螢幕物件
        """
        blocks = self.current_tetromino.get_blocks()
        for x, y in blocks:
            if y >= 0:  # 只繪製可見區域內的方塊
                screen_x = GRID_X + x * CELL_SIZE
                screen_y = GRID_Y + y * CELL_SIZE
                pygame.draw.rect(
                    screen,
                    self.current_tetromino.color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                )
                pygame.draw.rect(
                    screen, WHITE, (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1
                )

    def draw_ghost_piece(self, screen):
        """
        繪製幽靈方塊（預覽落點）- Tetris 99 風格
        參數：
        - screen: pygame 螢幕物件
        """
        ghost_blocks = self.current_tetromino.get_ghost_blocks(self.grid)

        # 使用半透明填充 + 邊框的方式（類似 Tetris 99）
        ghost_color = self.current_tetromino.color
        ghost_fill_color = tuple(c // 3 for c in ghost_color)  # 降低亮度作為填充色

        for x, y in ghost_blocks:
            if y >= 0:  # 只繪製可見區域內的方塊
                screen_x = GRID_X + x * CELL_SIZE
                screen_y = GRID_Y + y * CELL_SIZE

                # 繪製半透明填充
                pygame.draw.rect(
                    screen,
                    ghost_fill_color,
                    (screen_x + 2, screen_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                )

                # 繪製邊框
                pygame.draw.rect(
                    screen,
                    ghost_color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                    2,  # 邊框寬度
                )

                # 繪製內部點陣效果（更像 Tetris 99）
                for i in range(2):
                    for j in range(2):
                        dot_x = screen_x + 8 + i * 10
                        dot_y = screen_y + 8 + j * 10
                        pygame.draw.rect(screen, ghost_color, (dot_x, dot_y, 2, 2))

    def draw_hold_piece(self, screen, font):
        """
        繪製 Hold 方塊
        參數：
        - screen: pygame 螢幕物件
        - font: 字體物件
        """
        hold_x = 20
        hold_y = 50

        # 繪製 Hold 標題
        hold_text = font.render("HOLD", True, WHITE)
        screen.blit(hold_text, (hold_x, hold_y))

        # 繪製 Hold 方塊框
        hold_box = pygame.Rect(hold_x, hold_y + 30, 120, 80)
        pygame.draw.rect(screen, GRAY, hold_box, 2)

        if self.hold_tetromino:
            # 繪製 Hold 方塊
            shape = self.hold_tetromino.shapes[0]  # 使用初始形狀
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = hold_x + 10 + col_idx * 20
                        y = hold_y + 40 + row_idx * 20
                        pygame.draw.rect(
                            screen, self.hold_tetromino.color, (x, y, 18, 18)
                        )
                        pygame.draw.rect(screen, WHITE, (x, y, 18, 18), 1)

    def draw_next_piece(self, screen, font):
        """
        繪製下一個方塊
        參數：
        - screen: pygame 螢幕物件
        - font: 字體物件
        """
        next_x = 20
        next_y = 250  # 調整位置避免與控制說明重疊

        # 繪製 Next 標題
        next_text = font.render("NEXT", True, WHITE)
        screen.blit(next_text, (next_x, next_y))

        # 繪製 Next 方塊框
        next_box = pygame.Rect(next_x, next_y + 30, 120, 80)
        pygame.draw.rect(screen, GRAY, next_box, 2)

        if self.next_tetromino:
            # 繪製 Next 方塊
            shape = self.next_tetromino.shapes[0]  # 使用初始形狀
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = next_x + 10 + col_idx * 20
                        y = next_y + 40 + row_idx * 20
                        pygame.draw.rect(
                            screen, self.next_tetromino.color, (x, y, 18, 18)
                        )
                        pygame.draw.rect(screen, WHITE, (x, y, 18, 18), 1)

    def draw_info(self, screen, font):
        """
        顯示遊戲資訊
        參數：
        - screen: pygame 螢幕物件
        - font: 字體物件
        """
        info_x = GRID_X + GRID_WIDTH * CELL_SIZE + 20

        # 分數
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (info_x, 50))

        # 等級
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (info_x, 80))

        # 已消除行數
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (info_x, 110))

        # 控制說明
        controls = [
            "Controls:",
            "←→: Move (DAS)",
            "↓: Soft Drop",
            "X/↑: Rotate CW",
            "Z: Rotate CCW",
            "Space: Hard Drop",
            "C/Shift: Hold",
            "R: Restart",
            "",
            "Features:",
            "• SRS Rotation",
            "• 7-bag System",
            "• Ghost Piece",
            "• Hold Function",
            "• T-Spin Detection",
            "• Perfect Clear",
            "• Combo System",
            "• Back-to-Back",
        ]

        for i, control in enumerate(controls):
            # 使用較小的字體間距和適當的顏色
            if control == "":
                continue  # 跳過空行
            elif control.startswith("•"):
                # 功能說明使用較小的字體
                small_font = pygame.font.Font(None, 20)
                control_text = small_font.render(control, True, CYAN)
                screen.blit(control_text, (info_x, 150 + i * 22))
            elif control in ["Controls:", "Features:"]:
                # 標題使用白色
                control_text = font.render(control, True, WHITE)
                screen.blit(control_text, (info_x, 150 + i * 22))
            else:
                # 普通控制說明
                control_text = font.render(control, True, LIGHT_GRAY)
                screen.blit(control_text, (info_x, 150 + i * 22))

        # Back-to-back 顯示
        if self.back_to_back_count > 0:
            b2b_text = font.render(
                f"Back-to-Back: {self.back_to_back_count}", True, YELLOW
            )
            screen.blit(b2b_text, (info_x, 480))

        # Combo 顯示
        if self.combo_count > 1:
            combo_text = font.render(f"Combo: {self.combo_count}x", True, GREEN)
            screen.blit(combo_text, (info_x, 505))

        # Perfect Clear 計數顯示
        if self.perfect_clear_count > 0:
            pc_text = font.render(
                f"Perfect Clear: {self.perfect_clear_count}", True, CYAN
            )
            screen.blit(pc_text, (info_x, 530))

        # 動作文字顯示 (T-SPIN!, TETRIS!, etc.)
        if self.action_text and self.action_text_timer > 0:
            # 計算閃爍效果
            alpha = min(255, self.action_text_timer * 4)
            if self.action_text_timer % 10 < 5:  # 閃爍效果
                action_color = RED if "T-SPIN" in self.action_text else YELLOW
                action_font = pygame.font.Font(None, 32)
                action_surface = action_font.render(
                    self.action_text, True, action_color
                )
                screen.blit(action_surface, (info_x, 555))

        # Lock Delay 指示器（調試用）
        if self.is_on_ground:
            lock_progress = self.lock_delay_timer / self.lock_delay_max
            pygame.draw.rect(screen, GRAY, (info_x, 580, 100, 10))
            pygame.draw.rect(screen, RED, (info_x, 580, int(100 * lock_progress), 10))

        # 遊戲結束提示
        if self.game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(game_over_text, (info_x, 400))
            screen.blit(restart_text, (info_x, 430))


# ============================
# 遊戲初始化區塊
# ============================

# 初始化 Pygame
pygame.init()

# 設定視窗大小
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# 設定視窗標題
pygame.display.set_caption("俄羅斯方塊 Tetris")

# 建立時鐘物件控制幀率
clock = pygame.time.Clock()

# 建立字體物件
font = pygame.font.Font(None, 36)

# 建立遊戲物件
game = Game()

# 鍵盤狀態追蹤
keys_pressed = pygame.key.get_pressed()
keys_just_pressed = {}  # 改為字典以避免索引錯誤

# ============================
# 遊戲主迴圈區塊
# ============================

while True:
    # 計算時間差
    dt = clock.tick(FPS)

    # ============================
    # 事件處理區塊
    # ============================

    # 重置剛按下的鍵
    keys_just_pressed = {}

    for event in pygame.event.get():
        # 處理視窗關閉事件
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 處理鍵盤按下事件
        elif event.type == pygame.KEYDOWN:
            keys_just_pressed[event.key] = True

            # 重新開始遊戲
            if event.key == pygame.K_r and game.game_over:
                game = Game()  # 更新鍵盤狀態
    keys_pressed = pygame.key.get_pressed()

    # ============================
    # 遊戲邏輯更新區塊
    # ============================

    # 更新遊戲狀態
    game.update(dt)

    # 處理鍵盤輸入
    game.handle_input(keys_pressed, keys_just_pressed)

    # ============================
    # 畫面渲染區塊
    # ============================

    # 清除畫面背景（填充黑色）
    screen.fill(BLACK)

    # 繪製遊戲區域和已放置的方塊
    game.grid.draw(screen)

    # 繪製幽靈方塊（預覽落點）
    if not game.game_over:
        game.draw_ghost_piece(screen)

    # 繪製當前下落方塊
    if not game.game_over:
        game.draw_current_tetromino(screen)

    # 繪製 Hold 方塊
    game.draw_hold_piece(screen, font)

    # 繪製 Next 方塊
    game.draw_next_piece(screen, font)

    # 顯示遊戲資訊
    game.draw_info(screen, font)

    # 更新螢幕顯示
    pygame.display.flip()

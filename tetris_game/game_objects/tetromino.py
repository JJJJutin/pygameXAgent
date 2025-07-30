"""
Tetromino 四格方塊物件類別
定義俄羅斯方塊的形狀、旋轉、移動等行為
"""

from config.constants import GRID_WIDTH, TETROMINO_COLORS
from config.shapes import TETROMINO_SHAPES, SHAPE_COLORS


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

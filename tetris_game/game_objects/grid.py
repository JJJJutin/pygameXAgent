"""
遊戲區域物件類別
管理遊戲網格、方塊放置、行消除等邏輯
"""

import pygame
from config.constants import (
    BLACK,
    WHITE,
    CELL_SIZE,
    GRID_X,
    GRID_Y,
    GRID_WIDTH,
    GRID_HEIGHT,
    GRID_COLOR,
)


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

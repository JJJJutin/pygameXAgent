"""
T-Spin 直接測試腳本
直接測試T-Spin檢測邏輯，不依賴複雜的網格設置
"""

from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import BLACK, PURPLE


def test_t_spin_detection_directly():
    """直接測試T-Spin檢測邏輯"""
    print("=== 直接T-Spin檢測測試 ===")

    game = Game()

    # 手動設置一個簡單的T-Spin場景
    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置T方塊在位置 (4, 10)，rotation = 0 (朝上)
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 4
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0
    game.last_move_was_rotation = True

    # T方塊中心在 (5, 11)
    # 四個角落位置：
    # (4, 10) - 左上
    # (6, 10) - 右上
    # (4, 12) - 左下
    # (6, 12) - 右下

    print("測試案例1: 3個角落被佔用（正常T-Spin）")
    # 設置3個角落被佔用（左上、右上、左下）
    game.grid.grid[10][4] = PURPLE  # 左上
    game.grid.grid[10][6] = PURPLE  # 右上
    game.grid.grid[12][4] = PURPLE  # 左下
    # 右下角保持空

    result = game.check_t_spin()
    print(f"結果: {result} (期望: tspin，因為前角都被佔用)")

    print("\n測試案例2: 3個角落被佔用（Mini T-Spin）")
    # 清空重新設置
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置3個角落被佔用（右上、左下、右下 - 前角只有一個）
    game.grid.grid[10][6] = PURPLE  # 右上（前角）
    game.grid.grid[12][4] = PURPLE  # 左下（後角）
    game.grid.grid[12][6] = PURPLE  # 右下（後角）
    # 左上角保持空

    result = game.check_t_spin()
    print(f"結果: {result} (期望: mini，因為前角只有一個被佔用)")

    print("\n測試案例3: 只有2個角落被佔用（不是T-Spin）")
    # 清空重新設置
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置2個角落被佔用
    game.grid.grid[10][4] = PURPLE  # 左上
    game.grid.grid[10][6] = PURPLE  # 右上

    result = game.check_t_spin()
    print(f"結果: {result} (期望: None，因為少於3個角落)")

    print("\n測試案例4: 使用牆壁/地板作為角落")
    # 測試在邊界的T-Spin - 真正貼牆的情況
    game.current_tetromino.x = -1  # 讓T方塊部分超出左邊界
    game.current_tetromino.y = 18  # 接近底部

    # 清空重新設置
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # T方塊中心在 (0, 19)
    # 四個角落位置：
    # (-1, 18) - 左上 (牆壁)
    # (1, 18) - 右上
    # (-1, 20) - 左下 (牆壁+地板)
    # (1, 20) - 右下 (地板)

    # 設置右上角被佔用
    game.grid.grid[18][1] = PURPLE

    print(f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(
        f"T方塊中心: ({game.current_tetromino.x + 1}, {game.current_tetromino.y + 1})"
    )
    print("角落位置和狀態:")
    center_x = game.current_tetromino.x + 1
    center_y = game.current_tetromino.y + 1
    corners = [
        (center_x - 1, center_y - 1),  # 左上角
        (center_x + 1, center_y - 1),  # 右上角
        (center_x - 1, center_y + 1),  # 左下角
        (center_x + 1, center_y + 1),  # 右下角
    ]

    for i, (cx, cy) in enumerate(corners):
        corner_names = ["左上", "右上", "左下", "右下"]
        is_wall = cx < 0 or cx >= 10
        is_floor = cy >= 20
        is_block = 0 <= cx < 10 and 0 <= cy < 20 and game.grid.grid[cy][cx] != BLACK
        print(
            f"  {corner_names[i]} ({cx}, {cy}): 牆壁={is_wall}, 地板={is_floor}, 方塊={is_block}"
        )

    result = game.check_t_spin()
    print(f"結果: {result} (期望: tspin，因為牆壁和地板算作佔用)")


def test_score_system():
    """測試分數系統"""
    print("\n=== 分數系統測試 ===")

    game = Game()
    game.level = 1

    test_cases = [
        (0, True, "tspin", False, "T-SPIN (0 lines)"),
        (1, True, "tspin", False, "T-SPIN SINGLE"),
        (2, True, "tspin", False, "T-SPIN DOUBLE"),
        (3, True, "tspin", False, "T-SPIN TRIPLE"),
        (0, True, "mini", False, "T-SPIN MINI (0 lines)"),
        (1, True, "mini", False, "T-SPIN MINI SINGLE"),
        (2, True, "mini", False, "T-SPIN MINI DOUBLE"),
        (4, False, None, False, "TETRIS"),
    ]

    for lines, is_tspin, tspin_type, is_perfect_clear, description in test_cases:
        # 重置遊戲狀態
        game.last_clear_was_difficult = False
        game.back_to_back_count = 0
        game.combo_count = 0

        score = game.calculate_score(lines, is_tspin, tspin_type, is_perfect_clear)
        print(f"{description}: {score} 分")

    print("\n=== Back-to-Back測試 ===")
    # 測試Back-to-back
    game.last_clear_was_difficult = False
    game.back_to_back_count = 0

    score1 = game.calculate_score(2, True, "tspin", False)  # T-SPIN DOUBLE
    print(f"第一個T-SPIN DOUBLE: {score1} 分")

    score2 = game.calculate_score(2, True, "tspin", False)  # 第二個T-SPIN DOUBLE (B2B)
    print(f"Back-to-Back T-SPIN DOUBLE: {score2} 分 (應該是 {int(1200 * 1.5)} 分)")


if __name__ == "__main__":
    test_t_spin_detection_directly()
    test_score_system()

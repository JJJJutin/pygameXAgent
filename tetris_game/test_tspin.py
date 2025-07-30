"""
T-Spin 系統測試腳本
測試各種T-Spin情況的檢測和分數計算
"""

from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import BLACK, PURPLE


def setup_t_spin_scenario(game, grid_state, t_pos, t_rotation):
    """
    設置T-Spin測試場景

    參數:
    - game: Game實例
    - grid_state: 網格狀態（列表的列表，1表示佔用，0表示空）
    - t_pos: T方塊位置 (x, y)
    - t_rotation: T方塊旋轉狀態
    """
    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置網格狀態
    for y, row in enumerate(grid_state):
        for x, cell in enumerate(row):
            if cell == 1:
                game.grid.grid[y][x] = PURPLE  # 使用紫色表示障礙物

    # 設置T方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = t_pos[0]
    game.current_tetromino.y = t_pos[1]
    game.current_tetromino.rotation = t_rotation
    game.last_move_was_rotation = True


def test_t_spin_single():
    """測試標準T-Spin Single"""
    print("=== 測試 T-Spin Single ===")
    game = Game()

    # 創建T-Spin Single設置 - 使用更簡單的設置
    grid_state = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
        [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],  # 3 - T的上方，左上右上佔用
        [1, 1, 0, 0, 0, 1, 1, 1, 1, 1],  # 4 - 要被清除的行
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 5 - 左下右下佔用
    ]

    setup_t_spin_scenario(game, grid_state, (1, 2), 0)  # T在位置(1,2)朝上

    result = game.check_t_spin()
    print(f"T-Spin檢測結果: {result}")
    print(f"期望結果: tspin")
    print()


def test_mini_t_spin():
    """測試Mini T-Spin"""
    print("=== 測試 Mini T-Spin ===")
    game = Game()

    # 創建Mini T-Spin設置（只有後角被佔用）
    grid_state = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 2
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1],  # 3 - 只右上角佔用
        [1, 1, 0, 0, 0, 1, 1, 1, 1, 1],  # 4 - 要被清除的行
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 5 - 左下右下佔用
    ]

    setup_t_spin_scenario(game, grid_state, (1, 2), 0)  # T在位置(1,2)朝上

    result = game.check_t_spin()
    print(f"T-Spin檢測結果: {result}")
    print(f"期望結果: mini")
    print()


def test_score_calculation():
    """測試分數計算"""
    print("=== 測試分數計算 ===")
    game = Game()

    # 測試各種T-Spin分數
    test_cases = [
        (0, True, "tspin", "T-SPIN (0 lines)"),
        (1, True, "tspin", "T-SPIN SINGLE"),
        (2, True, "tspin", "T-SPIN DOUBLE"),
        (3, True, "tspin", "T-SPIN TRIPLE"),
        (0, True, "mini", "T-SPIN MINI (0 lines)"),
        (1, True, "mini", "T-SPIN MINI SINGLE"),
        (2, True, "mini", "T-SPIN MINI DOUBLE"),
    ]

    for lines, is_tspin, tspin_type, description in test_cases:
        game.level = 1  # 重置等級
        game.last_clear_was_difficult = False  # 重置B2B
        score = game.calculate_score(lines, is_tspin, tspin_type, False)
        print(f"{description}: {score} 分")

    print()


def run_all_tests():
    """執行所有測試"""
    print("T-Spin 系統測試開始")
    print("=" * 50)

    test_t_spin_single()
    test_mini_t_spin()
    test_score_calculation()

    print("測試完成！")


if __name__ == "__main__":
    run_all_tests()

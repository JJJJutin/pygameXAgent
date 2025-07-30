"""
模擬用戶遇到的T-Spin Wall Kick問題
根據用戶提供的圖片，模擬具體的遊戲情況
"""

from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import *


def simulate_user_scenario():
    """模擬用戶遇到的具體情況"""
    print("=== 模擬用戶T-Spin Wall Kick問題 ===")

    game = Game()

    # 根據用戶圖片，設置類似的遊戲狀態
    # 圖片顯示有一個複雜的方塊堆疊，底部有很多不同顏色的方塊

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 根據圖片模擬底部的方塊堆疊
    # 底部幾行有不同顏色的方塊
    patterns = [
        # 最底行 (19)
        [CYAN, CYAN, BLUE, BLUE, PURPLE, PURPLE, BLACK, ORANGE, ORANGE, CYAN],
        # 第二行 (18)
        [CYAN, RED, RED, BLUE, PURPLE, ORANGE, ORANGE, ORANGE, RED, CYAN],
        # 第三行 (17)
        [CYAN, BLUE, BLUE, BLUE, GREEN, GREEN, BLACK, RED, RED, CYAN],
        # 第四行 (16)
        [YELLOW, YELLOW, PURPLE, PURPLE, BLACK, GREEN, GREEN, YELLOW, PURPLE, PURPLE],
        # 第五行 (15)
        [YELLOW, YELLOW, PURPLE, PURPLE, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
        # 第六行 (14)
        [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
    ]

    # 填充底部模式
    for i, pattern in enumerate(patterns):
        row = 19 - i
        if row >= 0:
            for x, color in enumerate(pattern):
                if x < len(game.grid.grid[row]):
                    game.grid.grid[row][x] = color

    # 設置T方塊在可能導致問題的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 5  # 在中間偏右的位置
    game.current_tetromino.y = 13  # 在堆疊上方
    game.current_tetromino.rotation = 0  # 朝上

    print(f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"T方塊旋轉: {game.current_tetromino.rotation}")

    # 顯示當前網格狀態（重點區域）
    print("\n=== 網格狀態 (重點區域) ===")
    for y in range(10, 20):
        line = f"{y:2d}: "
        for x in range(10):
            if game.grid.grid[y][x] == BLACK:
                line += "."
            else:
                line += "#"
        print(line)

    # 顯示T方塊當前位置
    print(f"\nT方塊在網格中的位置 (rotation {game.current_tetromino.rotation}):")
    current_shape = game.current_tetromino.get_current_shape()
    for row_idx, row in enumerate(current_shape):
        for col_idx, cell in enumerate(row):
            if cell:
                world_x = game.current_tetromino.x + col_idx
                world_y = game.current_tetromino.y + row_idx
                print(f"  方塊格子在 ({world_x}, {world_y})")

    # 測試各種旋轉
    rotations_to_test = [1, 2, 3]  # 測試所有可能的目標旋轉

    for target_rotation in rotations_to_test:
        print(
            f"\n=== 測試旋轉 {game.current_tetromino.rotation} -> {target_rotation} ==="
        )

        # 檢查直接旋轉
        target_shape = game.current_tetromino.get_rotated_shape(target_rotation)
        direct_valid = game.grid.is_valid_position_at(
            target_shape, game.current_tetromino.x, game.current_tetromino.y
        )

        print(f"直接旋轉可行: {direct_valid}")

        if not direct_valid:
            print("嘗試Wall Kick...")

            # 保存原始狀態
            original_x = game.current_tetromino.x
            original_y = game.current_tetromino.y
            original_rotation = game.current_tetromino.rotation

            # 嘗試wall kick
            success = game.try_wall_kick(original_rotation, target_rotation)

            print(f"Wall Kick結果: {success}")

            if success:
                print(
                    f"  成功位置: ({game.current_tetromino.x}, {game.current_tetromino.y})"
                )
                print(
                    f"  使用kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
                )

                # 檢查是否是T-Spin
                if game.current_tetromino.shape_type == "T":
                    game.last_move_was_rotation = True
                    t_spin_result = game.check_t_spin()
                    if t_spin_result:
                        print(f"  ✅ 這是一個 {t_spin_result.upper()}!")
                    else:
                        print("  ❌ 不是T-Spin")

                # 恢復原始狀態以測試下一個旋轉
                game.current_tetromino.x = original_x
                game.current_tetromino.y = original_y
                game.current_tetromino.rotation = original_rotation
            else:
                print("  所有Wall Kick都失敗")
        else:
            print("直接旋轉成功，不需要Wall Kick")


def test_specific_tspin_wallkick():
    """測試特定的T-Spin Wall Kick場景"""
    print("\n\n=== 特定T-Spin Wall Kick場景測試 ===")

    game = Game()

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 創建一個經典的T-Spin Triple設置
    # 這個設置需要wall kick才能完成T-Spin

    # 填充底部，留出T-Spin洞
    for x in range(10):
        if x != 0:  # 在左側留出T-Spin洞
            game.grid.grid[19][x] = PURPLE
            game.grid.grid[18][x] = PURPLE
            game.grid.grid[17][x] = PURPLE

    # 設置T-Spin所需的角落方塊
    game.grid.grid[16][1] = PURPLE  # 左上角
    game.grid.grid[16][2] = PURPLE  # 右上角（T-Spin洞的）
    game.grid.grid[18][1] = PURPLE  # 左下角
    # 右下角 (19,1) 故意留空

    # 設置T方塊在需要wall kick的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 0
    game.current_tetromino.y = 15
    game.current_tetromino.rotation = 2  # 朝下狀態

    print(f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"T方塊旋轉: {game.current_tetromino.rotation} (朝下)")

    # 顯示設置
    print("\n=== T-Spin場景網格 ===")
    for y in range(14, 20):
        line = f"{y:2d}: "
        for x in range(6):
            if game.grid.grid[y][x] == BLACK:
                line += "."
            else:
                line += "#"
        print(line)

    # 嘗試旋轉到朝左 (rotation 3)
    target_rotation = 3
    print(f"\n嘗試T-Spin旋轉: {game.current_tetromino.rotation} -> {target_rotation}")

    # 檢查直接旋轉
    target_shape = game.current_tetromino.get_rotated_shape(target_rotation)
    direct_valid = game.grid.is_valid_position_at(
        target_shape, game.current_tetromino.x, game.current_tetromino.y
    )

    print(f"直接旋轉可行: {direct_valid}")

    if not direct_valid:
        print("需要Wall Kick，開始測試...")
        success = game.try_wall_kick(game.current_tetromino.rotation, target_rotation)

        print(f"Wall Kick結果: {success}")

        if success:
            print(f"成功位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
            print(
                f"使用kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
            )

            # 檢查T-Spin
            game.last_move_was_rotation = True
            t_spin_result = game.check_t_spin()
            if t_spin_result:
                print(f"✅ 檢測到 {t_spin_result.upper()}!")
            else:
                print("❌ 未檢測到T-Spin")
        else:
            print("❌ Wall Kick失敗")


if __name__ == "__main__":
    simulate_user_scenario()
    test_specific_tspin_wallkick()

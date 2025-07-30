#!/usr/bin/env python3
"""
專門測試會導致 wall kick 失敗的場景
創建真正需要 wall kick 且可能失敗的情況
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from config.shapes import WALL_KICK_DATA
from game_objects.tetromino import Tetromino


def debug_wall_kick_process(game, old_rotation, new_rotation):
    """詳細debug wall kick過程"""
    print(f"\n🔍 詳細分析 Wall Kick 過程:")
    print(f"旋轉: {old_rotation} -> {new_rotation}")

    # 獲取kick測試序列
    kick_data_type = "JLSTZ"  # T方塊使用JLSTZ
    kick_tests = WALL_KICK_DATA[kick_data_type].get((old_rotation, new_rotation), [])
    print(f"Kick測試序列: {kick_tests}")

    # 獲取旋轉後的形狀
    rotated_shape = game.current_tetromino.get_rotated_shape(new_rotation)
    print(f"旋轉後形狀:")
    for row in rotated_shape:
        print(f"  {''.join('■' if cell else '.' for cell in row)}")

    # 逐個測試每個kick
    for kick_index, (kick_x, kick_y) in enumerate(kick_tests):
        test_x = game.current_tetromino.x + kick_x
        test_y = game.current_tetromino.y + kick_y

        print(f"\n測試 Kick {kick_index}: 偏移({kick_x}, {kick_y})")
        print(f"測試位置: ({test_x}, {test_y})")

        # 檢查這個位置是否有效
        is_valid = game.grid.is_valid_position_at(rotated_shape, test_x, test_y)
        print(f"位置有效性: {'✅ 有效' if is_valid else '❌ 無效'}")

        if not is_valid:
            # 詳細分析為什麼無效
            print("無效原因分析:")
            for row_idx, row in enumerate(rotated_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        check_x = test_x + col_idx
                        check_y = test_y + row_idx

                        if check_x < 0:
                            print(f"  方塊({check_x}, {check_y}): ❌ 超出左邊界")
                        elif check_x >= GRID_WIDTH:
                            print(f"  方塊({check_x}, {check_y}): ❌ 超出右邊界")
                        elif check_y >= GRID_HEIGHT:
                            print(f"  方塊({check_x}, {check_y}): ❌ 超出下邊界")
                        elif check_y >= 0 and game.grid.grid[check_y][check_x] != BLACK:
                            print(f"  方塊({check_x}, {check_y}): ❌ 與已放置方塊重疊")
                        else:
                            print(f"  方塊({check_x}, {check_y}): ✅ 位置OK")
        else:
            print("✅ 這個kick可以成功!")
            break


def create_real_wallkick_failure_scenario():
    """創建真正會導致wall kick失敗的場景"""
    print("=== 真正的 Wall Kick 失敗場景 ===")

    game = Game()
    grid = game.grid.grid

    # 創建一個T方塊被完全包圍，無法wall kick的情況
    # 這模擬了一個非常緊密的空間

    setup = [
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "####.#####",  # 行13 - 只留一個很小的洞
        "####.#####",  # 行14
        "####.#####",  # 行15
        "####.#####",  # 行16
        "####.#####",  # 行17
        "####.#####",  # 行18
        "##########",  # 行19 - 底部完全封死
    ]

    for row_idx, row_pattern in enumerate(setup):
        row = 10 + row_idx
        for col, char in enumerate(row_pattern):
            if char == "#":
                grid[row][col] = WHITE

    # 將T方塊放在那個小洞裡，旋轉時會碰到周圍的方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 3  # 在洞的左邊
    game.current_tetromino.y = 11  # 在洞的上方
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_detailed_game_state(game)

    # 嘗試旋轉
    print("\n嘗試順時鐘旋轉...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    # 檢查直接旋轉
    original_rotation = game.current_tetromino.rotation
    game.current_tetromino.rotation = new_rotation
    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗")
        game.current_tetromino.rotation = original_rotation

        # 使用詳細debug來分析wall kick
        debug_wall_kick_process(game, old_rotation, new_rotation)

        # 嘗試wall kick
        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"\n✅ Wall kick 最終成功! 使用kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("\n❌ Wall kick 最終失敗!")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_detailed_game_state(game)

    return game


def create_edge_case_scenario():
    """創建邊緣情況：T方塊在牆邊且底下有方塊"""
    print("\n=== 邊緣情況：牆邊+底部有方塊 ===")

    game = Game()
    grid = game.grid.grid

    # 在右牆邊創建一個需要wall kick的情況
    setup = [
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "..........",  # 行13
        "..........",  # 行14
        "..........",  # 行15
        "........##",  # 行16 - 右邊有方塊
        "........##",  # 行17
        "........##",  # 行18
        "##########",  # 行19 - 底部全滿
    ]

    for row_idx, row_pattern in enumerate(setup):
        row = 10 + row_idx
        for col, char in enumerate(row_pattern):
            if char == "#":
                grid[row][col] = WHITE

    # T方塊放在右邊，旋轉時會撞牆
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 7  # 靠近右邊
    game.current_tetromino.y = 13
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_detailed_game_state(game)

    # 嘗試順時鐘旋轉
    print("\n嘗試順時鐘旋轉...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    original_rotation = game.current_tetromino.rotation
    game.current_tetromino.rotation = new_rotation
    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗")
        game.current_tetromino.rotation = original_rotation

        debug_wall_kick_process(game, old_rotation, new_rotation)

        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"\n✅ Wall kick 成功! 使用kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("\n❌ Wall kick 失敗!")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_detailed_game_state(game)

    return game


def print_detailed_game_state(game):
    """打印詳細的遊戲狀態"""
    grid = game.grid.grid
    tetromino = game.current_tetromino

    # 獲取當前方塊的佔用位置
    tetromino_blocks = set()
    if tetromino:
        blocks = tetromino.get_blocks()
        tetromino_blocks = set(blocks)

    print(f"T方塊位置: ({tetromino.x}, {tetromino.y}), 旋轉: {tetromino.rotation}")
    print("遊戲區域 (T=T方塊, #=已放置方塊, .=空白):")
    print("  0123456789")

    for row in range(10, 20):
        line = f"{row:2d}"
        for col in range(10):
            if (col, row) in tetromino_blocks:
                line += "T"
            elif grid[row][col] != BLACK:
                line += "#"
            else:
                line += "."
        print(line)


if __name__ == "__main__":
    pygame.init()

    print("🔧 專門測試 Wall Kick 失敗場景")
    print("=" * 60)

    try:
        # 執行失敗場景測試
        game1 = create_real_wallkick_failure_scenario()
        game2 = create_edge_case_scenario()

        print("\n" + "=" * 60)
        print("📊 結論:")
        print("如果以上場景中 Wall Kick 都成功了，")
        print("那麼問題可能在於：")
        print("1. 特定的場景設置沒有被正確模擬")
        print("2. 問題出現在遊戲的其他部分（如輸入處理、時機等）")
        print("3. Wall Kick 系統本身是正常的")

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

#!/usr/bin/env python3
"""
終極測試：強制 wall kick 失敗並分析問題
專門創建無法進行任何 wall kick 的情況
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from config.shapes import WALL_KICK_DATA
from game_objects.tetromino import Tetromino


def create_no_space_scenario():
    """創建完全沒有空間進行wall kick的情況"""
    print("=== 完全沒有空間的場景 ===")

    game = Game()
    grid = game.grid.grid

    # 創建一個T方塊被完全包圍的情況
    # 四周都是方塊，任何wall kick都不可能成功

    setup = [
        "..........",  # 行8
        "..........",  # 行9
        "##########",  # 行10 - 上面封死
        "#........#",  # 行11 - 兩邊封死
        "#........#",  # 行12
        "#..####..#",  # 行13 - 中間有障礙
        "#..####..#",  # 行14
        "#..####..#",  # 行15
        "#..####..#",  # 行16
        "##########",  # 行17 - 底部封死
    ]

    for row_idx, row_pattern in enumerate(setup):
        row = 8 + row_idx
        if row < GRID_HEIGHT:
            for col, char in enumerate(row_pattern):
                if char == "#":
                    grid[row][col] = WHITE

    # 將T方塊放在一個很小的空間裡
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1  # 在左邊的小空間
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_game_state_extended(game)

    # 嘗試旋轉
    print("\n嘗試順時鐘旋轉 (這應該會失敗)...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    # 檢查直接旋轉
    original_rotation = game.current_tetromino.rotation
    game.current_tetromino.rotation = new_rotation
    direct_rotation_valid = game.grid.is_valid_position(game.current_tetromino)

    if direct_rotation_valid:
        print("✅ 直接旋轉成功（意外！）")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗（如預期）")
        game.current_tetromino.rotation = original_rotation

        # 詳細分析wall kick過程
        print("\n🔍 詳細分析 Wall Kick 嘗試過程:")
        kick_data_type = "JLSTZ"
        kick_tests = WALL_KICK_DATA[kick_data_type].get(
            (old_rotation, new_rotation), []
        )
        print(f"Kick測試序列: {kick_tests}")

        rotated_shape = game.current_tetromino.get_rotated_shape(new_rotation)

        any_kick_successful = False
        for kick_index, (kick_x, kick_y) in enumerate(kick_tests):
            test_x = game.current_tetromino.x + kick_x
            test_y = game.current_tetromino.y + kick_y

            print(
                f"\nKick {kick_index}: 偏移({kick_x}, {kick_y}) -> 位置({test_x}, {test_y})"
            )

            is_valid = game.grid.is_valid_position_at(rotated_shape, test_x, test_y)
            print(f"結果: {'✅ 成功' if is_valid else '❌ 失敗'}")

            if not is_valid:
                # 分析失敗原因
                conflict_reasons = []
                for row_idx, row in enumerate(rotated_shape):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            check_x = test_x + col_idx
                            check_y = test_y + row_idx

                            if check_x < 0:
                                conflict_reasons.append(
                                    f"左邊界衝突 ({check_x}, {check_y})"
                                )
                            elif check_x >= GRID_WIDTH:
                                conflict_reasons.append(
                                    f"右邊界衝突 ({check_x}, {check_y})"
                                )
                            elif check_y >= GRID_HEIGHT:
                                conflict_reasons.append(
                                    f"下邊界衝突 ({check_x}, {check_y})"
                                )
                            elif (
                                check_y >= 0
                                and game.grid.grid[check_y][check_x] != BLACK
                            ):
                                conflict_reasons.append(
                                    f"方塊衝突 ({check_x}, {check_y})"
                                )

                if conflict_reasons:
                    print(
                        f"衝突原因: {', '.join(conflict_reasons[:3])}{'...' if len(conflict_reasons) > 3 else ''}"
                    )
            else:
                any_kick_successful = True
                break

        if any_kick_successful:
            print(f"\n✅ 找到可用的 Wall Kick!")
        else:
            print(f"\n❌ 所有 Wall Kick 都失敗了!")

        # 嘗試實際的wall kick
        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"✅ try_wall_kick() 返回成功! 使用kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("❌ try_wall_kick() 返回失敗!")
            game.last_move_was_rotation = False

    print("\n最終狀態：")
    print_game_state_extended(game)

    return game


def test_specific_user_scenario():
    """
    嘗試模擬用戶可能遇到的具體場景
    基於常見的T-spin設置
    """
    print("\n=== 模擬用戶場景：T-spin DT Cannon ===")

    game = Game()

    # 設置一個真實的T-spin DT cannon的殘局
    # 這是一個常見的T-spin設置，玩家可能會遇到wall kick問題

    grid_pattern = [
        "..........",  # 行0
        "..........",  # 行1
        "..........",  # 行2
        "..........",  # 行3
        "..........",  # 行4
        "..........",  # 行5
        "..........",  # 行6
        "..........",  # 行7
        "..........",  # 行8
        "..........",  # 行9
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "..........",  # 行13
        "..........",  # 行14
        "..........",  # 行15
        "###.....##",  # 行16 - DT cannon的典型設置
        "###.....##",  # 行17
        "###.....##",  # 行18
        "###.....##",  # 行19
    ]

    # 應用網格設置
    for row_idx, pattern in enumerate(grid_pattern):
        if row_idx < len(game.grid.grid):
            for col_idx, char in enumerate(pattern):
                if char == "#":
                    game.grid.grid[row_idx][col_idx] = WHITE

    # 將T方塊放在需要wall kick的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 2  # 在左側結構旁邊
    game.current_tetromino.y = 14
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態 (DT Cannon設置)：")
    print_game_state_extended(game)

    # 嘗試各種旋轉
    rotations_to_try = [
        (0, 1, "順時鐘 (0->1)"),
        (0, 3, "逆時鐘 (0->3)"),
        (1, 2, "順時鐘 (1->2)"),
        (2, 3, "順時鐘 (2->3)"),
    ]

    for old_rot, new_rot, description in rotations_to_try:
        print(f"\n--- 測試 {description} ---")

        # 重置方塊狀態
        game.current_tetromino.x = 2
        game.current_tetromino.y = 14
        game.current_tetromino.rotation = old_rot

        # 嘗試旋轉
        original_rotation = game.current_tetromino.rotation
        game.current_tetromino.rotation = new_rot

        if game.grid.is_valid_position(game.current_tetromino):
            print(f"✅ 直接旋轉成功")
        else:
            print(f"❌ 直接旋轉失敗，嘗試 wall kick...")
            game.current_tetromino.rotation = original_rotation

            kick_result = game.try_wall_kick(old_rot, new_rot)
            if kick_result:
                print(
                    f"✅ Wall kick 成功! kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
                )
            else:
                print(f"❌ Wall kick 失敗!")

    return game


def print_game_state_extended(game):
    """打印擴展的遊戲狀態（顯示更多行）"""
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

    # 顯示更多行來看到完整情況
    for row in range(8, 20):
        line = f"{row:2d}"
        for col in range(10):
            if (col, row) in tetromino_blocks:
                line += "T"
            elif row < len(grid) and grid[row][col] != BLACK:
                line += "#"
            else:
                line += "."
        print(line)


if __name__ == "__main__":
    pygame.init()

    print("🎯 終極 Wall Kick 測試")
    print("專門找出可能導致問題的場景")
    print("=" * 60)

    try:
        # 執行終極測試
        print("第一個測試：完全沒有空間的場景")
        game1 = create_no_space_scenario()

        print("\n" + "=" * 60)
        print("第二個測試：模擬用戶實際場景")
        game2 = test_specific_user_scenario()

        print("\n" + "=" * 60)
        print("🔍 問題分析:")
        print("如果上面的測試都能正常工作，那麼可能的問題包括：")
        print("1. Lock delay 期間的 wall kick 執行問題")
        print("2. 輸入處理的時機問題")
        print("3. 特定旋轉序列的問題")
        print("4. 遊戲狀態更新順序的問題")
        print("\n建議檢查：")
        print("- main.py 中的遊戲循環順序")
        print("- handle_input() 中的旋轉處理邏輯")
        print("- lock delay 期間是否禁用了某些操作")

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

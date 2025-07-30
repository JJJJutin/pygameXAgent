#!/usr/bin/env python3
"""
精確複製圖片中的 T-Spin Triple 設置
基於圖片中具體的方塊排列來測試 wall kick
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from config.shapes import WALL_KICK_DATA
from game_objects.tetromino import Tetromino


def create_exact_image_scenario():
    """
    精確重現圖片中的T-Spin Triple設置
    根據圖片中的方塊排列創建測試場景
    """
    print("=== 精確複製圖片場景：T-Spin Triple Wall Kick ===")

    game = Game()
    grid = game.grid.grid

    # 根據圖片精確重建場景
    # 圖片顯示的是一個典型的T-Spin Triple洞口設置
    # 左側高牆，右側有缺口，底部封閉

    # 我會創建一個需要真正wall kick的場景
    # 讓T方塊在特定位置無法直接旋轉，必須使用wall kick

    setup = [
        "..........",  # 行8
        "..........",  # 行9
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "..........",  # 行13
        "###.......",  # 行14 - 左側有障礙
        "###.......",  # 行15
        "###.......",  # 行16
        "###.......",  # 行17
        "###.......",  # 行18
        "##########",  # 行19 - 底部封閉
    ]

    for i, pattern in enumerate(setup):
        row = 8 + i
        if row < GRID_HEIGHT:
            for col, char in enumerate(pattern):
                if char == "#":
                    grid[row][col] = WHITE

    # 關鍵：將T方塊放在一個會與左側牆壁發生衝突的位置
    # 這樣當它嘗試旋轉時就必須使用wall kick
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1  # 緊貼左側障礙物
    game.current_tetromino.y = 15  # 在障礙物旁邊
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態（T方塊緊貼左側障礙物）：")
    print_detailed_state(game)

    # 嘗試向右旋轉（0 -> 1）
    print("\n嘗試順時鐘旋轉 (0 -> 1)...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    # 首先檢查直接旋轉是否可行
    temp_rotation = game.current_tetromino.rotation
    game.current_tetromino.rotation = new_rotation

    direct_valid = game.grid.is_valid_position(game.current_tetromino)
    print(f"直接旋轉可行性: {'✅ 可行' if direct_valid else '❌ 不可行'}")

    # 恢復原始狀態
    game.current_tetromino.rotation = temp_rotation

    if direct_valid:
        print("直接旋轉成功")
        game.current_tetromino.rotation = new_rotation
        game.last_move_was_rotation = True
    else:
        print("直接旋轉失敗，分析 Wall Kick...")

        # 詳細分析 wall kick 過程
        kick_tests = WALL_KICK_DATA["JLSTZ"].get((old_rotation, new_rotation), [])
        print(f"Wall Kick 測試序列: {kick_tests}")

        rotated_shape = game.current_tetromino.get_rotated_shape(new_rotation)
        print("旋轉後的形狀:")
        for i, row in enumerate(rotated_shape):
            print(f"  {i}: {''.join('■' if cell else '·' for cell in row)}")

        # 逐個測試每個 kick
        successful_kicks = []
        for kick_idx, (kick_x, kick_y) in enumerate(kick_tests):
            test_x = game.current_tetromino.x + kick_x
            test_y = game.current_tetromino.y + kick_y

            is_valid = game.grid.is_valid_position_at(rotated_shape, test_x, test_y)
            status = "✅ 成功" if is_valid else "❌ 失敗"
            print(
                f"  Kick {kick_idx}: 偏移({kick_x:+2d}, {kick_y:+2d}) -> 位置({test_x:2d}, {test_y:2d}) {status}"
            )

            if is_valid:
                successful_kicks.append((kick_idx, kick_x, kick_y, test_x, test_y))
            else:
                # 分析失敗原因
                conflicts = []
                for row_idx, shape_row in enumerate(rotated_shape):
                    for col_idx, cell in enumerate(shape_row):
                        if cell:
                            check_x = test_x + col_idx
                            check_y = test_y + row_idx

                            if check_x < 0:
                                conflicts.append("左邊界")
                            elif check_x >= GRID_WIDTH:
                                conflicts.append("右邊界")
                            elif check_y >= GRID_HEIGHT:
                                conflicts.append("下邊界")
                            elif check_y >= 0 and grid[check_y][check_x] != BLACK:
                                conflicts.append(f"方塊({check_x},{check_y})")

                if conflicts:
                    print(f"    衝突: {', '.join(set(conflicts))}")

        # 執行實際的 wall kick
        kick_result = game.try_wall_kick(old_rotation, new_rotation)

        if kick_result:
            print(f"\n✅ Wall Kick 最終成功!")
            print(f"使用 Kick {game.last_kick_index}: 偏移{game.last_kick_offset}")
            game.last_move_was_rotation = True
        else:
            print(f"\n❌ Wall Kick 最終失敗!")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_detailed_state(game)

    # 檢查 T-Spin
    if game.last_move_was_rotation:
        tspin_type = game.check_t_spin()
        if tspin_type:
            print(f"\n🎉 檢測到 T-Spin: {tspin_type.upper()}")
        else:
            print(f"\n❌ 未檢測到 T-Spin")

    return game


def create_forced_wall_kick_scenario():
    """
    創建一個必須使用特定wall kick的場景
    """
    print("\n=== 強制 Wall Kick 場景 ===")

    game = Game()
    grid = game.grid.grid

    # 創建一個T方塊被障礙物包圍，只能通過特定wall kick才能旋轉的情況
    setup = [
        "..........",  # 行12
        "..........",  # 行13
        "..........",  # 行14
        "#.........",  # 行15 - 左側有單個障礙
        "#.........",  # 行16
        "#.........",  # 行17
        "##########",  # 行18 - 底部封閉
        "##########",  # 行19
    ]

    for i, pattern in enumerate(setup):
        row = 12 + i
        if row < GRID_HEIGHT:
            for col, char in enumerate(pattern):
                if char == "#":
                    grid[row][col] = WHITE

    # 將T方塊放在一個特定位置，使其必須使用wall kick
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 0  # 完全靠左
    game.current_tetromino.y = 14  # 在障礙物上方
    game.current_tetromino.rotation = 0

    print("初始狀態（T方塊完全靠左）：")
    print_detailed_state(game)

    # 嘗試旋轉
    print("\n嘗試順時鐘旋轉...")
    old_rotation = 0
    new_rotation = 1

    original_rotation = game.current_tetromino.rotation
    game.current_tetromino.rotation = new_rotation

    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗，嘗試 Wall Kick")
        game.current_tetromino.rotation = original_rotation

        # 執行詳細的wall kick分析
        kick_tests = WALL_KICK_DATA["JLSTZ"].get((old_rotation, new_rotation), [])
        print(f"Wall Kick 序列: {kick_tests}")

        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"✅ Wall Kick 成功! Kick {game.last_kick_index}: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("❌ Wall Kick 失敗!")
            game.last_move_was_rotation = False

    print("\n最終狀態：")
    print_detailed_state(game)

    return game


def test_all_rotation_directions():
    """
    測試所有旋轉方向的wall kick
    """
    print("\n=== 測試所有旋轉方向 ===")

    game = Game()
    grid = game.grid.grid

    # 創建一個簡單的障礙物環境
    for row in range(16, 20):
        for col in [0, 9]:  # 左右兩側有障礙
            grid[row][col] = WHITE

    # 測試每個旋轉方向
    rotations_to_test = [
        (0, 1, "0→1 (上→右)"),
        (1, 2, "1→2 (右→下)"),
        (2, 3, "2→3 (下→左)"),
        (3, 0, "3→0 (左→上)"),
        (0, 3, "0→3 (上→左, 逆時鐘)"),
        (3, 2, "3→2 (左→下, 逆時鐘)"),
        (2, 1, "2→1 (下→右, 逆時鐘)"),
        (1, 0, "1→0 (右→上, 逆時鐘)"),
    ]

    for old_rot, new_rot, description in rotations_to_test:
        print(f"\n--- 測試 {description} ---")

        # 重置T方塊位置
        game.current_tetromino = Tetromino("T")
        game.current_tetromino.x = 4
        game.current_tetromino.y = 14
        game.current_tetromino.rotation = old_rot

        # 嘗試旋轉
        original_rotation = game.current_tetromino.rotation
        game.current_tetromino.rotation = new_rot

        if game.grid.is_valid_position(game.current_tetromino):
            print("✅ 直接旋轉成功")
        else:
            game.current_tetromino.rotation = original_rotation
            kick_result = game.try_wall_kick(old_rot, new_rot)
            if kick_result:
                print(
                    f"✅ Wall Kick 成功 (Kick {game.last_kick_index}: {game.last_kick_offset})"
                )
            else:
                print("❌ Wall Kick 失敗")


def print_detailed_state(game):
    """打印詳細的遊戲狀態"""
    grid = game.grid.grid
    tetromino = game.current_tetromino

    tetromino_blocks = set()
    if tetromino:
        blocks = tetromino.get_blocks()
        tetromino_blocks = set(blocks)

    print(f"T方塊: 位置({tetromino.x}, {tetromino.y}), 旋轉={tetromino.rotation}")

    # 顯示T方塊的形狀
    current_shape = tetromino.get_current_shape()
    print("T方塊當前形狀:")
    for i, row in enumerate(current_shape):
        print(f"  {i}: {''.join('■' if cell else '·' for cell in row)}")

    print("\n遊戲區域 (T=T方塊, #=已放置方塊, .=空白):")
    print("  0123456789")

    for row in range(8, 20):
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

    print("🎯 精確測試圖片中的 T-Spin Wall Kick 場景")
    print("=" * 70)

    try:
        game1 = create_exact_image_scenario()
        game2 = create_forced_wall_kick_scenario()
        test_all_rotation_directions()

        print("\n" + "=" * 70)
        print("🔍 分析結果:")
        print("如果上述測試中 Wall Kick 都能正常工作，")
        print("那麼問題可能出現在遊戲的實際運行時，而不是 Wall Kick 邏輯本身。")
        print("\n可能的問題：")
        print("1. 輸入處理時機問題")
        print("2. Lock delay 期間的限制")
        print("3. 特定遊戲狀態下的阻止機制")
        print("4. 按鍵響應的延遲或遺失")

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

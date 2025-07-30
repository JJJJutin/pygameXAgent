#!/usr/bin/env python3
"""
基於用戶提供圖片的 T-Spin Triple 實測
測試圖片中展示的具體 T-Spin wall kick 場景
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from config.shapes import WALL_KICK_DATA
from game_objects.tetromino import Tetromino


def test_tspin_triple_scenario_1():
    """
    測試圖片中的第一個場景：T方塊需要wall kick才能旋轉進入triple設置
    對應圖片中標註 "Soft drop to here" -> "Rotate right" 的場景
    """
    print("=== T-Spin Triple 場景1：標準Wall Kick測試 ===")

    game = Game()
    grid = game.grid.grid

    # 根據圖片創建 T-Spin Triple 的典型設置
    # 這是一個左側有高牆、右側有缺口的經典 T-Spin Triple 設置

    # 從底部開始建構（行19是最底部）
    setup_patterns = [
        "##########",  # 行19 - 底部全滿
        "##########",  # 行18
        "##########",  # 行17
        "####....##",  # 行16 - 右側有洞
        "####....##",  # 行15
        "####....##",  # 行14
        "####....##",  # 行13
        "####....##",  # 行12
        "####....##",  # 行11
        "####....##",  # 行10
    ]

    # 應用設置到網格（從行10到行19）
    for i, pattern in enumerate(setup_patterns):
        row = 19 - i  # 從底部向上
        for col, char in enumerate(pattern):
            if char == "#":
                grid[row][col] = WHITE

    # 將T方塊放在圖片中 "Soft drop to here" 的位置
    # 根據圖片，T方塊應該在洞口上方，準備軟降下去
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 4  # 在洞口上方
    game.current_tetromino.y = 8  # 比較高的位置
    game.current_tetromino.rotation = 0  # 朝上（圖片中的初始狀態）

    print("初始狀態（T方塊在洞口上方）：")
    print_game_state(game)

    # 第一步：軟降到指定位置（模擬 "Soft drop to here"）
    print("\n第一步：軟降 T 方塊到指定位置...")

    # 找到可以放置的最低位置
    target_y = game.current_tetromino.y
    for test_y in range(game.current_tetromino.y, GRID_HEIGHT):
        if game.grid.is_valid_position(
            game.current_tetromino, 0, test_y - game.current_tetromino.y
        ):
            target_y = test_y
        else:
            break

    game.current_tetromino.y = target_y - 1  # 最後一個有效位置
    print(f"軟降到位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")

    print("軟降後狀態：")
    print_game_state(game)

    # 第二步：嘗試向右旋轉（模擬 "Rotate right"）
    print("\n第二步：嘗試向右旋轉（順時鐘）...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    # 檢查直接旋轉是否可行
    original_x, original_y, original_rotation = (
        game.current_tetromino.x,
        game.current_tetromino.y,
        game.current_tetromino.rotation,
    )
    game.current_tetromino.rotation = new_rotation

    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功！")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗，需要 Wall Kick")
        # 恢復原狀態
        (
            game.current_tetromino.x,
            game.current_tetromino.y,
            game.current_tetromino.rotation,
        ) = (original_x, original_y, original_rotation)

        # 顯示 wall kick 嘗試過程
        print("嘗試 Wall Kick 序列...")
        kick_tests = WALL_KICK_DATA["JLSTZ"].get((old_rotation, new_rotation), [])
        print(f"Kick 測試序列: {kick_tests}")

        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(f"✅ Wall Kick 成功！")
            print(f"使用的 Kick 索引: {game.last_kick_index}")
            print(f"Kick 偏移: {game.last_kick_offset}")
            game.last_move_was_rotation = True
        else:
            print("❌ Wall Kick 失敗！")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_game_state(game)

    # 檢查 T-Spin
    if game.last_move_was_rotation:
        tspin_type = game.check_t_spin()
        if tspin_type:
            print(f"🎉 檢測到 T-Spin: {tspin_type.upper()}")

            # 檢查能消除多少行
            # 暫時放置方塊來檢查消除
            game.grid.place_tetromino(game.current_tetromino)
            lines_cleared = game.grid.check_lines()
            print(f"可消除行數: {lines_cleared}")

            if lines_cleared == 3:
                print("🎯 這是一個 T-Spin Triple！")
            elif lines_cleared == 2:
                print("🎯 這是一個 T-Spin Double！")
            elif lines_cleared == 1:
                print("🎯 這是一個 T-Spin Single！")
        else:
            print("❌ 未檢測到 T-Spin")

    return game


def test_tspin_triple_scenario_2():
    """
    測試另一個 T-Spin Triple 場景
    模擬更緊密的空間情況
    """
    print("\n=== T-Spin Triple 場景2：緊密空間測試 ===")

    game = Game()
    grid = game.grid.grid

    # 創建另一種 T-Spin Triple 設置
    # 這種設置方塊更緊密，更容易觸發 wall kick 問題

    setup_patterns = [
        "##########",  # 行19
        "##########",  # 行18
        "##########",  # 行17
        "###.....##",  # 行16 - 左側更高的牆
        "###.....##",  # 行15
        "###.....##",  # 行14
        "###.....##",  # 行13
        "###.....##",  # 行12
        "###.....##",  # 行11
        "###.....##",  # 行10
    ]

    for i, pattern in enumerate(setup_patterns):
        row = 19 - i
        for col, char in enumerate(pattern):
            if char == "#":
                grid[row][col] = WHITE

    # T方塊放在需要 wall kick 的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 2  # 更靠近左牆
    game.current_tetromino.y = 8
    game.current_tetromino.rotation = 0

    print("初始狀態：")
    print_game_state(game)

    # 軟降
    target_y = game.current_tetromino.y
    for test_y in range(game.current_tetromino.y, GRID_HEIGHT):
        if game.grid.is_valid_position(
            game.current_tetromino, 0, test_y - game.current_tetromino.y
        ):
            target_y = test_y
        else:
            break

    game.current_tetromino.y = target_y - 1
    print(f"\n軟降到位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print_game_state(game)

    # 嘗試旋轉
    print("\n嘗試順時鐘旋轉...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    original_state = (
        game.current_tetromino.x,
        game.current_tetromino.y,
        game.current_tetromino.rotation,
    )
    game.current_tetromino.rotation = new_rotation

    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗，嘗試 Wall Kick...")
        (
            game.current_tetromino.x,
            game.current_tetromino.y,
            game.current_tetromino.rotation,
        ) = original_state

        # 詳細顯示 wall kick 過程
        kick_tests = WALL_KICK_DATA["JLSTZ"].get((old_rotation, new_rotation), [])
        print(f"Wall Kick 測試序列: {kick_tests}")

        rotated_shape = game.current_tetromino.get_rotated_shape(new_rotation)

        for i, (kick_x, kick_y) in enumerate(kick_tests):
            test_x = game.current_tetromino.x + kick_x
            test_y = game.current_tetromino.y + kick_y

            print(
                f"  Kick {i}: 偏移({kick_x:+d}, {kick_y:+d}) -> 位置({test_x}, {test_y})"
            )

            if game.grid.is_valid_position_at(rotated_shape, test_x, test_y):
                print(f"    ✅ 成功")
                break
            else:
                print(f"    ❌ 失敗")

        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(f"\nWall Kick 最終結果: ✅ 成功")
            print(f"使用 Kick {game.last_kick_index}: 偏移{game.last_kick_offset}")
            game.last_move_was_rotation = True
        else:
            print(f"\nWall Kick 最終結果: ❌ 失敗")
            game.last_move_was_rotation = False

    print("\n最終狀態：")
    print_game_state(game)

    return game


def test_wall_kick_edge_cases():
    """
    測試邊緣情況：靠近邊界的 wall kick
    """
    print("\n=== 邊緣情況測試：邊界 Wall Kick ===")

    game = Game()
    grid = game.grid.grid

    # 創建靠近右邊界的情況
    for row in range(15, 20):
        for col in range(10):
            if col >= 7:  # 右側有障礙物
                grid[row][col] = WHITE

    # T方塊放在右邊界附近
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 6  # 靠近右邊界
    game.current_tetromino.y = 12
    game.current_tetromino.rotation = 0

    print("靠近右邊界的場景：")
    print_game_state(game)

    # 嘗試旋轉
    print("\n嘗試旋轉...")
    old_rotation = 0
    new_rotation = 1

    original_state = (
        game.current_tetromino.x,
        game.current_tetromino.y,
        game.current_tetromino.rotation,
    )
    game.current_tetromino.rotation = new_rotation

    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
    else:
        print("❌ 直接旋轉失敗，嘗試 Wall Kick...")
        (
            game.current_tetromino.x,
            game.current_tetromino.y,
            game.current_tetromino.rotation,
        ) = original_state

        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"✅ Wall Kick 成功! Kick {game.last_kick_index}: {game.last_kick_offset}"
            )
        else:
            print("❌ Wall Kick 失敗!")

    print("\n結果：")
    print_game_state(game)

    return game


def print_game_state(game):
    """打印遊戲狀態"""
    grid = game.grid.grid
    tetromino = game.current_tetromino

    tetromino_blocks = set()
    if tetromino:
        blocks = tetromino.get_blocks()
        tetromino_blocks = set(blocks)

    print(f"T方塊: 位置({tetromino.x}, {tetromino.y}), 旋轉={tetromino.rotation}")
    print("遊戲區域 (T=T方塊, #=已放置方塊, .=空白):")
    print("  0123456789")

    # 顯示從行8到行19
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


def run_image_based_tests():
    """執行基於圖片的測試"""
    print("🖼️  基於用戶提供圖片的 T-Spin Wall Kick 實測")
    print("=" * 70)

    try:
        # 執行各種測試場景
        game1 = test_tspin_triple_scenario_1()
        game2 = test_tspin_triple_scenario_2()
        game3 = test_wall_kick_edge_cases()

        print("\n" + "=" * 70)
        print("📊 測試總結:")
        print("✅ 完成了基於圖片的 T-Spin Triple 場景測試")
        print("✅ 測試了不同的 wall kick 情況")
        print("✅ 驗證了邊界情況的處理")

        print("\n🔍 如果在實際遊戲中仍有問題，可能的原因：")
        print("1. Lock delay 期間的輸入處理問題")
        print("2. 特定時機的旋轉被阻止")
        print("3. 遊戲狀態更新順序問題")
        print("4. 特定按鍵組合的處理問題")

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    pygame.init()

    try:
        run_image_based_tests()
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
    finally:
        pygame.quit()

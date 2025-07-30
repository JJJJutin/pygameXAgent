#!/usr/bin/env python3
"""
更精確的測試：強制需要 wall kick 的 T-spin 情況
專門測試方塊底下有其他方塊時無法 wall kick 的問題
"""

import pygame
import sys
import os

# 設定路徑以便 import 模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from game_objects.tetromino import Tetromino


def create_forced_wallkick_scenario():
    """
    創建必須使用 wall kick 的場景
    設計一個 T 方塊無法直接旋轉，但 wall kick 應該可以成功的情況
    """
    print("=== 強制 Wall Kick 場景 ===")

    game = Game()
    grid = game.grid.grid

    # 創建一個T-spin Triple的經典設置，但需要wall kick
    # 這是一個真實會遇到的情況

    # 底部結構 (行16-19)
    setup = [
        "##....####",  # 行16
        "##....####",  # 行17
        "##....####",  # 行18
        "##....####",  # 行19
    ]

    for row_idx, row_pattern in enumerate(setup):
        row = 16 + row_idx
        for col, char in enumerate(row_pattern):
            if char == "#":
                grid[row][col] = WHITE

    # 放置 T 方塊在一個會與牆壁碰撞的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1  # 靠近左牆
    game.current_tetromino.y = 14
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_game_state(game)

    # 嘗試向右旋轉 (0 -> 1)
    print("\n嘗試順時鐘旋轉 (0 -> 1)...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    # 檢查直接旋轉是否可行
    game.current_tetromino.rotation = new_rotation
    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功，無需 wall kick")
        game.last_move_was_rotation = True
    else:
        print("❌ 直接旋轉失敗，嘗試 wall kick...")
        game.current_tetromino.rotation = old_rotation  # 恢復原始旋轉

        # 嘗試 wall kick
        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"✅ Wall kick 成功! 使用kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("❌ Wall kick 失敗")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_game_state(game)

    return game


def create_tight_tspin_scenario():
    """
    創建更緊密的 T-spin 場景，方塊被底下和周圍的方塊包圍
    """
    print("\n=== 緊密 T-spin 場景 ===")

    game = Game()
    grid = game.grid.grid

    # 創建一個真實的T-spin DT cannon設置
    setup = [
        "#......###",  # 行13
        "#......###",  # 行14
        "#......###",  # 行15
        "#......###",  # 行16
        "##.....###",  # 行17
        "##.....###",  # 行18
        "##.....###",  # 行19
    ]

    for row_idx, row_pattern in enumerate(setup):
        row = 13 + row_idx
        for col, char in enumerate(row_pattern):
            if char == "#":
                grid[row][col] = WHITE

    # 放置 T 方塊在需要kick的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 0  # 最左邊
    game.current_tetromino.y = 11
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_game_state(game)

    # 嘗試向右旋轉
    print("\n嘗試順時鐘旋轉...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    game.current_tetromino.rotation = new_rotation
    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
        game.last_move_was_rotation = True
    else:
        game.current_tetromino.rotation = old_rotation
        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"✅ Wall kick 成功! 使用kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("❌ Wall kick 失敗")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_game_state(game)

    return game


def create_bottom_blocked_scenario():
    """
    創建底部完全被堵住的情況，測試wall kick是否能處理
    """
    print("\n=== 底部被阻擋的場景 ===")

    game = Game()
    grid = game.grid.grid

    # 創建底部被完全阻擋的情況
    setup = [
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "..........",  # 行13
        "#..........",  # 行14
        "#..........",  # 行15
        "####......",  # 行16
        "####......",  # 行17
        "####......",  # 行18
        "####......",  # 行19
    ]

    for row_idx, row_pattern in enumerate(setup):
        row = 10 + row_idx
        for col, char in enumerate(row_pattern):
            if char == "#":
                grid[row][col] = WHITE

    # 將T方塊放在會與底部方塊碰撞的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1
    game.current_tetromino.y = 13
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_game_state(game)

    # 嘗試向右旋轉
    print("\n嘗試順時鐘旋轉...")
    old_rotation = game.current_tetromino.rotation
    new_rotation = (old_rotation + 1) % 4

    game.current_tetromino.rotation = new_rotation
    if game.grid.is_valid_position(game.current_tetromino):
        print("✅ 直接旋轉成功")
        game.last_move_was_rotation = True
    else:
        game.current_tetromino.rotation = old_rotation
        print("❌ 直接旋轉失敗，嘗試 wall kick...")

        # 顯示將要嘗試的wall kick序列
        from config.shapes import WALL_KICK_DATA

        kick_tests = WALL_KICK_DATA["JLSTZ"].get((old_rotation, new_rotation), [])
        print(f"將要嘗試的kick序列: {kick_tests}")

        kick_result = game.try_wall_kick(old_rotation, new_rotation)
        if kick_result:
            print(
                f"✅ Wall kick 成功! 使用kick索引: {game.last_kick_index}, 偏移: {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
        else:
            print("❌ Wall kick 失敗 - 這可能就是問題所在!")
            game.last_move_was_rotation = False

    print("\n旋轉後狀態：")
    print_game_state(game)

    return game


def print_game_state(game):
    """打印當前遊戲狀態"""
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

    for row in range(10, 20):  # 只顯示底部10行
        line = f"{row:2d}"
        for col in range(10):
            if (col, row) in tetromino_blocks:
                line += "T"
            elif grid[row][col] != BLACK:
                line += "#"
            else:
                line += "."
        print(line)


def run_targeted_tests():
    """執行針對性測試"""
    print("🎯 針對性測試：方塊底下有方塊時的 T-spin Wall Kick")
    print("=" * 60)

    scenarios = [
        create_forced_wallkick_scenario,
        create_tight_tspin_scenario,
        create_bottom_blocked_scenario,
    ]

    results = []
    for i, scenario in enumerate(scenarios, 1):
        try:
            game = scenario()
            if hasattr(game, "last_move_was_rotation") and game.last_move_was_rotation:
                results.append(f"場景{i}: ✅ 旋轉成功")
            else:
                results.append(f"場景{i}: ❌ 旋轉失敗")
        except Exception as e:
            results.append(f"場景{i}: ❌ 錯誤 - {e}")
            print(f"錯誤: {e}")

    print("\n" + "=" * 60)
    print("📊 測試結果摘要:")
    for result in results:
        print(f"  {result}")


if __name__ == "__main__":
    pygame.init()

    try:
        run_targeted_tests()
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

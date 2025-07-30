#!/usr/bin/env python3
"""
測試當方塊底下有其他方塊時的 T-spin Wall Kick 功能
專門測試用戶回報的問題：「無法在方塊底下有方塊的狀況下順利t-spin wallkick」
"""

import pygame
import sys
import os

# 設定路徑以便 import 模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from game_objects.tetromino import Tetromino


def create_test_scenario_1():
    """
    測試場景1：經典 T-spin Double 設置
    在方塊底下有其他方塊的情況下進行 T-spin
    """
    print("=== 測試場景1：經典 T-spin Double 設置 ===")

    game = Game()

    # 建立底部結構：為 T-spin Double 準備的經典設置
    # 最下面幾行先填上一些方塊作為底座
    grid = game.grid.grid

    # 底座 (行19)
    for col in range(10):
        if col not in [8, 9]:  # 留出T-spin洞口
            grid[19][col] = WHITE

    # 第二層 (行18)
    for col in range(10):
        if col not in [7, 8, 9]:  # 留出T-spin空間
            grid[18][col] = WHITE

    # 第三層 (行17)
    for col in range(10):
        if col not in [6, 7, 8, 9]:  # 留出T-spin空間和額外的洞
            grid[17][col] = WHITE

    # 創建一個朝上的 T 方塊，放在需要 wall kick 的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 7  # 位置在T-spin區域上方
    game.current_tetromino.y = 15
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_game_state(game)

    # 嘗試向右旋轉 (0 -> 1)，這應該需要 wall kick
    print("\n嘗試順時鐘旋轉 (0 -> 1)，期望觸發 wall kick...")
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

    # 檢查 T-spin
    if game.last_move_was_rotation:
        tspin_type = game.check_t_spin()
        if tspin_type:
            print(f"🎉 檢測到 T-spin: {tspin_type}")
        else:
            print("❌ 未檢測到 T-spin")

    return game


def create_test_scenario_2():
    """
    測試場景2：緊密空間中的 T-spin
    方塊底下、左右都有障礙物的情況
    """
    print("\n=== 測試場景2：緊密空間中的 T-spin ===")

    game = Game()
    grid = game.grid.grid

    # 創建更緊密的環境
    # 底部填滿除了小洞之外的所有位置
    for row in range(17, 20):
        for col in range(10):
            if not (
                (row == 17 and col in [4, 5])
                or (row == 18 and col in [4, 5])
                or (row == 19 and col in [4, 5, 6])
            ):
                grid[row][col] = WHITE

    # 放置 T 方塊在需要 wall kick 的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 3
    game.current_tetromino.y = 15
    game.current_tetromino.rotation = 0  # 朝上

    print("初始狀態：")
    print_game_state(game)

    # 嘗試旋轉
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


def create_test_scenario_3():
    """
    測試場景3：特殊 kick 情況
    測試 TST kick 和 Fin kick
    """
    print("\n=== 測試場景3：特殊 kick 情況 (TST/Fin kick) ===")

    game = Game()
    grid = game.grid.grid

    # 創建需要特殊 kick 的情況
    # 這種設置通常需要使用較大的垂直偏移
    for row in range(16, 20):
        for col in range(10):
            if not (
                (row >= 16 and row <= 17 and col in [3, 4, 5])
                or (row >= 18 and col in [4])
            ):
                grid[row][col] = WHITE

    # 放置 T 方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 3
    game.current_tetromino.y = 14
    game.current_tetromino.rotation = 2  # 朝下

    print("初始狀態：")
    print_game_state(game)

    # 嘗試旋轉到朝右 (2 -> 3)
    print("\n嘗試旋轉 (2 -> 3)...")
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

            # 檢查是否為特殊 kick
            if game.last_kick_index == 4:
                print("🌟 這是 TST kick (最後一個kick)!")
            elif game.last_kick_offset and abs(game.last_kick_offset[1]) == 2:
                print("🌟 這是 Fin kick (垂直移動2格)!")
        else:
            print("❌ Wall kick 失敗")
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


def run_all_tests():
    """執行所有測試"""
    print("🔥 開始測試：方塊底下有方塊時的 T-spin Wall Kick")
    print("=" * 60)

    # 執行測試場景
    scenarios = [create_test_scenario_1, create_test_scenario_2, create_test_scenario_3]

    results = []
    for i, scenario in enumerate(scenarios, 1):
        try:
            game = scenario()
            results.append(f"場景{i}: ✅ 完成")
        except Exception as e:
            results.append(f"場景{i}: ❌ 錯誤 - {e}")
            print(f"錯誤: {e}")

    print("\n" + "=" * 60)
    print("📊 測試結果摘要:")
    for result in results:
        print(f"  {result}")

    print("\n💡 如果看到 Wall kick 失敗，可能的原因：")
    print("  1. Wall kick 資料不正確")
    print("  2. 位置檢查邏輯有問題")
    print("  3. 碰撞檢測在底部方塊存在時不正確")
    print("  4. T-spin 設置不適合")


if __name__ == "__main__":
    # 初始化 pygame （測試需要）
    pygame.init()

    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

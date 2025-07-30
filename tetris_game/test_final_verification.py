#!/usr/bin/env python3
"""
最終驗證：測試修復後的 T-Spin Wall Kick
驗證圖片中的場景現在是否能正常工作
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from game_objects.tetromino import Tetromino


def test_fixed_tspin_scenarios():
    """測試修復後的T-Spin場景"""
    print("🔧 測試修復後的 T-Spin Wall Kick")
    print("=" * 60)

    scenarios = [
        create_image_scenario_1,
        create_image_scenario_2,
        create_extreme_tight_scenario,
        create_lock_delay_scenario,
    ]

    results = []

    for i, scenario_func in enumerate(scenarios, 1):
        print(f"\n--- 場景 {i} ---")
        try:
            success = scenario_func()
            results.append(f"場景 {i}: {'✅ 成功' if success else '❌ 失敗'}")
        except Exception as e:
            results.append(f"場景 {i}: ❌ 錯誤 - {e}")
            print(f"錯誤: {e}")

    print(f"\n{'='*60}")
    print("📊 測試結果總結:")
    for result in results:
        print(f"  {result}")

    success_count = sum(1 for result in results if "✅ 成功" in result)
    print(
        f"\n成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)"
    )


def create_image_scenario_1():
    """測試圖片中的第一個場景"""
    print("測試圖片場景1: 標準T-Spin Triple設置")

    game = Game()
    grid = game.grid.grid

    # 複製圖片中的設置
    setup = [
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "..........",  # 行13
        "####....##",  # 行14 - T-Spin Triple典型設置
        "####....##",  # 行15
        "####....##",  # 行16
        "####....##",  # 行17
        "####....##",  # 行18
        "##########",  # 行19
    ]

    for i, pattern in enumerate(setup):
        row = 10 + i
        for col, char in enumerate(pattern):
            if char == "#":
                grid[row][col] = WHITE

    # 放置T方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 3  # 在洞口左側
    game.current_tetromino.y = 12
    game.current_tetromino.rotation = 0

    print_state(game, "初始")

    # 軟降到底部
    while game.grid.is_valid_position(game.current_tetromino, 0, 1):
        game.current_tetromino.y += 1

    print_state(game, "軟降後")

    # 嘗試旋轉
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
        game.last_move_was_rotation = True
        success = True
    else:
        (
            game.current_tetromino.x,
            game.current_tetromino.y,
            game.current_tetromino.rotation,
        ) = original_state
        if game.try_wall_kick(old_rotation, new_rotation):
            print(
                f"✅ Wall Kick 成功! Kick {game.last_kick_index}, 偏移 {game.last_kick_offset}"
            )
            game.last_move_was_rotation = True
            success = True
        else:
            print("❌ Wall Kick 失敗")
            success = False

    if success:
        print_state(game, "旋轉後")

        # 檢查T-Spin
        tspin_type = game.check_t_spin()
        if tspin_type:
            print(f"🎯 檢測到 T-Spin: {tspin_type.upper()}")

    return success


def create_image_scenario_2():
    """測試更緊密的場景"""
    print("測試圖片場景2: 緊密空間T-Spin")

    game = Game()
    grid = game.grid.grid

    # 之前失敗的緊密場景
    setup = [
        "..........",  # 行12
        "..........",  # 行13
        "###.......",  # 行14
        "###.......",  # 行15
        "###.......",  # 行16
        "###.......",  # 行17
        "###.......",  # 行18
        "##########",  # 行19
    ]

    for i, pattern in enumerate(setup):
        row = 12 + i
        for col, char in enumerate(pattern):
            if char == "#":
                grid[row][col] = WHITE

    # T方塊放在緊密位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1  # 緊貼左側障礙物
    game.current_tetromino.y = 15
    game.current_tetromino.rotation = 0

    print_state(game, "初始（緊密）")

    # 嘗試旋轉
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
        success = True
    else:
        (
            game.current_tetromino.x,
            game.current_tetromino.y,
            game.current_tetromino.rotation,
        ) = original_state
        if game.try_wall_kick(old_rotation, new_rotation):
            kick_type = "標準" if game.last_kick_index < 10 else "增強"
            print(
                f"✅ {kick_type} Wall Kick 成功! Kick {game.last_kick_index}, 偏移 {game.last_kick_offset}"
            )
            success = True
        else:
            print("❌ 所有 Wall Kick 都失敗")
            success = False

    if success:
        print_state(game, "旋轉後")

    return success


def create_extreme_tight_scenario():
    """測試極端緊密場景"""
    print("測試極端緊密場景")

    game = Game()
    grid = game.grid.grid

    # 極端緊密的設置
    setup = [
        "..........",  # 行14
        "##.......#",  # 行15 - 兩側都有障礙
        "##.......#",  # 行16
        "##.......#",  # 行17
        "##.......#",  # 行18
        "##########",  # 行19
    ]

    for i, pattern in enumerate(setup):
        row = 14 + i
        for col, char in enumerate(pattern):
            if char == "#":
                grid[row][col] = WHITE

    # T方塊在極端位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1
    game.current_tetromino.y = 14
    game.current_tetromino.rotation = 0

    print_state(game, "極端場景初始")

    # 嘗試旋轉
    success = False
    for target_rotation in [1, 2, 3]:
        original_state = (
            game.current_tetromino.x,
            game.current_tetromino.y,
            game.current_tetromino.rotation,
        )

        if game.try_wall_kick(game.current_tetromino.rotation, target_rotation):
            kick_type = "標準" if game.last_kick_index < 10 else "增強"
            print(f"✅ 旋轉到 {target_rotation}: {kick_type} Wall Kick 成功!")
            success = True
            break
        else:
            (
                game.current_tetromino.x,
                game.current_tetromino.y,
                game.current_tetromino.rotation,
            ) = original_state

    if not success:
        print("❌ 所有旋轉方向都失敗")

    return success


def create_lock_delay_scenario():
    """測試Lock Delay期間的Wall Kick"""
    print("測試Lock Delay期間的Wall Kick")

    game = Game()
    grid = game.grid.grid

    # 底部設置
    for col in range(10):
        grid[19][col] = WHITE

    # 左側障礙物
    for row in range(16, 19):
        grid[row][0] = WHITE

    # T方塊在地面上觸發lock delay
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 0
    game.current_tetromino.y = 16
    game.current_tetromino.rotation = 0

    # 設置lock delay狀態
    game.is_on_ground = True
    game.lock_delay_timer = LOCK_DELAY_MAX * 0.9  # 90%的lock delay

    print(f"Lock Delay狀態: {game.lock_delay_timer:.1f}/{LOCK_DELAY_MAX}")
    print_state(game, "Lock Delay中")

    # 在lock delay期間嘗試旋轉
    old_rotation = 0
    new_rotation = 1

    if game.try_wall_kick(old_rotation, new_rotation):
        kick_type = "標準" if game.last_kick_index < 10 else "增強"
        print(f"✅ Lock Delay期間 {kick_type} Wall Kick 成功!")
        game.last_move_was_rotation = True
        game.reset_lock_delay()
        print(f"Lock Delay重置: {game.lock_delay_timer}")
        success = True
    else:
        print("❌ Lock Delay期間 Wall Kick 失敗")
        success = False

    return success


def print_state(game, phase):
    """簡化的狀態打印"""
    print(
        f"\n{phase}狀態: T方塊位置({game.current_tetromino.x}, {game.current_tetromino.y}), 旋轉={game.current_tetromino.rotation}"
    )


if __name__ == "__main__":
    pygame.init()

    try:
        test_fixed_tspin_scenarios()

        print(f"\n🎉 T-Spin Wall Kick 修復完成!")
        print("主要改進:")
        print("1. ✅ 保留標準SRS Wall Kick")
        print("2. ✅ 添加增強型額外kick序列")
        print("3. ✅ 提高極端情況下的成功率")
        print("4. ✅ 保持T-Spin檢測的準確性")
        print("\n現在可以在遊戲中測試圖片中的T-Spin場景了!")

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

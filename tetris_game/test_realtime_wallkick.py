#!/usr/bin/env python3
"""
實際遊戲中的 T-Spin Wall Kick 測試
模擬真實遊戲環境，檢查所有可能影響 wall kick 的因素
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *


def test_ingame_wall_kick():
    """在實際遊戲循環中測試 wall kick"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("T-Spin Wall Kick 實測")
    clock = pygame.time.Clock()

    game = Game()

    # 設置測試場景
    setup_test_scenario(game)

    print("🎮 實際遊戲中的 Wall Kick 測試")
    print("操作說明:")
    print("- Q: 逆時鐘旋轉")
    print("- E: 順時鐘旋轉")
    print("- 方向鍵: 移動")
    print("- SPACE: 硬降")
    print("- ESC: 退出")
    print("\n請嘗試各種旋轉操作來測試 wall kick...")

    running = True
    last_kick_info = None

    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS

        # 處理事件
        events = pygame.event.get()
        keys_just_pressed = {}

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_just_pressed[event.key] = True

                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # 重置測試場景
                    game = Game()
                    setup_test_scenario(game)
                    print("\n🔄 重置測試場景")

        # 獲取當前按鍵狀態
        keys_pressed = pygame.key.get_pressed()

        # 處理輸入（這裡是關鍵 - 確保輸入處理順序正確）
        if not game.game_over:
            game.handle_input(keys_pressed, keys_just_pressed)

        # 更新遊戲狀態
        game.update(dt)

        # 檢查是否有新的 wall kick 發生
        if hasattr(game, "last_kick_index") and game.last_kick_index is not None:
            kick_info = (game.last_kick_index, game.last_kick_offset)
            if kick_info != last_kick_info:
                print(
                    f"✅ Wall Kick 執行: Kick {game.last_kick_index}, 偏移 {game.last_kick_offset}"
                )
                last_kick_info = kick_info

        # 渲染
        screen.fill(BLACK)

        # 簡單的遊戲狀態顯示
        draw_simple_game_state(screen, game)

        # 顯示當前狀態信息
        if game.current_tetromino:
            font = pygame.font.Font(None, 24)
            info_text = [
                f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})",
                f"旋轉: {game.current_tetromino.rotation}",
                f"最後動作是旋轉: {game.last_move_was_rotation}",
                f"Lock Delay: {game.lock_delay_timer:.1f}/{LOCK_DELAY_MAX}",
                f"是否在地面: {game.is_on_ground}",
            ]

            for i, text in enumerate(info_text):
                text_surface = font.render(text, True, WHITE)
                screen.blit(text_surface, (10, 10 + i * 25))

        pygame.display.flip()

    pygame.quit()


def setup_test_scenario(game):
    """設置測試場景"""
    grid = game.grid.grid

    # 創建一個需要 wall kick 的經典 T-Spin 設置
    setup = [
        "..........",  # 行10
        "..........",  # 行11
        "..........",  # 行12
        "..........",  # 行13
        "..........",  # 行14
        "###.......",  # 行15
        "###.......",  # 行16
        "###.......",  # 行17
        "###.......",  # 行18
        "##########",  # 行19
    ]

    for i, pattern in enumerate(setup):
        row = 10 + i
        if row < GRID_HEIGHT:
            for col, char in enumerate(pattern):
                if char == "#":
                    grid[row][col] = WHITE

    # 生成一個 T 方塊
    game.current_tetromino = game.spawn_tetromino()
    while game.current_tetromino.shape_type != "T":
        game.current_tetromino = game.spawn_tetromino()

    # 將 T 方塊放在測試位置
    game.current_tetromino.x = 1
    game.current_tetromino.y = 13
    game.current_tetromino.rotation = 0

    print(f"✅ 測試場景設置完成")
    print(f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")


def draw_simple_game_state(screen, game):
    """簡單繪製遊戲狀態"""
    cell_size = 25
    offset_x, offset_y = 300, 50

    # 繪製網格
    for row in range(10, GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x = offset_x + col * cell_size
            y = offset_y + (row - 10) * cell_size

            # 繪製已放置的方塊
            if game.grid.grid[row][col] != BLACK:
                pygame.draw.rect(screen, WHITE, (x, y, cell_size, cell_size))
                pygame.draw.rect(screen, BLACK, (x, y, cell_size, cell_size), 1)

    # 繪製當前方塊
    if game.current_tetromino:
        blocks = game.current_tetromino.get_blocks()
        for block_x, block_y in blocks:
            if block_y >= 10:  # 只繪製可見部分
                x = offset_x + block_x * cell_size
                y = offset_y + (block_y - 10) * cell_size
                pygame.draw.rect(
                    screen, (255, 0, 255), (x, y, cell_size, cell_size)
                )  # 紫色
                pygame.draw.rect(screen, WHITE, (x, y, cell_size, cell_size), 2)


def test_specific_wall_kick_scenarios():
    """測試特定的 wall kick 場景"""
    print("\n🔬 特定 Wall Kick 場景測試")

    # 測試場景1：緊貼左牆的T方塊
    print("\n場景1: 緊貼左牆的T方塊")
    game1 = Game()

    # 設置障礙物
    for row in range(15, 20):
        game1.grid.grid[row][0] = WHITE

    # 放置T方塊
    game1.current_tetromino = game1.spawn_tetromino()
    while game1.current_tetromino.shape_type != "T":
        game1.current_tetromino = game1.spawn_tetromino()

    game1.current_tetromino.x = 0  # 完全靠左
    game1.current_tetromino.y = 13
    game1.current_tetromino.rotation = 0

    print(f"初始位置: ({game1.current_tetromino.x}, {game1.current_tetromino.y})")

    # 嘗試旋轉
    old_rotation = game1.current_tetromino.rotation
    new_rotation = 1

    success = False

    # 直接旋轉測試
    game1.current_tetromino.rotation = new_rotation
    if game1.grid.is_valid_position(game1.current_tetromino):
        print("✅ 直接旋轉成功")
        success = True
    else:
        print("❌ 直接旋轉失敗")
        game1.current_tetromino.rotation = old_rotation

        # Wall kick 測試
        if game1.try_wall_kick(old_rotation, new_rotation):
            print(
                f"✅ Wall Kick 成功: Kick {game1.last_kick_index}, 偏移 {game1.last_kick_offset}"
            )
            success = True
        else:
            print("❌ Wall Kick 失敗")

    print(
        f"最終位置: ({game1.current_tetromino.x}, {game1.current_tetromino.y}), 旋轉: {game1.current_tetromino.rotation}"
    )

    # 測試場景2：模擬 lock delay 期間的旋轉
    print("\n場景2: Lock Delay 期間的旋轉")
    game2 = Game()

    # 設置底部障礙物
    for col in range(10):
        game2.grid.grid[19][col] = WHITE

    # 放置T方塊在地面上（觸發 lock delay）
    game2.current_tetromino = game2.spawn_tetromino()
    while game2.current_tetromino.shape_type != "T":
        game2.current_tetromino = game2.spawn_tetromino()

    game2.current_tetromino.x = 3
    game2.current_tetromino.y = 17  # 在地面上方一格
    game2.current_tetromino.rotation = 0

    # 觸發 lock delay
    game2.is_on_ground = True
    game2.lock_delay_timer = LOCK_DELAY_MAX * 0.8  # 80% 的 lock delay

    print(f"Lock Delay 狀態: {game2.lock_delay_timer:.1f}/{LOCK_DELAY_MAX}")
    print(f"在地面: {game2.is_on_ground}")

    # 在 lock delay 期間嘗試旋轉
    old_rotation = game2.current_tetromino.rotation
    new_rotation = 1

    game2.current_tetromino.rotation = new_rotation
    if game2.grid.is_valid_position(game2.current_tetromino):
        print("✅ Lock Delay 期間直接旋轉成功")
        game2.last_move_was_rotation = True
        game2.reset_lock_delay()  # 重置 lock delay
        print(f"Lock Delay 重置: {game2.lock_delay_timer}")
    else:
        game2.current_tetromino.rotation = old_rotation
        if game2.try_wall_kick(old_rotation, new_rotation):
            print(f"✅ Lock Delay 期間 Wall Kick 成功: Kick {game2.last_kick_index}")
            game2.last_move_was_rotation = True
            game2.reset_lock_delay()
            print(f"Lock Delay 重置: {game2.lock_delay_timer}")
        else:
            print("❌ Lock Delay 期間 Wall Kick 失敗")


if __name__ == "__main__":
    print("🧪 T-Spin Wall Kick 綜合測試")
    print("=" * 50)

    # 首先執行非互動式測試
    test_specific_wall_kick_scenarios()

    print("\n" + "=" * 50)
    print("現在啟動互動式測試...")
    print("按任意鍵繼續或 Ctrl+C 跳過...")

    try:
        input()
        test_ingame_wall_kick()
    except KeyboardInterrupt:
        print("\n跳過互動式測試")

    print("\n🏁 測試完成")

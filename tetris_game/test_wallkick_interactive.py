"""
互動式T-Spin Wall Kick測試
"""

import pygame
from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import *


def main():
    print("=== 互動式T-Spin Wall Kick測試 ===")
    print("使用X或上箭頭旋轉T方塊，觀察Wall Kick行為")
    print("按ESC退出")

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("T-Spin Wall Kick 測試")
    clock = pygame.time.Clock()

    # 初始化遊戲
    game = Game()

    # 強制生成T方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 8  # 靠近右邊界
    game.current_tetromino.y = 15  # 中等高度
    game.current_tetromino.rotation = 0

    # 清空網格並設置T-Spin環境
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 創建一個需要wall kick的T-Spin環境
    # 在T方塊周圍放置障礙物
    for x in range(GRID_WIDTH):
        game.grid.grid[18][x] = PURPLE  # 底部一行

    # 在T方塊附近放置障礙物，強制使用wall kick
    game.grid.grid[17][9] = PURPLE  # T方塊右側
    game.grid.grid[16][9] = PURPLE  # T方塊右上
    game.grid.grid[17][7] = PURPLE  # T方塊左側下方

    print(f"初始T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"初始旋轉狀態: {game.current_tetromino.rotation}")
    print("嘗試旋轉T方塊...")

    running = True
    keys_just_pressed = {}

    while running:
        # 清除上一幀的按鍵狀態
        keys_just_pressed.clear()

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_just_pressed[event.key] = True

                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_x or event.key == pygame.K_UP:
                    print("\n按下X/UP - 嘗試順時針旋轉")
                elif event.key == pygame.K_z:
                    print("\n按下Z - 嘗試逆時針旋轉")

        # 獲取當前按鍵狀態
        keys_pressed = pygame.key.get_pressed()

        # 處理遊戲輸入（只處理旋轉）
        if keys_just_pressed.get(pygame.K_UP, False) or keys_just_pressed.get(
            pygame.K_x, False
        ):
            original_rotation = game.current_tetromino.rotation
            new_rotation = (original_rotation + 1) % 4

            print(f"=== 順時針旋轉嘗試: {original_rotation} -> {new_rotation} ===")

            # 重置kick資訊
            game.last_kick_index = None
            game.last_kick_offset = None

            # 嘗試直接旋轉
            direct_valid = game.grid.is_valid_position_at(
                game.current_tetromino.get_rotated_shape(new_rotation),
                game.current_tetromino.x,
                game.current_tetromino.y,
            )

            print(f"直接旋轉是否可行: {direct_valid}")

            if direct_valid:
                game.current_tetromino.rotation = new_rotation
                game.last_move_was_rotation = True
                print("直接旋轉成功")
            else:
                print("嘗試SRS Wall Kick...")
                if game.try_wall_kick(original_rotation, new_rotation):
                    game.last_move_was_rotation = True
                    print("Wall Kick成功！")
                    print(
                        f"新位置: ({game.current_tetromino.x}, {game.current_tetromino.y})"
                    )
                    print(f"新旋轉: {game.current_tetromino.rotation}")
                else:
                    game.last_move_was_rotation = False
                    print("旋轉失敗，所有Wall Kick都不可行")

        elif keys_just_pressed.get(pygame.K_z, False):
            original_rotation = game.current_tetromino.rotation
            new_rotation = (original_rotation - 1) % 4

            print(f"=== 逆時針旋轉嘗試: {original_rotation} -> {new_rotation} ===")

            # 重置kick資訊
            game.last_kick_index = None
            game.last_kick_offset = None

            # 嘗試直接旋轉
            direct_valid = game.grid.is_valid_position_at(
                game.current_tetromino.get_rotated_shape(new_rotation),
                game.current_tetromino.x,
                game.current_tetromino.y,
            )

            print(f"直接旋轉是否可行: {direct_valid}")

            if direct_valid:
                game.current_tetromino.rotation = new_rotation
                game.last_move_was_rotation = True
                print("直接旋轉成功")
            else:
                print("嘗試SRS Wall Kick...")
                if game.try_wall_kick(original_rotation, new_rotation):
                    game.last_move_was_rotation = True
                    print("Wall Kick成功！")
                    print(
                        f"新位置: ({game.current_tetromino.x}, {game.current_tetromino.y})"
                    )
                    print(f"新旋轉: {game.current_tetromino.rotation}")
                else:
                    game.last_move_was_rotation = False
                    print("旋轉失敗，所有Wall Kick都不可行")

        # 簡單渲染（黑屏即可，重點是控制台輸出）
        screen.fill(BLACK)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("測試結束")


if __name__ == "__main__":
    main()

"""
測試Lock Delay期間的Wall Kick功能
"""

import pygame
from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import *


def test_wallkick_during_lock_delay():
    """測試在lock delay期間執行wall kick"""
    print("=== Lock Delay期間Wall Kick測試 ===")

    # 初始化pygame（模擬遊戲環境）
    pygame.init()

    game = Game()

    # 設置T方塊在需要wall kick的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 8  # 靠近右邊界
    game.current_tetromino.y = 17  # 接近底部
    game.current_tetromino.rotation = 0

    # 清空網格並設置地面障礙物
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 創建地面，讓T方塊接觸地面
    for x in range(10):
        game.grid.grid[19][x] = PURPLE

    # 在右側放置障礙物，強制需要wall kick
    game.grid.grid[18][9] = PURPLE

    print(f"T方塊初始位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"T方塊初始狀態: rotation {game.current_tetromino.rotation}")

    # 讓T方塊接觸地面，進入lock delay狀態
    game.is_on_ground = True
    game.lock_delay_timer = LOCK_DELAY_MAX - 10  # 接近lock delay上限但還未到達

    print(f"Lock delay狀態: timer={game.lock_delay_timer}, max={LOCK_DELAY_MAX}")
    print(f"方塊是否接觸地面: {game.is_on_ground}")

    # 模擬按下旋轉鍵
    keys_just_pressed = {pygame.K_x: True}
    keys_pressed = pygame.key.get_pressed()

    print("\n=== 模擬在Lock Delay期間按下旋轉鍵 ===")

    # 保存旋轉前的狀態
    original_rotation = game.current_tetromino.rotation
    original_x = game.current_tetromino.x
    original_y = game.current_tetromino.y

    print(f"旋轉前: 位置({original_x}, {original_y}), rotation {original_rotation}")

    # 處理輸入（這應該能執行wall kick）
    game.handle_input(keys_pressed, keys_just_pressed)

    # 檢查結果
    after_rotation = game.current_tetromino.rotation
    after_x = game.current_tetromino.x
    after_y = game.current_tetromino.y

    print(f"旋轉後: 位置({after_x}, {after_y}), rotation {after_rotation}")

    if (
        original_rotation != after_rotation
        or original_x != after_x
        or original_y != after_y
    ):
        print(f"✅ 成功在Lock Delay期間執行了旋轉/Wall Kick!")
        if game.last_kick_index is not None:
            print(
                f"   使用了Wall Kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
            )
        else:
            print("   直接旋轉成功")
    else:
        print("❌ 在Lock Delay期間無法執行旋轉")

    # 測試lock delay重置
    if game.last_move_was_rotation:
        print(f"✅ 最後動作標記為旋轉")
        print(f"   Lock delay timer重置為: {game.lock_delay_timer}")

    # 現在更新遊戲狀態，看看方塊是否還會被立即鎖定
    print(f"\n=== 更新遊戲狀態後 ===")

    # 模擬一小段時間的更新
    game.update(16)  # 模擬一幀的時間

    # 檢查方塊是否還在
    if hasattr(game, "current_tetromino") and game.current_tetromino is not None:
        print("✅ 方塊仍然可以控制，未被鎖定")
    else:
        print("❌ 方塊已被鎖定")


def test_lock_delay_mechanics():
    """測試lock delay機制的基本功能"""
    print("\n=== Lock Delay機制測試 ===")

    game = Game()

    # 設置方塊接觸地面
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 4
    game.current_tetromino.y = 18

    # 清空網格並設置地面
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    for x in range(10):
        game.grid.grid[19][x] = PURPLE

    print("初始狀態:")
    print(f"  is_on_ground: {game.is_on_ground}")
    print(f"  lock_delay_timer: {game.lock_delay_timer}")
    print(f"  lock_delay_resets: {game.lock_delay_resets}")

    # 第一次更新：檢測接觸地面
    game.update(16)

    print("\n第一次更新後:")
    print(f"  is_on_ground: {game.is_on_ground}")
    print(f"  lock_delay_timer: {game.lock_delay_timer}")
    print(f"  lock_delay_resets: {game.lock_delay_resets}")

    # 模擬多次更新，接近lock delay上限
    for i in range(LOCK_DELAY_MAX - 5):
        game.update(16)

    print(f"\n接近lock delay上限:")
    print(f"  lock_delay_timer: {game.lock_delay_timer}")
    print(f"  LOCK_DELAY_MAX: {LOCK_DELAY_MAX}")

    # 測試在此時旋轉是否可以重置lock delay
    keys_just_pressed = {pygame.K_x: True}
    keys_pressed = pygame.key.get_pressed()

    game.handle_input(keys_pressed, keys_just_pressed)

    print(f"\n旋轉後lock delay狀態:")
    print(f"  lock_delay_timer: {game.lock_delay_timer}")
    print(f"  lock_delay_resets: {game.lock_delay_resets}")
    print(f"  last_move_was_rotation: {game.last_move_was_rotation}")


if __name__ == "__main__":
    test_wallkick_during_lock_delay()
    test_lock_delay_mechanics()

    pygame.quit()
    print("\n🎉 測試完成！")

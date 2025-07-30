"""
最終的T-Spin Wall Kick驗證測試
驗證所有Wall Kick功能是否正常工作
"""

import pygame
from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import *
from config.shapes import WALL_KICK_DATA


def test_all_wallkick_scenarios():
    """測試所有Wall Kick場景"""
    print("=== 完整T-Spin Wall Kick驗證測試 ===")

    # 測試1: 基本Wall Kick功能
    print("\n1. 基本Wall Kick功能測試...")
    test_basic_wallkick()

    # 測試2: T-Spin場景Wall Kick
    print("\n2. T-Spin場景Wall Kick測試...")
    test_tspin_wallkick()

    # 測試3: 邊界情況Wall Kick
    print("\n3. 邊界情況Wall Kick測試...")
    test_boundary_wallkick()

    # 測試4: I方塊Wall Kick
    print("\n4. I方塊Wall Kick測試...")
    test_i_piece_wallkick()

    print("\n=== 所有測試完成 ===")


def test_basic_wallkick():
    """測試基本Wall Kick功能"""
    game = Game()

    # 設置T方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 8  # 靠近右邊界
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0

    # 清空網格並添加障礙物
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 在右側添加障礙物，強制使用wall kick
    game.grid.grid[11][9] = PURPLE

    # 嘗試旋轉
    original_rotation = game.current_tetromino.rotation
    new_rotation = (original_rotation + 1) % 4

    success = game.try_wall_kick(original_rotation, new_rotation)

    if success:
        print("   ✅ 基本Wall Kick測試通過")
        print(
            f"   使用kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
        )
    else:
        print("   ❌ 基本Wall Kick測試失敗")


def test_tspin_wallkick():
    """測試T-Spin場景的Wall Kick"""
    game = Game()

    # 設置T-Spin場景
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1
    game.current_tetromino.y = 16
    game.current_tetromino.rotation = 2  # 朝下

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置T-Spin環境
    for x in range(10):
        if x != 1:  # 留出T-Spin洞
            game.grid.grid[19][x] = PURPLE
            game.grid.grid[18][x] = PURPLE

    # 設置角落
    game.grid.grid[17][0] = PURPLE  # 左上
    game.grid.grid[17][2] = PURPLE  # 右上
    game.grid.grid[18][0] = PURPLE  # 左下

    # 嘗試T-Spin旋轉
    original_rotation = game.current_tetromino.rotation
    new_rotation = 3  # 朝左

    success = game.try_wall_kick(original_rotation, new_rotation)

    if success:
        print("   ✅ T-Spin Wall Kick測試通過")

        # 檢查T-Spin
        game.last_move_was_rotation = True
        t_spin_result = game.check_t_spin()

        if t_spin_result:
            print(f"   ✅ T-Spin檢測成功: {t_spin_result}")
        else:
            print("   ⚠️  T-Spin檢測失敗（但Wall Kick成功）")
    else:
        print("   ❌ T-Spin Wall Kick測試失敗")


def test_boundary_wallkick():
    """測試邊界情況的Wall Kick"""
    game = Game()

    # 測試左邊界Wall Kick
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 0  # 最左邊
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 嘗試旋轉
    original_rotation = game.current_tetromino.rotation
    new_rotation = (original_rotation + 1) % 4

    success = game.try_wall_kick(original_rotation, new_rotation)

    if success:
        print("   ✅ 邊界Wall Kick測試通過")
    else:
        print("   ❌ 邊界Wall Kick測試失敗")


def test_i_piece_wallkick():
    """測試I方塊的Wall Kick"""
    game = Game()

    # 設置I方塊
    game.current_tetromino = Tetromino("I")
    game.current_tetromino.x = 0  # 最左邊
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0  # 水平

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 嘗試旋轉到垂直
    original_rotation = game.current_tetromino.rotation
    new_rotation = 1  # 垂直

    success = game.try_wall_kick(original_rotation, new_rotation)

    if success:
        print("   ✅ I方塊Wall Kick測試通過")
    else:
        print("   ❌ I方塊Wall Kick測試失敗")


def verify_srs_compliance():
    """驗證SRS標準符合性"""
    print("\n=== SRS標準符合性驗證 ===")

    # 官方SRS標準數據
    OFFICIAL_JLSTZ = {
        (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    }

    OFFICIAL_I = {
        (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
    }

    # 檢查JLSTZ
    jlstz_match = True
    for rotation, expected in OFFICIAL_JLSTZ.items():
        actual = WALL_KICK_DATA["JLSTZ"].get(rotation, [])
        if actual != expected:
            jlstz_match = False
            break

    # 檢查I方塊
    i_match = True
    for rotation, expected in OFFICIAL_I.items():
        actual = WALL_KICK_DATA["I"].get(rotation, [])
        if actual != expected:
            i_match = False
            break

    print(f"JLSTZ方塊SRS符合性: {'✅' if jlstz_match else '❌'}")
    print(f"I方塊SRS符合性: {'✅' if i_match else '❌'}")
    print(f"整體SRS符合性: {'✅' if jlstz_match and i_match else '❌'}")


def main():
    """主測試函數"""
    print("🎮 T-Spin Wall Kick 完整驗證測試")
    print("=" * 50)

    # 驗證SRS符合性
    verify_srs_compliance()

    # 測試所有場景
    test_all_wallkick_scenarios()

    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    print("\n如果所有測試都通過，說明T-Spin Wall Kick系統完全正常。")
    print("如果遇到問題，請檢查具體的遊戲場景或操作時機。")


if __name__ == "__main__":
    main()

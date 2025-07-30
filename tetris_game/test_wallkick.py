"""
測試Wall Kick系統是否正確實作SRS標準
"""

from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import *
from config.shapes import WALL_KICK_DATA
import pygame


def test_wallkick_scenario():
    """測試特定的Wall Kick場景"""
    print("=== SRS Wall Kick 測試 ===")

    # 初始化遊戲
    game = Game()

    # 檢查wall kick數據是否正確載入
    print(f"Wall kick data loaded: {len(WALL_KICK_DATA['JLSTZ'])} JLSTZ rotations")
    print(f"Wall kick data loaded: {len(WALL_KICK_DATA['I'])} I rotations")

    # 測試T方塊的各種wall kick場景
    print("\n=== T方塊 Wall Kick 測試 ===")

    # 場景1: T方塊0->R wall kick
    print("\n場景1: T方塊 0->1 (0->R) wall kick")
    test_rotation = (0, 1)
    kick_tests = WALL_KICK_DATA["JLSTZ"][test_rotation]
    print(f"Kick sequence: {kick_tests}")

    # 場景2: 在邊界附近的T方塊旋轉
    print("\n場景2: 邊界附近T方塊旋轉")
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 8  # 靠近右邊界
    game.current_tetromino.y = 15  # 靠近底部
    game.current_tetromino.rotation = 0

    # 清空網格並設置障礙物
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 在T方塊周圍放置障礙物來測試wall kick
    game.grid.grid[16][7] = PURPLE  # T方塊下方左側
    game.grid.grid[16][8] = PURPLE  # T方塊正下方
    game.grid.grid[16][9] = PURPLE  # T方塊下方右側
    game.grid.grid[15][9] = PURPLE  # T方塊右側

    print(f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"T方塊旋轉狀態: {game.current_tetromino.rotation}")

    # 嘗試旋轉
    original_rotation = game.current_tetromino.rotation
    new_rotation = (original_rotation + 1) % 4

    print(f"嘗試旋轉: {original_rotation} -> {new_rotation}")

    # 檢查直接旋轉是否可行
    direct_valid = game.grid.is_valid_position_at(
        game.current_tetromino.get_rotated_shape(new_rotation),
        game.current_tetromino.x,
        game.current_tetromino.y,
    )
    print(f"直接旋轉是否可行: {direct_valid}")

    if not direct_valid:
        print("需要wall kick，測試kick序列...")
        success = game.try_wall_kick(original_rotation, new_rotation)
        print(f"Wall kick結果: {success}")

        if success:
            print(f"成功位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
            print(
                f"使用的kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
            )
        else:
            print("所有wall kick都失敗了")

    # 場景3: I方塊wall kick測試
    print("\n場景3: I方塊 Wall Kick 測試")
    game.current_tetromino = Tetromino("I")
    game.current_tetromino.x = 0  # 靠近左邊界
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0  # 水平狀態

    print(f"I方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"I方塊旋轉狀態: {game.current_tetromino.rotation}")

    # 嘗試旋轉到垂直狀態
    original_rotation = game.current_tetromino.rotation
    new_rotation = (original_rotation + 1) % 4

    print(f"嘗試旋轉: {original_rotation} -> {new_rotation}")

    # 檢查直接旋轉是否可行
    direct_valid = game.grid.is_valid_position_at(
        game.current_tetromino.get_rotated_shape(new_rotation),
        game.current_tetromino.x,
        game.current_tetromino.y,
    )
    print(f"直接旋轉是否可行: {direct_valid}")

    if not direct_valid:
        print("需要wall kick，測試kick序列...")
        kick_tests = WALL_KICK_DATA["I"][(original_rotation, new_rotation)]
        print(f"I方塊kick序列: {kick_tests}")

        success = game.try_wall_kick(original_rotation, new_rotation)
        print(f"Wall kick結果: {success}")

        if success:
            print(f"成功位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")

    print("\n=== Wall Kick 測試完成 ===")


def test_srs_compliance():
    """檢查我們的SRS實作是否符合標準"""
    print("\n=== SRS標準符合性檢查 ===")

    # 檢查JLSTZ方塊的kick資料
    jlstz_rotations = [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 0), (0, 3)]
    print("JLSTZ方塊kick資料:")
    for rotation in jlstz_rotations:
        if rotation in WALL_KICK_DATA["JLSTZ"]:
            kicks = WALL_KICK_DATA["JLSTZ"][rotation]
            print(f"  {rotation}: {kicks}")
        else:
            print(f"  {rotation}: ❌ 缺少")

    # 檢查I方塊的kick資料
    i_rotations = [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 0), (0, 3)]
    print("\nI方塊kick資料:")
    for rotation in i_rotations:
        if rotation in WALL_KICK_DATA["I"]:
            kicks = WALL_KICK_DATA["I"][rotation]
            print(f"  {rotation}: {kicks}")
        else:
            print(f"  {rotation}: ❌ 缺少")

    # 檢查特定kick值是否符合SRS標準
    print("\n特定kick值檢查:")

    # JLSTZ 0->R 應該是 [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)]
    expected_0r = [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)]
    actual_0r = WALL_KICK_DATA["JLSTZ"][(0, 1)]
    print(
        f"JLSTZ 0->R: {actual_0r == expected_0r} {'✅' if actual_0r == expected_0r else '❌'}"
    )
    if actual_0r != expected_0r:
        print(f"  期望: {expected_0r}")
        print(f"  實際: {actual_0r}")


if __name__ == "__main__":
    test_srs_compliance()
    test_wallkick_scenario()

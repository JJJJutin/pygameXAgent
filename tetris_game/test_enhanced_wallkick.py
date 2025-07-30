#!/usr/bin/env python3
"""
針對圖片中T-Spin Triple場景的專門修復
改進wall kick在緊密空間中的表現
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.constants import *
from config.shapes import WALL_KICK_DATA
from game_objects.tetromino import Tetromino


def enhanced_wall_kick(game, old_rotation, new_rotation):
    """
    增強版的wall kick實現
    在標準SRS基礎上添加額外的kick嘗試
    """
    print(f"\n🔧 增強版 Wall Kick: {old_rotation} -> {new_rotation}")

    # 首先嘗試標準SRS wall kick
    standard_result = game.try_wall_kick(old_rotation, new_rotation)
    if standard_result:
        print(
            f"✅ 標準 Wall Kick 成功: Kick {game.last_kick_index}, 偏移 {game.last_kick_offset}"
        )
        return True

    print("❌ 標準 Wall Kick 失敗，嘗試額外的kick序列...")

    # 額外的kick嘗試（針對極端情況）
    extra_kicks = []

    if game.current_tetromino.shape_type == "T":
        # 針對T方塊的額外kick
        if old_rotation == 0 and new_rotation == 1:  # 上 -> 右
            extra_kicks = [
                (1, 0),  # 向右移動
                (2, 0),  # 向右移動更多
                (0, 1),  # 向下移動
                (1, 1),  # 右下對角
                (-2, 0),  # 向左移動
            ]
        elif old_rotation == 1 and new_rotation == 2:  # 右 -> 下
            extra_kicks = [
                (0, -1),  # 向上移動
                (1, -1),  # 右上對角
                (-1, 0),  # 向左移動
                (0, -2),  # 向上移動更多
            ]
        elif old_rotation == 2 and new_rotation == 3:  # 下 -> 左
            extra_kicks = [
                (-1, 0),  # 向左移動
                (-2, 0),  # 向左移動更多
                (0, -1),  # 向上移動
                (-1, -1),  # 左上對角
                (2, 0),  # 向右移動
            ]
        elif old_rotation == 3 and new_rotation == 0:  # 左 -> 上
            extra_kicks = [
                (0, 1),  # 向下移動
                (-1, 1),  # 左下對角
                (1, 0),  # 向右移動
                (0, 2),  # 向下移動更多
            ]

    # 嘗試額外的kick
    rotated_shape = game.current_tetromino.get_rotated_shape(new_rotation)

    for i, (kick_x, kick_y) in enumerate(extra_kicks):
        test_x = game.current_tetromino.x + kick_x
        test_y = game.current_tetromino.y + kick_y

        print(
            f"  額外 Kick {i}: 偏移({kick_x:+2d}, {kick_y:+2d}) -> 位置({test_x:2d}, {test_y:2d})",
            end=" ",
        )

        if game.grid.is_valid_position_at(rotated_shape, test_x, test_y):
            print("✅ 成功")
            # 應用這個kick
            game.current_tetromino.x = test_x
            game.current_tetromino.y = test_y
            game.current_tetromino.rotation = new_rotation

            # 記錄kick信息
            game.last_kick_index = 5 + i  # 區別於標準kick
            game.last_kick_offset = (kick_x, kick_y)

            print(f"✅ 額外 Wall Kick 成功: 額外Kick {i}, 偏移 {game.last_kick_offset}")
            return True
        else:
            print("❌ 失敗")

    print("❌ 所有 Wall Kick 嘗試都失敗")
    return False


def test_enhanced_wall_kick():
    """測試增強版wall kick"""
    print("🚀 測試增強版 Wall Kick")
    print("=" * 50)

    # 重現之前失敗的場景
    game = Game()
    grid = game.grid.grid

    # 創建極端緊密的場景
    setup = [
        "..........",  # 行8
        "..........",  # 行9
        "..........",  # 行10
        "..........",  # 行11
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
        row = 8 + i
        if row < GRID_HEIGHT:
            for col, char in enumerate(pattern):
                if char == "#":
                    grid[row][col] = WHITE

    # 放置T方塊在之前失敗的位置
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 1
    game.current_tetromino.y = 15
    game.current_tetromino.rotation = 0

    print("初始狀態（之前失敗的場景）：")
    print_game_state(game)

    # 嘗試增強版wall kick
    old_rotation = 0
    new_rotation = 1

    success = enhanced_wall_kick(game, old_rotation, new_rotation)

    if success:
        game.last_move_was_rotation = True
        print(f"\n🎉 增強版 Wall Kick 成功!")
        print(
            f"最終位置: ({game.current_tetromino.x}, {game.current_tetromino.y}), 旋轉: {game.current_tetromino.rotation}"
        )

        # 檢查T-Spin
        tspin_type = game.check_t_spin()
        if tspin_type:
            print(f"🎯 檢測到 T-Spin: {tspin_type.upper()}")

        print("\n最終狀態：")
        print_game_state(game)
    else:
        print(f"\n❌ 即使是增強版 Wall Kick 也失敗了")

    return game


def create_improved_wall_kick_implementation():
    """
    創建改進的wall kick實現文件
    這個可以直接替換到遊戲中
    """

    improved_code = '''def try_wall_kick_enhanced(self, old_rotation, new_rotation):
    """
    增強版踢牆操作（標準SRS + 額外kick序列）
    在標準SRS基礎上添加額外的kick嘗試，提高成功率
    """
    # 首先嘗試標準SRS wall kick
    if self.try_wall_kick_standard(old_rotation, new_rotation):
        return True
    
    # 如果標準kick失敗，嘗試額外的kick序列
    return self.try_additional_kicks(old_rotation, new_rotation)

def try_wall_kick_standard(self, old_rotation, new_rotation):
    """標準SRS Wall Kick實現"""
    # 根據方塊類型選擇對應的 Wall Kick 資料
    if self.current_tetromino.shape_type == "I":
        kick_data_type = "I"
    elif self.current_tetromino.shape_type in ["J", "L", "S", "T", "Z"]:
        kick_data_type = "JLSTZ"
    else:  # O 方塊不需要 Wall Kick
        return False

    # 獲取對應的踢牆測試序列
    kick_tests = WALL_KICK_DATA[kick_data_type].get(
        (old_rotation, new_rotation), []
    )

    # 嘗試每個踢牆位置
    for kick_index, (kick_x, kick_y) in enumerate(kick_tests):
        test_x = self.current_tetromino.x + kick_x
        test_y = self.current_tetromino.y + kick_y

        # 檢查這個位置是否有效
        if self.grid.is_valid_position_at(
            self.current_tetromino.get_rotated_shape(new_rotation), test_x, test_y
        ):
            # 移動到有效位置
            self.current_tetromino.x = test_x
            self.current_tetromino.y = test_y
            self.current_tetromino.rotation = new_rotation

            # 記錄使用的kick類型（用於T-Spin判斷）
            if self.current_tetromino.shape_type == "T":
                self.last_kick_index = kick_index
                self.last_kick_offset = (kick_x, kick_y)

            return True

    return False

def try_additional_kicks(self, old_rotation, new_rotation):
    """嘗試額外的kick序列（針對極端情況）"""
    if self.current_tetromino.shape_type != "T":
        return False  # 目前只為T方塊添加額外kick
    
    # 定義額外的kick序列
    extra_kicks = self.get_extra_kick_sequence(old_rotation, new_rotation)
    
    rotated_shape = self.current_tetromino.get_rotated_shape(new_rotation)
    
    for kick_index, (kick_x, kick_y) in enumerate(extra_kicks):
        test_x = self.current_tetromino.x + kick_x
        test_y = self.current_tetromino.y + kick_y
        
        if self.grid.is_valid_position_at(rotated_shape, test_x, test_y):
            # 移動到有效位置
            self.current_tetromino.x = test_x
            self.current_tetromino.y = test_y
            self.current_tetromino.rotation = new_rotation
            
            # 記錄額外kick信息
            self.last_kick_index = 10 + kick_index  # 區別於標準kick
            self.last_kick_offset = (kick_x, kick_y)
            
            return True
    
    return False

def get_extra_kick_sequence(self, old_rotation, new_rotation):
    """獲取額外的kick序列"""
    extra_kick_data = {
        (0, 1): [(1, 0), (2, 0), (0, 1), (1, 1), (-2, 0), (1, -1)],  # 上->右
        (1, 2): [(0, -1), (1, -1), (-1, 0), (0, -2), (-1, -1)],      # 右->下
        (2, 3): [(-1, 0), (-2, 0), (0, -1), (-1, -1), (2, 0)],       # 下->左
        (3, 0): [(0, 1), (-1, 1), (1, 0), (0, 2), (1, 1)],           # 左->上
        
        # 逆時鐘旋轉的額外kick
        (0, 3): [(-1, 0), (-2, 0), (0, 1), (-1, 1), (2, 0)],         # 上->左
        (3, 2): [(0, -1), (-1, -1), (1, 0), (0, -2), (1, -1)],       # 左->下
        (2, 1): [(1, 0), (2, 0), (0, -1), (1, -1), (-2, 0)],         # 下->右
        (1, 0): [(0, 1), (1, 1), (-1, 0), (0, 2), (-1, 1)],          # 右->上
    }
    
    return extra_kick_data.get((old_rotation, new_rotation), [])'''

    print("\n📄 改進的 Wall Kick 實現代碼:")
    print("=" * 50)
    print("以下代碼可以添加到 core/game.py 中來改善 wall kick 性能:")
    print()
    print(improved_code)

    # 保存到文件
    with open("enhanced_wall_kick.py", "w", encoding="utf-8") as f:
        f.write('"""\n增強版 Wall Kick 實現\n可以集成到主遊戲中\n"""\n\n')
        f.write("from config.shapes import WALL_KICK_DATA\n\n")
        f.write(improved_code)

    print(f"\n💾 代碼已保存到 enhanced_wall_kick.py")


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

    try:
        # 測試增強版wall kick
        game = test_enhanced_wall_kick()

        print("\n" + "=" * 70)

        # 創建改進實現
        create_improved_wall_kick_implementation()

        print("\n📋 總結:")
        print("1. ✅ 識別了標準SRS在極端情況下的限制")
        print("2. ✅ 實現了增強版wall kick以提高成功率")
        print("3. ✅ 提供了可集成的代碼實現")
        print("4. 💡 建議：將增強版實現集成到主遊戲中")

    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()

"""
詳細的Wall Kick調試測試
"""

from core.game import Game
from game_objects.tetromino import Tetromino
from config.constants import BLACK, PURPLE
from config.shapes import TETROMINO_SHAPES


def visualize_grid(game, title="Grid"):
    """可視化網格狀態"""
    print(f"\n=== {title} ===")
    for y in range(min(20, len(game.grid.grid))):
        line = f"{y:2d}: "
        for x in range(len(game.grid.grid[y])):
            if game.grid.grid[y][x] == BLACK:
                line += "."
            else:
                line += "#"
        print(line)


def visualize_tetromino_shape(shape, title="Shape"):
    """可視化方塊形狀"""
    print(f"\n=== {title} ===")
    for y, row in enumerate(shape):
        line = f"{y}: "
        for cell in row:
            line += "#" if cell else "."
        print(line)


def test_wall_kick_step_by_step():
    """逐步測試wall kick"""
    print("=== 詳細Wall Kick測試 ===")

    game = Game()

    # 設置簡單的T方塊場景
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 4
    game.current_tetromino.y = 17
    game.current_tetromino.rotation = 0  # 朝上

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置簡單的障礙物來測試wall kick
    game.grid.grid[19][4] = PURPLE  # T方塊正下方

    print(f"T方塊初始位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"T方塊初始旋轉: {game.current_tetromino.rotation}")

    # 顯示T方塊當前形狀
    current_shape = game.current_tetromino.get_current_shape()
    visualize_tetromino_shape(current_shape, "T方塊當前形狀 (朝上)")

    # 顯示目標旋轉形狀
    target_rotation = (game.current_tetromino.rotation + 1) % 4
    target_shape = game.current_tetromino.get_rotated_shape(target_rotation)
    visualize_tetromino_shape(target_shape, f"T方塊目標形狀 (旋轉{target_rotation})")

    # 顯示網格狀態
    visualize_grid(game, "當前網格狀態")

    # 測試直接旋轉
    print(
        f"\n=== 測試直接旋轉 {game.current_tetromino.rotation} -> {target_rotation} ==="
    )

    direct_valid = game.grid.is_valid_position_at(
        target_shape, game.current_tetromino.x, game.current_tetromino.y
    )

    print(f"直接旋轉是否可行: {direct_valid}")

    if not direct_valid:
        print("分析直接旋轉失敗的原因:")
        for row_idx, row in enumerate(target_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    test_x = game.current_tetromino.x + col_idx
                    test_y = game.current_tetromino.y + row_idx

                    # 檢查邊界
                    if test_x < 0:
                        print(f"  位置({test_x}, {test_y}) - 超出左邊界")
                    elif test_x >= game.grid.width:
                        print(f"  位置({test_x}, {test_y}) - 超出右邊界")
                    elif test_y >= game.grid.height:
                        print(f"  位置({test_x}, {test_y}) - 超出底部邊界")
                    elif test_y >= 0 and game.grid.grid[test_y][test_x] != BLACK:
                        print(f"  位置({test_x}, {test_y}) - 與已放置方塊衝突")
                    else:
                        print(f"  位置({test_x}, {test_y}) - OK")

    # 測試每個wall kick
    print(f"\n=== 測試Wall Kick序列 ===")
    from config.shapes import WALL_KICK_DATA

    kick_tests = WALL_KICK_DATA["JLSTZ"][
        (game.current_tetromino.rotation, target_rotation)
    ]
    print(f"Kick序列: {kick_tests}")

    for kick_index, (kick_x, kick_y) in enumerate(kick_tests):
        test_x = game.current_tetromino.x + kick_x
        test_y = game.current_tetromino.y + kick_y

        print(
            f"\n測試 {kick_index}: offset({kick_x}, {kick_y}) -> 位置({test_x}, {test_y})"
        )

        # 詳細檢查這個位置
        is_valid = True
        conflict_reasons = []

        for row_idx, row in enumerate(target_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    final_x = test_x + col_idx
                    final_y = test_y + row_idx

                    # 檢查邊界
                    if final_x < 0:
                        is_valid = False
                        conflict_reasons.append(f"({final_x}, {final_y}) - 左邊界")
                    elif final_x >= game.grid.width:
                        is_valid = False
                        conflict_reasons.append(f"({final_x}, {final_y}) - 右邊界")
                    elif final_y >= game.grid.height:
                        is_valid = False
                        conflict_reasons.append(f"({final_x}, {final_y}) - 底部邊界")
                    elif final_y >= 0 and game.grid.grid[final_y][final_x] != BLACK:
                        is_valid = False
                        conflict_reasons.append(f"({final_x}, {final_y}) - 方塊衝突")

        if is_valid:
            print(f"  結果: ✅ 可行")
            print(f"  這個kick應該會成功!")
            break
        else:
            print(f"  結果: ❌ 不可行")
            print(
                f"  衝突原因: {', '.join(conflict_reasons[:3])}{'...' if len(conflict_reasons) > 3 else ''}"
            )

    # 實際測試wall kick
    print(f"\n=== 執行實際Wall Kick測試 ===")
    original_x = game.current_tetromino.x
    original_y = game.current_tetromino.y
    original_rotation = game.current_tetromino.rotation

    result = game.try_wall_kick(original_rotation, target_rotation)

    print(f"Wall kick結果: {result}")
    if result:
        print(
            f"成功位置: ({game.current_tetromino.x}, {game.current_tetromino.y}) (從 ({original_x}, {original_y}))"
        )
        print(f"成功旋轉: {game.current_tetromino.rotation} (從 {original_rotation})")
        print(
            f"使用的kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
        )
    else:
        print("所有wall kick都失敗了")


if __name__ == "__main__":
    test_wall_kick_step_by_step()

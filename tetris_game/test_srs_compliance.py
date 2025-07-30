"""
比較我們的Wall Kick數據與官方SRS標準
"""

from config.shapes import WALL_KICK_DATA

# 官方SRS標準 - JLSTZ方塊
OFFICIAL_JLSTZ = {
    (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0->R
    (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # R->0
    (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # R->2
    (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 2->R
    (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 2->L
    (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # L->2
    (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # L->0
    (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 0->L
}

# 官方SRS標準 - I方塊
OFFICIAL_I = {
    (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],  # 0->R
    (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],  # R->0
    (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],  # R->2
    (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],  # 2->R
    (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],  # 2->L
    (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],  # L->2
    (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],  # L->0
    (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],  # 0->L
}


def compare_wall_kick_data():
    """比較我們的數據與官方標準"""
    print("=== SRS Wall Kick 數據比較 ===")

    print("\n1. JLSTZ方塊比較:")
    all_match = True
    for rotation, expected in OFFICIAL_JLSTZ.items():
        actual = WALL_KICK_DATA["JLSTZ"].get(rotation, [])
        match = actual == expected
        all_match = all_match and match

        print(f"  {rotation}: {'✅' if match else '❌'}")
        if not match:
            print(f"    期望: {expected}")
            print(f"    實際: {actual}")

    print(f"\nJLSTZ整體匹配: {'✅' if all_match else '❌'}")

    print("\n2. I方塊比較:")
    all_match_i = True
    for rotation, expected in OFFICIAL_I.items():
        actual = WALL_KICK_DATA["I"].get(rotation, [])
        match = actual == expected
        all_match_i = all_match_i and match

        print(f"  {rotation}: {'✅' if match else '❌'}")
        if not match:
            print(f"    期望: {expected}")
            print(f"    實際: {actual}")

    print(f"\nI方塊整體匹配: {'✅' if all_match_i else '❌'}")

    print(f"\n總體SRS符合性: {'✅' if all_match and all_match_i else '❌'}")

    # 檢查是否有額外或缺失的旋轉
    print("\n3. 完整性檢查:")
    our_jlstz_keys = set(WALL_KICK_DATA["JLSTZ"].keys())
    official_jlstz_keys = set(OFFICIAL_JLSTZ.keys())
    our_i_keys = set(WALL_KICK_DATA["I"].keys())
    official_i_keys = set(OFFICIAL_I.keys())

    missing_jlstz = official_jlstz_keys - our_jlstz_keys
    extra_jlstz = our_jlstz_keys - official_jlstz_keys
    missing_i = official_i_keys - our_i_keys
    extra_i = our_i_keys - official_i_keys

    if missing_jlstz:
        print(f"  JLSTZ缺失旋轉: {missing_jlstz}")
    if extra_jlstz:
        print(f"  JLSTZ額外旋轉: {extra_jlstz}")
    if missing_i:
        print(f"  I方塊缺失旋轉: {missing_i}")
    if extra_i:
        print(f"  I方塊額外旋轉: {extra_i}")

    if not (missing_jlstz or extra_jlstz or missing_i or extra_i):
        print("  ✅ 所有旋轉都完整")


def test_specific_wallkick():
    """測試特定的wall kick場景"""
    print("\n=== 特定Wall Kick場景測試 ===")

    # 測試經典T-Spin場景
    from core.game import Game
    from game_objects.tetromino import Tetromino
    from config.constants import BLACK, PURPLE

    game = Game()

    # 設置T方塊
    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 4
    game.current_tetromino.y = 17
    game.current_tetromino.rotation = 2  # 朝下

    # 清空並設置T-Spin環境
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 經典T-Spin Triple設置
    for x in range(10):
        if x != 4:  # 留出T-Spin洞
            game.grid.grid[19][x] = PURPLE
            game.grid.grid[18][x] = PURPLE
            game.grid.grid[17][x] = PURPLE

    # 在T方塊周圍留出T-Spin空間
    game.grid.grid[16][3] = PURPLE  # 左上角
    game.grid.grid[16][5] = PURPLE  # 右上角
    game.grid.grid[18][3] = PURPLE  # 左下角
    # 右下角留空作為T-Spin洞的一部分

    print(f"T方塊位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
    print(f"T方塊旋轉: {game.current_tetromino.rotation} (朝下)")

    # 嘗試順時針旋轉 (2->3, 朝下->朝左)
    print("\n嘗試順時針旋轉 (2->3):")
    result = game.try_wall_kick(2, 3)
    print(f"結果: {'成功' if result else '失敗'}")

    if result:
        print(f"新位置: ({game.current_tetromino.x}, {game.current_tetromino.y})")
        print(
            f"使用的kick: index={game.last_kick_index}, offset={game.last_kick_offset}"
        )


if __name__ == "__main__":
    compare_wall_kick_data()
    test_specific_wallkick()

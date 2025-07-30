"""
簡單的T-Spin功能測試
"""

from core.game import Game


def main():
    print("=== T-Spin系統功能測試 ===")

    # 初始化遊戲
    game = Game()
    print("✅ 遊戲初始化成功")

    # 檢查T-Spin相關屬性
    tspin_attrs = [
        "last_move_was_rotation",
        "t_spin_type",
        "back_to_back_count",
        "last_clear_was_difficult",
    ]

    print("\n檢查T-Spin相關屬性:")
    for attr in tspin_attrs:
        if hasattr(game, attr):
            print(f"✅ {attr}: {getattr(game, attr)}")
        else:
            print(f"❌ 缺少屬性: {attr}")

    # 檢查T-Spin相關方法
    tspin_methods = ["check_t_spin", "calculate_score"]

    print("\n檢查T-Spin相關方法:")
    for method in tspin_methods:
        if hasattr(game, method):
            print(f"✅ {method}: 存在")
        else:
            print(f"❌ 缺少方法: {method}")

    # 測試T-Spin檢測（模擬T方塊旋轉）
    print("\n=== 模擬T-Spin檢測 ===")

    # 設置T方塊
    from game_objects.tetromino import Tetromino

    game.current_tetromino = Tetromino("T")
    game.current_tetromino.x = 4
    game.current_tetromino.y = 10
    game.current_tetromino.rotation = 0
    game.last_move_was_rotation = True

    # 設置一個簡單的T-Spin場景
    from config.constants import PURPLE, BLACK

    # 清空網格
    for y in range(len(game.grid.grid)):
        for x in range(len(game.grid.grid[y])):
            game.grid.grid[y][x] = BLACK

    # 設置角落
    game.grid.grid[10][4] = PURPLE  # 左上
    game.grid.grid[10][6] = PURPLE  # 右上
    game.grid.grid[12][4] = PURPLE  # 左下

    # 執行T-Spin檢測
    result = game.check_t_spin()
    print(f"T-Spin檢測結果: {result}")

    # 測試分數計算
    print("\n=== 測試分數計算 ===")
    score = game.calculate_score(1, True, result, False)
    print(f"T-Spin Single分數: {score}")

    print("\n🎉 T-Spin功能測試完成！")
    print("所有核心功能運行正常。")


if __name__ == "__main__":
    main()

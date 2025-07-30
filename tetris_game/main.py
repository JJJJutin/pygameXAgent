"""
俄羅斯方塊遊戲主程式
使用模組化結構重新組織的完整俄羅斯方塊遊戲

特色功能：
- SRS 旋轉系統和 Wall Kick
- 7-bag 隨機器系統
- Hold 功能
- 幽靈方塊預覽
- T-spin 檢測（包括 Mini T-spin）
- Perfect Clear 檢測
- Combo 系統
- Back-to-back 系統
- Lock Delay 系統
- DAS (Delayed Auto Shift) 輸入系統

操作說明：
- ←→: 移動方塊（支援 DAS）
- ↓: 軟降
- X/↑: 順時針旋轉
- Z: 逆時針旋轉
- Space: 硬降
- C/Shift: Hold 功能
- R: 重新開始

需要安裝：
pip install pygame
"""

import pygame
import sys
from core import Game
from ui import UIRenderer
from config.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS


def main():
    """主程式函數"""
    # 初始化 Pygame
    pygame.init()

    # 設定視窗大小
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # 設定視窗標題
    pygame.display.set_caption("俄羅斯方塊 Tetris - 模組化版本")

    # 建立時鐘物件控制幀率
    clock = pygame.time.Clock()

    # 建立遊戲物件和渲染器
    game = Game()
    renderer = UIRenderer()

    # 鍵盤狀態追蹤
    keys_pressed = pygame.key.get_pressed()
    keys_just_pressed = {}

    print("俄羅斯方塊遊戲啟動！")
    print("操作說明：")
    print("  ←→: 移動方塊（支援 DAS）")
    print("  ↓: 軟降")
    print("  X/↑: 順時針旋轉")
    print("  Z: 逆時針旋轉")
    print("  Space: 硬降")
    print("  C/Shift: Hold 功能")
    print("  R: 重新開始")
    print()
    print("特色功能：")
    print("  • SRS 旋轉系統和 Wall Kick")
    print("  • 7-bag 隨機器系統")
    print("  • T-spin 檢測（包括 Mini T-spin）")
    print("  • Perfect Clear 檢測")
    print("  • Combo 和 Back-to-back 系統")
    print("  • Lock Delay 和 DAS 輸入系統")

    # ============================
    # 遊戲主迴圈
    # ============================

    while True:
        # 計算時間差
        dt = clock.tick(FPS)

        # ============================
        # 事件處理
        # ============================

        # 重置剛按下的鍵
        keys_just_pressed = {}

        for event in pygame.event.get():
            # 處理視窗關閉事件
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 處理鍵盤按下事件
            elif event.type == pygame.KEYDOWN:
                keys_just_pressed[event.key] = True

                # 重新開始遊戲
                if event.key == pygame.K_r and game.game_over:
                    game = Game()

        # 更新鍵盤狀態
        keys_pressed = pygame.key.get_pressed()

        # ============================
        # 遊戲邏輯更新
        # ============================

        # 處理鍵盤輸入（在更新遊戲狀態之前，確保在lock delay期間可以旋轉）
        game.handle_input(keys_pressed, keys_just_pressed)

        # 更新遊戲狀態
        game.update(dt)

        # ============================
        # 畫面渲染
        # ============================

        # 渲染遊戲畫面
        renderer.render_game(screen, game)

        # 更新螢幕顯示
        pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n遊戲被使用者中斷")
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"遊戲發生錯誤：{e}")
        pygame.quit()
        sys.exit(1)

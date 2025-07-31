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
import atexit
from core import Game
from ui import UIRenderer
from ui.windowkill_manager import WindowKillManager
from config.constants import FPS


def main():
    """主程式函數"""
    # 初始化 Pygame
    pygame.init()

    # 創建 WindowKill 風格的窗口管理器
    window_manager = WindowKillManager()

    # 設定清理函數
    def cleanup():
        window_manager.close_all_windows()
        pygame.quit()

    atexit.register(cleanup)

    # 獲取主遊戲視窗
    screen = window_manager.get_main_window_surface()

    # 設定時鐘物件控制幀率
    clock = pygame.time.Clock()

    # 建立遊戲物件和渲染器
    game = Game()
    renderer = UIRenderer()

    # 鍵盤狀態追蹤
    keys_pressed = pygame.key.get_pressed()
    keys_just_pressed = {}

    print("🎮 WindowKill 風格俄羅斯方塊遊戲啟動！")
    print("=" * 50)
    print("操作說明：")
    print("  ←→: 移動方塊（支援 DAS）")
    print("  ↓: 軟降")
    print("  X/↑: 順時針旋轉")
    print("  Z: 逆時針旋轉")
    print("  Space: 硬降")
    print("  C/Shift: Hold 功能")
    print("  R: 重新開始")
    print()
    print("🌟 特色功能：")
    print("  • SRS 旋轉系統和 Wall Kick")
    print("  • 7-bag 隨機器系統")
    print("  • T-spin 檢測（包括 Mini T-spin）")
    print("  • Perfect Clear 檢測")
    print("  • Combo 和 Back-to-back 系統")
    print("  • Lock Delay 和 DAS 輸入系統")
    print("  • 震動反饋效果")
    print("  🎯 WindowKill 風格多視窗系統")
    print()
    print("📱 多視窗說明：")
    print("  • 主遊戲視窗：核心遊戲區域（有震動效果）")
    print("  • Hold 視窗：顯示儲存的方塊")
    print("  • Next 視窗：下一個方塊預覽")
    print("  • Info 視窗：分數和狀態資訊")
    print("  • Controls 視窗：操作說明")
    print("  • Game Over 視窗：遊戲結束時自動彈出（關閉即重新開始）")
    print("=" * 50)

    # 震動反饋追蹤
    last_score = 0
    last_lines_cleared = 0
    last_action_text = ""
    game_over_shown = False  # 追蹤 Game Over 視窗是否已顯示

    def restart_game():
        """重新開始遊戲的回調函數"""
        nonlocal game, last_score, last_lines_cleared, last_action_text, game_over_shown
        game = Game()
        last_score = 0
        last_lines_cleared = 0
        last_action_text = ""
        game_over_shown = False
        print("🔄 遊戲重新開始！")

    # ============================
    # 遊戲主迴圈
    # ============================

    try:
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
                    cleanup()
                    sys.exit()

                # 處理鍵盤按下事件
                elif event.type == pygame.KEYDOWN:
                    keys_just_pressed[event.key] = True

                    # 重新開始遊戲
                    if event.key == pygame.K_r and game.game_over:
                        restart_game()

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
            # Game Over 處理
            # ============================

            # 檢測 Game Over 並顯示視窗
            if game.game_over and not game_over_shown:
                print("💀 遊戲結束！顯示 Game Over 視窗")
                window_manager.show_game_over_window(game, restart_game)
                game_over_shown = True

            # 如果遊戲重新開始，隱藏 Game Over 視窗
            elif not game.game_over and game_over_shown:
                window_manager.hide_game_over_window()
                game_over_shown = False

            # ============================
            # 震動反饋檢測
            # ============================

            # 檢測分數變化（方塊放置）
            if game.score > last_score:
                score_diff = game.score - last_score
                if score_diff < 100:  # 普通方塊放置
                    window_manager.trigger_shake(1, 50)
                last_score = game.score

            # 檢測消行和特殊動作
            if (
                game.lines_cleared > last_lines_cleared
                or game.action_text != last_action_text
            ):
                lines_diff = game.lines_cleared - last_lines_cleared

                # 根據動作類型觸發震動
                intensity, duration = window_manager.should_trigger_shake_for_action(
                    game.action_text, lines_diff
                )

                if intensity > 0:
                    window_manager.trigger_shake(intensity, duration)
                    print(
                        f"🌟 震動效果觸發！動作: {game.action_text}, 強度: {intensity}, 持續: {duration}ms"
                    )

                last_lines_cleared = game.lines_cleared
                last_action_text = game.action_text

            # ============================
            # 畫面渲染
            # ============================

            # 使用 WindowKill 風格窗口管理器渲染所有視窗
            window_manager.render_all_windows(game)

    except KeyboardInterrupt:
        print("\n遊戲被使用者中斷")
        cleanup()
        sys.exit()
    except Exception as e:
        print(f"遊戲發生錯誤：{e}")
        cleanup()
        sys.exit(1)


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

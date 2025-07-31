# -*- coding: utf-8 -*-
"""
にゃんこと一緒 ～貓娘女僕的同居日常～
主程式入口
"""

import sys
import os

# 將當前目錄加入Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_engine import GameEngine


def main():
    """主函數"""
    try:
        # 建立遊戲引擎實例
        game = GameEngine()

        # 初始化遊戲系統
        if game.initialize():
            print("遊戲初始化成功！")
            # 開始遊戲主循環
            game.run()
        else:
            print("遊戲初始化失敗！")
            return 1

    except Exception as e:
        print(f"遊戲運行時發生錯誤: {e}")
        return 1

    finally:
        # 清理資源
        print("遊戲結束，感謝遊玩！")

    return 0


if __name__ == "__main__":
    sys.exit(main())

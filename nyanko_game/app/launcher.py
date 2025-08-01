# -*- coding: utf-8 -*-
"""
遊戲啟動器
負責初始化和啟動遊戲引擎
"""

import pygame
import sys
import os
from core.game_engine import GameEngine


def main():
    """主要啟動函數"""
    try:
        # 初始化 Pygame
        pygame.init()

        # 創建並初始化遊戲引擎
        game_engine = GameEngine()

        # 初始化遊戲
        if not game_engine.initialize():
            print("遊戲初始化失敗")
            return 1

        # 啟動遊戲主循環
        return game_engine.run()

    except Exception as e:
        print(f"遊戲啟動失敗: {e}")
        return 1
    finally:
        pygame.quit()


if __name__ == "__main__":
    sys.exit(main())

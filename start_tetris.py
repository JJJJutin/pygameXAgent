#!/usr/bin/env python3
"""
俄羅斯方塊遊戲啟動腳本
從外部目錄啟動遊戲的便利腳本
"""

import sys
import os

# 確保可以匯入 tetris_game 模組
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from tetris_game.main import main

    if __name__ == "__main__":
        print("=" * 60)
        print("            俄羅斯方塊遊戲 - 模組化版本")
        print("=" * 60)
        print()
        main()

except ImportError as e:
    print(f"匯入錯誤：{e}")
    print("請確保已安裝 pygame：pip install pygame")
    sys.exit(1)
except Exception as e:
    print(f"啟動錯誤：{e}")
    sys.exit(1)

# -*- coding: utf-8 -*-
"""
にゃんこと一緒 ～貓娘女僕的同居日常～
主程式入口
"""

import sys
import os

# 將當前目錄加入Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.launcher import main


if __name__ == "__main__":
    sys.exit(main())

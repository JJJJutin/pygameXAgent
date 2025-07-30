"""
俄羅斯方塊遊戲主模組
"""

__version__ = "1.0.0"
__author__ = "Tetris Game Developer"

from .core import Game
from .ui import UIRenderer

__all__ = ["Game", "UIRenderer"]

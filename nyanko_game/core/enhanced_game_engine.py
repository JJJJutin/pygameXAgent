# -*- coding: utf-8 -*-
"""
增強的遊戲引擎 - 整合事件驅動時間系統
繼承原有遊戲引擎，添加事件驅動時間系統支持
"""

import pygame
import sys
from typing import Optional
from config.settings import *
from core.game_engine import GameEngine
from systems.event_driven_time_system import EventDrivenTimeSystem
from systems.dialogue_system import DialogueSystem
from systems.affection_system import AffectionSystem


class EnhancedGameEngine(GameEngine):
    """增強的遊戲引擎 - 支持事件驅動時間系統"""

    def __init__(self):
        """初始化增強版遊戲引擎"""
        super().__init__()

        # 替換為事件驅動時間系統
        self.event_driven_time_system = None
        self.activity_result_callback = None

        # 整合狀態
        self.integration_active = False

    def initialize(self):
        """初始化增強版遊戲引擎"""
        return super().initialize()

    def run(self):
        """運行增強版遊戲引擎"""
        return super().run()

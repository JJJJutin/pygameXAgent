# -*- coding: utf-8 -*-
"""
系統模組
包含遊戲的核心系統組件
"""

from .dialogue_system import DialogueSystem, DialogueNode
from .affection_system import AffectionSystem, RelationshipLevel
from .time_system import TimeSystem, TimePeriod, GameTime
from .event_system import EventSystem, EventType, GameEvent

__all__ = [
    "DialogueSystem",
    "DialogueNode",
    "AffectionSystem",
    "RelationshipLevel",
    "TimeSystem",
    "TimePeriod",
    "GameTime",
    "EventSystem",
    "EventType",
    "GameEvent",
]

# 模組初始化完成
print("系統模組初始化完成 - 載入對話系統、好感度系統、時間系統、事件系統")

# -*- coding: utf-8 -*-
"""
活動結果顯示混入類別
提供活動完成後的結果顯示功能，防止關閉後立即觸發其他互動
"""

import pygame
from typing import Dict, Any
from config.settings import Colors


class ActivityResultMixin:
    """活動結果顯示混入類別"""

    def __init__(self):
        """初始化活動結果顯示相關變數"""
        self.activity_result_display = False
        self.activity_result = {}
        self.result_timer = 0
        self.input_delay_timer = 0  # 輸入延遲計時器，防止關閉活動結果後立即觸發其他互動

    def show_activity_result(self, result_info: Dict[str, Any]):
        """
        顯示活動結果

        Args:
            result_info: 活動結果資訊字典，包含:
                - activity_name: 活動名稱
                - energy_change: 體力變化
                - affection_change: 好感度變化
                - mood_change: 心情變化
                - time_cost: 時間消耗
        """
        self.activity_result = {
            "name": result_info["activity_name"],
            "changes": {
                "體力": result_info.get("energy_change", 0),
                "好感度": result_info.get("affection_change", 0),
                "心情": result_info.get("mood_change", 0),
            },
            "time_cost": result_info.get("time_cost", 0),
        }
        self.activity_result_display = True
        self.result_timer = pygame.time.get_ticks()

    def handle_activity_result_event(self, event: pygame.event.Event) -> bool:
        """
        處理活動結果顯示相關事件

        Args:
            event: pygame 事件

        Returns:
            bool: 如果事件被處理則返回 True，否則返回 False
        """
        current_time = pygame.time.get_ticks()

        # 活動結果顯示中 - 阻止所有互動
        if self.activity_result_display:
            # 只有 KEYDOWN 和 MOUSEBUTTONDOWN 事件可以關閉活動結果顯示
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.activity_result_display = False
                # 設置輸入延遲，防止立即觸發其他互動
                self.input_delay_timer = current_time + 300  # 300ms延遲
                print("🎯 活動結果顯示已關閉，設置輸入延遲 300ms")
            # 阻止所有事件類型被傳遞到其他系統
            return True  # 事件已被處理，阻止其他事件處理

        # 檢查輸入延遲
        if current_time < self.input_delay_timer:
            print(f"⏳ 輸入延遲中，剩餘時間: {self.input_delay_timer - current_time}ms")
            return True  # 在延遲期間忽略所有輸入，事件已被處理

        return False  # 事件未被處理，繼續其他事件處理

    def render_activity_result(self, screen: pygame.Surface):
        """
        渲染活動結果顯示

        Args:
            screen: pygame 螢幕表面
        """
        if not self.activity_result_display:
            return

        # 檢查自動關閉時間（顯示1.5秒）
        current_time = pygame.time.get_ticks()
        if current_time - self.result_timer > 1500:
            self.activity_result_display = False
            # 自動關閉時也設置輸入延遲，防止立即觸發其他互動
            self.input_delay_timer = current_time + 300  # 300ms延遲
            print("🎯 活動結果顯示自動關閉，設置輸入延遲 300ms")
            return

        screen_width, screen_height = screen.get_size()

        # 結果框大小和位置
        result_width = 400
        result_height = 200
        result_x = (screen_width - result_width) // 2
        result_y = (screen_height - result_height) // 2

        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # 結果框背景
        result_surface = pygame.Surface((result_width, result_height))
        result_surface.fill(Colors.WHITE)
        pygame.draw.rect(
            result_surface, Colors.PRIMARY_COLOR, result_surface.get_rect(), 3
        )

        # 獲取字體（假設場景有 ui_font 屬性）
        ui_font = getattr(self, "ui_font", pygame.font.Font(None, 24))

        # 標題
        title_text = ui_font.render("活動完成", True, Colors.PRIMARY_COLOR)
        title_rect = title_text.get_rect()
        title_rect.centerx = result_width // 2
        title_rect.y = 20
        result_surface.blit(title_text, title_rect)

        # 活動名稱
        activity_text = ui_font.render(
            self.activity_result["name"], True, Colors.DARK_GRAY
        )
        activity_rect = activity_text.get_rect()
        activity_rect.centerx = result_width // 2
        activity_rect.y = 60
        result_surface.blit(activity_text, activity_rect)

        # 變化詳情
        y_offset = 100
        for stat, change in self.activity_result["changes"].items():
            if change != 0:
                color = Colors.GREEN if change > 0 else Colors.RED
                change_text = ui_font.render(f"{stat}: {change:+d}", True, color)
                change_rect = change_text.get_rect()
                change_rect.centerx = result_width // 2
                change_rect.y = y_offset
                result_surface.blit(change_text, change_rect)
                y_offset += 25

        # 時間消耗
        if self.activity_result.get("time_cost", 0) > 0:
            time_text = ui_font.render(
                f"消耗時間點數: {self.activity_result['time_cost']}", True, Colors.BLUE
            )
            time_rect = time_text.get_rect()
            time_rect.centerx = result_width // 2
            time_rect.y = y_offset
            result_surface.blit(time_text, time_rect)
            y_offset += 25

        # 關閉提示
        hint_text = ui_font.render("點擊任意處或按任意鍵關閉", True, Colors.GRAY)
        hint_rect = hint_text.get_rect()
        hint_rect.centerx = result_width // 2
        hint_rect.y = result_height - 30
        result_surface.blit(hint_text, hint_rect)

        screen.blit(result_surface, (result_x, result_y))

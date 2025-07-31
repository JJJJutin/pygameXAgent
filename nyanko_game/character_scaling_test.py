#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物立繪智能縮放測試程式
測試人物立繪根據背景解析度的自動縮放功能
"""

import pygame
import sys
import os

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *
from systems.image_manager import image_manager


def test_character_scaling():
    """測試人物立繪縮放功能"""

    # 初始化 pygame
    pygame.init()

    # 先設置一個臨時顯示模式以避免載入圖片時的錯誤
    temp_screen = pygame.display.set_mode((800, 600))

    # 測試不同的解析度
    test_resolutions = [
        (1280, 720),  # 遊戲原始解析度
        (1920, 1080),  # Full HD
        (2560, 1440),  # 2K
        (3840, 2160),  # 4K
        (800, 600),  # 較小解析度
    ]

    print("人物立繪智能縮放測試")
    print("=" * 50)

    # 載入圖片資源
    image_manager.load_all_images()

    for width, height in test_resolutions:
        print(f"\n測試解析度: {width}x{height}")

        # 計算人物立繪尺寸
        char_width, char_height = image_manager.get_adaptive_character_size(
            width, height
        )

        # 計算人物立繪位置
        char_x, char_y = image_manager.get_adaptive_character_position(
            width, height, char_width, char_height
        )

        # 計算縮放比例
        original_char_height = ImageScaling.CHARACTER_ORIGINAL_HEIGHT
        scale_ratio = char_height / original_char_height

        print(f"  人物立繪尺寸: {char_width}x{char_height}")
        print(f"  縮放比例: {scale_ratio:.2f}x")
        print(f"  位置座標: ({char_x}, {char_y})")
        print(f"  佔螢幕高度比例: {(char_height / height * 100):.1f}%")

    print("\n" + "=" * 50)
    print("測試完成!")

    # 創建互動式測試視窗
    print("\n開始互動式測試 (按 ESC 退出, 1-5 切換解析度)")

    current_resolution_index = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        # 獲取當前測試解析度
        current_width, current_height = test_resolutions[current_resolution_index]

        # 設置視窗
        screen = pygame.display.set_mode((current_width, current_height))
        pygame.display.set_caption(
            f"人物立繪縮放測試 - {current_width}x{current_height}"
        )

        # 載入並縮放背景
        background = image_manager.get_background_for_time("living_room", "morning")
        if background:
            scaled_bg = pygame.transform.scale(
                background, (current_width, current_height)
            )
        else:
            scaled_bg = None

        # 計算人物立繪
        char_width, char_height = image_manager.get_adaptive_character_size(
            current_width, current_height
        )
        char_x, char_y = image_manager.get_adaptive_character_position(
            current_width, current_height, char_width, char_height
        )
        nyanko_image = image_manager.get_scaled_character_image(
            "nyanko", "normal", "default", (char_width, char_height)
        )

        # 渲染一幀
        screen.fill((200, 220, 255))  # 淺藍色背景

        # 繪製背景
        if scaled_bg:
            screen.blit(scaled_bg, (0, 0))

        # 繪製人物立繪
        if nyanko_image:
            screen.blit(nyanko_image, (char_x, char_y))

        # 繪製資訊
        font = pygame.font.Font(None, 36)
        info_lines = [
            f"解析度: {current_width}x{current_height}",
            f"人物尺寸: {char_width}x{char_height}",
            f"縮放比例: {char_height / ImageScaling.CHARACTER_ORIGINAL_HEIGHT:.2f}x",
            f"位置: ({char_x}, {char_y})",
            "",
            "按鍵: 1-5 切換解析度, ESC 退出",
        ]

        for i, line in enumerate(info_lines):
            if line:  # 跳過空行
                text = font.render(line, True, (255, 255, 255))
                # 添加黑色邊框提高可讀性
                text_rect = text.get_rect()
                text_rect.topleft = (20, 20 + i * 40)
                pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(10, 5))
                screen.blit(text, (20, 20 + i * 40))

        pygame.display.flip()

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key >= pygame.K_1 and event.key <= pygame.K_5:
                    # 切換解析度
                    new_index = event.key - pygame.K_1
                    if new_index < len(test_resolutions):
                        current_resolution_index = new_index

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    test_character_scaling()

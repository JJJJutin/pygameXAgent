# -*- coding: utf-8 -*-
"""
全螢幕縮放功能測試程式
"""

import pygame
import sys
import os

# 將當前目錄加入Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *
from systems.image_manager import image_manager


def main():
    """主測試函數"""
    # 初始化pygame
    pygame.init()

    # 獲取螢幕資訊
    info = pygame.display.Info()
    native_width = info.current_w
    native_height = info.current_h

    print(f"螢幕原始解析度: {native_width}x{native_height}")
    print(f"遊戲設計解析度: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    # 設置全螢幕模式
    screen = pygame.display.set_mode((native_width, native_height), pygame.FULLSCREEN)
    pygame.display.set_caption("全螢幕縮放測試")

    # 載入圖片資源（在設置視頻模式之後）
    image_manager.load_all_images()

    # 計算縮放比例
    scale_x = native_width / SCREEN_WIDTH
    scale_y = native_height / SCREEN_HEIGHT
    scale_factor = min(scale_x, scale_y)

    print(f"建議縮放比例: {scale_factor:.2f}")

    # 創建遊戲表面
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # 計算縮放後的尺寸和偏移
    scaled_width = int(SCREEN_WIDTH * scale_factor)
    scaled_height = int(SCREEN_HEIGHT * scale_factor)
    offset_x = (native_width - scaled_width) // 2
    offset_y = (native_height - scaled_height) // 2

    print(f"縮放後尺寸: {scaled_width}x{scaled_height}")
    print(f"渲染偏移: ({offset_x}, {offset_y})")

    # 創建字體
    try:
        font = pygame.font.Font(FontSettings.DEFAULT_FONT, 24)
        big_font = pygame.font.Font(FontSettings.DEFAULT_FONT, 36)
    except:
        font = pygame.font.Font(None, 24)
        big_font = pygame.font.Font(None, 36)

    # 測試狀態
    current_time = "morning"
    nyanko_mood = "normal"
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_F11:
                    running = False
                elif event.key == pygame.K_1:
                    # 切換時間
                    current_time = "morning" if current_time == "evening" else "evening"
                elif event.key == pygame.K_2:
                    # 切換にゃんこ表情
                    nyanko_mood = "happy" if nyanko_mood == "normal" else "normal"

        # 清空遊戲表面
        game_surface.fill((50, 50, 100))

        # 繪製背景
        if current_time == "morning":
            bg = image_manager.get_image("bg_livingroom_morning")
        else:
            bg = image_manager.get_image("bg_livingroom_evening")

        if bg:
            # 縮放背景到遊戲表面大小
            scaled_bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.blit(scaled_bg, (0, 0))

        # 繪製にゃんこ
        if nyanko_mood == "happy":
            nyanko_img = image_manager.get_image("nyanko_happy")
        else:
            nyanko_img = image_manager.get_image("nyanko_normal")

        if nyanko_img:
            # 縮放にゃんこ圖片
            char_width, char_height = 250, 350
            scaled_nyanko = pygame.transform.scale(
                nyanko_img, (char_width, char_height)
            )

            # 置中偏右顯示
            char_x = SCREEN_WIDTH - char_width - 100
            char_y = SCREEN_HEIGHT - char_height - 50

            game_surface.blit(scaled_nyanko, (char_x, char_y))

        # 繪製UI
        title_text = big_font.render("全螢幕縮放測試", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = SCREEN_WIDTH // 2
        title_rect.y = 20
        game_surface.blit(title_text, title_rect)

        # 顯示解析度資訊
        info_texts = [
            f"原始解析度: {native_width}x{native_height}",
            f"遊戲解析度: {SCREEN_WIDTH}x{SCREEN_HEIGHT}",
            f"縮放比例: {scale_factor:.2f}x",
            f"縮放後尺寸: {scaled_width}x{scaled_height}",
            "",
            f"當前時間: {'早上' if current_time == 'morning' else '晚上'}",
            f"にゃんこ表情: {'開心' if nyanko_mood == 'happy' else '正常'}",
            "",
            "操作說明:",
            "1 - 切換早晚背景",
            "2 - 切換にゃんこ表情",
            "ESC/F11 - 退出",
        ]

        for i, text in enumerate(info_texts):
            if text:
                color = (
                    (255, 255, 0) if text.startswith("操作說明") else (255, 255, 255)
                )
                rendered_text = font.render(text, True, color)
                game_surface.blit(rendered_text, (50, 100 + i * 25))

        # 清空螢幕（黑色邊框）
        screen.fill((0, 0, 0))

        # 縮放並渲染遊戲表面
        scaled_surface = pygame.transform.smoothscale(
            game_surface, (scaled_width, scaled_height)
        )
        screen.blit(scaled_surface, (offset_x, offset_y))

        # 更新顯示
        pygame.display.flip()
        clock.tick(60)

    # 清理
    pygame.quit()
    print("全螢幕縮放測試結束")


if __name__ == "__main__":
    main()

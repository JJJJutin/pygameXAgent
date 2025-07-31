# -*- coding: utf-8 -*-
"""
圖片系統演示程式
演示如何在遊戲中切換背景和角色圖片
"""

import pygame
import sys
import os

# 將當前目錄加入Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from systems.image_manager import image_manager
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    """主演示函數"""
    # 初始化pygame
    pygame.init()

    # 創建螢幕
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("にゃんこ遊戲 - 圖片系統演示")

    # 初始化時鐘
    clock = pygame.time.Clock()

    # 載入圖片資源
    image_manager.load_all_images()

    # 創建字體
    try:
        font = pygame.font.Font(r"C:\Windows\Fonts\msjh.ttc", 24)
        big_font = pygame.font.Font(r"C:\Windows\Fonts\msjh.ttc", 36)
    except:
        font = pygame.font.Font(None, 24)
        big_font = pygame.font.Font(None, 36)

    # 演示狀態
    current_time = "morning"
    nyanko_mood = "normal"

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    # 切換時間
                    current_time = "morning" if current_time == "evening" else "evening"
                elif event.key == pygame.K_2:
                    # 切換にゃんこ表情
                    nyanko_mood = "happy" if nyanko_mood == "normal" else "normal"

        # 清空螢幕
        screen.fill((0, 0, 0))

        # 繪製背景
        if current_time == "morning":
            bg = image_manager.get_image("bg_livingroom_morning")
        else:
            bg = image_manager.get_image("bg_livingroom_evening")

        if bg:
            # 縮放背景到螢幕大小
            scaled_bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))

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

            screen.blit(scaled_nyanko, (char_x, char_y))

        # 繪製UI
        title_text = big_font.render("にゃんこ遊戲圖片系統演示", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = SCREEN_WIDTH // 2
        title_rect.y = 20
        screen.blit(title_text, title_rect)

        # 顯示當前狀態
        time_text = font.render(
            f"當前時間: {'早上' if current_time == 'morning' else '晚上'}",
            True,
            (255, 255, 255),
        )
        screen.blit(time_text, (50, 100))

        mood_text = font.render(
            f"にゃんこ表情: {'開心' if nyanko_mood == 'happy' else '正常'}",
            True,
            (255, 255, 255),
        )
        screen.blit(mood_text, (50, 130))

        # 操作說明
        instructions = [
            "操作說明:",
            "1 - 切換早晚背景",
            "2 - 切換にゃんこ表情",
            "ESC - 退出",
        ]

        for i, instruction in enumerate(instructions):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            text = font.render(instruction, True, color)
            screen.blit(text, (50, 180 + i * 30))

        # 載入的圖片列表
        loaded_text = font.render("已載入的圖片:", True, (255, 255, 0))
        screen.blit(loaded_text, (50, 320))

        image_list = [
            "✓ 客廳早上背景",
            "✓ 客廳晚上背景",
            "✓ にゃんこ正常立繪",
            "✓ にゃんこ開心立繪",
        ]

        for i, item in enumerate(image_list):
            text = font.render(item, True, (0, 255, 0))
            screen.blit(text, (50, 350 + i * 25))

        # 更新顯示
        pygame.display.flip()
        clock.tick(60)

    # 清理
    pygame.quit()
    print("圖片系統演示結束")


if __name__ == "__main__":
    main()

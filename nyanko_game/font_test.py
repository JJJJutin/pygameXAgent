# -*- coding: utf-8 -*-
"""
字體測試程式
用於測試中文字體是否能正確顯示
"""

import pygame
import sys
import os

# 將當前目錄加入Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import FontSettings, Colors


def test_fonts():
    """測試字體顯示"""
    pygame.init()

    # 建立視窗
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("字體測試")
    clock = pygame.time.Clock()

    # 測試文字
    test_texts = [
        "にゃんこと一緒 ～貓娘女僕的同居日常～",
        "開始遊戲",
        "載入遊戲",
        "遊戲設定",
        "離開遊戲",
        "客廳",
        "廚房",
        "臥室",
        "浴室",
        "主人，早安喵～今天也要一起度過美好的一天呢！",
    ]

    # 建立字體
    fonts = []
    font_sizes = [16, 20, 24, 32]

    for size in font_sizes:
        try:
            font = pygame.font.Font(FontSettings.DEFAULT_FONT, size)
            fonts.append((f"微軟正黑體 {size}px", font))
            print(f"成功載入微軟正黑體 {size}px")
        except (FileNotFoundError, OSError):
            font = pygame.font.Font(None, size)
            fonts.append((f"系統預設字體 {size}px", font))
            print(f"使用系統預設字體 {size}px")

    running = True
    scroll_offset = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_offset -= 20
                elif event.key == pygame.K_DOWN:
                    scroll_offset += 20

        # 清空螢幕
        screen.fill(Colors.WHITE)

        # 繪製標題
        title_font = fonts[-1][1]  # 使用最大字體
        title_text = title_font.render("字體測試 - 按ESC退出", True, Colors.BLACK)
        screen.blit(title_text, (20, 20))

        # 繪製測試文字
        y_offset = 80 + scroll_offset

        for font_name, font in fonts:
            # 繪製字體名稱
            font_name_surface = font.render(font_name, True, Colors.BLUE)
            screen.blit(font_name_surface, (20, y_offset))
            y_offset += 30

            # 繪製測試文字
            for text in test_texts[:3]:  # 只顯示前3個文字以節省空間
                try:
                    text_surface = font.render(text, True, Colors.DARK_GRAY)
                    screen.blit(text_surface, (40, y_offset))
                    y_offset += font.get_height() + 5
                except Exception as e:
                    error_text = font.render(f"渲染錯誤: {str(e)}", True, Colors.RED)
                    screen.blit(error_text, (40, y_offset))
                    y_offset += font.get_height() + 5

            y_offset += 20  # 字體間的間距

        # 繪製操作提示
        hint_font = fonts[0][1]  # 使用最小字體
        hint_text = hint_font.render("使用上下箭頭鍵捲動", True, Colors.GRAY)
        screen.blit(hint_text, (20, 550))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("字體測試完成")


if __name__ == "__main__":
    test_fonts()

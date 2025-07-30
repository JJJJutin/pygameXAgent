# pip install pygame
import pygame
import sys

# 初始化 Pygame
pygame.init()
# 設定視窗大小
width, height = 640, 480
screen = pygame.display.set_mode((width, height))

# 設定視窗標題
pygame.display.set_caption("Pygame?")
# 設定白色
white = (255, 255, 255)

# 主迴圈
clock = pygame.time.Clock()

while True:
    # 處理事件
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  # 離開遊戲
    # 填充背景顏色
    screen.fill(white)
    # 更新顯示
    pygame.display.flip()
    # 控制遊戲幀率
    clock.tick(60)

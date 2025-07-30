# pip install pygame
import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 設定視窗大小
width, height = 640, 480
screen = pygame.display.set_mode((width, height))

# 設定視窗標題
pygame.display.set_caption("Pygame?")

# 設定顏色
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

# 動態顏色變數
square_color = red
bg_color = white
text_color = black


# 隨機顏色生成函數
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


# 方塊設定
square_size = 50
square_x = width // 2 - square_size // 2  # 置中
square_y = height // 2 - square_size // 2
move_speed = 5

# 記錄上一次位置，用於檢測移動
last_x, last_y = square_x, square_y

# 字體設定 - 使用微軟正黑體
font = pygame.font.Font(r"C:\Windows\Fonts\msjh.ttc", 24)

# 主迴圈
clock = pygame.time.Clock()

while True:
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  # 離開遊戲

    # 記錄移動前位置
    prev_x, prev_y = square_x, square_y

    # 鍵盤檢測
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        square_y -= move_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        square_y += move_speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        square_x -= move_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        square_x += move_speed
    # 持續改變背景顏色和文字顏色
    bg_color = random_color()
    text_color = random_color()

    # 邊界檢測
    square_x = max(0, min(square_x, width - square_size))
    square_y = max(0, min(square_y, height - square_size))

    # 檢測方塊是否移動，如果移動則改變顏色
    if square_x != prev_x or square_y != prev_y:
        square_color = bg_color

    # 填充背景顏色
    screen.fill(bg_color)

    # 繪製紅色方塊
    pygame.draw.rect(
        screen, square_color, (square_x, square_y, square_size, square_size)
    )

    # 計算方塊中心點座標
    center_x = square_x + square_size // 2
    center_y = square_y + square_size // 2

    # 顯示座標文字
    coord_text = font.render(f"中心位置: ({center_x}, {center_y})", True, text_color)
    screen.blit(coord_text, (10, 10))

    # 更新顯示
    pygame.display.flip()

    # 控制遊戲幀率
    clock.tick(60)

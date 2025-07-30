"""
UI 渲染器
負責繪製遊戲介面、方塊、資訊顯示等視覺元素
"""

import pygame
from config.constants import (
    WHITE,
    BLACK,
    GRAY,
    LIGHT_GRAY,
    CYAN,
    RED,
    YELLOW,
    GREEN,
    CELL_SIZE,
    GRID_X,
    GRID_Y,
    LOCK_DELAY_MAX,
    GRID_WIDTH,
)


class UIRenderer:
    """UI 渲染器類別"""

    def __init__(self):
        """初始化渲染器"""
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)

    def draw_current_tetromino(self, screen, game):
        """
        繪製當前下落方塊
        參數：
        - screen: pygame 螢幕物件
        - game: Game 物件
        """
        blocks = game.current_tetromino.get_blocks()
        for x, y in blocks:
            if y >= 0:  # 只繪製可見區域內的方塊
                screen_x = GRID_X + x * CELL_SIZE
                screen_y = GRID_Y + y * CELL_SIZE
                pygame.draw.rect(
                    screen,
                    game.current_tetromino.color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                )
                pygame.draw.rect(
                    screen, WHITE, (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1
                )

    def draw_ghost_piece(self, screen, game):
        """
        繪製幽靈方塊（預覽落點）- Tetris 99 風格
        參數：
        - screen: pygame 螢幕物件
        - game: Game 物件
        """
        ghost_blocks = game.current_tetromino.get_ghost_blocks(game.grid)

        # 使用半透明填充 + 邊框的方式（類似 Tetris 99）
        ghost_color = game.current_tetromino.color
        ghost_fill_color = tuple(c // 3 for c in ghost_color)  # 降低亮度作為填充色

        for x, y in ghost_blocks:
            if y >= 0:  # 只繪製可見區域內的方塊
                screen_x = GRID_X + x * CELL_SIZE
                screen_y = GRID_Y + y * CELL_SIZE

                # 繪製半透明填充
                pygame.draw.rect(
                    screen,
                    ghost_fill_color,
                    (screen_x + 2, screen_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                )

                # 繪製邊框
                pygame.draw.rect(
                    screen,
                    ghost_color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                    2,  # 邊框寬度
                )

                # 繪製內部點陣效果（更像 Tetris 99）
                for i in range(2):
                    for j in range(2):
                        dot_x = screen_x + 8 + i * 10
                        dot_y = screen_y + 8 + j * 10
                        pygame.draw.rect(screen, ghost_color, (dot_x, dot_y, 2, 2))

    def draw_hold_piece(self, screen, game):
        """
        繪製 Hold 方塊
        參數：
        - screen: pygame 螢幕物件
        - game: Game 物件
        """
        hold_x = 20
        hold_y = 50

        # 繪製 Hold 標題
        hold_text = self.font.render("HOLD", True, WHITE)
        screen.blit(hold_text, (hold_x, hold_y))

        # 繪製 Hold 方塊框
        hold_box = pygame.Rect(hold_x, hold_y + 30, 120, 80)
        pygame.draw.rect(screen, GRAY, hold_box, 2)

        if game.hold_tetromino:
            # 繪製 Hold 方塊
            shape = game.hold_tetromino.shapes[0]  # 使用初始形狀
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = hold_x + 10 + col_idx * 20
                        y = hold_y + 40 + row_idx * 20
                        pygame.draw.rect(
                            screen, game.hold_tetromino.color, (x, y, 18, 18)
                        )
                        pygame.draw.rect(screen, WHITE, (x, y, 18, 18), 1)

    def draw_next_piece(self, screen, game):
        """
        繪製下一個方塊
        參數：
        - screen: pygame 螢幕物件
        - game: Game 物件
        """
        next_x = 20
        next_y = 250  # 調整位置避免與控制說明重疊

        # 繪製 Next 標題
        next_text = self.font.render("NEXT", True, WHITE)
        screen.blit(next_text, (next_x, next_y))

        # 繪製 Next 方塊框
        next_box = pygame.Rect(next_x, next_y + 30, 120, 80)
        pygame.draw.rect(screen, GRAY, next_box, 2)

        if game.next_tetromino:
            # 繪製 Next 方塊
            shape = game.next_tetromino.shapes[0]  # 使用初始形狀
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = next_x + 10 + col_idx * 20
                        y = next_y + 40 + row_idx * 20
                        pygame.draw.rect(
                            screen, game.next_tetromino.color, (x, y, 18, 18)
                        )
                        pygame.draw.rect(screen, WHITE, (x, y, 18, 18), 1)

    def draw_info(self, screen, game):
        """
        顯示遊戲資訊
        參數：
        - screen: pygame 螢幕物件
        - game: Game 物件
        """
        info_x = GRID_X + GRID_WIDTH * CELL_SIZE + 20

        # 分數
        score_text = self.font.render(f"Score: {game.score}", True, WHITE)
        screen.blit(score_text, (info_x, 50))

        # 等級
        level_text = self.font.render(f"Level: {game.level}", True, WHITE)
        screen.blit(level_text, (info_x, 80))

        # 已消除行數
        lines_text = self.font.render(f"Lines: {game.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (info_x, 110))

        # 控制說明
        controls = [
            "Controls:",
            "←→: Move (DAS)",
            "↓: Soft Drop",
            "X/↑: Rotate CW",
            "Z: Rotate CCW",
            "Space: Hard Drop",
            "C/Shift: Hold",
            "R: Restart",
            "",
            "Features:",
            "• SRS Rotation",
            "• 7-bag System",
            "• Ghost Piece",
            "• Hold Function",
            "• T-Spin Detection",
            "• Perfect Clear",
            "• Combo System",
            "• Back-to-Back",
        ]

        for i, control in enumerate(controls):
            # 使用較小的字體間距和適當的顏色
            if control == "":
                continue  # 跳過空行
            elif control.startswith("•"):
                # 功能說明使用較小的字體
                control_text = self.small_font.render(control, True, CYAN)
                screen.blit(control_text, (info_x, 150 + i * 22))
            elif control in ["Controls:", "Features:"]:
                # 標題使用白色
                control_text = self.font.render(control, True, WHITE)
                screen.blit(control_text, (info_x, 150 + i * 22))
            else:
                # 普通控制說明
                control_text = self.font.render(control, True, LIGHT_GRAY)
                screen.blit(control_text, (info_x, 150 + i * 22))

        # Back-to-back 顯示
        if game.back_to_back_count > 0:
            b2b_text = self.font.render(
                f"Back-to-Back: {game.back_to_back_count}", True, YELLOW
            )
            screen.blit(b2b_text, (info_x, 480))

        # Combo 顯示
        if game.combo_count > 1:
            combo_text = self.font.render(f"Combo: {game.combo_count}x", True, GREEN)
            screen.blit(combo_text, (info_x, 505))

        # Perfect Clear 計數顯示
        if game.perfect_clear_count > 0:
            pc_text = self.font.render(
                f"Perfect Clear: {game.perfect_clear_count}", True, CYAN
            )
            screen.blit(pc_text, (info_x, 530))

        # 動作文字顯示 (T-SPIN!, TETRIS!, etc.)
        if game.action_text and game.action_text_timer > 0:
            # 計算閃爍效果
            if game.action_text_timer % 10 < 5:  # 閃爍效果
                action_color = RED if "T-SPIN" in game.action_text else YELLOW
                action_font = pygame.font.Font(None, 32)
                action_surface = action_font.render(
                    game.action_text, True, action_color
                )
                screen.blit(action_surface, (info_x, 555))

        # Lock Delay 指示器（調試用）
        if game.is_on_ground:
            lock_progress = game.lock_delay_timer / LOCK_DELAY_MAX
            pygame.draw.rect(screen, GRAY, (info_x, 580, 100, 10))
            pygame.draw.rect(screen, RED, (info_x, 580, int(100 * lock_progress), 10))

        # 遊戲結束提示
        if game.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            screen.blit(game_over_text, (info_x, 400))
            screen.blit(restart_text, (info_x, 430))

    def render_game(self, screen, game):
        """
        渲染整個遊戲畫面
        參數：
        - screen: pygame 螢幕物件
        - game: Game 物件
        """
        # 清除畫面背景（填充黑色）
        screen.fill(BLACK)

        # 繪製遊戲區域和已放置的方塊
        game.grid.draw(screen)

        # 繪製幽靈方塊（預覽落點）
        if not game.game_over:
            self.draw_ghost_piece(screen, game)

        # 繪製當前下落方塊
        if not game.game_over:
            self.draw_current_tetromino(screen, game)

        # 繪製 Hold 方塊
        self.draw_hold_piece(screen, game)

        # 繪製 Next 方塊
        self.draw_next_piece(screen, game)

        # 顯示遊戲資訊
        self.draw_info(screen, game)

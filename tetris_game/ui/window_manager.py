"""
多視窗管理器
負責管理不同的遊戲視窗並處理震動效果
"""

import pygame
import math
import random
from config.constants import (
    WHITE,
    BLACK,
    GRAY,
    LIGHT_GRAY,
    CYAN,
    RED,
    YELLOW,
    GREEN,
    PURPLE,
    ORANGE,
    CELL_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    LOCK_DELAY_MAX,
)


class WindowManager:
    """多視窗管理器類別"""

    def __init__(self):
        """初始化窗口管理器"""
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 48)

        # 震動效果參數
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # 計算總視窗大小
        self.total_width = 1400
        self.total_height = 800

        # 創建主視窗
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        pygame.display.set_caption("Tetris - 多視窗版本")

        # 計算各區域位置
        self.calculate_areas()

    def calculate_areas(self):
        """計算各個區域的位置和大小"""
        # Hold 區域 (左上)
        self.hold_area = {"x": 20, "y": 50, "width": 160, "height": 120}

        # 主遊戲區域 (中央)
        game_width = GRID_WIDTH * CELL_SIZE + 40
        game_height = GRID_HEIGHT * CELL_SIZE + 60
        self.game_area = {
            "x": (self.total_width - game_width) // 2,
            "y": (self.total_height - game_height) // 2,
            "width": game_width,
            "height": game_height,
        }

        # Next 區域 (右上)
        self.next_area = {
            "x": self.game_area["x"] + self.game_area["width"] + 20,
            "y": 50,
            "width": 160,
            "height": 300,
        }

        # 資訊區域 (右中)
        self.info_area = {
            "x": self.next_area["x"],
            "y": self.next_area["y"] + self.next_area["height"] + 20,
            "width": 200,
            "height": 300,
        }

        # 操作說明區域 (左下)
        self.controls_area = {
            "x": 20,
            "y": self.hold_area["y"] + self.hold_area["height"] + 30,
            "width": 350,
            "height": 500,
        }

    def trigger_shake(self, intensity, duration):
        """觸發震動效果"""
        self.shake_intensity = intensity
        self.shake_duration = duration

    def update_shake(self, dt):
        """更新震動效果"""
        if self.shake_duration > 0:
            self.shake_duration -= dt

            # 計算震動偏移
            if self.shake_duration > 0:
                self.shake_offset_x = random.randint(
                    -self.shake_intensity, self.shake_intensity
                )
                self.shake_offset_y = random.randint(
                    -self.shake_intensity, self.shake_intensity
                )
            else:
                self.shake_offset_x = 0
                self.shake_offset_y = 0

    def draw_area_border(self, area, color=WHITE, width=2):
        """繪製區域邊框"""
        pygame.draw.rect(
            self.screen,
            color,
            (area["x"], area["y"], area["width"], area["height"]),
            width,
        )

    def draw_main_game(self, game):
        """繪製主遊戲區域"""
        # 應用震動偏移
        offset_x = self.game_area["x"] + 20 + self.shake_offset_x
        offset_y = self.game_area["y"] + 40 + self.shake_offset_y

        # 繪製區域背景和邊框
        game_rect = pygame.Rect(
            self.game_area["x"] + self.shake_offset_x,
            self.game_area["y"] + self.shake_offset_y,
            self.game_area["width"],
            self.game_area["height"],
        )
        pygame.draw.rect(self.screen, BLACK, game_rect)
        pygame.draw.rect(self.screen, CYAN, game_rect, 3)

        # 繪製標題
        title_text = self.font.render("TETRIS", True, WHITE)
        title_rect = title_text.get_rect(
            center=(
                self.game_area["x"]
                + self.game_area["width"] // 2
                + self.shake_offset_x,
                self.game_area["y"] + 20 + self.shake_offset_y,
            )
        )
        self.screen.blit(title_text, title_rect)

        # 繪製遊戲網格
        game.grid.draw(self.screen, offset_x, offset_y)

        # 繪製幽靈方塊
        if not game.game_over:
            self.draw_ghost_piece(game, offset_x, offset_y)

        # 繪製當前方塊
        if not game.game_over:
            self.draw_current_tetromino(game, offset_x, offset_y)

        # 遊戲結束畫面
        if game.game_over:
            game_over_text = self.large_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(
                center=(
                    self.game_area["x"] + self.game_area["width"] // 2,
                    self.game_area["y"] + self.game_area["height"] // 2,
                )
            )
            self.screen.blit(game_over_text, game_over_rect)

            restart_text = self.font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(
                    self.game_area["x"] + self.game_area["width"] // 2,
                    self.game_area["y"] + self.game_area["height"] // 2 + 50,
                )
            )
            self.screen.blit(restart_text, restart_rect)

    def draw_current_tetromino(self, game, offset_x, offset_y):
        """繪製當前下落方塊"""
        blocks = game.current_tetromino.get_blocks()
        for x, y in blocks:
            if y >= 0:
                screen_x = offset_x + x * CELL_SIZE
                screen_y = offset_y + y * CELL_SIZE
                pygame.draw.rect(
                    self.screen,
                    game.current_tetromino.color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                )
                pygame.draw.rect(
                    self.screen, WHITE, (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1
                )

    def draw_ghost_piece(self, game, offset_x, offset_y):
        """繪製幽靈方塊"""
        ghost_blocks = game.current_tetromino.get_ghost_blocks(game.grid)

        ghost_color = game.current_tetromino.color
        ghost_fill_color = tuple(c // 3 for c in ghost_color)

        for x, y in ghost_blocks:
            if y >= 0:
                screen_x = offset_x + x * CELL_SIZE
                screen_y = offset_y + y * CELL_SIZE

                pygame.draw.rect(
                    self.screen,
                    ghost_fill_color,
                    (screen_x + 2, screen_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                )

                pygame.draw.rect(
                    self.screen,
                    ghost_color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                    2,
                )

    def draw_hold_area(self, game):
        """繪製 Hold 區域"""
        area = self.hold_area

        # 繪製背景和邊框
        pygame.draw.rect(
            self.screen, BLACK, (area["x"], area["y"], area["width"], area["height"])
        )
        self.draw_area_border(area, YELLOW)

        # 繪製標題
        title_text = self.font.render("HOLD", True, WHITE)
        title_rect = title_text.get_rect(
            center=(area["x"] + area["width"] // 2, area["y"] + 20)
        )
        self.screen.blit(title_text, title_rect)

        if game.hold_tetromino:
            # 繪製 Hold 方塊
            shape = game.hold_tetromino.shapes[0]
            start_x = area["x"] + (area["width"] - len(shape[0]) * 25) // 2
            start_y = area["y"] + 50

            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = start_x + col_idx * 25
                        y = start_y + row_idx * 25
                        color = game.hold_tetromino.color
                        if not game.can_hold:  # 如果不能 hold，顯示灰色
                            color = tuple(c // 2 for c in color)
                        pygame.draw.rect(self.screen, color, (x, y, 23, 23))
                        pygame.draw.rect(self.screen, WHITE, (x, y, 23, 23), 1)

    def draw_next_area(self, game):
        """繪製 Next 區域"""
        area = self.next_area

        # 繪製背景和邊框
        pygame.draw.rect(
            self.screen, BLACK, (area["x"], area["y"], area["width"], area["height"])
        )
        self.draw_area_border(area, GREEN)

        # 繪製標題
        title_text = self.font.render("NEXT", True, WHITE)
        title_rect = title_text.get_rect(
            center=(area["x"] + area["width"] // 2, area["y"] + 20)
        )
        self.screen.blit(title_text, title_rect)

        if game.next_tetromino:
            # 繪製 Next 方塊
            shape = game.next_tetromino.shapes[0]
            start_x = area["x"] + (area["width"] - len(shape[0]) * 25) // 2
            start_y = area["y"] + 50

            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = start_x + col_idx * 25
                        y = start_y + row_idx * 25
                        pygame.draw.rect(
                            self.screen, game.next_tetromino.color, (x, y, 23, 23)
                        )
                        pygame.draw.rect(self.screen, WHITE, (x, y, 23, 23), 1)

        # 顯示 bag 資訊
        if hasattr(game, "piece_bag"):
            bag_text = self.small_font.render("Bag:", True, LIGHT_GRAY)
            self.screen.blit(bag_text, (area["x"] + 10, area["y"] + 120))

            bag_info = f"剩餘: {len(game.piece_bag)}"
            bag_info_text = self.small_font.render(bag_info, True, LIGHT_GRAY)
            self.screen.blit(bag_info_text, (area["x"] + 10, area["y"] + 140))

    def draw_info_area(self, game):
        """繪製資訊區域"""
        area = self.info_area

        # 繪製背景和邊框
        pygame.draw.rect(
            self.screen, BLACK, (area["x"], area["y"], area["width"], area["height"])
        )
        self.draw_area_border(area, PURPLE)

        # 繪製標題
        title_text = self.font.render("INFO", True, WHITE)
        title_rect = title_text.get_rect(
            center=(area["x"] + area["width"] // 2, area["y"] + 20)
        )
        self.screen.blit(title_text, title_rect)

        y_offset = area["y"] + 50

        # 基本資訊
        info_items = [
            f"分數: {game.score}",
            f"等級: {game.level}",
            f"行數: {game.lines_cleared}",
        ]

        for item in info_items:
            text = self.small_font.render(item, True, WHITE)
            self.screen.blit(text, (area["x"] + 10, y_offset))
            y_offset += 25

        y_offset += 15

        # 特殊狀態
        if game.back_to_back_count > 0:
            b2b_text = self.small_font.render(
                f"Back-to-Back: {game.back_to_back_count}", True, YELLOW
            )
            self.screen.blit(b2b_text, (area["x"] + 10, y_offset))
            y_offset += 25

        if game.combo_count > 1:
            combo_text = self.small_font.render(
                f"Combo: {game.combo_count}x", True, GREEN
            )
            self.screen.blit(combo_text, (area["x"] + 10, y_offset))
            y_offset += 25

        if game.perfect_clear_count > 0:
            pc_text = self.small_font.render(
                f"Perfect Clear: {game.perfect_clear_count}", True, CYAN
            )
            self.screen.blit(pc_text, (area["x"] + 10, y_offset))
            y_offset += 25

        # 動作文字顯示
        if game.action_text and game.action_text_timer > 0:
            if game.action_text_timer % 10 < 5:
                action_color = RED if "T-SPIN" in game.action_text else YELLOW
                action_text = self.small_font.render(
                    game.action_text, True, action_color
                )
                self.screen.blit(action_text, (area["x"] + 10, y_offset))
                y_offset += 25

        # Lock Delay 指示器
        if game.is_on_ground:
            lock_text = self.small_font.render("Lock Delay:", True, LIGHT_GRAY)
            self.screen.blit(lock_text, (area["x"] + 10, y_offset))
            y_offset += 20

            lock_progress = game.lock_delay_timer / LOCK_DELAY_MAX
            pygame.draw.rect(self.screen, GRAY, (area["x"] + 10, y_offset, 150, 8))
            pygame.draw.rect(
                self.screen,
                RED,
                (area["x"] + 10, y_offset, int(150 * lock_progress), 8),
            )

    def draw_controls_area(self):
        """繪製操作說明區域"""
        area = self.controls_area

        # 繪製背景和邊框
        pygame.draw.rect(
            self.screen, BLACK, (area["x"], area["y"], area["width"], area["height"])
        )
        self.draw_area_border(area, ORANGE)

        # 繪製標題
        title_text = self.font.render("操作說明", True, WHITE)
        title_rect = title_text.get_rect(
            center=(area["x"] + area["width"] // 2, area["y"] + 20)
        )
        self.screen.blit(title_text, title_rect)

        # 操作說明內容
        controls = [
            "基本操作:",
            "← →: 移動方塊 (DAS)",
            "↓: 軟降",
            "X / ↑: 順時針旋轉",
            "Z: 逆時針旋轉",
            "Space: 硬降",
            "C / Shift: Hold 功能",
            "R: 重新開始",
            "",
            "特色功能:",
            "• SRS 旋轉系統",
            "• 7-bag 隨機器",
            "• 幽靈方塊預覽",
            "• Hold 功能",
            "• T-Spin 檢測",
            "• Perfect Clear 檢測",
            "• Combo 系統",
            "• Back-to-Back 獎勵",
            "• Lock Delay 系統",
            "• 震動反饋效果",
        ]

        y_offset = area["y"] + 50
        for control in controls:
            if control == "":
                y_offset += 10
                continue
            elif control.startswith("•"):
                control_text = self.small_font.render(control, True, CYAN)
            elif control in ["基本操作:", "特色功能:"]:
                control_text = self.font.render(control, True, WHITE)
            else:
                control_text = self.small_font.render(control, True, LIGHT_GRAY)

            self.screen.blit(control_text, (area["x"] + 10, y_offset))
            y_offset += 22

    def render_all_windows(self, game, screen=None):
        """渲染所有視窗區域"""
        # 更新震動效果
        self.update_shake(16)  # 假設 60fps，約16ms per frame

        # 清除整個螢幕
        self.screen.fill(BLACK)

        # 繪製所有區域
        self.draw_main_game(game)
        self.draw_hold_area(game)
        self.draw_next_area(game)
        self.draw_info_area(game)
        self.draw_controls_area()

        # 更新顯示
        pygame.display.flip()

    def get_main_window_surface(self):
        """獲取主遊戲視窗表面"""
        return self.screen

    def should_trigger_shake_for_action(self, action_text, lines_cleared):
        """根據動作決定是否觸發震動"""
        if "T-SPIN" in action_text:
            # T-spin 震動
            if "TRIPLE" in action_text:
                return 8, 300  # 強震動，300ms
            elif "DOUBLE" in action_text:
                return 6, 200  # 中等震動，200ms
            else:
                return 4, 150  # 輕微震動，150ms
        elif lines_cleared >= 4:
            # Tetris 震動
            return 6, 250
        elif lines_cleared > 0:
            # 普通消行震動
            return 2, 100
        elif "PERFECT CLEAR" in action_text:
            # Perfect Clear 震動
            return 10, 500

        return 0, 0  # 無震動

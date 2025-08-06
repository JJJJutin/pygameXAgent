"""
WindowKill 風格的多視窗管理器
使用 Tkinter 創建多個獨立的桌面視窗，每個視窗顯示不同的遊戲資訊
保持震動功能並實現真正的多視窗體驗
"""

import pygame
import tkinter as tk
from tkinter import Canvas
import random
import threading
import time

# 嘗試導入PIL，如果失敗則使用替代方案
try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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


class WindowKillManager:
    """WindowKill 風格的多視窗管理器"""

    def __init__(self):
        """初始化多視窗管理器"""
        # Pygame 字體初始化（在主視窗中使用）
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 48)

        # 震動效果參數
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # 創建 Tkinter 根視窗（隱藏）
        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏主視窗

        # 主遊戲視窗（使用 Pygame）
        # 優化後的視窗大小：移除標題後減少高度，增加少量邊距
        self.main_window_size = (
            GRID_WIDTH * CELL_SIZE + 60,  # 左右各30像素邊距
            GRID_HEIGHT * CELL_SIZE + 60,  # 上下各約30像素邊距（原來100，現在60）
        )
        self.main_screen = pygame.display.set_mode(self.main_window_size)
        pygame.display.set_caption("TETRIS WINDOWS")

        # 設置遊戲圖示
        try:
            icon = pygame.image.load("assets/tetris_icon.png")
            pygame.display.set_icon(icon)
        except:
            print("無法加載遊戲圖示")

        # 創建 Tkinter 子視窗
        self.create_tkinter_windows()

        # 創建圖示（用於Tkinter視窗）
        self.setup_tkinter_icon()

        # Game Over 視窗相關
        self.game_over_window = None
        self.restart_callback = None

        # 遊戲數據暫存
        self.game_data = None

        # 視窗動畫參數
        self.window_animations = {
            "hold_window": {
                "target_x": 100,
                "target_y": 100,
                "current_x": 100,
                "current_y": 100,
            },
            "next_window": {
                "target_x": 800,
                "target_y": 100,
                "current_x": 800,
                "current_y": 100,
            },
            "info_window": {
                "target_x": 800,
                "target_y": 300,
                "current_x": 800,
                "current_y": 300,
            },
            "controls_window": {
                "target_x": 100,
                "target_y": 400,
                "current_x": 100,
                "current_y": 400,
            },
        }

    def create_tkinter_windows(self):
        """創建 Tkinter 視窗"""
        # Hold 視窗
        self.hold_window = tk.Toplevel(self.root)
        self.hold_window.title("Hold")
        self.hold_window.geometry("180x140+100+100")
        self.hold_window.configure(bg="black")
        self.hold_window.attributes("-topmost", True)
        self.hold_canvas = Canvas(
            self.hold_window,
            width=160,
            height=120,
            bg="black",
            highlightbackground="yellow",
            highlightthickness=3,
        )
        self.hold_canvas.pack(pady=10)

        # Next 視窗
        self.next_window = tk.Toplevel(self.root)
        self.next_window.title("Next")
        self.next_window.geometry("180x140+800+100")
        self.next_window.configure(bg="black")
        self.next_window.attributes("-topmost", True)
        self.next_canvas = Canvas(
            self.next_window,
            width=160,
            height=120,
            bg="black",
            highlightbackground="green",
            highlightthickness=3,
        )
        self.next_canvas.pack(pady=10)

        # 資訊視窗
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("Info")
        self.info_window.geometry("250x300+800+300")
        self.info_window.configure(bg="black")
        self.info_window.attributes("-topmost", True)
        self.info_canvas = Canvas(
            self.info_window,
            width=230,
            height=280,
            bg="black",
            highlightbackground="purple",
            highlightthickness=3,
        )
        self.info_canvas.pack(pady=10)

        # 操作說明視窗
        self.controls_window = tk.Toplevel(self.root)
        self.controls_window.title("Controls")
        self.controls_window.geometry("280x220+100+400")
        self.controls_window.configure(bg="black")
        self.controls_window.attributes("-topmost", True)
        self.controls_canvas = Canvas(
            self.controls_window,
            width=260,
            height=200,
            bg="black",
            highlightbackground="orange",
            highlightthickness=3,
        )
        self.controls_canvas.pack(pady=10)

        # 繪製靜態內容
        self.draw_static_controls()

    def setup_tkinter_icon(self):
        """為所有Tkinter視窗設置圖示"""
        if PIL_AVAILABLE:
            try:
                # 使用PIL加載圖片並轉換為PhotoImage
                pil_image = Image.open("assets/tetris_icon.png")
                # 調整圖片大小為適合的圖示尺寸
                pil_image = pil_image.resize((32, 32), Image.Resampling.LANCZOS)
                self.tk_icon = ImageTk.PhotoImage(pil_image)

                # 為所有視窗設置圖示
                self.hold_window.iconphoto(False, self.tk_icon)
                self.next_window.iconphoto(False, self.tk_icon)
                self.info_window.iconphoto(False, self.tk_icon)
                self.controls_window.iconphoto(False, self.tk_icon)

                print("✅ Tkinter視窗圖示設置成功")
                return
            except Exception as e:
                print(f"⚠️ 使用PIL設置圖示失敗: {e}")

        # 如果PIL不可用，創建一個簡單的文字圖示
        try:
            # 創建一個簡單的文字圖示
            print("🔄 PIL不可用，跳過Tkinter視窗圖示設置")
            # 注意：Tkinter對圖示格式要求較嚴格，PNG需要PIL支持
            # 我們可以在視窗標題中添加表情符號作為替代方案
            self.hold_window.title("🎮 Hold")
            self.next_window.title("🎯 Next")
            self.info_window.title("📊 Info")
            self.controls_window.title("🎮 Controls")
            print("✅ 已為視窗標題添加表情符號作為替代")

        except Exception as e:
            print(f"⚠️ 設置替代圖示方案失敗: {e}")

    def draw_static_controls(self):
        """繪製操作說明（靜態內容）"""
        self.controls_canvas.delete("all")

        # 標題
        self.controls_canvas.create_text(
            130, 20, text="操作說明", fill="white", font=("Arial", 16, "bold")
        )

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
        ]

        y_offset = 50
        for control in controls:
            if control == "":
                y_offset += 15
                continue
            elif control.startswith("•"):
                color = "cyan"
                font_size = 10
            elif control == "基本操作:":
                color = "white"
                font_size = 12
            else:
                color = "lightgray"
                font_size = 10

            self.controls_canvas.create_text(
                20,
                y_offset,
                text=control,
                fill=color,
                font=("Arial", font_size),
                anchor="w",
            )
            y_offset += 20

    def trigger_shake(self, intensity, duration):
        """觸發震動效果"""
        self.shake_intensity = intensity
        self.shake_duration = duration

        # 觸發視窗動畫
        self.trigger_window_shake()

    def trigger_window_shake(self):
        """觸發視窗震動動畫"""
        for window_name, anim in self.window_animations.items():
            # 隨機震動偏移
            shake_x = random.randint(
                -self.shake_intensity * 3, self.shake_intensity * 3
            )
            shake_y = random.randint(
                -self.shake_intensity * 3, self.shake_intensity * 3
            )

            anim["target_x"] = anim["current_x"] + shake_x
            anim["target_y"] = anim["current_y"] + shake_y

    def update_shake(self, dt):
        """更新震動效果"""
        if self.shake_duration > 0:
            self.shake_duration -= dt

            # 計算主視窗震動偏移
            if self.shake_duration > 0:
                self.shake_offset_x = random.randint(
                    -self.shake_intensity, self.shake_intensity
                )
                self.shake_offset_y = random.randint(
                    -self.shake_intensity, self.shake_intensity
                )

                # 移動 pygame 視窗（需要系統級 API，這裡模擬震動效果）
                # 在實際實現中可能需要使用 win32api 來移動視窗

            else:
                self.shake_offset_x = 0
                self.shake_offset_y = 0

        # 更新 Tkinter 視窗位置動畫
        self.update_window_animations()

    def update_window_animations(self):
        """更新視窗動畫"""
        for window_name, anim in self.window_animations.items():
            # 平滑回到原位
            diff_x = anim["target_x"] - anim["current_x"]
            diff_y = anim["target_y"] - anim["current_y"]

            if abs(diff_x) > 1 or abs(diff_y) > 1:
                anim["current_x"] += diff_x * 0.1
                anim["current_y"] += diff_y * 0.1

                # 移動對應的視窗
                if window_name == "hold_window":
                    self.hold_window.geometry(
                        f"180x140+{int(anim['current_x'])}+{int(anim['current_y'])}"
                    )
                elif window_name == "next_window":
                    self.next_window.geometry(
                        f"180x140+{int(anim['current_x'])}+{int(anim['current_y'])}"
                    )
                elif window_name == "info_window":
                    self.info_window.geometry(
                        f"250x300+{int(anim['current_x'])}+{int(anim['current_y'])}"
                    )
                elif window_name == "controls_window":
                    self.controls_window.geometry(
                        f"280x220+{int(anim['current_x'])}+{int(anim['current_y'])}"
                    )

    def draw_main_game(self, game):
        """繪製主遊戲視窗（Pygame）"""
        # 應用震動偏移
        offset_x = 30 + self.shake_offset_x
        offset_y = 20 + self.shake_offset_y  # 減少上邊距，因為移除了標題

        # 清除背景
        self.main_screen.fill(BLACK)

        # 繪製遊戲網格
        game.grid.draw(self.main_screen, offset_x, offset_y)

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
                center=(self.main_window_size[0] // 2, self.main_window_size[1] // 2)
            )
            self.main_screen.blit(game_over_text, game_over_rect)

            restart_text = self.font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(
                center=(
                    self.main_window_size[0] // 2,
                    self.main_window_size[1] // 2 + 50,
                )
            )
            self.main_screen.blit(restart_text, restart_rect)

    def draw_current_tetromino(self, game, offset_x, offset_y):
        """繪製當前下落方塊"""
        blocks = game.current_tetromino.get_blocks()
        for x, y in blocks:
            if y >= 0:
                screen_x = offset_x + x * CELL_SIZE
                screen_y = offset_y + y * CELL_SIZE
                pygame.draw.rect(
                    self.main_screen,
                    game.current_tetromino.color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                )
                pygame.draw.rect(
                    self.main_screen,
                    WHITE,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                    1,
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
                    self.main_screen,
                    ghost_fill_color,
                    (screen_x + 2, screen_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                )

                pygame.draw.rect(
                    self.main_screen,
                    ghost_color,
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                    2,
                )

    def update_hold_window(self, game):
        """更新 Hold 視窗"""
        self.hold_canvas.delete("all")

        # 標題
        self.hold_canvas.create_text(
            80, 15, text="HOLD", fill="white", font=("Arial", 14, "bold")
        )

        if game.hold_tetromino:
            # 繪製 Hold 方塊
            shape = game.hold_tetromino.shapes[0]
            start_x = 80 - (len(shape[0]) * 10)
            start_y = 35

            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = start_x + col_idx * 20
                        y = start_y + row_idx * 20

                        # 轉換顏色為 tkinter 格式
                        color = game.hold_tetromino.color
                        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

                        # 如果不能 hold，顯示灰色
                        if not game.can_hold:
                            hex_color = "#404040"

                        self.hold_canvas.create_rectangle(
                            x, y, x + 18, y + 18, fill=hex_color, outline="white"
                        )

    def update_next_window(self, game):
        """更新 Next 視窗"""
        self.next_canvas.delete("all")

        # 標題
        self.next_canvas.create_text(
            80, 15, text="NEXT", fill="white", font=("Arial", 14, "bold")
        )

        if game.next_tetromino:
            # 繪製 Next 方塊
            shape = game.next_tetromino.shapes[0]
            start_x = 80 - (len(shape[0]) * 10)
            start_y = 35

            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = start_x + col_idx * 20
                        y = start_y + row_idx * 20

                        # 轉換顏色為 tkinter 格式
                        color = game.next_tetromino.color
                        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

                        self.next_canvas.create_rectangle(
                            x, y, x + 18, y + 18, fill=hex_color, outline="white"
                        )

    def update_info_window(self, game):
        """更新資訊視窗"""
        self.info_canvas.delete("all")

        # 標題
        self.info_canvas.create_text(
            115, 15, text="INFO", fill="white", font=("Arial", 14, "bold")
        )

        y_offset = 40

        # 基本資訊
        # 計算到下一等級需要的行數
        lines_to_next_level = (game.level * 10) - game.lines_cleared
        if lines_to_next_level <= 0:
            lines_to_next_level = 10 - (game.lines_cleared % 10)

        # 獲取當前等級的速度
        current_speed_frames = game.get_fall_speed_for_level(game.level)
        speed_seconds = round(current_speed_frames / 60, 2)

        info_items = [
            f"分數: {game.score:,}",
            f"等級: {game.level}",
            f"行數: {game.lines_cleared}",
            f"下級需要: {lines_to_next_level} 行",
            f"速度: {speed_seconds}s/格",
        ]

        for item in info_items:
            self.info_canvas.create_text(
                20, y_offset, text=item, fill="white", font=("Arial", 12), anchor="w"
            )
            y_offset += 25

        y_offset += 15

        # 特殊狀態
        if game.back_to_back_count > 0:
            self.info_canvas.create_text(
                20,
                y_offset,
                text=f"Back-to-Back: {game.back_to_back_count}",
                fill="yellow",
                font=("Arial", 10),
                anchor="w",
            )
            y_offset += 20

        if game.combo_count > 1:
            self.info_canvas.create_text(
                20,
                y_offset,
                text=f"Combo: {game.combo_count}x",
                fill="green",
                font=("Arial", 10),
                anchor="w",
            )
            y_offset += 20

        if game.perfect_clear_count > 0:
            self.info_canvas.create_text(
                20,
                y_offset,
                text=f"Perfect Clear: {game.perfect_clear_count}",
                fill="cyan",
                font=("Arial", 10),
                anchor="w",
            )
            y_offset += 20

        # 動作文字顯示
        if game.action_text and game.action_text_timer > 0:
            if game.action_text_timer % 10 < 5:
                action_color = "red" if "T-SPIN" in game.action_text else "yellow"
                self.info_canvas.create_text(
                    20,
                    y_offset,
                    text=game.action_text,
                    fill=action_color,
                    font=("Arial", 10, "bold"),
                    anchor="w",
                )
                y_offset += 20

        # Lock Delay 指示器
        if game.is_on_ground:
            self.info_canvas.create_text(
                20,
                y_offset,
                text="Lock Delay:",
                fill="lightgray",
                font=("Arial", 10),
                anchor="w",
            )
            y_offset += 15

            lock_progress = game.lock_delay_timer / LOCK_DELAY_MAX
            # 繪製進度條
            self.info_canvas.create_rectangle(
                20, y_offset, 170, y_offset + 8, fill="gray", outline=""
            )
            self.info_canvas.create_rectangle(
                20,
                y_offset,
                20 + int(150 * lock_progress),
                y_offset + 8,
                fill="red",
                outline="",
            )

    def render_all_windows(self, game):
        """渲染所有視窗"""
        # 更新震動效果
        self.update_shake(16)  # 假設 60fps，約16ms per frame

        # 更新遊戲數據
        self.game_data = game

        # 繪製主遊戲視窗
        self.draw_main_game(game)

        # 更新 Tkinter 視窗
        self.update_hold_window(game)
        self.update_next_window(game)
        self.update_info_window(game)

        # 更新 Tkinter 視窗
        self.root.update()

        # 更新 Pygame 顯示
        pygame.display.flip()

    def get_main_window_surface(self):
        """獲取主遊戲視窗表面"""
        return self.main_screen

    def should_trigger_shake_for_action(self, action_text, lines_cleared):
        """根據動作決定是否觸發震動"""
        if "T-SPIN" in action_text:
            if "TRIPLE" in action_text:
                return 8, 300
            elif "DOUBLE" in action_text:
                return 6, 200
            else:
                return 4, 150
        elif lines_cleared >= 4:
            return 6, 250
        elif lines_cleared > 0:
            return 2, 100
        elif "PERFECT CLEAR" in action_text:
            return 10, 500

        return 0, 0

    def show_game_over_window(self, game, restart_callback):
        """顯示 Game Over 視窗"""
        self.restart_callback = restart_callback

        # 如果視窗已存在，先關閉
        if self.game_over_window:
            try:
                self.game_over_window.destroy()
            except:
                pass

        # 創建 Game Over 視窗
        self.game_over_window = tk.Toplevel(self.root)
        self.game_over_window.title("💀 Game Over")
        self.game_over_window.geometry("320x200")
        self.game_over_window.configure(bg="black")
        self.game_over_window.resizable(False, False)
        self.game_over_window.attributes("-topmost", True)

        # 設置視窗在螢幕中央
        self.game_over_window.update_idletasks()
        width = self.game_over_window.winfo_width()
        height = self.game_over_window.winfo_height()
        x = (self.game_over_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.game_over_window.winfo_screenheight() // 2) - (height // 2)
        self.game_over_window.geometry(f"{width}x{height}+{x}+{y}")

        # 設置視窗關閉事件
        self.game_over_window.protocol("WM_DELETE_WINDOW", self.on_game_over_close)

        # 為Game Over視窗設置圖示
        try:
            if hasattr(self, "tk_icon"):
                self.game_over_window.iconphoto(False, self.tk_icon)
        except:
            pass

        # 創建 Canvas（符合其他視窗的風格）
        self.game_over_canvas = Canvas(
            self.game_over_window,
            width=300,
            height=180,
            bg="black",
            highlightbackground="red",
            highlightthickness=3,
        )
        self.game_over_canvas.pack(pady=10)

        # 繪製 Game Over 內容
        self.draw_game_over_content(game)

        # 讓視窗置於最前
        self.game_over_window.lift()
        self.game_over_window.focus_force()

    def draw_game_over_content(self, game):
        """繪製 Game Over 視窗內容"""
        # 清除 Canvas
        self.game_over_canvas.delete("all")

        # 標題（符合其他視窗的風格）
        self.game_over_canvas.create_text(
            150, 25, text="GAME OVER", fill="white", font=("Arial", 18, "bold")
        )

        y_pos = 60

        # 遊戲統計資訊（簡潔風格）
        stats = [
            f"分數: {game.score:,}",
            f"等級: {game.level}",
            f"行數: {game.lines_cleared}",
        ]

        # 繪製統計資訊
        for stat in stats:
            self.game_over_canvas.create_text(
                150, y_pos, text=stat, fill="white", font=("Arial", 14), anchor="center"
            )
            y_pos += 25

    def on_game_over_close(self):
        """Game Over 視窗關閉事件"""
        try:
            # 先儲存回調函數，因為關閉視窗後可能會清空
            callback = self.restart_callback

            if self.game_over_window:
                self.game_over_window.destroy()
                self.game_over_window = None

            # 呼叫重新開始回調
            if callback:
                callback()

        except Exception as e:
            print(f"Game Over 視窗關閉錯誤: {e}")
            # 即使出錯也嘗試重新開始遊戲
            if self.restart_callback:
                try:
                    self.restart_callback()
                except:
                    pass

    def hide_game_over_window(self):
        """隱藏 Game Over 視窗"""
        if self.game_over_window:
            try:
                self.game_over_window.destroy()
                self.game_over_window = None
            except:
                pass

    def close_all_windows(self):
        """關閉所有視窗"""
        try:
            # 先關閉 Game Over 視窗
            if self.game_over_window:
                self.game_over_window.destroy()
                self.game_over_window = None

            # 關閉所有其他視窗
            self.root.destroy()
        except Exception as e:
            print(f"關閉視窗時發生錯誤: {e}")

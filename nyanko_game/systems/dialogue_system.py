# -*- coding: utf-8 -*-
"""
對話系統核心
負責處理遊戲中的對話顯示、選擇分支和文字效果
"""

import pygame
import json
import os
from typing import Dict, List, Optional, Any, Callable
from config.settings import *


class DialogueNode:
    """對話節點類別"""

    def __init__(self, data: Dict[str, Any]):
        """初始化對話節點"""
        self.id = data.get("id", "")
        self.speaker = data.get("speaker", "")
        self.text = data.get("text", "")
        self.emotion = data.get("emotion", "normal")
        self.choices = data.get("choices", [])
        self.conditions = data.get("conditions", {})
        self.effects = data.get("effects", {})
        self.next_dialogue = data.get("next_dialogue", None)
        self.flags = data.get("flags", {})

    def has_choices(self) -> bool:
        """檢查是否有選擇選項"""
        return len(self.choices) > 0

    def get_valid_choices(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """獲取符合條件的選擇選項"""
        valid_choices = []
        for choice in self.choices:
            if self._check_choice_conditions(choice, game_state):
                valid_choices.append(choice)
        return valid_choices

    def _check_choice_conditions(
        self, choice: Dict[str, Any], game_state: Dict[str, Any]
    ) -> bool:
        """檢查選擇選項的條件"""
        conditions = choice.get("conditions", {})

        # 檢查好感度條件
        if "affection_min" in conditions:
            if game_state.get("nyanko_affection", 0) < conditions["affection_min"]:
                return False

        if "affection_max" in conditions:
            if game_state.get("nyanko_affection", 0) > conditions["affection_max"]:
                return False

        # 檢查時間條件
        if "time_period" in conditions:
            if game_state.get("current_time", "") != conditions["time_period"]:
                return False

        # 檢查旗標條件
        if "flags" in conditions:
            for flag, required_value in conditions["flags"].items():
                if game_state.get("flags", {}).get(flag) != required_value:
                    return False

        return True


class DialogueSystem:
    """對話系統主類別"""

    def __init__(self, game_engine):
        """初始化對話系統"""
        self.game_engine = game_engine
        self.dialogue_data: Dict[str, DialogueNode] = {}
        self.current_dialogue: Optional[DialogueNode] = None
        self.dialogue_history: List[str] = []

        # 文字顯示相關
        self.displayed_text = ""
        self.full_text = ""
        self.text_progress = 0
        self.text_speed = UISettings.TEXT_SPEED_NORMAL
        self.text_complete = False

        # UI相關
        self.dialogue_box_rect = None
        self.choice_buttons = []
        self.selected_choice = 0
        self.font = None
        self.speaker_font = None

        # 狀態
        self.is_active = False
        self.waiting_for_input = False
        self.auto_mode = False
        self.last_dialogue_end_time = 0  # 上次對話結束時間
        self.dialogue_cooldown = 0.1  # 對話冷卻時間（秒）- 減少冷卻時間
        self.dialogue_start_time = 0  # 對話開始時間
        self.input_delay = 0.05  # 對話開始後的輸入延遲（秒）- 進一步減少延遲

        # 回調函數
        self.on_dialogue_end: Optional[Callable] = None
        self.on_choice_selected: Optional[Callable] = None

        # 統一選擇系統集成
        self.unified_choice_system = None
        self.use_unified_choices = True
        self.waiting_for_choice = False

        self._initialize_ui()

    def set_unified_choice_system(self, unified_choice_system):
        """設置統一選擇系統"""
        self.unified_choice_system = unified_choice_system
        if unified_choice_system:
            # 設置回調函數
            unified_choice_system.on_choice_selected = self._on_unified_choice_selected
            unified_choice_system.on_choice_cancelled = (
                self._on_unified_choice_cancelled
            )

    def _on_unified_choice_selected(self, choice):
        """統一選擇系統選擇回調"""
        self.waiting_for_choice = False

        if choice.choice_type == "dialogue" and choice.next_dialogue:
            # 對話選擇 - 執行效果後繼續對話
            print(f"🎭 玩家選擇對話選項: {choice.text}")
            if choice.affection_change != 0:
                print(f"   好感度變化: {choice.affection_change:+d}")
            self._transition_to_next_dialogue(
                choice.next_dialogue, getattr(self, "current_game_state", {})
            )
        else:
            # 其他類型選擇，結束對話
            print(f"🎯 玩家選擇活動/場景選項: {choice.text}")
            self.end_dialogue()

    def _on_unified_choice_cancelled(self):
        """統一選擇系統取消回調"""
        self.waiting_for_choice = False
        # 回到對話等待輸入狀態
        self.waiting_for_input = True

    def _initialize_ui(self):
        """初始化UI元素"""
        screen_width, screen_height = self.game_engine.get_screen_size()

        # 對話框位置 - 為選擇按鈕預留空間
        box_height = UISettings.DIALOGUE_BOX_HEIGHT
        box_margin = UISettings.DIALOGUE_BOX_MARGIN

        # 計算選擇按鈕需要的最大空間（3個按鈕 + 間距）
        max_choice_buttons = 3
        button_height = 35
        button_spacing = 8
        choice_area_height = max_choice_buttons * (button_height + button_spacing) + 20

        # 調整對話框位置，確保選擇按鈕不會超出螢幕
        dialogue_y = screen_height - box_height - choice_area_height - box_margin

        self.dialogue_box_rect = pygame.Rect(
            box_margin,
            dialogue_y,
            screen_width - 2 * box_margin,
            box_height,
        )

        # 載入字體
        try:
            self.font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.DIALOGUE_FONT_SIZE
            )
            self.speaker_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.SPEAKER_FONT_SIZE
            )
        except (FileNotFoundError, OSError):
            self.font = pygame.font.Font(None, FontSettings.DIALOGUE_FONT_SIZE)
            self.speaker_font = pygame.font.Font(None, FontSettings.SPEAKER_FONT_SIZE)

    def load_dialogue_data(self, file_path: str) -> bool:
        """
        載入對話資料

        Args:
            file_path: 對話資料檔案路徑

        Returns:
            bool: 是否載入成功
        """
        try:
            if not os.path.exists(file_path):
                print(f"警告: 對話資料檔案不存在: {file_path}")
                return False

            # 嘗試多種編碼方式
            encodings = ["utf-8-sig", "utf-8", "utf-16"]
            data = None

            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as file:
                        data = json.load(file)
                        print(f"成功使用 {encoding} 編碼載入對話檔案")
                        break
                except Exception as e:
                    continue

            if data is None:
                print(f"無法載入對話檔案: 嘗試了所有編碼方式")
                return False

            # 解析對話資料
            self.dialogue_data.clear()

            for category, dialogues in data.get("dialogue_database", {}).items():
                for dialogue_type, dialogue_list in dialogues.items():
                    for dialogue_data in dialogue_list:
                        node = DialogueNode(dialogue_data)
                        self.dialogue_data[node.id] = node

            print(f"成功載入 {len(self.dialogue_data)} 個對話節點")
            return True

        except Exception as e:
            print(f"載入對話資料失敗: {e}")
            return False

    def start_dialogue(
        self, dialogue_id: str, game_state: Dict[str, Any] = None
    ) -> bool:
        """
        開始對話

        Args:
            dialogue_id: 對話ID
            game_state: 遊戲狀態

        Returns:
            bool: 是否成功開始對話
        """
        # 檢查是否已有對話在進行中
        if self.is_active:
            print(f"警告: 對話系統忙碌中，無法開始新對話: {dialogue_id}")
            return False

        # 檢查冷卻時間
        import time

        current_time = time.time()
        if current_time - self.last_dialogue_end_time < self.dialogue_cooldown:
            print(f"警告: 對話冷卻中，請稍候再試: {dialogue_id}")
            return False

        if dialogue_id not in self.dialogue_data:
            print(f"警告: 找不到對話ID: {dialogue_id}")
            return False

        # 記錄對話開始時間
        self.dialogue_start_time = current_time

        self.current_dialogue = self.dialogue_data[dialogue_id]
        self.full_text = self.current_dialogue.text
        self.displayed_text = ""
        self.text_progress = 0.0  # 修復：確保從0開始
        self.text_complete = False
        self.is_active = True
        self.waiting_for_input = False
        self.waiting_for_choice = False  # 修復：重置選擇等待狀態
        self.selected_choice = 0

        # 記錄到歷史
        self.dialogue_history.append(dialogue_id)

        print(f"開始對話: {dialogue_id}")
        print(f"說話者: {self.current_dialogue.speaker}")
        print(f"內容: {self.current_dialogue.text}")

        return True

    def update(self, dt: float, game_state: Dict[str, Any]):
        """
        更新對話系統

        Args:
            dt: 時間差
            game_state: 遊戲狀態
        """
        if not self.is_active or not self.current_dialogue:
            return

        # 儲存當前遊戲狀態以供回調使用
        self.current_game_state = game_state

        # 更新文字顯示
        if not self.text_complete:
            self._update_text_display(dt)

        # 文字顯示完成後，等待玩家確認再顯示選項
        # 不在這裡自動顯示選項，而是等待玩家按鍵或點擊

    def _update_text_display(self, dt: float):
        """更新文字顯示效果"""
        if self.text_complete:
            return

        # 計算應該顯示的字元數量
        chars_per_second = self.text_speed
        self.text_progress += chars_per_second * dt

        current_length = int(self.text_progress)
        if current_length >= len(self.full_text):
            current_length = len(self.full_text)
            self.text_complete = True
            self.waiting_for_input = True

        self.displayed_text = self.full_text[:current_length]

    def _show_unified_choices(self, game_state: Dict[str, Any]):
        """顯示統一選擇選項"""
        if not self.unified_choice_system:
            print("❌ 統一選擇系統未設置")
            return

        # 獲取對話選擇
        valid_choices = self.current_dialogue.get_valid_choices(game_state)
        print(f"🗨️ 找到 {len(valid_choices)} 個有效對話選項")

        # 轉換為統一格式
        dialogue_choices = []
        for choice in valid_choices:
            dialogue_choices.append(
                {
                    "text": choice.get("text", ""),
                    "next_dialogue": choice.get("next_dialogue"),
                    "affection_change": choice.get("affection_change", 0),
                    "flags": choice.get("flags", {}),
                    "conditions": choice.get("conditions", {}),
                }
            )

        # 添加上下文選項（活動、場景切換等）
        enhanced_choices = self.unified_choice_system.add_contextual_choices(
            dialogue_choices
        )
        print(f"🎯 增強後共有 {len(enhanced_choices)} 個選擇選項")

        if enhanced_choices:
            print(f"💭 顯示 {len(enhanced_choices)} 個選擇選項")
            # 顯示選擇
            self.unified_choice_system.show_choices(
                enhanced_choices, "にゃんこ的回應", "mixed"
            )
            self.waiting_for_choice = True
            self.waiting_for_input = False
            print("⏳ 等待玩家選擇...")
        else:
            # 如果沒有可用選擇，直接等待繼續輸入
            self.waiting_for_input = True
            self.waiting_for_choice = False
            print("❗ 沒有可用的選擇選項，等待玩家繼續")

    def _update_choice_buttons(self, game_state: Dict[str, Any]):
        """更新選擇按鈕"""
        valid_choices = self.current_dialogue.get_valid_choices(game_state)

        if valid_choices:
            self.choice_buttons = valid_choices
            if self.selected_choice >= len(self.choice_buttons):
                self.selected_choice = 0
            self.waiting_for_input = True  # 修復：等待玩家選擇
            print(f"💭 顯示 {len(valid_choices)} 個傳統選擇按鈕")
        else:
            # 沒有選擇選項，等待繼續
            self.choice_buttons = []
            self.waiting_for_input = True

    def handle_event(
        self, event: pygame.event.Event, game_state: Dict[str, Any]
    ) -> bool:
        """
        處理事件

        Args:
            event: pygame事件
            game_state: 遊戲狀態

        Returns:
            bool: 是否處理了事件
        """
        if not self.is_active:
            return False

        # 如果統一選擇系統正在等待玩家選擇，對話系統不處理事件
        if (
            self.waiting_for_choice
            and self.unified_choice_system
            and self.unified_choice_system.is_active
        ):
            print("🎯 統一選擇系統激活中，對話系統跳過事件處理")
            return False

        # 檢查輸入延遲 - 防止對話開始後立即響應輸入
        import time

        current_time = time.time()
        if current_time - self.dialogue_start_time < self.input_delay:
            print(
                f"⏳ 對話輸入延遲中，剩餘時間: {self.input_delay - (current_time - self.dialogue_start_time):.2f}秒"
            )
            return True  # 返回True表示已處理，防止事件傳遞給其他系統

        if event.type == pygame.KEYDOWN:
            print(f"💬 對話系統收到按鍵事件: {pygame.key.name(event.key)}")

            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                return self._handle_confirm_key(game_state)

            elif event.key == pygame.K_UP:
                if self.text_complete and self.choice_buttons:
                    self.selected_choice = (self.selected_choice - 1) % len(
                        self.choice_buttons
                    )
                    return True

            elif event.key == pygame.K_DOWN:
                if self.text_complete and self.choice_buttons:
                    self.selected_choice = (self.selected_choice + 1) % len(
                        self.choice_buttons
                    )
                    return True

            elif event.key == pygame.K_ESCAPE:
                print("❌ ESC - 結束對話")
                self.end_dialogue()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                return self._handle_mouse_click(event.pos, game_state)

        return False

    def _handle_confirm_key(self, game_state: Dict[str, Any]) -> bool:
        """處理確認鍵"""
        if not self.text_complete:
            # 加速顯示文字
            self.text_complete = True
            self.displayed_text = self.full_text
            self.waiting_for_input = True
            print("💬 文字顯示完成，等待玩家確認")
            return True

        # 文字已完成，檢查是否有選項需要顯示
        if self.text_complete and not self.waiting_for_choice:
            has_choices = self.current_dialogue.has_choices()
            if has_choices:
                print("💭 檢測到對話選項，準備顯示選擇...")
                # 顯示選項
                if self.use_unified_choices and self.unified_choice_system:
                    print("🎯 使用統一選擇系統顯示選項")
                    self._show_unified_choices(game_state)
                else:
                    print("📋 使用傳統選擇按鈕顯示選項")
                    self._update_choice_buttons(game_state)
                return True
            else:
                print("⏭️ 無對話選項，準備繼續到下一個對話")
                # 沒有選項，繼續下一個對話或結束
                self._advance_dialogue(game_state)
                return True

        if self.choice_buttons and not self.waiting_for_choice:
            # 選擇選項（傳統模式）
            print(f"✅ 處理傳統選擇: 選項 {self.selected_choice}")
            self.process_choice(self.selected_choice, game_state)
            return True
        else:
            # 統一選擇系統已激活，或者沒有選項，繼續下一個對話或結束
            if not self.waiting_for_choice:
                print("⏭️ 無選項可選，繼續到下一個對話")
                self._advance_dialogue(game_state)
            return True

    def _handle_mouse_click(self, mouse_pos: tuple, game_state: Dict[str, Any]) -> bool:
        """處理滑鼠點擊"""
        if not self.text_complete:
            # 加速顯示文字
            self.text_complete = True
            self.displayed_text = self.full_text
            self.waiting_for_input = True
            return True

        # 文字已完成，檢查是否有選項需要顯示
        if self.text_complete and not self.waiting_for_choice:
            has_choices = self.current_dialogue.has_choices()
            if has_choices:
                # 顯示選項
                if self.use_unified_choices and self.unified_choice_system:
                    self._show_unified_choices(game_state)
                else:
                    self._update_choice_buttons(game_state)
                return True

        # 檢查是否點擊了選擇按鈕
        if self.choice_buttons:
            choice_index = self._get_clicked_choice(mouse_pos)
            if choice_index is not None:
                self.process_choice(choice_index, game_state)
                return True

        # 點擊對話框繼續
        if self.dialogue_box_rect.collidepoint(mouse_pos):
            # 沒有選項，繼續下一個對話或結束
            self._advance_dialogue(game_state)
            return True

        return False

    def _get_clicked_choice(self, mouse_pos: tuple) -> Optional[int]:
        """獲取點擊的選擇項目索引"""
        # 計算選擇按鈕位置
        choice_y_start = self.dialogue_box_rect.bottom + 10
        button_height = 30
        button_spacing = 5

        for i, choice in enumerate(self.choice_buttons):
            button_rect = pygame.Rect(
                self.dialogue_box_rect.x,
                choice_y_start + i * (button_height + button_spacing),
                self.dialogue_box_rect.width,
                button_height,
            )

            if button_rect.collidepoint(mouse_pos):
                return i

        return None

    def process_choice(self, choice_index: int, game_state: Dict[str, Any]):
        """
        處理選擇

        Args:
            choice_index: 選擇索引
            game_state: 遊戲狀態
        """
        if not self.choice_buttons or choice_index >= len(self.choice_buttons):
            return

        choice = self.choice_buttons[choice_index]
        print(f"玩家選擇: {choice.get('text', '')}")

        # 執行選擇效果
        self._apply_choice_effects(choice, game_state)

        # 呼叫回調函數
        if self.on_choice_selected:
            self.on_choice_selected(choice, game_state)

        # 繼續到下一個對話
        next_dialogue_id = choice.get("next_dialogue")
        if next_dialogue_id:
            # 先重置當前對話狀態，然後開始新對話
            self._transition_to_next_dialogue(next_dialogue_id, game_state)
        else:
            self.end_dialogue()

    def _transition_to_next_dialogue(
        self, next_dialogue_id: str, game_state: Dict[str, Any]
    ):
        """
        過渡到下一個對話

        Args:
            next_dialogue_id: 下一個對話ID
            game_state: 遊戲狀態
        """
        # 檢查對話ID是否存在
        if next_dialogue_id not in self.dialogue_data:
            print(f"警告: 找不到對話ID: {next_dialogue_id}")
            self.end_dialogue()
            return

        # 重置當前對話狀態但保持系統活躍
        self.current_dialogue = self.dialogue_data[next_dialogue_id]
        self.full_text = self.current_dialogue.text
        self.displayed_text = ""
        self.text_progress = 0.0  # 修復：確保從0開始，使用浮點數
        self.text_complete = False
        self.waiting_for_input = False
        self.waiting_for_choice = False  # 修復：重置選擇等待狀態
        self.selected_choice = 0
        self.choice_buttons = []

        # 記錄到歷史
        self.dialogue_history.append(next_dialogue_id)

        print(f"繼續對話: {next_dialogue_id}")
        print(f"說話者: {self.current_dialogue.speaker}")
        print(f"內容: {self.current_dialogue.text}")

    def _apply_choice_effects(self, choice: Dict[str, Any], game_state: Dict[str, Any]):
        """應用選擇效果"""
        # 好感度變化
        affection_change = choice.get("affection_change", 0)
        if affection_change != 0:
            current_affection = game_state.get("nyanko_affection", 0)
            new_affection = max(0, min(100, current_affection + affection_change))
            game_state["nyanko_affection"] = new_affection
            print(f"好感度變化: {affection_change:+d} (當前: {new_affection})")

        # 設定旗標
        flags = choice.get("flags", {})
        if flags:
            if "flags" not in game_state:
                game_state["flags"] = {}
            game_state["flags"].update(flags)

    def _advance_dialogue(self, game_state: Dict[str, Any]):
        """推進對話"""
        if self.current_dialogue and self.current_dialogue.next_dialogue:
            self.start_dialogue(self.current_dialogue.next_dialogue, game_state)
        else:
            self.end_dialogue()

    def end_dialogue(self):
        """結束對話"""
        print("對話結束")

        # 記錄對話結束時間
        import time

        self.last_dialogue_end_time = time.time()

        # 重置所有狀態
        self.is_active = False
        self.current_dialogue = None
        self.displayed_text = ""
        self.full_text = ""
        self.text_progress = 0.0
        self.text_complete = False
        self.waiting_for_input = False
        self.waiting_for_choice = False
        self.choice_buttons = []
        self.selected_choice = 0

        if self.on_dialogue_end:
            self.on_dialogue_end()

    def render(self, screen: pygame.Surface):
        """
        渲染對話界面

        Args:
            screen: pygame螢幕表面
        """
        if not self.is_active or not self.current_dialogue:
            return

        # 繪製對話框背景
        self._render_dialogue_box(screen)

        # 繪製說話者名字
        self._render_speaker_name(screen)

        # 繪製對話文字
        self._render_dialogue_text(screen)

        # 繪製選擇按鈕（只有當選項已經顯示時）
        if self.text_complete and self.choice_buttons and not self.waiting_for_choice:
            self._render_choice_buttons(screen)

        # 繪製繼續提示（文字完成後，且尚未顯示選項時）
        elif self.text_complete and not self.waiting_for_choice:
            # 檢查是否有潛在的選項需要顯示
            has_choices = (
                self.current_dialogue.has_choices() if self.current_dialogue else False
            )
            if has_choices:
                prompt_text = "按空白鍵查看選項..."
            else:
                prompt_text = "按空白鍵繼續..."

            prompt_surface = self.speaker_font.render(prompt_text, True, Colors.GRAY)
            prompt_x = self.dialogue_box_rect.right - prompt_surface.get_width() - 15
            prompt_y = self.dialogue_box_rect.bottom - prompt_surface.get_height() - 10
            screen.blit(prompt_surface, (prompt_x, prompt_y))

    def _render_dialogue_box(self, screen: pygame.Surface):
        """繪製對話框背景"""
        # 對話框背景
        pygame.draw.rect(screen, Colors.WHITE, self.dialogue_box_rect)
        pygame.draw.rect(screen, Colors.DARK_GRAY, self.dialogue_box_rect, 3)

        # 內側陰影效果
        inner_rect = pygame.Rect(
            self.dialogue_box_rect.x + 3,
            self.dialogue_box_rect.y + 3,
            self.dialogue_box_rect.width - 6,
            self.dialogue_box_rect.height - 6,
        )
        pygame.draw.rect(screen, Colors.LIGHT_GRAY, inner_rect, 1)

    def _render_speaker_name(self, screen: pygame.Surface):
        """繪製說話者名字"""
        if not self.current_dialogue.speaker:
            return

        speaker_text = self.speaker_font.render(
            self.current_dialogue.speaker, True, Colors.PRIMARY_COLOR
        )

        # 名字背景框
        name_padding = 8
        name_rect = pygame.Rect(
            self.dialogue_box_rect.x + 20,
            self.dialogue_box_rect.y - 25,
            speaker_text.get_width() + name_padding * 2,
            25,
        )

        pygame.draw.rect(screen, Colors.PRIMARY_COLOR, name_rect)
        pygame.draw.rect(screen, Colors.DARK_GRAY, name_rect, 2)

        # 名字文字
        text_pos = (name_rect.x + name_padding, name_rect.y + 3)
        screen.blit(speaker_text, text_pos)

    def _render_dialogue_text(self, screen: pygame.Surface):
        """繪製對話文字"""
        if not self.displayed_text:
            return

        # 文字區域
        text_rect = pygame.Rect(
            self.dialogue_box_rect.x + UISettings.DIALOGUE_TEXT_MARGIN,
            self.dialogue_box_rect.y + UISettings.DIALOGUE_TEXT_MARGIN,
            self.dialogue_box_rect.width - 2 * UISettings.DIALOGUE_TEXT_MARGIN,
            self.dialogue_box_rect.height - 2 * UISettings.DIALOGUE_TEXT_MARGIN,
        )

        # 分行顯示文字
        lines = self._wrap_text(self.displayed_text, self.font, text_rect.width)

        line_height = self.font.get_height()
        y_offset = 0

        for line in lines:
            if y_offset + line_height > text_rect.height:
                break

            text_surface = self.font.render(line, True, Colors.TEXT_COLOR)
            screen.blit(text_surface, (text_rect.x, text_rect.y + y_offset))
            y_offset += line_height + 2

    def _wrap_text(
        self, text: str, font: pygame.font.Font, max_width: int
    ) -> List[str]:
        """文字換行處理"""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    # 單詞太長，強制分行
                    lines.append(word)
                    current_line = ""

        if current_line:
            lines.append(current_line.strip())

        return lines

    def _render_choice_buttons(self, screen: pygame.Surface):
        """繪製選擇按鈕"""
        choice_y_start = self.dialogue_box_rect.bottom + 10
        button_height = 35
        button_spacing = 8

        for i, choice in enumerate(self.choice_buttons):
            button_rect = pygame.Rect(
                self.dialogue_box_rect.x,
                choice_y_start + i * (button_height + button_spacing),
                self.dialogue_box_rect.width,
                button_height,
            )

            # 按鈕背景
            if i == self.selected_choice:
                button_color = Colors.SECONDARY_COLOR
                border_color = Colors.PRIMARY_COLOR
                border_width = 3
            else:
                button_color = Colors.WHITE
                border_color = Colors.GRAY
                border_width = 2

            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, border_width)

            # 按鈕文字
            choice_text = self.font.render(
                choice.get("text", ""), True, Colors.TEXT_COLOR
            )

            text_x = button_rect.x + 15
            text_y = button_rect.centery - choice_text.get_height() // 2
            screen.blit(choice_text, (text_x, text_y))

            # 選擇指示器
            if i == self.selected_choice:
                indicator = "►"
                indicator_surface = self.font.render(
                    indicator, True, Colors.PRIMARY_COLOR
                )
                indicator_x = button_rect.right - indicator_surface.get_width() - 15
                indicator_y = button_rect.centery - indicator_surface.get_height() // 2
                screen.blit(indicator_surface, (indicator_x, indicator_y))

    def _render_continue_prompt(self, screen: pygame.Surface):
        """繪製繼續提示"""
        prompt_text = "按空白鍵繼續..."
        prompt_surface = self.speaker_font.render(prompt_text, True, Colors.GRAY)

        prompt_x = self.dialogue_box_rect.right - prompt_surface.get_width() - 15
        prompt_y = self.dialogue_box_rect.bottom - prompt_surface.get_height() - 10

        screen.blit(prompt_surface, (prompt_x, prompt_y))

    def skip_text(self):
        """跳過文字顯示動畫"""
        if not self.text_complete:
            self.text_complete = True
            self.displayed_text = self.full_text
            self.waiting_for_input = True

    def set_text_speed(self, speed: int):
        """設定文字顯示速度"""
        self.text_speed = max(10, min(200, speed))

    def is_dialogue_active(self) -> bool:
        """檢查對話是否活躍"""
        return self.is_active

    def get_current_speaker(self) -> str:
        """獲取當前說話者"""
        return self.current_dialogue.speaker if self.current_dialogue else ""

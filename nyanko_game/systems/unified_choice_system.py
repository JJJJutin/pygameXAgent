# -*- coding: utf-8 -*-
"""
統一選擇系統
將活動選擇和對話選擇合併為一個統一的選擇界面
"""

import pygame
from typing import Dict, List, Optional, Any, Callable
from config.settings import *
from systems.dialogue_system import DialogueNode


class UnifiedChoice:
    """統一選擇選項類別"""

    def __init__(self, choice_data: Dict[str, Any], choice_type: str = "auto"):
        """
        初始化選擇選項

        Args:
            choice_data: 選擇數據
            choice_type: 選擇類型 ('dialogue', 'activity', 'scene_action', 'auto')
        """
        # 自動檢測選項類型
        if choice_type == "auto" or choice_type == "mixed":
            if choice_data.get("activity_id"):
                self.choice_type = "activity"
            elif choice_data.get("scene_action") or choice_data.get("target_scene"):
                self.choice_type = "scene_action"
            elif choice_data.get("next_dialogue"):
                self.choice_type = "dialogue"
            else:
                self.choice_type = "dialogue"  # 預設類型
        else:
            self.choice_type = choice_type

        self.text = choice_data.get("text", "")
        self.description = choice_data.get("description", "")

        # 對話相關
        self.next_dialogue = choice_data.get("next_dialogue")
        self.affection_change = choice_data.get("affection_change", 0)
        self.flags = choice_data.get("flags", {})
        self.conditions = choice_data.get("conditions", {})

        # 活動相關
        self.activity_id = choice_data.get("activity_id")
        self.time_cost = choice_data.get("time_cost", 0)
        self.energy_change = choice_data.get("energy_change", 0)
        self.mood_change = choice_data.get("mood_change", 0)

        # 場景動作相關
        self.scene_action = choice_data.get("scene_action")
        self.target_scene = choice_data.get("target_scene")

        # 顯示相關
        self.icon = choice_data.get("icon")
        self.color = choice_data.get("color", Colors.TEXT_COLOR)

    def is_available(self, game_state: Dict[str, Any]) -> bool:
        """檢查選擇是否可用"""
        # 檢查基本條件
        if not self._check_conditions(game_state):
            return False

        # 檢查活動特定條件
        if self.choice_type == "activity":
            # 檢查時間點數（從事件驅動時間系統獲取）
            if self.time_cost > 0:
                # 嘗試從事件驅動時間系統獲取時間點數
                time_points = 0
                if hasattr(game_state, "get") and "time_points" in game_state:
                    time_points = game_state.get("time_points", 0)
                else:
                    # 如果game_state中沒有time_points，嘗試從全局獲取
                    time_points = game_state.get("time_points", 2)  # 預設2點

                if time_points < self.time_cost:
                    return False

            # 檢查體力條件
            if self.energy_change < 0:
                current_energy = game_state.get("nyanko_energy", 100)
                if current_energy + self.energy_change < 0:
                    return False

        return True

    def _check_conditions(self, game_state: Dict[str, Any]) -> bool:
        """檢查選擇條件"""
        # 檢查好感度條件
        if "affection_min" in self.conditions:
            if game_state.get("nyanko_affection", 0) < self.conditions["affection_min"]:
                return False

        if "affection_max" in self.conditions:
            if game_state.get("nyanko_affection", 0) > self.conditions["affection_max"]:
                return False

        # 檢查時間條件
        if "time_period" in self.conditions:
            current_period = game_state.get("current_time_period", "")
            if current_period != self.conditions["time_period"]:
                return False

        # 檢查旗標條件
        if "flags" in self.conditions:
            for flag, required_value in self.conditions["flags"].items():
                if game_state.get("flags", {}).get(flag) != required_value:
                    return False

        return True

    def get_display_text(self) -> str:
        """獲取顯示文字"""
        if self.choice_type == "activity" and self.time_cost > 0:
            return f"{self.text} (消耗{self.time_cost}點)"
        return self.text

    def get_effects_text(self) -> str:
        """獲取效果說明文字"""
        effects = []

        if self.affection_change != 0:
            effects.append(f"好感{self.affection_change:+d}")

        if self.energy_change != 0:
            effects.append(f"體力{self.energy_change:+d}")

        if self.mood_change != 0:
            effects.append(f"心情{self.mood_change:+d}")

        return " | ".join(effects) if effects else ""


class UnifiedChoiceSystem:
    """統一選擇系統"""

    def __init__(self, game_engine):
        """初始化統一選擇系統"""
        self.game_engine = game_engine
        self.choices: List[UnifiedChoice] = []
        self.selected_choice = 0
        self.is_active = False

        # UI相關
        self.choice_box_rect = None
        self.font = None
        self.title_font = None
        self.desc_font = None

        # 回調函數
        self.on_choice_selected: Optional[Callable] = None
        self.on_choice_cancelled: Optional[Callable] = None

        self._initialize_ui()

    def _initialize_ui(self):
        """初始化UI"""
        try:
            self.font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.DIALOGUE_FONT_SIZE
            )
            self.title_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.SPEAKER_FONT_SIZE
            )
            self.desc_font = pygame.font.Font(
                FontSettings.DEFAULT_FONT, FontSettings.FONT_SIZE_SMALL
            )
        except (FileNotFoundError, OSError):
            self.font = pygame.font.Font(None, FontSettings.DIALOGUE_FONT_SIZE)
            self.title_font = pygame.font.Font(None, FontSettings.SPEAKER_FONT_SIZE)
            self.desc_font = pygame.font.Font(None, FontSettings.FONT_SIZE_SMALL)

    def show_choices(
        self,
        choices: List[Dict[str, Any]],
        title: str = "選擇行動",
        choice_type: str = "dialogue",
    ):
        """
        顯示選擇選項

        Args:
            choices: 選擇選項數據列表
            title: 選擇標題
            choice_type: 選擇類型
        """
        self.choices = []
        game_state = getattr(self.game_engine, "game_state", {})

        # 如果是活動選擇，需要獲取當前時間點數
        if choice_type == "activity" and hasattr(
            self.game_engine, "event_driven_time_system"
        ):
            time_system = self.game_engine.event_driven_time_system
            if time_system:
                current_time_points = time_system.game_time.time_points
                game_state["time_points"] = current_time_points

        for choice_data in choices:
            # 對於 mixed 類型，讓 UnifiedChoice 自動檢測類型
            if choice_type == "mixed":
                choice = UnifiedChoice(choice_data, "auto")
            else:
                choice = UnifiedChoice(choice_data, choice_type)
            if choice.is_available(game_state):
                self.choices.append(choice)

        if self.choices:
            self.selected_choice = 0
            self.is_active = True
            self.title = title
        else:
            print("沒有可用的選擇選項")

    def show_dialogue_choices(
        self, dialogue_node: DialogueNode, game_state: Dict[str, Any]
    ):
        """顯示對話選擇選項"""
        valid_choices = dialogue_node.get_valid_choices(game_state)

        # 轉換對話選擇為統一格式
        unified_choices = []
        for choice in valid_choices:
            unified_choices.append(
                {
                    "text": choice.get("text", ""),
                    "next_dialogue": choice.get("next_dialogue"),
                    "affection_change": choice.get("affection_change", 0),
                    "flags": choice.get("flags", {}),
                    "conditions": choice.get("conditions", {}),
                }
            )

        self.show_choices(unified_choices, "にゃんこ的回應", "dialogue")

    def show_activity_choices(self, activities: List[Any]):
        """顯示活動選擇選項"""
        activity_choices = []

        for activity in activities:
            activity_choices.append(
                {
                    "text": activity.name,
                    "description": activity.description,
                    "activity_id": activity.id,
                    "time_cost": activity.time_cost,
                    "energy_change": activity.energy_change,
                    "affection_change": activity.affection_change,
                    "mood_change": activity.mood_change,
                }
            )

        self.show_choices(activity_choices, "選擇活動", "activity")

    def show_scene_action_choices(self, scene_actions: List[Dict[str, Any]]):
        """顯示場景動作選擇"""
        self.show_choices(scene_actions, "場景動作", "scene_action")

    def add_contextual_choices(
        self, base_choices: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        為對話選擇添加上下文選項（如活動、場景切換等）

        Args:
            base_choices: 基礎對話選擇

        Returns:
            包含上下文選項的完整選擇列表
        """
        enhanced_choices = base_choices.copy()

        # 獲取當前場景
        current_scene = "living_room"  # 預設值
        if (
            hasattr(self.game_engine, "scene_manager")
            and self.game_engine.scene_manager
        ):
            current_scene = getattr(
                self.game_engine.scene_manager, "current_scene_name", "living_room"
            )

        # 場景名稱映射 (從類名映射到簡單名稱)
        scene_name_map = {
            "EnhancedLivingRoomScene": "living_room",
            "LivingRoomScene": "living_room",
            "KitchenScene": "kitchen",
            "BedroomScene": "bedroom",
            "BathroomScene": "bathroom",
            "MainMenuScene": "main_menu",
        }

        # 如果獲取的是類名，轉換為簡單名稱
        if current_scene in scene_name_map:
            current_scene = scene_name_map[current_scene]
        elif (
            hasattr(self.game_engine, "scene_manager")
            and self.game_engine.scene_manager.current_scene
        ):
            scene_class_name = (
                self.game_engine.scene_manager.current_scene.__class__.__name__
            )
            current_scene = scene_name_map.get(scene_class_name, "living_room")

        # 添加活動選項（如果當前時間段有可用活動）
        if hasattr(self.game_engine, "get_scene_activities"):
            activities = self.game_engine.get_scene_activities(current_scene)

            if activities:
                # 為前3個活動添加直接選項
                for i, activity in enumerate(activities[:3]):
                    activity_choice = {
                        "text": f"🎯 {activity.name}",
                        "description": activity.description,
                        "activity_id": activity.id,
                        "time_cost": activity.time_cost,
                        "energy_change": activity.energy_change,
                        "affection_change": activity.affection_change,
                        "mood_change": activity.mood_change,
                        "color": Colors.SECONDARY_COLOR,
                    }

                    # 檢查活動可用性
                    game_state = getattr(self.game_engine, "game_state", {})
                    if hasattr(self.game_engine, "event_driven_time_system"):
                        time_system = self.game_engine.event_driven_time_system
                        time_points = (
                            time_system.game_time.time_points if time_system else 0
                        )

                        # 檢查時間點數是否足夠
                        if time_points >= activity.time_cost:
                            enhanced_choices.append(activity_choice)
                        else:
                            # 時間點數不足，但仍顯示選項（會標示為不可用）
                            activity_choice["text"] = (
                                f"⏳ {activity.name} (時間點數不足)"
                            )
                            activity_choice["color"] = Colors.GRAY
                            enhanced_choices.append(activity_choice)
                    else:
                        enhanced_choices.append(activity_choice)

                # 如果有更多活動，添加"查看更多活動"選項
                if len(activities) > 3:
                    enhanced_choices.append(
                        {
                            "text": "💫 查看更多活動...",
                            "description": "查看所有可用的活動選項",
                            "scene_action": "show_all_activities",
                            "color": Colors.GRAY,
                        }
                    )

        # 根據場景添加特定的場景動作
        if current_scene == "living_room":
            # 客廳場景 - 添加場景切換選項
            scene_choices = [
                {
                    "text": "🍳 去廚房看看",
                    "target_scene": "kitchen",
                    "scene_action": "change_scene",
                    "description": "和にゃんこ一起去廚房",
                },
                {
                    "text": "🛏️ 去臥室休息",
                    "target_scene": "bedroom",
                    "scene_action": "change_scene",
                    "description": "去臥室放鬆一下",
                },
                {
                    "text": "🛁 去浴室",
                    "target_scene": "bathroom",
                    "scene_action": "change_scene",
                    "description": "去浴室整理一下",
                },
            ]
            enhanced_choices.extend(scene_choices)

        elif current_scene == "kitchen":
            # 廚房場景 - 添加廚房特定選項
            kitchen_choices = [
                {
                    "text": "🥘 一起做料理",
                    "activity_id": "cooking_together",
                    "time_cost": 2,
                    "energy_change": -10,
                    "affection_change": 5,
                    "mood_change": 3,
                    "description": "和にゃんこ一起準備美味的料理",
                },
                {
                    "text": "☕ 泡茶聊天",
                    "activity_id": "tea_chat",
                    "time_cost": 1,
                    "energy_change": 5,
                    "affection_change": 3,
                    "mood_change": 2,
                    "description": "在廚房泡茶和にゃんこ聊天",
                },
            ]
            enhanced_choices.extend(kitchen_choices)

        elif current_scene == "bedroom":
            # 臥室場景 - 添加臥室特定選項
            bedroom_choices = [
                {
                    "text": "😴 一起午睡",
                    "activity_id": "nap_together",
                    "time_cost": 2,
                    "energy_change": 20,
                    "affection_change": 4,
                    "mood_change": 5,
                    "description": "和にゃんこ一起午睡恢復精力",
                    "conditions": {"time_period": "afternoon"},
                },
                {
                    "text": "💤 準備睡覺",
                    "activity_id": "sleep_together",
                    "time_cost": 3,
                    "energy_change": 50,
                    "affection_change": 6,
                    "mood_change": 8,
                    "description": "和にゃんこ一起進入夢鄉",
                    "conditions": {"time_period": "night"},
                },
            ]
            enhanced_choices.extend(bedroom_choices)

        # 添加通用選項
        general_choices = [
            {
                "text": "⏰ 跳過時間",
                "scene_action": "skip_time",
                "description": "跳過當前時間段",
                "color": Colors.GRAY,
            },
            {
                "text": "💬 繼續聊天",
                "scene_action": "continue_chat",
                "description": "和にゃんこ繼續聊天",
                "affection_change": 1,
            },
        ]
        enhanced_choices.extend(general_choices)

        return enhanced_choices

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        處理事件

        Args:
            event: pygame事件

        Returns:
            bool: 是否處理了事件
        """
        if not self.is_active or not self.choices:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_choice = (self.selected_choice - 1) % len(self.choices)
                return True

            elif event.key == pygame.K_DOWN:
                self.selected_choice = (self.selected_choice + 1) % len(self.choices)
                return True

            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._execute_selected_choice()
                return True

            elif event.key == pygame.K_ESCAPE:
                self._cancel_choice()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵
                mouse_pos = getattr(event, "pos", pygame.mouse.get_pos())
                choice_index = self._get_clicked_choice(mouse_pos)
                if choice_index is not None:
                    self.selected_choice = choice_index
                    self._execute_selected_choice()
                    return True

        return False

    def _execute_selected_choice(self):
        """執行選中的選擇"""
        if not self.choices or self.selected_choice >= len(self.choices):
            return

        choice = self.choices[self.selected_choice]

        # 執行選擇效果
        self._apply_choice_effects(choice)

        # 根據選擇類型執行相應操作
        if choice.choice_type == "dialogue":
            self._handle_dialogue_choice(choice)
        elif choice.choice_type == "activity":
            self._handle_activity_choice(choice)
        elif choice.choice_type == "scene_action":
            self._handle_scene_action_choice(choice)

        # 調用回調函數
        if self.on_choice_selected:
            self.on_choice_selected(choice)

        self.is_active = False

    def _apply_choice_effects(self, choice: UnifiedChoice):
        """應用選擇效果"""
        if not hasattr(self.game_engine, "game_state"):
            return

        game_state = self.game_engine.game_state

        # 應用好感度變化
        if choice.affection_change != 0:
            current_affection = game_state.get("nyanko_affection", 0)
            new_affection = max(
                0, min(100, current_affection + choice.affection_change)
            )
            game_state["nyanko_affection"] = new_affection
            print(f"好感度變化: {choice.affection_change:+d} (當前: {new_affection})")

        # 應用其他狀態變化
        if choice.energy_change != 0:
            current_energy = game_state.get("nyanko_energy", 100)
            new_energy = max(0, min(100, current_energy + choice.energy_change))
            game_state["nyanko_energy"] = new_energy

        if choice.mood_change != 0:
            current_mood = game_state.get("nyanko_mood", 75)
            new_mood = max(0, min(100, current_mood + choice.mood_change))
            game_state["nyanko_mood"] = new_mood

        # 設定旗標
        if choice.flags:
            if "flags" not in game_state:
                game_state["flags"] = {}
            game_state["flags"].update(choice.flags)

    def _handle_dialogue_choice(self, choice: UnifiedChoice):
        """處理對話選擇"""
        if choice.next_dialogue and hasattr(self.game_engine, "start_dialogue"):
            self.game_engine.start_dialogue(choice.next_dialogue)

    def _handle_activity_choice(self, choice: UnifiedChoice):
        """處理活動選擇"""
        if choice.activity_id and hasattr(self.game_engine, "execute_activity"):
            success = self.game_engine.execute_activity(choice.activity_id)
            if success:
                print(f"✅ 成功執行活動: {choice.text}")

                # 顯示活動結果（如果有相關UI）
                if (
                    hasattr(self.game_engine, "scene_manager")
                    and self.game_engine.scene_manager.current_scene
                ):
                    current_scene = self.game_engine.scene_manager.current_scene
                    if hasattr(current_scene, "show_activity_result"):
                        result_info = {
                            "activity_name": choice.text,
                            "energy_change": choice.energy_change,
                            "affection_change": choice.affection_change,
                            "mood_change": choice.mood_change,
                            "time_cost": choice.time_cost,
                        }
                        current_scene.show_activity_result(result_info)
            else:
                print(f"❌ 無法執行活動: {choice.text}")
        else:
            print(f"⚠️ 活動系統未初始化或活動ID無效: {choice.activity_id}")

    def _handle_scene_action_choice(self, choice: UnifiedChoice):
        """處理場景動作選擇"""
        if choice.scene_action == "change_scene" and choice.target_scene:
            if hasattr(self.game_engine, "scene_manager"):
                self.game_engine.scene_manager.change_scene(choice.target_scene)

        elif choice.scene_action == "show_activities":
            # 顯示活動選項
            if hasattr(self.game_engine, "get_scene_activities"):
                current_scene = getattr(
                    self.game_engine, "current_scene", "living_room"
                )
                activities = self.game_engine.get_scene_activities(current_scene)
                self.show_activity_choices(activities)
                return  # 不關閉選擇界面

        elif choice.scene_action == "show_all_activities":
            # 顯示所有活動選項
            if hasattr(self.game_engine, "get_scene_activities"):
                current_scene = getattr(
                    self.game_engine, "current_scene", "living_room"
                )
                activities = self.game_engine.get_scene_activities(current_scene)
                self.show_activity_choices(activities)
                return  # 不關閉選擇界面

        elif choice.scene_action == "skip_time":
            # 跳過時間
            if hasattr(self.game_engine, "skip_time_period"):
                self.game_engine.skip_time_period()
            elif hasattr(self.game_engine, "event_driven_time_system"):
                self.game_engine.event_driven_time_system.skip_time_period()

        elif choice.scene_action == "continue_chat":
            # 繼續聊天 - 隨機選擇一個適當的對話
            chat_dialogues = ["casual_chat_01", "relaxing_01"]
            import random

            dialogue_id = random.choice(chat_dialogues)
            if hasattr(self.game_engine, "start_dialogue"):
                self.game_engine.start_dialogue(dialogue_id)

    def _cancel_choice(self):
        """取消選擇"""
        self.is_active = False
        if self.on_choice_cancelled:
            self.on_choice_cancelled()

    def _get_clicked_choice(self, mouse_pos: tuple) -> Optional[int]:
        """獲取點擊的選擇項目索引"""
        if not self.choice_box_rect:
            return None

        # 計算選擇按鈕位置
        choice_y_start = self.choice_box_rect.y + 60
        button_height = 50
        button_spacing = 5

        for i, choice in enumerate(self.choices):
            button_rect = pygame.Rect(
                self.choice_box_rect.x + 20,
                choice_y_start + i * (button_height + button_spacing),
                self.choice_box_rect.width - 40,
                button_height,
            )

            if button_rect.collidepoint(mouse_pos):
                return i

        return None

    def render(self, screen: pygame.Surface):
        """渲染選擇界面"""
        if not self.is_active or not self.choices:
            return

        screen_width, screen_height = screen.get_size()

        # 計算選擇框大小
        box_width = min(600, screen_width - 100)
        box_height = min(len(self.choices) * 55 + 120, screen_height - 100)
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2

        self.choice_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        # 選擇框背景
        choice_surface = pygame.Surface((box_width, box_height))
        choice_surface.fill(Colors.WHITE)
        pygame.draw.rect(
            choice_surface, Colors.PRIMARY_COLOR, choice_surface.get_rect(), 3
        )

        # 標題
        title_text = self.title_font.render(
            getattr(self, "title", "選擇"), True, Colors.DARK_GRAY
        )
        title_rect = title_text.get_rect()
        title_rect.centerx = box_width // 2
        title_rect.y = 15
        choice_surface.blit(title_text, title_rect)

        # 選擇選項
        y_offset = 60
        for i, choice in enumerate(self.choices):
            self._render_choice_button(choice_surface, choice, i, y_offset, box_width)
            y_offset += 55

        # 操作提示
        hint_text = self.desc_font.render(
            "↑↓ 選擇  Enter 確認  ESC 取消", True, Colors.GRAY
        )
        hint_rect = hint_text.get_rect()
        hint_rect.centerx = box_width // 2
        hint_rect.y = box_height - 25
        choice_surface.blit(hint_text, hint_rect)

        screen.blit(choice_surface, (box_x, box_y))

    def _render_choice_button(
        self,
        surface: pygame.Surface,
        choice: UnifiedChoice,
        index: int,
        y_offset: int,
        box_width: int,
    ):
        """渲染選擇按鈕"""
        button_rect = pygame.Rect(20, y_offset, box_width - 40, 45)

        # 按鈕背景
        if index == self.selected_choice:
            button_color = Colors.SECONDARY_COLOR
            border_color = Colors.PRIMARY_COLOR
            border_width = 3
        else:
            button_color = Colors.LIGHT_GRAY
            border_color = Colors.GRAY
            border_width = 2

        pygame.draw.rect(surface, button_color, button_rect)
        pygame.draw.rect(surface, border_color, button_rect, border_width)

        # 按鈕文字
        text_color = (
            Colors.TEXT_COLOR if choice.color == Colors.TEXT_COLOR else choice.color
        )
        choice_text = self.font.render(choice.get_display_text(), True, text_color)

        text_x = button_rect.x + 15
        text_y = button_rect.y + 5
        surface.blit(choice_text, (text_x, text_y))

        # 效果說明
        effects_text = choice.get_effects_text()
        if effects_text:
            effects_surface = self.desc_font.render(effects_text, True, Colors.GRAY)
            surface.blit(effects_surface, (text_x, text_y + 25))

        # 選擇指示器
        if index == self.selected_choice:
            indicator = "►"
            indicator_surface = self.font.render(indicator, True, Colors.PRIMARY_COLOR)
            indicator_x = button_rect.right - indicator_surface.get_width() - 15
            indicator_y = button_rect.centery - indicator_surface.get_height() // 2
            surface.blit(indicator_surface, (indicator_x, indicator_y))

# 對話系統選項顯示順序修復報告

## 修改概述

根據用戶需求「讓選項在對話結束後再呈現」，修改了對話系統的邏輯，使選項不會在文字顯示完成後立即出現，而是需要玩家主動確認後才顯示。

## 修改內容

### 1. 移除自動選項顯示

**修改位置：** `systems/dialogue_system.py` - `update()` 方法

**原邏輯：**

- 文字顯示完成後自動檢查是否有選項
- 如果有選項則立即顯示

**新邏輯：**

- 文字顯示完成後不自動顯示選項
- 等待玩家主動確認

```python
# 更新文字顯示
if not self.text_complete:
    self._update_text_display(dt)

# 文字顯示完成後，等待玩家確認再顯示選項
# 不在這裡自動顯示選項，而是等待玩家按鍵或點擊
```

### 2. 修改確認鍵處理邏輯

**修改位置：** `systems/dialogue_system.py` - `_handle_confirm_key()` 方法

**新增邏輯：**

- 文字完成後第一次按確認鍵：檢查並顯示選項
- 如果有選項則顯示選項，如果沒有選項則繼續下一個對話

```python
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
```

### 3. 修改鼠標點擊處理邏輯

**修改位置：** `systems/dialogue_system.py` - `_handle_mouse_click()` 方法

**新增邏輯：**

- 點擊對話框時，如果文字已完成但選項尚未顯示，則顯示選項
- 與鍵盤確認鍵保持一致的行為

```python
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
```

### 4. 改進繼續提示顯示

**修改位置：** `systems/dialogue_system.py` - `render()` 方法

**改進內容：**

- 智能提示文字：如果有選項則顯示「按空白鍵查看選項...」
- 如果沒有選項則顯示「按空白鍵繼續...」

```python
# 繪製繼續提示（文字完成後，且尚未顯示選項時）
elif self.text_complete and not self.choice_buttons and not self.waiting_for_choice:
    # 檢查是否有潛在的選項需要顯示
    has_choices = self.current_dialogue.has_choices() if self.current_dialogue else False
    if has_choices:
        prompt_text = "按空白鍵查看選項..."
    else:
        prompt_text = "按空白鍵繼續..."
```

## 用戶體驗改進

### 修改前的流程：

1. 文字動態顯示
2. 文字完成 → **選項立即出現**
3. 玩家選擇選項

### 修改後的流程：

1. 文字動態顯示
2. 文字完成 → **顯示「按空白鍵查看選項...」提示**
3. 玩家按確認鍵 → **選項出現**
4. 玩家選擇選項

## 優勢

1. **更好的閱讀體驗**：玩家可以完整閱讀對話內容，不會被突然出現的選項打斷
2. **更自然的節奏**：給玩家時間消化對話內容
3. **更清晰的交互**：明確區分「閱讀階段」和「選擇階段」
4. **智能提示**：根據是否有選項顯示不同的提示文字

## 技術細節

### 狀態管理

- `text_complete`：文字是否顯示完成
- `waiting_for_choice`：是否正在等待選擇（統一選擇系統）
- `choice_buttons`：當前可用的選項列表

### 渲染條件

```python
# 選項只在玩家確認後顯示
if self.text_complete and self.choice_buttons and not self.waiting_for_choice:
    self._render_choice_buttons(screen)

# 智能繼續提示
elif self.text_complete and not self.choice_buttons and not self.waiting_for_choice:
    # 根據是否有選項顯示不同提示
```

### 事件處理優先級

1. 文字加速顯示（未完成時）
2. 選項顯示檢查（完成後首次確認）
3. 選項選擇處理（選項已顯示時）
4. 對話繼續（無選項時）

## 測試建議

### 測試場景

1. **有選項的對話**：
   - 文字顯示完成後應顯示「按空白鍵查看選項...」
   - 按確認鍵後應顯示選項
2. **無選項的對話**：

   - 文字顯示完成後應顯示「按空白鍵繼續...」
   - 按確認鍵後應進入下一個對話或結束

3. **統一選擇系統**：

   - 確保統一選擇系統的選項也遵循相同的顯示邏輯

4. **鼠標操作**：
   - 點擊對話框應與按鍵操作有相同效果

## 兼容性

此修改保持了與現有系統的完全兼容：

- 統一選擇系統正常工作
- 傳統選擇按鈕正常工作
- 對話數據格式無需修改
- 其他系統無需調整

## 總結

此修改成功實現了「讓選項在對話結束後再呈現」的需求，提供了更好的用戶體驗，同時保持了系統的穩定性和兼容性。玩家現在可以完整閱讀對話內容後，再決定是否查看和選擇選項。

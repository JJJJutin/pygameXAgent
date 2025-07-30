# T-Spin 系統實作文檔

## 概述

此文檔詳細說明了在俄羅斯方塊遊戲中實作的完整 T-Spin 檢測系統，包括：

- T-Spin Mini
- T-Spin Single
- T-Spin Double
- T-Spin Triple

## T-Spin 檢測規則

### 基本條件

1. **方塊類型**：只有 T 方塊能執行 T-Spin
2. **最後動作**：最後一個動作必須是旋轉（`last_move_was_rotation = True`）
3. **3-Corner 規則**：T 方塊周圍 4 個對角位置中，至少 3 個必須被佔用

### 3-Corner 規則詳細說明

檢查 T 方塊中心位置周圍的 4 個對角位置：

- 左上角 (center_x-1, center_y-1)
- 右上角 (center_x+1, center_y-1)
- 左下角 (center_x-1, center_y+1)
- 右下角 (center_x+1, center_y+1)

被佔用的條件包括：

- 遊戲區域邊界（牆壁、地板）
- 已放置的方塊

### 2-Corner 規則（Mini vs 正常 T-Spin）

根據 T 方塊的朝向檢查「前角」（指向側的角落）：

- **旋轉 0°（朝上）**：前角 = 左上角、右上角
- **旋轉 90°（朝右）**：前角 = 右上角、右下角
- **旋轉 180°（朝下）**：前角 = 左下角、右下角
- **旋轉 270°（朝左）**：前角 = 左上角、左下角

#### 判斷邏輯

- **正常 T-Spin**：前角兩個都被佔用 或 使用了特殊 kick
- **Mini T-Spin**：前角只有一個或零個被佔用（且非特殊 kick）

### 特殊 Kick 例外

某些 SRS Wall Kick 會覆蓋 2-Corner 規則，即使前角未完全佔用也算正常 T-Spin：

- **TST kick**：通常是最後一個 kick 測試（索引 4）
- **Fin kick**：垂直移動 2 格的 kick (`abs(kick_offset_y) == 2`)

## T-Spin 類型和分數

### T-Spin Mini

| 消行數 | 分數 | 名稱               | 困難動作 |
| ------ | ---- | ------------------ | -------- |
| 0      | 100  | T-SPIN MINI        | 否       |
| 1      | 200  | T-SPIN MINI SINGLE | 是       |
| 2      | 400  | T-SPIN MINI DOUBLE | 是       |
| 3      | -    | 不可能             | -        |

### 正常 T-Spin

| 消行數 | 分數 | 名稱          | 困難動作 |
| ------ | ---- | ------------- | -------- |
| 0      | 400  | T-SPIN        | 否       |
| 1      | 800  | T-SPIN SINGLE | 是       |
| 2      | 1200 | T-SPIN DOUBLE | 是       |
| 3      | 1600 | T-SPIN TRIPLE | 是       |

## Back-to-Back 系統

- **觸發條件**：連續執行困難動作（Tetris、T-Spin Single/Double/Triple、T-Spin Mini Single/Double）
- **加成**：分數 × 1.5
- **不中斷 B2B 的動作**：T-Spin 0 lines（Mini 或正常）
- **中斷 B2B 的動作**：非困難的消行動作

## 實作細節

### 核心方法

1. `check_t_spin()` - 主要檢測邏輯
2. `try_wall_kick()` - 記錄 kick 資訊
3. `calculate_score()` - 分數計算系統

### 關鍵變數

- `last_move_was_rotation` - 記錄最後動作是否為旋轉
- `last_kick_index` - 記錄使用的 kick 索引
- `last_kick_offset` - 記錄 kick 的偏移量
- `back_to_back_count` - Back-to-back 計數
- `last_clear_was_difficult` - 上次清除是否為困難動作

### Debug 輸出

遊戲會在控制台輸出 T-Spin 檢測過程：

```
T-spin 檢測: 中心位置=(x,y), 被填充的角落=3/4 [0,1,2], 旋轉=0
檢測到正常 T-spin!
```

## 測試建議

1. **基本 T-Spin**：在標準 T-Spin 設置中測試各種旋轉
2. **Mini T-Spin**：測試只有後角被佔用的情況
3. **特殊 Kick**：測試 TST 和 Fin kick 的例外情況
4. **Back-to-Back**：測試連續 T-Spin 的分數加成
5. **邊界情況**：測試貼近牆壁和地板的 T-Spin

## 參考資料

- [Tetris Wiki - T-Spin](https://tetris.wiki/T-Spin)
- [Hard Drop - T-Spin](https://harddrop.com/wiki/T-Spin)
- SRS (Super Rotation System) 規範

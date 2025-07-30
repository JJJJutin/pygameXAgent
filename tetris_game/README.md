# 俄羅斯方塊遊戲 (Tetris Game)

一個使用 Python 和 Pygame 開發的完整俄羅斯方塊遊戲，採用模組化架構設計。

## 特色功能

### 核心功能

- **SRS 旋轉系統**：標準的 Super Rotation System 和 Wall Kick
- **7-bag 隨機器系統**：確保方塊分布的公平性
- **Hold 功能**：可以儲存當前方塊供稍後使用
- **幽靈方塊預覽**：顯示方塊的落點位置

### 進階功能

- **T-spin 檢測**：完整的 T-spin 和 Mini T-spin 檢測
- **Perfect Clear 檢測**：全消檢測和特殊計分
- **Combo 系統**：連續消行加成系統
- **Back-to-back 系統**：困難動作連續獎勵
- **Lock Delay 系統**：方塊鎖定延遲機制
- **DAS 輸入系統**：專業級的方向鍵重複輸入

## 操作說明

| 按鍵    | 功能                 |
| ------- | -------------------- |
| ←→      | 移動方塊（支援 DAS） |
| ↓       | 軟降                 |
| X/↑     | 順時針旋轉           |
| Z       | 逆時針旋轉           |
| Space   | 硬降                 |
| C/Shift | Hold 功能            |
| R       | 重新開始             |

## 檔案結構

```
tetris_game/
├── main.py                 # 主程式執行檔
├── __init__.py            # 主模組初始化
├── config/                # 配置模組
│   ├── __init__.py
│   ├── constants.py       # 遊戲常數定義
│   └── shapes.py          # 方塊形狀和 Wall Kick 資料
├── core/                  # 核心邏輯模組
│   ├── __init__.py
│   └── game.py            # 主要遊戲邏輯
├── game_objects/          # 遊戲物件模組
│   ├── __init__.py
│   ├── tetromino.py       # 方塊物件類別
│   └── grid.py            # 遊戲區域類別
├── ui/                    # 使用者介面模組
│   ├── __init__.py
│   └── renderer.py        # UI 渲染器
└── utils/                 # 工具模組（預留）
```

## 安裝和執行

### 環境需求

- Python 3.6 或更高版本
- Pygame 庫

### 安裝步驟

1. 安裝 Pygame：

   ```bash
   pip install pygame
   ```

2. 執行遊戲：
   ```bash
   python main.py
   ```

## 計分系統

### 基礎分數

- Single (1 行): 100 分
- Double (2 行): 300 分
- Triple (3 行): 500 分
- Tetris (4 行): 800 分

### T-spin 分數

- T-spin (0 行): 400 分
- T-spin Single: 800 分
- T-spin Double: 1200 分
- T-spin Triple: 1600 分
- Mini T-spin: 100-400 分

### 特殊加成

- **Combo 加成**：連續消行每次 +50 分
- **Back-to-back 加成**：困難動作連續時 +50% 分數
- **Perfect Clear 加成**：全消時大幅加分
- **軟降/硬降加成**：手動下落額外分數

## 技術特點

### 模組化設計

- 清晰的職責分離
- 易於維護和擴展
- 可重用的組件

### 標準化實現

- 符合現代俄羅斯方塊標準
- SRS 旋轉系統
- 標準的計分規則

### 效能優化

- 高效的碰撞檢測
- 流暢的 60 FPS 運行
- 優化的渲染系統

## 開發說明

這個遊戲採用物件導向設計，主要類別包括：

- `Game`: 遊戲核心邏輯控制器
- `Tetromino`: 四格方塊物件
- `GameGrid`: 遊戲區域管理
- `UIRenderer`: 視覺渲染器

每個模組都有清楚的職責分工，便於後續的功能擴展和維護。

## 版本資訊

- 版本：1.0.0
- 開發者：Tetris Game Developer
- 授權：MIT License

## 未來計劃

- [ ] 音效和音樂系統
- [ ] 多人對戰模式
- [ ] 自訂按鍵設定
- [ ] 成績記錄系統
- [ ] 不同遊戲模式
- [ ] 視覺特效增強

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個遊戲！

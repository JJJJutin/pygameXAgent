# 俄羅斯方塊遊戲專案

## 專案結構重組說明

原本位於 `class3/tetris.py` 的單一檔案遊戲已經重新組織成模組化結構，提升了程式碼的可維護性和可擴展性。

## 新的檔案結構

```
tetris_game/                   # 主遊戲資料夾
├── main.py                    # 主程式執行檔
├── __init__.py               # 主模組初始化
├── README.md                 # 遊戲說明文檔
├── requirements.txt          # 依賴套件清單
├── config/                   # 配置模組
│   ├── __init__.py
│   ├── constants.py          # 遊戲常數（顏色、尺寸、速度等）
│   └── shapes.py             # 方塊形狀定義和Wall Kick資料
├── core/                     # 核心邏輯模組
│   ├── __init__.py
│   └── game.py               # 主要遊戲邏輯類別
├── game_objects/             # 遊戲物件模組
│   ├── __init__.py
│   ├── tetromino.py          # 四格方塊物件類別
│   └── grid.py               # 遊戲區域類別
├── ui/                       # 使用者介面模組
│   ├── __init__.py
│   └── renderer.py           # UI渲染器
└── utils/                    # 工具模組（預留）
    └── __init__.py

start_tetris.py               # 外部啟動腳本
```

## 模組化的優點

1. **清晰的職責分離**：每個模組都有明確的功能定位
2. **易於維護**：修改某個功能不會影響其他部分
3. **便於擴展**：可以輕鬆添加新功能
4. **程式碼重用**：各模組可以獨立測試和使用
5. **團隊協作**：多人開發時可以分工協作

## 啟動方式

### 方法 1：直接執行主程式

```bash
cd tetris_game
python main.py
```

### 方法 2：使用啟動腳本

```bash
python start_tetris.py
```

## 功能保持完整

重組後的遊戲保持了原有的所有功能：

- ✅ SRS 旋轉系統和 Wall Kick
- ✅ 7-bag 隨機器系統
- ✅ Hold 功能
- ✅ 幽靈方塊預覽
- ✅ T-spin 檢測（包括 Mini T-spin）
- ✅ Perfect Clear 檢測
- ✅ Combo 系統
- ✅ Back-to-back 系統
- ✅ Lock Delay 系統
- ✅ DAS 輸入系統
- ✅ 完整的計分系統

## 後續擴展建議

1. **音效系統**：在 `utils/` 添加音效管理模組
2. **設定系統**：在 `config/` 添加可配置的遊戲設定
3. **成績系統**：添加高分記錄功能
4. **多人模式**：擴展核心邏輯支援多人對戰
5. **視覺特效**：增強 UI 渲染器的視覺效果

這個模組化結構為未來的功能擴展提供了良好的基礎架構！

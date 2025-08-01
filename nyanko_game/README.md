# にゃんこと一緒 ～貓娘女僕的同居日常～ v2.0

一個以 pygame 開發的視覺小說/戀愛模擬遊戲，以可愛的貓娘女僕にゃんこ為主角。

## 🎮 遊戲特色

- 🐱 可愛的貓娘女僕角色にゃんこ
- 💬 豐富的對話系統與選擇分支
- ❤️ 深度好感度系統
- ⏰ 動態時間與活動系統
- 🎵 沉浸式音效與音樂
- 🏠 多場景互動體驗
- 💾 完整的存檔系統

## 🔧 系統需求

- Python 3.8+
- pygame 2.0+
- Windows 10+ / macOS / Linux

## 🚀 安裝與執行

### 基本安裝
```bash
# 1. 安裝 Python 依賴
pip install pygame

# 2. 執行遊戲
python main.py
```

### 開發環境
```bash
# 使用開發工具運行
python scripts/run_dev.py run

# 檢查依賴
python scripts/run_dev.py check

# 查看專案結構
python scripts/run_dev.py struct
```

## 📁 專案結構 (v2.0 重構版)

```
nyanko_game/
├── 📁 app/                          # 應用程式主體
│   ├── launcher.py                  # 應用程式啟動器
│   └── config.py                    # 應用程式配置
├── 📁 core/                         # 核心引擎
│   ├── engine.py                    # 主要遊戲引擎
│   ├── state_manager.py             # 遊戲狀態管理
│   ├── event_dispatcher.py          # 事件分發器
│   └── game_loop.py                 # 遊戲主循環
├── 📁 scenes/                       # 場景系統
│   ├── scene_base.py                # 場景基底類別
│   ├── scene_manager.py             # 場景管理器
│   ├── 📁 menu/                     # 選單相關場景
│   └── 📁 gameplay/                 # 遊戲場景
├── 📁 systems/                      # 遊戲系統
│   ├── 📁 character/                # 角色系統
│   ├── 📁 dialogue/                 # 對話系統
│   ├── 📁 time/                     # 時間系統
│   ├── 📁 events/                   # 事件系統
│   ├── 📁 audio/                    # 音效系統
│   ├── 📁 ui/                       # UI 系統
│   ├── 📁 graphics/                 # 圖形系統
│   └── 📁 save/                     # 存檔系統
├── 📁 data/                         # 資料層
│   ├── 📁 models/                   # 資料模型
│   ├── 📁 repositories/             # 資料存取層
│   └── 📁 validators/               # 資料驗證
├── 📁 config/                       # 配置檔案
├── 📁 utils/                        # 工具函數
├── 📁 assets/                       # 遊戲資源
├── 📁 tests/                        # 測試檔案
├── 📁 scripts/                      # 開發腳本
└── 📄 main.py                       # 程式入口點
```

## 🎯 操作說明

- **Space/Enter**: 確認/繼續對話
- **ESC**: 返回/暫停選單
- **F11**: 切換全螢幕模式
- **F1**: 顯示除錯資訊 (除錯模式)
- **F2**: 切換FPS顯示
- **F12**: 截圖

## 🛠️ 開發說明

### 新增對話
編輯 `assets/data/dialogue_data.json` 檔案來新增或修改對話內容。

### 新增場景
1. 在 `scenes/gameplay/` 目錄下建立新的場景檔案
2. 繼承 `scene_base.BaseScene` 類別
3. 在場景管理器中註冊新場景

### 新增角色
1. 在 `systems/character/` 目錄下建立角色檔案
2. 定義角色屬性和行為
3. 在對話系統中配置角色資料

### 修改設定
編輯 `config/game_config.py` 來調整遊戲設定。

## 🏗️ 架構特色

### 模組化設計
- **清晰的職責分離**: 每個模組專注特定功能
- **低耦合高內聚**: 模組間依賴關係簡單明確
- **易於擴展**: 新增功能時有清晰的放置位置

### 事件驅動架構
- **發布-訂閱模式**: 系統間通過事件通信
- **解耦設計**: 減少直接依賴關係
- **靈活響應**: 易於添加新的事件處理邏輯

### 統一配置管理
- **集中配置**: 所有設定集中管理
- **分類清晰**: 按功能區分配置檔案
- **動態載入**: 支援運行時配置更新

### 完整日誌系統
- **分級日誌**: 支援不同等級的日誌記錄
- **檔案輪轉**: 自動管理日誌檔案大小
- **除錯支援**: 提供詳細的除錯資訊

## 🧪 測試

```bash
# 運行單元測試
python -m pytest tests/unit/

# 運行整合測試  
python -m pytest tests/integration/

# 運行所有測試
python -m pytest tests/
```

## 📚 文檔

- [重構說明](RESTRUCTURE_PLAN.md)
- [遷移指南](MIGRATION_GUIDE.md)

## 📝 授權

此專案僅供學習和非商業用途使用。

## 📈 版本歷史

### v2.0.0 (重構版) - 現在
- 🔄 完全重構檔案結構
- 🏗️ 採用模組化架構設計
- 🎯 引入事件驅動系統
- 📊 統一狀態管理
- 🛠️ 改進開發者工具
- 📝 完善文檔和測試

### v1.0.0 (初版)
- 🎮 基本遊戲功能
- 💬 對話系統
- ❤️ 好感度系統
- ⏰ 時間系統
- 🏠 多場景支援

---

**にゃんこと一緒に素晴らしい時間を過ごしましょう！**

# 🕒 時間系統完整教學指南

## 📋 系統概述

「にゃんこと一緒」採用了一個完整的時間循環系統，將一天劃分為 6 個不同的時間段，每個時間段都有其特殊的氛圍、活動和對話內容。這個系統為遊戲提供了真實 ˇ 的生活節奏感。

## ⏰ 六個時間段詳細說明

### 🌅 1. 清晨 (EARLY_MORNING) - 06:00~08:00

```python
TimePeriod.EARLY_MORNING = "early_morning"  # 6:00-8:00
```

- **特色**：安靜的晨光時光
- **活動**：起床、梳洗、準備新的一天
- **氛圍**：寧靜、清新
- **にゃんこ狀態**：剛起床，有點迷糊可愛

### 🌞 2. 上午 (MORNING) - 08:00~12:00

```python
TimePeriod.MORNING = "morning"  # 8:00-12:00
```

- **特色**：活力充沛的時光
- **活動**：早餐、晨間對話、計劃一天
- **氛圍**：明亮、充滿希望
- **にゃんこ狀態**：精神飽滿，準備好服務主人

### ☀️ 3. 下午 (AFTERNOON) - 12:00~18:00

```python
TimePeriod.AFTERNOON = "afternoon"  # 12:00-18:00
```

- **特色**：悠閒的午後時光
- **活動**：午餐、下午茶、娛樂活動
- **氛圍**：輕鬆、溫暖
- **にゃんこ狀態**：溫和體貼，享受與主人的相處

### 🌆 4. 傍晚 (EVENING) - 18:00~21:00

```python
TimePeriod.EVENING = "evening"  # 18:00-21:00
```

- **特色**：溫馨的黃昏時光
- **活動**：準備晚餐、用餐、餐後整理
- **氛圍**：溫馨、有家的感覺
- **にゃんこ狀態**：專注料理，展現賢妻良母的一面

### 🌙 5. 夜晚 (NIGHT) - 21:00~24:00

```python
TimePeriod.NIGHT = "night"  # 21:00-24:00
```

- **特色**：安靜的夜晚時光
- **活動**：放鬆、聊天、睡前準備
- **氛圍**：寧靜、親密
- **にゃんこ狀態**：溫柔、更加親近

### 🌌 6. 深夜 (LATE_NIGHT) - 00:00~06:00

```python
TimePeriod.LATE_NIGHT = "late_night"  # 0:00-6:00
```

- **特色**：安眠的深夜時光
- **活動**：休息、偶爾的深夜對話
- **氛圍**：寧靜、神秘
- **にゃんこ狀態**：睡眠中或半夢半醒

## 🔧 核心技術實現

### 時間段判斷邏輯

```python
def get_time_period(self) -> TimePeriod:
    """獲取當前時間段"""
    if 6 <= self.hour < 8:
        return TimePeriod.EARLY_MORNING
    elif 8 <= self.hour < 12:
        return TimePeriod.MORNING
    elif 12 <= self.hour < 18:
        return TimePeriod.AFTERNOON
    elif 18 <= self.hour < 21:
        return TimePeriod.EVENING
    elif 21 <= self.hour < 24:
        return TimePeriod.NIGHT
    else:  # 0 <= hour < 6
        return TimePeriod.LATE_NIGHT
```

### 時間推進機制

```python
def update(self, dt: float):
    """更新時間系統"""
    if self.is_paused or not self.auto_advance:
        return

    # 時間推進（dt是以秒為單位的時間差）
    minutes_to_add = dt * self.time_scale * (1/60)  # 轉換為分鐘

    # 檢查時間段變化
    old_period = self.current_time_period
    self.game_time.add_minutes(int(minutes_to_add))
    new_period = self.game_time.get_time_period()

    if old_period != new_period:
        self._on_time_period_change(old_period, new_period)
```

## 🎮 使用方法教學

### 1. 基本時間操作

#### 獲取當前時間信息

```python
# 獲取當前時間段
current_period = game.time_system.get_current_time_period()
print(f"當前時間段: {current_period.value}")

# 獲取格式化時間
time_str = game.time_system.get_current_time().format_full()
print(f"當前時間: {time_str}")

# 獲取時間段名稱
period_name = game.time_system.get_current_time_period_name()
print(f"時間段: {period_name}")
```

#### 手動設置時間

```python
# 設置特定時間
game.time_system.set_time(hour=14, minute=30)  # 設置為下午2:30

# 推進時間
game.time_system.advance_time(hours=2)  # 推進2小時
game.time_system.advance_time(minutes=30)  # 推進30分鐘
```

### 2. 時間事件系統

#### 註冊時間事件

```python
# 創建自定義時間事件
event_data = {
    "id": "tea_time",
    "name": "下午茶時間",
    "description": "每天下午3點的茶點時間",
    "event_type": "daily",
    "trigger_time": {"hour": 15, "minute": 0},
    "callback_function": "on_tea_time"
}

game.time_system.register_time_event("tea_time", event_data)
```

#### 處理時間變化事件

```python
# 設置回調函數
def on_time_period_change(old_period, new_period):
    print(f"時間段變化: {old_period.value} → {new_period.value}")

    # 根據時間段執行不同邏輯
    if new_period == TimePeriod.MORNING:
        # 早晨邏輯
        game.start_dialogue("greeting_morning_01")
    elif new_period == TimePeriod.EVENING:
        # 傍晚邏輯
        game.start_dialogue("cooking_together_01")

game.time_system.on_time_period_change = on_time_period_change
```

### 3. 場景整合

#### 根據時間段切換背景

```python
def get_background_for_time(time_period):
    """根據時間段獲取背景圖片"""
    if time_period in [TimePeriod.EARLY_MORNING, TimePeriod.MORNING, TimePeriod.AFTERNOON]:
        return "bg_livingroom_morning"
    else:
        return "bg_livingroom_evening"

# 在場景渲染中使用
current_period = game.time_system.get_current_time_period()
background_name = get_background_for_time(current_period)
background = image_manager.get_image(background_name)
```

#### 時間相關的對話選擇

```python
def get_dialogue_for_time_period(base_dialogue_id, time_period):
    """根據時間段獲取對應的對話ID"""
    dialogue_map = {
        TimePeriod.EARLY_MORNING: f"{base_dialogue_id}_early_morning",
        TimePeriod.MORNING: f"{base_dialogue_id}_morning",
        TimePeriod.AFTERNOON: f"{base_dialogue_id}_afternoon",
        TimePeriod.EVENING: f"{base_dialogue_id}_evening",
        TimePeriod.NIGHT: f"{base_dialogue_id}_night",
        TimePeriod.LATE_NIGHT: f"{base_dialogue_id}_late_night"
    }
    return dialogue_map.get(time_period, base_dialogue_id)

# 使用範例
current_period = game.time_system.get_current_time_period()
dialogue_id = get_dialogue_for_time_period("greeting", current_period)
game.start_dialogue(dialogue_id)
```

## 📊 實際應用範例

### 完整的一日循環實現

```python
class DailySchedule:
    """一日活動安排"""

    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.schedule = {
            TimePeriod.EARLY_MORNING: [
                {"time": "06:00", "activity": "wake_up", "dialogue": "good_morning_sleepy"},
                {"time": "07:00", "activity": "morning_routine", "dialogue": "morning_wash"}
            ],
            TimePeriod.MORNING: [
                {"time": "08:00", "activity": "breakfast", "dialogue": "breakfast_together_01"},
                {"time": "09:30", "activity": "morning_chat", "dialogue": "morning_plans"},
                {"time": "11:00", "activity": "morning_activity", "dialogue": "what_to_do_morning"}
            ],
            TimePeriod.AFTERNOON: [
                {"time": "12:00", "activity": "lunch", "dialogue": "lunch_time"},
                {"time": "14:00", "activity": "afternoon_tea", "dialogue": "afternoon_tea_time"},
                {"time": "16:00", "activity": "entertainment", "dialogue": "tv_together_01"}
            ],
            TimePeriod.EVENING: [
                {"time": "18:00", "activity": "dinner_prep", "dialogue": "cooking_together_01"},
                {"time": "19:30", "activity": "dinner", "dialogue": "dinner_together_01"},
                {"time": "20:30", "activity": "cleanup", "dialogue": "cleaning_together_01"}
            ],
            TimePeriod.NIGHT: [
                {"time": "21:00", "activity": "relax", "dialogue": "relaxing_01"},
                {"time": "22:00", "activity": "bedtime_prep", "dialogue": "bedroom_bedtime_chat"},
                {"time": "23:00", "activity": "goodnight", "dialogue": "goodnight_01"}
            ]
        }

    def get_current_activities(self):
        """獲取當前時間段的活動"""
        current_period = self.game_engine.time_system.get_current_time_period()
        return self.schedule.get(current_period, [])

    def check_scheduled_events(self):
        """檢查是否有預定事件要觸發"""
        current_time = self.game_engine.time_system.get_current_time()
        current_period = self.game_engine.time_system.get_current_time_period()

        activities = self.get_current_activities()

        for activity in activities:
            # 檢查時間是否匹配
            if self._is_time_match(current_time, activity["time"]):
                self._trigger_activity(activity)

    def _is_time_match(self, current_time, target_time):
        """檢查時間是否匹配"""
        target_hour, target_minute = map(int, target_time.split(":"))
        return (current_time.hour == target_hour and
                current_time.minute == target_minute)

    def _trigger_activity(self, activity):
        """觸發活動"""
        dialogue_id = activity["dialogue"]
        if dialogue_id:
            self.game_engine.start_dialogue(dialogue_id)
```

## 🎯 進階功能

### 1. 時間加速/減速

```python
# 調整時間流逝速度
game.time_system.set_time_scale(2.0)  # 2倍速
game.time_system.set_time_scale(0.5)  # 半速
game.time_system.set_time_scale(1.0)  # 正常速度
```

### 2. 時間暫停

```python
# 暫停時間
game.time_system.pause_time()

# 恢復時間
game.time_system.resume_time()

# 切換暫停狀態
game.time_system.toggle_pause()
```

### 3. 特殊日期處理

```python
def check_special_dates(game_time):
    """檢查特殊日期"""
    if game_time.month == 12 and game_time.day == 25:
        return "christmas"
    elif game_time.month == 2 and game_time.day == 14:
        return "valentine"
    elif game_time.month == 10 and game_time.day == 31:
        return "halloween"
    return None

# 在時間更新時檢查
special_date = check_special_dates(game.time_system.get_current_time())
if special_date:
    game.trigger_special_event(special_date)
```

## 📈 效能優化建議

### 1. 避免頻繁的時間檢查

```python
# ❌ 不好的做法 - 每幀都檢查
def bad_update():
    current_period = game.time_system.get_current_time_period()
    # 每幀都執行複雜邏輯

# ✅ 好的做法 - 只在時間段變化時檢查
def good_update():
    if game.time_system.time_period_changed:
        current_period = game.time_system.get_current_time_period()
        # 只在變化時執行邏輯
        game.time_system.time_period_changed = False
```

### 2. 批量處理時間事件

```python
def process_time_events_batch():
    """批量處理時間事件"""
    current_time = game.time_system.get_current_time()
    pending_events = []

    # 收集所有待觸發事件
    for event in game.time_system.get_pending_events():
        if event.should_trigger(current_time):
            pending_events.append(event)

    # 按優先級排序後批量執行
    pending_events.sort(key=lambda e: e.priority)
    for event in pending_events:
        event.execute()
```

## 🔧 故障排除

### 常見問題和解決方案

1. **時間不推進**

   ```python
   # 檢查時間是否被暫停
   if game.time_system.is_paused:
       game.time_system.resume_time()

   # 檢查自動推進是否開啟
   if not game.time_system.auto_advance:
       game.time_system.auto_advance = True
   ```

2. **時間段變化事件不觸發**

   ```python
   # 確保回調函數已設置
   game.time_system.on_time_period_change = your_callback_function

   # 檢查事件是否正確註冊
   events = game.time_system.get_registered_events()
   print(f"已註冊事件: {list(events.keys())}")
   ```

3. **時間顯示不正確**
   ```python
   # 使用正確的格式化方法
   formatted_time = game.time_system.get_current_time().format_full()
   print(f"當前時間: {formatted_time}")
   ```

## 🎨 自定義擴展

### 創建自定義時間段

```python
class CustomTimePeriod(Enum):
    """自定義時間段"""
    DAWN = "dawn"  # 黎明 5:00-6:00
    DUSK = "dusk"  # 黃昏 17:00-18:00

def get_extended_time_period(hour):
    """擴展的時間段判斷"""
    if hour == 5:
        return CustomTimePeriod.DAWN
    elif hour == 17:
        return CustomTimePeriod.DUSK
    else:
        # 使用原有的時間段邏輯
        return original_get_time_period(hour)
```

---

這個完整的時間系統為遊戲提供了豐富的時間感和生活節奏，讓玩家能夠體驗到真實的一日循環，與にゃんこ共度不同時間段的美好時光。

_教學文檔編寫日期: 2025 年 8 月 1 日_  
_適用版本: 當前開發版本_

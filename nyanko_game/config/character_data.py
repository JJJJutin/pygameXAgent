# -*- coding: utf-8 -*-
"""
角色資料配置
定義遊戲中角色的基本資料和屬性
"""

# にゃんこ角色基本資料
NYANKO_DATA = {
    "name": "にゃんこ",
    "full_name": "Nyan-ko",
    "age": 18,
    "species": "貓娘",
    "role": "女僕",
    # 外觀設定
    "appearance": {
        "hair_color": "銀白色",
        "hair_style": "長髮微捲",
        "eye_color": "琥珀金色",
        "height": "155cm",
        "skin_tone": "白皙帶粉嫩",
    },
    # 貓咪特徵
    "cat_features": {
        "ears": "毛茸茸的銀白色貓耳",
        "tail": "長且蓬鬆的銀白色貓尾，尾端粉紅色",
        "other": "會隨情緒擺動",
    },
    # 服裝設定
    "outfits": {
        "default": "黑白女僕裝",
        "casual": "居家便服",
        "sleepwear": "可愛睡衣",
        "special": "特殊場合服裝",
    },
    # 配件
    "accessories": {
        "collar": "脖子上的鈴鐺項圈",
        "cuffs": "蕾絲袖口",
        "bow": "胸前粉紅色蝴蝶結",
        "socks": "黑色長襪",
        "shoes": "小皮鞋",
    },
    # 性格特徵
    "personality": {
        "base_traits": ["柔軟", "體貼", "坦率", "害羞"],
        "attitude": "不會拒絕主人的請求",
        "special": "喜歡開黃腔調侃主人",
        "speech_pattern": "每句話結尾加'喵'",
    },
    # 表情設定
    "emotions": {
        "normal": "高傲冷漠，嘴角微微上揚",
        "happy": "開心時會搖尾巴",
        "shy": "臉頰泛紅，害羞表情",
        "angry": "貓耳豎起，稍微鼓臉",
        "sad": "耳朵下垂，眼神失落",
        "excited": "雙眼發亮，尾巴高舉",
        "confused": "歪著頭，一臉疑惑",
    },
    # 語言習慣
    "speech": {
        "self_reference": ["人家", "にゃんこ"],
        "common_phrases": ["喵～", "嘿嘿", "好棒喵！", "主人～", "人家知道了喵"],
        "sounds": ["喵", "nya", "嗯嗯"],
        "ending": "喵",
    },
    # 初始狀態
    "initial_stats": {
        "affection": 10,
        "relationship_level": "初識",
        "trust": 5,
        "happiness": 50,
    },
}

# 主角（玩家）資料
PLAYER_DATA = {
    "default_name": "主人",
    "role": "主人",
    "relationship_to_nyanko": "主僕關係，帶有戀愛情感",
}

# 關係等級定義
RELATIONSHIP_LEVELS = {
    0: {
        "name": "初識",
        "description": "剛剛認識的階段",
        "unlocked_events": ["basic_greeting", "simple_tasks"],
    },
    20: {
        "name": "熟悉",
        "description": "已經習慣彼此的存在",
        "unlocked_events": ["daily_conversation", "light_jokes"],
    },
    40: {
        "name": "友好",
        "description": "成為了好朋友",
        "unlocked_events": ["personal_sharing", "cooking_together"],
    },
    60: {
        "name": "親密",
        "description": "關係變得很親密",
        "unlocked_events": ["intimate_moments", "special_dates"],
    },
    80: {
        "name": "戀人",
        "description": "確立了戀愛關係",
        "unlocked_events": ["romantic_scenes", "deep_conversations"],
    },
    100: {
        "name": "相愛",
        "description": "深深愛著彼此",
        "unlocked_events": ["ultimate_intimacy", "future_planning"],
    },
}

# 好感度事件修正值
AFFECTION_MODIFIERS = {
    # 正面互動
    "praise": 3,
    "gift": 5,
    "cooking_together": 4,
    "gentle_touch": 2,
    "compliment": 3,
    "help_with_chores": 2,
    "listen_carefully": 3,
    "special_care": 10,
    "romantic_gesture": 8,
    # 負面互動
    "ignore": -2,
    "scold": -5,
    "harsh_words": -4,
    "neglect": -3,
    "refuse_help": -2,
    "interrupt": -1,
    # 特殊事件
    "birthday_celebration": 15,
    "anniversary": 12,
    "surprise_gift": 8,
    "comfort_when_sad": 6,
    "defend_nyanko": 10,
}

# 角色動作和反應
NYANKO_ACTIONS = {
    "happy_actions": ["搖尾巴", "貓耳豎起", "眼睛發亮", "輕快地走動", "發出滿足的喵聲"],
    "shy_actions": ["臉頰泛紅", "低頭看地", "玩弄裙擺", "輕咬下唇", "偷偷瞄向主人"],
    "angry_actions": ["貓耳貼後", "尾巴豎直", "雙手叉腰", "鼓起臉頰", "發出不滿的哼聲"],
    "sad_actions": ["耳朵下垂", "尾巴無力地垂下", "眼中含淚", "聲音顫抖", "蜷縮身體"],
}

# 對話主題分類
DIALOGUE_TOPICS = {
    "daily_life": ["今天的天氣", "家務分配", "用餐時間", "休息娛樂", "購物清單"],
    "personal": ["過去的回憶", "夢想和目標", "喜歡的事物", "害怕的東西", "個人秘密"],
    "romantic": ["對主人的感情", "理想的約會", "未來的計畫", "浪漫回憶", "愛的表達"],
    "playful": ["開玩笑", "撒嬌", "捉弄主人", "遊戲提議", "有趣的想法"],
}

import json
import os

# 測試對話檔案
dialogue_file = "assets/dialogue_data.json"

print(f"檢查檔案是否存在: {os.path.exists(dialogue_file)}")

if os.path.exists(dialogue_file):
    try:
        with open(dialogue_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ JSON載入成功!")

        # 計算對話數量
        total_dialogues = 0
        for category, subcategories in data.get("dialogue_database", {}).items():
            for subcategory, dialogues in subcategories.items():
                total_dialogues += len(dialogues)

        print(f"總對話數量: {total_dialogues}")

        # 檢查是否有我們需要的對話ID
        all_dialogue_ids = []
        for category, subcategories in data.get("dialogue_database", {}).items():
            for subcategory, dialogues in subcategories.items():
                for dialogue in dialogues:
                    all_dialogue_ids.append(dialogue.get("id"))

        print(f"所有對話ID: {all_dialogue_ids}")

        if "greeting_morning_01" in all_dialogue_ids:
            print("✅ 找到 greeting_morning_01!")
        else:
            print("❌ 找不到 greeting_morning_01")

    except Exception as e:
        print(f"❌ 載入失敗: {e}")
else:
    print("❌ 檔案不存在")

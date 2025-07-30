# open() 開啟模式
# r 讀取模式 檔案必須存在
# w 寫入模式 檔案不存在則建立
# a 附加模式 檔案不存在則建立
# r+ 讀寫模式 檔案必須存在
# w+ 讀寫模式（可覆蓋） 檔案不存在則建立
# a+ 讀寫模式（可附加） 檔案不存在則建立

f = open("class1-1.py", "r", encoding="utf-8")  # 讀取模式
content = f.read()  # 讀取檔案內容
print(content)  # 印出檔案內容
f.close()  # 關閉檔案
##############################################
with open("class1-1.py", "r", encoding="utf-8") as f:  # 使用 with 語句自動關閉檔案
    content = f.read()  # 讀取檔案內容
    print(content)  # 印出檔案內容
# 不用再呼叫 f.close()，因為 with 語句會自動關閉檔案

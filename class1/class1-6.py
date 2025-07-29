n = int(input("請輸入金字塔的層數："))  # 取得使用者輸入的整數

for i in range(1, n + 1):
    print(str(i % 10) * i)

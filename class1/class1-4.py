score = int(input("請輸入成績："))  # 取得使用者輸入並轉為整數

if score >= 10000:
    print("等第：SSS")
elif score >= 1000:
    print("等第：SS")
elif score >= 999:
    print("等第：S")
elif score > 90:
    print("等第：A")
elif score >= 80:
    print("等第：B")
elif score >= 70:
    print("等第：C")
elif score >= 60:
    print("等第：D")
else:
    print("等第：F")

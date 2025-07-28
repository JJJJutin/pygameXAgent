# 比較運算子，只能同樣類型作比較
print(1 < 1)  # False 小於
print(1 <= 1)  # True 小於等於
print(1 > 1)  # False 大於
print(1 >= 1)  # True 大於等於
print(1 == 1)  # True 等於
print(1 != 1)  # False 不等於

# 布林運算
print(True and False)  # False
print(True and True)  # True
print(False and True)  # False
print(False and False)  # False

print(True or False)  # True
print(True or True)  # True
print(False or True)  # True
print(False or False)  # False

print(not False)  # True
print(not True)  # False

# 優先順序
# 1. ()括號
# 2. **指數運算
# 3. * / // % 乘除整除取餘
# 4. + - 加減
# 5. == != > < >= <= 比較運算
# 6. and
# 7. or
# 8. not 邏輯運算
# 9. = 賦值運算
# 10. , 逗號分隔
# 11. # 註解

# 密碼門檢查
password = input("請輸入密碼：")  # 取得使用者輸入的密碼
if password == "123456":
    print("歡迎傻逼")  # 密碼正確 歡迎傻逼
elif password == "04879487":
    print("歡迎智者")  # 密碼正確 歡迎智者
elif password == "000000":
    print("歡迎開發者")  # 密碼正確 歡迎開發者
else:
    print("密碼錯誤")  # 密碼錯誤
# if-elif-else差別
# if: 當條件成立時執行的區塊
# elif: 當前面的if條件不成立時，檢查這個條件是否成立
# else: 當所有的if和elif條件都不成立時，執行這個區塊

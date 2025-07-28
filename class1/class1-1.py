print("hello world")  # 這是在終端機印出hello world的訊息

"""
這是多行註解的範例
可以用來說明程式碼的功能或其他資訊
"""

# 這是單行註解的範例
# 可以用來解釋程式碼的某一行或某一段

# ctrl + / 可以快速註解或取消註解選中的行

# 基本型態
print(123)  # int 印出整數123
print(1.234)  # float 印出浮點數1.234
print("這是一個字串")  # str 印出字串
print(True)  # bool 印出布林值True
print(False)  # bool 印出布林值False

# 變數
x = 10  # 新增一個整數變數"x"，值為10,"="的作用是將右邊的值賦給左邊的變數
print(x)  # 印出變數x的值
x = "apple"  # 將變數x重新賦值為字串"apple"
print(x)  # 印出變數x的新值

# 運算值
print(1 + 1)  # 加法 1+1=2
print(1 - 1)  # 減法 1-1=0
print(1 * 1)  # 乘法 1*1=1
print(1 / 1)  # 除法 1/1=1.0
print(2**3)  # 指數運算 2**3=8
print(1 % 1)  # 取餘數 1%1=0
print(1 // 1)  # 整數除法 1//1=1

# 優先順序
# 1. ()括號
# 2. **指數運算
# 3. * / // % 乘除整除取餘
# 4. + - 加減
# 5. == != > < >= <= 比較運算
# 6. and or not 邏輯運算
# 7. = 賦值運算
# 8. , 逗號分隔
# 9. # 註解
# 這些運算符號的優先順序會影響到運算的結果

# 字串運算
print("Hello" + " " + "World")  # 字串連接
print("Hello" * 3)  # 字串重複
# 字串格式化
name = "Steeeeeeeeeeeeeve"
age = 30
# 以下會出錯
# print("I...am" + name + "and I am" + age + "years old")  # 使用逗號分隔
# 正確的字串格式化方法
print(f"I...am {name} and I am {age} years old")  # 使用f-string格式化

print(len("apple"))  # len()為一種函式，用來計算字串的長度

# type() 用來檢查變數的型態
print(type(123))  # <class 'int'>
print(type(1.234))  # <class 'float'>
print(type("apple"))  # <class 'str'>
print(type(True))  # <class 'bool'>

# 型態轉換
print(int(1.234))  # 將float轉換為int
print(float(123))  # 將int轉換為float
print(str(123))  # 將int轉換為str
print(bool(0))  # 將0轉換為bool，結果為False
print(bool(1))  # 將1轉換為bool，結果為True
print(bool(""))  # 將空字串轉換為bool，結果為False
print(bool("Hello"))  # 將非空字串轉換為bool，結果為True
print(bool([]))  # 將空列表轉換為bool，結果為False
print(bool([1, 2, 3]))  # 將非空列表轉換為bool，結果為True
# 這些型態轉換可以幫助我們在不同的情況下使用不同的資料型態

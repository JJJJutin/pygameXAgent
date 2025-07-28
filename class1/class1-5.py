# for 迴圈
# for 迴圈用來重複執行某段程式碼，通常會搭配可迭代物件（如list、str、range等）

# 基本語法
# for 變數 in 可迭代物件:
# range(5) # 產生一個從0到4的數字序列
for i in range(5):  # 從0到4
    print(i)  # 印出0到4的數字

# range 可以指定起始值和結束值 但不包含結束值
# range(1, 5) # 會產生 1, 2, 3, 4
for i in range(1, 5):
    print(i)

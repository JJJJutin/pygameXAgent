# sort:將列表中的元素進行排序 預設是從小到大排序
my_list = [3, 1, 2]
my_list.sort()
print(my_list)  # 印出排序後的 my_list [1, 2, 3]

# 由大到小排序
my_list.sort(reverse=True)
print(my_list)  # 印出排序後的 my_list [3, 2, 1]

# 算術指定運算子
a = 1
a += 1  # 等同於 a = a + 1
print(a)  # 印出 a 的值 2
a -= 1  # 等同於 a = a - 1
print(a)  # 印出 a 的值 1
a *= 2  # 等同於 a = a * 2
print(a)  # 印出 a 的值 2
a /= 2  # 等同於 a = a / 2
print(a)  # 印出 a 的值 1.0
a //= 2  # 等同於 a = a // 2
print(a)  # 印出 a 的值 0.0
a %= 2  # 等同於 a = a % 2
print(a)  # 印出 a 的值 0.0
a **= 2  # 等同於 a = a ** 2
print(a)  # 印出 a 的值 0.0

# 優先順序
# 1. ()括號
# 2. **指數運算
# 3. * / // % 乘除整除取餘
# 4. + - 加減
# 5. == != > < >= <= 比較運算
# 6. and
# 7. or
# 8. not 邏輯運算
# 9. = += -= *= /= //= %= **= 其他運算

# while 迴圈
# while 迴圈用來重複執行某段程式碼，直到條件不成立為止
# 條件為 True 時，會一直執行下去
# 條件為 False 時，會跳出迴圈

i = 0
while i < 5:
    print(i)
    i += 1

# break 可以用來跳出迴圈
# 先判斷break屬於哪個迴圈 再跳出
while i < 10:
    for j in range(5):
        print(j)

    if i == 5:
        break  # 當 i 等於 5 時，跳出迴圈
    print(i)
    i += 1

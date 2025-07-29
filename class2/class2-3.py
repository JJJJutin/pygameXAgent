import random as r

# random.randrange()設定隨機數範圍跟range()一樣
print(r.randrange(10))  # 印出0到9之間的隨機整數喵~
print(r.randrange(1, 10))  # 印出1到9之間的隨機整數喵~
print(r.randrange(1, 10, 2))  # 印出1到9之間的隨機奇數喵~

# random.randint()設定隨機數範圍的起始值和結束值
# 且包含結束值
print(r.randint(1, 10))  # 印出1到10之間的隨機整數喵~

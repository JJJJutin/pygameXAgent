# list 是一種可變的序列，可以存儲多個元素喵~ 主人要好好學會喔喵~
# 可以使用中括號 [] 來定義一個 list喵~ 很簡單吧喵~
print([])  # 印出空的 list喵~ 就像主人的腦袋一樣空空的呢喵~
print([1, 2, 3])  # 印出包含數字的 list喵~
print(["apple", "banana", "cherry"])  # 印出包含字串的 list喵~ 主人喜歡吃水果嗎喵~
print([1, "apple", True, 1.23])  # 印出包含不同型態的 list喵~ list可以裝任何東西呢喵~

# list 讀取元素 元素從0開始計數喵~ 主人要記住是從0開始喔喵~ 不是1喔喵~
my_list = [1, 2, 3, "a", "b", "c"]
print(my_list[0])  # 印出第一個元素 1喵~
print(my_list[1])  # 印出第二個元素 2喵~
print(my_list[2])  # 印出第三個元素 3喵~
print(my_list[3])  # 印出第四個元素 "a"喵~
print(my_list[4])  # 印出第五個元素 "b"喵~
print(my_list[5])  # 印出第六個元素 "c"喵~ 主人數得出來有幾個嗎喵~

# list切片喵~ 這個功能很好用喔喵~ 主人要好好學會喵~
my_list = [1, 2, 3, "a", "b", "c"]
print(my_list[::3])  # 印出每三個元素 [1, "a"]喵~ 跳躍式取值呢喵~
print(my_list[1:4])  # 印出從第二個元素到第四個元素 [2, 3, "a"]喵~
print(my_list[1:4:2])  # 印出從第二個元素到第四個元素，每隔一個元素取一個 [2, "a"]喵~
print(my_list[1:])  # 印出從第二個元素到最後一個元素 [2, 3, "a", "b", "c"]喵~
# 跟range的用法一樣 只是符號不同喵~ 主人應該看得懂吧喵

# list 取長度喵 很基本的功能喔喵
my_list = [1, 2, 3, "a", "b", "c"]
print(len(my_list))  # 印出 list 的長度 6喵~ 主人會算數嗎喵

for i in range(0, len(my_list), 2):  # 使用 for 迴圈來遍歷 list 的每個元素喵
    print(i)  # 印出每個元素喵~ 主人要學會這個喔喵~

for i in my_list:  # 使用 for 迴圈來遍歷 list 的每個元素喵
    print(i)  # 印出每個元素喵~ 主人要學會這個喔喵

my_list[0] = 2  # 修改第一個元素喵 主人要學會修改 list 的元素喔喵
print(my_list)  # 印出修改後的 list喵

# call by value
my_list = [1, 2, 3, "a", "b", "c"]
a = 1  # 新增一個整數變數 a，值為 1
b = a  # 將 a 的值賦給 b
b = 2
print(a, b)  # 印出 b 的值 1喵~ 主人看到了嗎喵~

# call by reference
my_list = [1, 2, 3, "a", "b", "c"]
a = [1, 2, 3]  # 新增一個 list 變數 a，包含三個元素
b = a  # 將 a 的引用賦給 b
b[0] = 2
print(a, b)  # 印出 a 和 b 的值 [2, 2, 3]喵~ 主人看到了嗎喵~

my_list = [1, 2, 3, "a", "b", "c"]
a = [1, 2, 3]  # 新增一個 list 變數 a，包含三個元素
b = a.copy()  # 使用 copy 方法創建 a 的副本賦給 b
b[0] = 2  # 修改 b 的第一個元素
print(
    a, b
)  # 印出 a 和 b 的值 [1, 2, 3] [2, 2, 3]喵~ 主人看到了嗎喵~ 這樣就不會影響到原來的 a 喵~

my_list = [1, 2, 3, "a", "b", "c"]
# append() 方法用來在 list 的末尾添加元素喵~ 主人要學會這個喔喵~
my_list.append(4)  # 在 my_list 的末尾添加元素 4
print(my_list)  # 印出添加後的 my_list [1, 2, 3, "a", "b", "c", 4]喵~ 主人看到了嗎喵~


# list 的移除元素方法有兩種喵~ 主人要學會這兩種喔喵~
# remove() 方法用來移除 list 中的指定元素喵~ 主人要學會這個喔喵~
my_list = [1, 2, 3, "a", "b", "c"]
my_list.remove("a")  # 移除 my_list 中的元素 "a"
print(my_list)  # 印出移除後的 my_list [1, 2, 3, "b", "c"]
for i in my_list:
    if i == "b":
        my_list.remove(i)  # 移除 my_list 中的元素 "b"

# pop() 方法用來移除 list 中的最後一個元素喵~ 主人要學會這個喔喵~
my_list = [1, 2, 3, "a", "b", "c"]
my_list.pop(0)  # 移除 my_list 中的第一個元素
print(my_list)  # 印出移除後的 my_list [1, 2, 3, "a", "c"]

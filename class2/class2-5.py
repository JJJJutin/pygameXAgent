# 字典 dictionary
# dict是一種透過key-value對來存儲資料, key是唯一的標識符，value是與之對應的資料喵~
# dict是一種無序的資料結構, 所以不能使用index來存取元素喵~
# dict的key必須是不可變的類型, 例如數字、字串或元組喵~
# dict的value可以是任意類型, 包括可變的類型喵~
# dict的key-value是透過冒號(:)來分隔的, 每個key-value對之間用逗號(,)分隔喵~
a = {"name": "Nyan-ko", "age": 18, "is_catgirl": True}  # 新增一個字典

# 取得dict中的key
print(a.keys())  # dict_keys(['name', 'age', 'is_catgirl'])

# 取得dict中的value
print(a.values())  # dict_values(['Nyan-ko', 18, True])

for value in a.values():
    print(value)  # 依序印出每個value

# 取得dict中的key-value對
print(a.items())  # dict_items([('name', 'Nyan-ko'), ('age', 18), ('is_catgirl', True)])

for key, value in a.items():
    print(f"{key}: {value}")  # 依序印出每個key-value對

# 新增一個key-value對
a["favorite_food"] = "sushi"
print(a)  # dict_keys(['name', 'age', 'is_catgirl', 'favorite_food'])
# 修改一個key-value對
a["favorite_food"] = "ramen"
print(a)  # dict_keys(['name', 'age', 'is_catgirl', 'favorite_food'])

# 刪除一個key-value對, pop()
print(a.pop("favorite_food"))  # 刪除並印出'favorite_food'的值 ramen

#  救回傳預設值
print(a.get("favorite_food", "unknown"))  # 印出'unknown'

# 如果資料不存在且沒有預設值, 就會報錯

# 判斷key是否存在
print("name" in a)  # 印出True
print("favorite_food" in a)  # 印出False

# 比較複雜的dict
b = {
    "hobbies": ["playing", "sleeping", "eating"],
    "address": {"city": "Tokyo", "zip": "123-4567"},
}  # value 可以是list或dict喵~

print(b["hobbies"])  # 印出['playing', 'sleeping', 'eating']
print(b["hobbies"][0])  # 印出'playing'

print(b["address"])  # 印出{'city': 'Tokyo', 'zip': '123-4567'}
print(b["address"]["city"])  # 印出'Tokyo'

# 成績登記系統, key為學生名字 value為成績 每個科目有三個成績
grades = {
    "Alice": {"math": [90, 85, 88], "english": [92, 81, 84], "science": [89, 90, 91]},
    "Bob": {"math": [75, 80, 78], "english": [70, 72, 68], "science": [80, 85, 82]},
    "Charlie": {"math": [88, 90, 92], "english": [85, 87, 89], "science": [90, 92, 94]},
}

# try except #例外處理結構
# 錯誤處理
try:
    # 可能會發生錯誤的程式碼
    result = 10 / 0  # 故意製造一個錯誤
except ZeroDivisionError:
    print(input("請輸入一個數字："))
except Exception as e:
    print(f"應當輸入數字")


# 函數定義
# 以def開頭 加上函數名稱和括號 最後加上冒號
# 括弧內可以有參數
def nyan():
    print("這是一個函數喵~")


for i in range(3):
    nyan()  # 呼叫函數

# 函數可以有參數
name = "にゃんこ"


def nyan(name):
    print(f"妳好喵~ 我叫 {name}")


nyan(name)  # 呼叫函數並傳入參數
nyan("nyanko")  # 呼叫函數並傳入參數


# 函數可以有多個回傳值
def add(a, b):
    return a + b  # 回傳兩個值


print(add(5, 3))  # 印出8
print(add("nyan", "ko"))  # 印出"nyanko"

nyanko = add("nyan", "ko")
print(nyanko)  # 印出"nyanko"


def add(a, b):
    return a + b, a - b  # 回傳兩個值


print(add(5, 3))  # 印出(8, 2)
print(add("nyan", "ko"))  # 印出("nyanko", "nyan")

nyanko, nyan = add("nyan", "ko")
print(f"{nyanko} and {nyan}")  # 印出"nyanko" and "nyan"


# 函數可以有預設參數
def add(a, b=10):
    print(f"加法結果: {a + b}")  # 印出加法結果


add(5, 3)  # 印出加法結果: 8
add(5)  # 印出加法結果: 15


# 建議導入參數型態
# 可以在函數定義中指定參數的型態 當呼叫函數時 會檢查參數是否符合指定的型態
# -> 表示回傳值的型態
def add(a: int, b: int = 16) -> int:
    return a + b


print(add(5, 3))  # 印出8
print(add("nyan", "ko"))


# def 區域變數和全域變數
length = 5


def square_area():
    area = length**2
    # area 是區域變數
    # length 是全域變數
    # length = length + 1 # 這樣會產生錯誤
    # 因為 length 是全域變數 不能在區域變數中修改
    print(f"面積是 {area}")


square_area()  # 印出面積是 25

length = 5


def square_area():
    global length  # 使用 global 關鍵字來修改全域變數
    area = length**2
    length += 1  # 修改全域變數
    print(f"面積是 {area}")


length = 10
square_area()  # 印出面積是 100

length = 5
area = 1000


def square_area():
    area = length**2
    # length 是全域變數 area 是區域變數


square_area()
print(f"面積是 {area}")  # 印出面積是 1000


length = 5
area = 1000


def square_area():
    area = length**2
    # length 是全域變數 area 是區域變數
    return area  # 回傳區域變數 area


area = square_area()  # 呼叫函數並將回傳值賦值給全域變數 area
print(f"面積是 {area}")  # 印出面積是 25

length = 5
area = 1000


def square_area():
    area = length**2
    # length 是全域變數 area 是區域變數


square_area()
print(f"面積是 {area}")  # 印出面積是 1000


def square_area():
    global area  # 使用 global 關鍵字來修改全域變數
    area = length**2


square_area()  # 呼叫函數
print(f"面積是 {area}")  # 印出面積是 25


def hello():
    # 函數輸入參數皆為區域變數
    """
    HELLO
    """
    print(f"HELLO {name}")

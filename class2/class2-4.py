import random

low = 0
high = 100
answer = random.randint(low + 1, high - 1)  # 避免答案等於邊界
while True:
    guess = int(input(f"請輸入{low}~{high}的整數:"))
    if guess == answer:
        print("恭喜猜中!")
        break
    elif guess > answer:
        print("再小一點")
        high = guess
    else:
        print("再大一點")
        low = guess

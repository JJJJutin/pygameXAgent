shopping_list = []

while True:
    print("\n目前購物清單：")
    for idx, item in enumerate(shopping_list):
        print(f"{idx}: {item}")
    print("功能選單：")
    print("1. 新增東西")
    print("2. 修改東西")
    print("3. 刪除東西")
    print("4. 離開程式")
    choice = input("請輸入選項編號：")

    if choice == "1":
        item = input("請輸入要新增的東西：")
        shopping_list.append(item)
    elif choice == "2":
        idx = int(input("請輸入要修改的編號："))
        if 0 <= idx < len(shopping_list):
            new_item = input("請輸入新的內容：")
            shopping_list[idx] = new_item
        else:
            print("編號錯誤")
    elif choice == "3":
        print("刪除方式：")
        print("a. 用名稱刪除 (remove)")
        print("b. 用位置刪除 (pop)")
        del_choice = input("請選擇刪除方式(a/b)：")
        if del_choice == "a":
            item = input("請輸入要刪除的名稱：")
            if item in shopping_list:
                shopping_list.remove(item)
            else:
                print("找不到該項目")
        elif del_choice == "b":
            idx = int(input("請輸入要刪除的位置編號："))
            if 0 <= idx < len(shopping_list):
                shopping_list.pop(idx)
            else:
                print("編號錯誤")
        else:
            print("請輸入正確的刪除方式")
    elif choice == "4":
        print("不想逛了就回家！")
        break
    else:
        print("請輸入正確的選項編號")

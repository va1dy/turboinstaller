import menu

def disk_menu():
    options = ["sda (100GB)", "sdb (500GB)", "Назад"]
    while True:
        choice = menu.menu("Disk Configuration", options)
        if choice == -1 or options[choice] == "Назад":
            break
        print(f"Вы выбрали диск: {options[choice]}")
        input("Нажмите Enter чтобы вернуться...")

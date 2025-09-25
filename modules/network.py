import menu

def network_menu():
    options = ["DHCP", "Static IP", "Назад"]
    while True:
        choice = menu.menu("Network Setup", options)
        if choice == -1 or options[choice] == "Назад":
            break
        print(f"Вы выбрали: {options[choice]}")
        input("Нажмите Enter чтобы вернуться...")

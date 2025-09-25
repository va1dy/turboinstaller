import menu

def network_menu():
    options = ["iwd", "networkmanager", "none", "Назад"]
    while True:
        choice = menu.menu("Network Setup", options)
        if choice == -1 or options[choice] == "Назад":
            return None
        selected = options[choice]
        # возвращаем выбранное значение
        return selected

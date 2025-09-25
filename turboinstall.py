import menu
from modules import disks, network

# словарь для хранения последних выборов подменю
selected_values = {
    "Network": None,
    "Disk Configuration": None
}

def main():
    toggles = {1: False}
    options = ["Disk Configuration", "Enable trojan-repo", "Network", "Exit"]
    descriptions = {
        0: "Настройка разметки дисков\nи установка загрузчика",
        1: "Тест кнопки включения",
        2: "Настройка сети (Выбрать сетевой мендежер)",
        3: "Выход из программы"
    }

    while True:
        # создаём динамическое описание справа
        dynamic_desc = {}
        for i, opt in enumerate(options):
            if opt in selected_values and selected_values[opt]:
                dynamic_desc[i] = f"You selected: {selected_values[opt]}"
            else:
                dynamic_desc[i] = descriptions.get(i, "")

        banner = r"""
         _____ _     ____  ____  ____  _  _      ____ _____ ____  _     _     _____ ____ 
        /__ __Y \ /\/  __\/  _ \/  _ \/ \/ \  /|/ ___Y__ __Y  _ \/ \   / \   /  __//  __\
          / \ | | |||  \/|| | //| / \|| || |\ |||    \ / \ | / \|| |   | |   |  \  |  \/|
          | | | \_/||    /| |_\\| \_/|| || | \||\___ | | | | |-||| |_/\| |_/\|  /_ |    /
          \_/ \____/\_/\_\\____/\____/\_/\_/  \|\____/ \_/ \_/ \|\____/\____/\____\\_/\_\
        """

        choice = menu.menu(
            banner,
            options,
            toggles=toggles,
            descriptions=dynamic_desc
        )

        if choice == -1 or options[choice] == "Exit":
            break
        elif options[choice] == "Disk Configuration":
            sel = disks.disk_menu()
            if sel is not None:
                selected_values["Disk Configuration"] = sel  # сохраняем лог команд
        elif options[choice] == "Network":
            sel = network.network_menu()
            if sel is not None:
                selected_values["Network"] = sel

if __name__ == "__main__":
    try:
        menu.clear()
        main()
    finally:
        menu.reset_console()

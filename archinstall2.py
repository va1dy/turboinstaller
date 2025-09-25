import menu
from modules import disks, network

def main():
    toggles = {1: False}
    options = ["Disk Configuration", "Enable Feature X", "Network", "Exit"]
    descriptions = {
        0: "Настройка разметки дисков, форматирование,\nустановка загрузчика.",
        1: "Включает или отключает экспериментальную функцию X.",
        2: "Настройка сетевых интерфейсов: DHCP или статический IP.",
        3: "Выход из установщика."
    }

    while True:
        choice = menu.menu("Main Menu", options, toggles=toggles, descriptions=descriptions)
        if choice == -1 or options[choice] == "Exit":
            break
        elif options[choice] == "Disk Configuration":
            disks.disk_menu()
        elif options[choice] == "Network":
            network.network_menu()

if __name__ == "__main__":
    try:
        menu.clear()
        main()
    finally:
        menu.reset_console()

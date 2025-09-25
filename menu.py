import sys, termios, tty, shutil

import easter_eggs

FG = {"black":30,"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37}
BG = {"black":40,"red":41,"green":42,"yellow":43,"blue":44,"magenta":45,"cyan":46,"white":47}
sequence = []
some_numbers = "1 4 8 8".split()
bad_apple = "b a".split()

def color_text(text, fg=None, bg=None, bold=False):
    codes = []
    if bold: codes.append("1")
    if fg: codes.append(str(FG.get(fg, 37)))
    if bg: codes.append(str(BG.get(bg, 40)))
    return f"\033[{';'.join(codes)}m{text}\033[0m" if codes else text

def clear():
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def draw_description(desc_text, col_split):
    width, _ = shutil.get_terminal_size()
    right_width = width - col_split

    if not desc_text.strip():
        return  # если текста нет, не рисуем

    # авто-ломка длинных строк
    lines = []
    for line in desc_text.split("\n"):
        while len(line) > right_width - 2:
            lines.append(line[:right_width-2])
            line = line[right_width-2:]
        lines.append(line)

    # добавляем пустую строку сверху и снизу
    lines = [""] + lines + [""]

    # выводим справа через пробелы
    for line in lines:
        print(" " * col_split + color_text(line.ljust(right_width), fg="white", bg="blue"))

def menu(title, options, selected=0, toggles=None, descriptions=None, dynamic_description=None):
    """
    Меню с описанием справа.
    :param toggles: dict {index: bool}
    :param descriptions: dict {index: str} - обычное описание
    :param dynamic_description: dict {index: str} - динамическое описание справа
    """
    toggles = toggles or {}
    descriptions = descriptions or {}

    while True:
        clear()
        width, _ = shutil.get_terminal_size()
        col_split = width // 2

        if title:
            print(title)
            print("-" * width)

        # вывод меню слева
        for i, opt in enumerate(options):
            prefix = ""
            if i in toggles:
                prefix = color_text("[ON]", fg="black", bg="green") + " " if toggles[i] else color_text("[OFF]", fg="white", bg="red") + " "
            if i == selected:
                line = f"{prefix}{color_text(opt, fg='black', bg='green', bold=True)}"
            else:
                line = f"{prefix}{opt}"
            print(line)

        # описание справа
        desc_to_show = ""
        if dynamic_description and selected in dynamic_description:
            desc_to_show = dynamic_description[selected]
        else:
            desc_to_show = descriptions.get(selected, "")
        draw_description(desc_to_show, col_split)

        # обработка клавиш
        key = getch()
        sequence.append(key)

        if len(sequence) > len(some_numbers):
            sequence.pop(0)
        if len(sequence) > len(bad_apple):
            sequence.pop(0)

        if sequence == some_numbers:
            clear()
            easter_eggs.poshalko()
            sequence.clear()
        if sequence == bad_apple:
            clear()
            easter_eggs.ba_poshalko()
            sequence.clear()

        if key == '\x1b[A':  # стрелка вверх
            selected = (selected - 1) % len(options)
        elif key == '\x1b[B':  # стрелка вниз
            selected = (selected + 1) % len(options)
        elif key in ('\r', '\n'):
            if selected in toggles:
                toggles[selected] = not toggles[selected]
            else:
                return selected
        elif key == '\x1b':  # ESC
            return -1

def reset_console():
    clear()
    sys.stdout.write("\033[0m")
    sys.stdout.flush()


# =========================
# пример использования
# =========================
if __name__ == "__main__":
    try:
        clear()
        toggles = {1: False}
        options = ["Disk Configuration", "Enable trojan-repo", "Network", "Exit"]
        descriptions = {
            0: "Настройка разметки дисков\nи установка загрузчика",
            1: "Тест кнопки включения",
            2: "Настройка сети (Выбрать сетевой менеджер)",
            3: "Выход из программы"
        }
        dynamic_desc = {}

        while True:
            banner = r"""
             _____ _     ____  ____  ____  _  _      ____ _____ ____  _     _     _____ ____ 
            /__ __Y \ /\/  __\/  _ \/  _ \/ \/ \  /|/ ___Y__ __Y  _ \/ \   / \   /  __//  __\
              / \ | | |||  \/|| | //| / \|| || |\ |||    \ / \ | / \|| |   | |   |  \  |  \/|
              | | | \_/||    /| |_\\| \_/|| || | \||\___ | | | | |-||| |_/\| |_/\|  /_ |    /
              \_/ \____/\_/\_\\____/\____/\_/\_/  \|\____/ \_/ \_/ \|\____/\____/\____\\_/\_\
            """
            choice = menu(banner, options, toggles=toggles, descriptions=descriptions, dynamic_description=dynamic_desc)
            if choice == -1 or options[choice] == "Exit":
                break
            elif options[choice] == "Enable trojan-repo":
                toggles[1] = not toggles[1]
            else:
                print(f"Вы выбрали: {options[choice]}")
                input("Нажмите Enter, чтобы вернуться в меню...")
    finally:
        reset_console()

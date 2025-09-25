import sys, termios, tty, shutil

FG = {"black":30,"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37}
BG = {"black":40,"red":41,"green":42,"yellow":43,"blue":44,"magenta":45,"cyan":46,"white":47}

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

def menu(title, options, selected=0, toggles=None, descriptions=None, dynamic_description=None):
    """
    Меню с описанием справа.
    :param toggles: dict {index: bool}
    :param descriptions: dict {index: str} - обычное описание
    :param dynamic_description: str - если задано, показывается справа вместо описания
    """
    toggles = toggles or {}
    descriptions = descriptions or {}

    while True:
        clear()
        width, height = shutil.get_terminal_size((80, 20))
        col_split = width // 2
        right_width = width - col_split

        if title:
            print(title)
            print("-" * width)

        for i, opt in enumerate(options):
            # индикатор [ON]/[OFF]
            prefix = ""
            if i in toggles:
                prefix = color_text("[ON]", fg="black", bg="green") + " " if toggles[i] else color_text("[OFF]", fg="white", bg="red") + " "
            # текст пункта
            text = f"{prefix}{opt}"
            if i == selected:
                line = f"{prefix}{color_text(opt, fg='black', bg='green', bold=True)}"
            else:
                line = text
            print(line.ljust(col_split))

        # описание справа
        if dynamic_description is not None:
            desc_lines = dynamic_description.split("\n")
        else:
            desc_lines = descriptions.get(selected, "").split("\n")

        for idx in range(len(desc_lines)):
            line = desc_lines[idx]
            padded = line.ljust(right_width - 2)  # оставляем небольшой отступ справа
            sys.stdout.write(f"\033[{idx + 3};{col_split + 2}H")  # +2 для отступа
            sys.stdout.write(color_text(padded, fg="white", bg="blue") + "\033[0m")

        key = getch()
        if key == '\x1b[A':
            selected = (selected - 1) % len(options)
        elif key == '\x1b[B':
            selected = (selected + 1) % len(options)
        elif key in ('\r', '\n'):
            if selected in toggles:
                toggles[selected] = not toggles[selected]
            else:
                return selected
        elif key == '\x1b':
            return -1

def text_input_menu(title="", dynamic_description_func=None):
    """
    Интерактивный ввод текста с динамическим описанием справа.
    dynamic_description_func(text) -> str
    """
    text = ""
    while True:
        clear()
        width, height = shutil.get_terminal_size((80, 20))
        col_split = width // 2
        right_width = width - col_split

        # заголовок
        if title:
            print(title)
            print("-" * width)

        # левая колонка: текущий ввод
        print(color_text("> " + text, fg="green", bold=True).ljust(col_split))

        # правая колонка: динамическое описание
        if dynamic_description_func:
            desc_lines = dynamic_description_func(text).split("\n")
        else:
            desc_lines = []

        for idx in range(max(len(desc_lines), 1)):
            line = desc_lines[idx] if idx < len(desc_lines) else ""
            padded = line.ljust(right_width)
            sys.stdout.write(f"\033[{idx+3};{col_split+1}H")
            sys.stdout.write(color_text(padded, fg="white", bg="blue") + "\n")

        # считываем один символ
        key = getch()
        if key in ('\r', '\n'):
            if text.strip():
                return text
        elif key == '\x7f':  # backspace
            text = text[:-1]
        elif key == '\x03':  # ctrl-c
            print("\nОтменено")
            return ""
        else:
            text += key

def reset_console():
    clear()
    sys.stdout.write("\033[0m")
    sys.stdout.flush()

import menu

EXCLUDED_PREFIXES = ("zram", "loop", "ram", "sr")
EXCLUDED_NAMES = {"fd0"}

# Хранение дисков и разделов
disks_state = {}
command_log = []

FILESYSTEMS = ["ext4", "ext3", "xfs", "fat32", "btrfs", "linux-swap"]
MOUNTPOINTS = ["/", "/boot", "/home", "/var", "/mnt", "none"]

def get_disks():
    import subprocess
    result = subprocess.run(
        ["lsblk", "-d", "-o", "NAME,SIZE", "-n"],
        stdout=subprocess.PIPE,
        text=True
    )
    disks = []
    for line in result.stdout.strip().split("\n"):
        if line:
            name, size = line.split()
            if name.startswith(EXCLUDED_PREFIXES) or name in EXCLUDED_NAMES:
                continue
            disks.append({"name": name, "size": size})
    return disks

def load_disks():
    disks = get_disks()
    for d in disks:
        if d["name"] not in disks_state:
            partitions = get_partitions_real(d["name"])
            disks_state[d["name"]] = {"size": d["size"], "partitions": partitions}

def get_partitions_real(disk_name):
    import subprocess
    result = subprocess.run(
        ["lsblk", "-o", "NAME,SIZE,TYPE", "-n", f"/dev/{disk_name}"],
        stdout=subprocess.PIPE,
        text=True
    )
    partitions = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split()
        if len(parts) < 3:
            continue
        name, size, typ = parts[:3]
        if typ == "part":
            partitions.append({
                "name": name,
                "size": size,
                "fs": None,
                "mount": None,
                "flags": []
            })
    return partitions

def disk_menu():
    load_disks()
    while True:
        options = [f"{name} (Size: {data['size']})" for name, data in disks_state.items()]
        options += ["Show Commands", "Done"]
        choice = menu.menu("Выберите диск, Show Commands или Done", options)
        if choice == -1 or options[choice] == "Done":
            break
        elif options[choice] == "Show Commands":
            show_commands()
        else:
            disk_name = list(disks_state.keys())[choice]
            partition_menu(disk_name)

    # Сохраняем текущие настройки разделов для всех дисков
    disk_config = {}
    for disk_name, disk_data in disks_state.items():
        disk_config[disk_name] = []
        for part in disk_data["partitions"]:
            disk_config[disk_name].append({
                "name": part["name"],
                "size": part["size"],
                "fs": part["fs"],
                "mount": part["mount"],
                "flags": part["flags"]
            })
    return disk_config if disk_config else None


def partition_menu(disk_name):
    disk = disks_state[disk_name]
    while True:
        parts = disk["partitions"]
        total_size = disk["size"]
        used_space = sum(parse_size(p["size"]) for p in parts)
        free_space = parse_size(total_size) - used_space
        options = []
        for p in parts:
            flags = f" [{' '.join(p['flags'])}]" if p['flags'] else ""
            mount = f" mount:{p['mount']}" if p['mount'] else ""
            fs = f" fs:{p['fs']}" if p['fs'] else ""
            options.append(f"{p['name']} ({p['size']}){fs}{mount}{flags}")
        if free_space > 0:
            options.append(f"Free Space ({free_space}G)")
        options.append("Back")

        choice = menu.menu(f"Разделы диска {disk_name}", options)
        if choice == -1 or options[choice] == "Back":
            break
        elif "Free Space" in options[choice]:
            create_partition(disk_name, free_space)
        else:
            manage_partition(disk_name, choice)

def parse_size(size_str):
    """
    Преобразует размер вида '238.5G', '512M' в число гигабайт (float)
    """
    try:
        if size_str.endswith("G"):
            return float(size_str[:-1])
        elif size_str.endswith("M"):
            return float(size_str[:-1]) / 1024
        elif size_str.endswith("K"):
            return float(size_str[:-1]) / (1024*1024)
        else:
            return float(size_str)
    except ValueError:
        # Если вдруг строка некорректная, возвращаем 0
        return 0


def create_partition(disk_name, free_space):
    name = f"{disk_name}_new{len(disks_state[disk_name]['partitions']) + 1}"

    # Размер
    size_input = input(f"Введите размер нового раздела (макс {free_space}G, Enter = всё место): ").strip()
    if size_input == "":
        size_float = free_space
    else:
        size_input = size_input.upper().replace("GB", "").replace("G", "")
        try:
            size_float = float(size_input)
        except ValueError:
            print("Неверный формат размера!")
            return
        if size_float > free_space:
            print("Слишком большой размер!")
            return

    # Выбор файловой системы через меню
    fs_options = FILESYSTEMS + ["Cancel"]
    fs_choice = menu.menu("Выберите файловую систему", fs_options)
    if fs_choice == -1 or fs_options[fs_choice] == "Cancel":
        return
    fs = fs_options[fs_choice]

    # Mountpoint для обычных FS
    mount = "none"
    if fs != "linux-swap":
        mount_input = input("Введите mountpoint (например /, /boot, /home, none): ").strip()
        if mount_input != "":
            mount = mount_input

    # Флаги boot/esp автоматические
    flags = []
    if fs != "linux-swap" and mount in ["/boot", "/boot/efi"]:
        flags = ["boot", "esp"]

    # Создаём раздел в памяти
    new_part = {
        "name": name,
        "size": f"{size_float}G",
        "fs": fs,
        "mount": mount,
        "flags": flags
    }
    disks_state[disk_name]["partitions"].append(new_part)

    # Лог команд
    command_log.append(f"# Создать раздел {name} размер {size_float}G на {disk_name}")
    command_log.append(f"sudo fdisk /dev/{disk_name}  # добавить раздел {name}")
    if fs != "linux-swap":
        command_log.append(f"sudo mkfs.{fs} /dev/{name}  # форматирование")
        if mount != "none":
            command_log.append(f"sudo mount /dev/{name} {mount}  # монтирование")
    else:
        command_log.append(f"sudo mkswap /dev/{name}  # форматирование swap")
    if flags:
        command_log.append(f"# флаги для {name}: {' '.join(flags)}")


def manage_partition(disk_name, idx):
    part = disks_state[disk_name]["partitions"][idx]
    options = ["Delete", "Mark as boot/esp", "Back"]
    choice = menu.menu(f"Управление разделом {part['name']}", options)
    if choice == 0:
        command_log.append(f"sudo fdisk /dev/{disk_name}  # удалить раздел {part['name']}")
        disks_state[disk_name]["partitions"].pop(idx)
    elif choice == 1:
        if "boot" not in part["flags"]:
            part["flags"].append("boot")
            command_log.append(f"# пометка {part['name']} как boot/esp")

def show_commands():
    if not command_log:
        print("\nНет созданных разделов/действий.\n")
    else:
        print("\n=== Команды для выполнения всех операций ===\n")
        for cmd in command_log:
            print(cmd)
        print("\n=== Конец команд ===\n")
    input("Нажмите Enter, чтобы вернуться в меню...")

if __name__ == "__main__":
    disk_menu()
    input("\nDone! Press Enter to see all commands...")
    print("\n=== Список всех команд ===")
    for cmd in command_log:
        print(cmd)

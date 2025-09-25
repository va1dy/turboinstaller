import subprocess

import menu

def get_disks():
    result = subprocess.run(
        ["lsblk", "-d", "-o", "NAME,SIZE", "-n"],
        stdout=subprocess.PIPE,
        text=True
    )
    disks = []
    for line in result.stdout.strip().split("\n"):
        if line:
            name, size = line.split()
            disks.append(f"{name} ({size})")
    return disks

def disk_menu():
    options = get_disks() + ["Назад"]
    while True:
        choice = menu.menu("Disk Configuration", options)
        if choice == -1 or options[choice] == "Назад":
            break
        print(f"Вы выбрали диск: {options[choice]}")
        input("нажмите enter чтобы вернуться...")
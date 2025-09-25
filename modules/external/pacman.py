# pacman_api.py
import subprocess
from dataclasses import dataclass
from exceptions.pacman import PacmanError

@dataclass
class PackageInfo:
    name: str
    version: str
    desc: str = ""
    repo: str = ""
    size: str = ""
    installed_size: str = ""
    build_date: str = ""
    install_date: str = ""

def _run(args):
    try:
        result = subprocess.run(
            ["pacman"] + args,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise PacmanError(e.stderr.strip())

def install(*packages, yes=True):
    args = ["-S"]
    if yes:
        args.append("--noconfirm")
    return _run(args + list(packages))

def remove(*packages, yes=True):
    args = ["-R"]
    if yes:
        args.append("--noconfirm")
    return _run(args + list(packages))

def update(yes=True):
    args = ["-Syu"]
    if yes:
        args.append("--noconfirm")
    return _run(args)

def search(query):
    out = _run(["-Ss", query])
    results = []
    for line in out.splitlines():
        if line.startswith(" "):  # описание пакета
            results[-1][-1] += " " + line.strip()
        else:
            parts = line.split()
            repo, name, version = parts[0], parts[1], parts[2]
            desc = " ".join(parts[3:])
            results.append([repo, name, version, desc])
    return results

def info(package):
    out = _run(["-Qi", package])
    data = {}
    for line in out.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip()
    return PackageInfo(
        name=data.get("Name", package),
        version=data.get("Version", ""),
        desc=data.get("Description", ""),
        repo=data.get("Repository", ""),
        size=data.get("Download Size", ""),
        installed_size=data.get("Installed Size", ""),
        build_date=data.get("Build Date", ""),
        install_date=data.get("Install Date", ""),
    )

def list_installed():
    out = _run(["-Qe"])
    return [tuple(line.split()) for line in out.splitlines()]

def list_outdated():
    out = _run(["-Qu"])
    return [tuple(line.split()[:2]) for line in out.splitlines()]

def list_files(package):
    out = _run(["-Ql", package])
    return [line.split(None, 1)[1] for line in out.splitlines()]

def owns(file_path):
    out = _run(["-Qo", file_path])
    parts = out.split()
    return parts[1] if len(parts) > 1 else None

def is_installed(package):
    try:
        _run(["-Qi", package])
        return True
    except PacmanError:
        return False

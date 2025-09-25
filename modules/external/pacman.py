# pacman_api.py
import subprocess
from dataclasses import dataclass
from exceptions.pacman import PacmanError

_extra_args: list[str] = []

def set_global_args(*args):
    global _extra_args
    _extra_args = list(args)

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

def _run(args, extra_args=None):
    final_args = ["pacman"] + _extra_args + (extra_args or []) + args
    try:
        result = subprocess.run(
            final_args,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise PacmanError(e.stderr.strip())

# === базовые операции ===

def install(*packages, yes=True, extra_args=None):
    args = ["-S"]
    if yes:
        args.append("--noconfirm")
    return _run(args + list(packages), extra_args=extra_args)

def remove(*packages, yes=True, extra_args=None):
    args = ["-R"]
    if yes:
        args.append("--noconfirm")
    return _run(args + list(packages), extra_args=extra_args)

def update(yes=True, extra_args=None):
    args = ["-Syu"]
    if yes:
        args.append("--noconfirm")
    return _run(args, extra_args=extra_args)

# === информация ===

def search(query, extra_args=None):
    out = _run(["-Ss", query], extra_args=extra_args)
    results = []
    for line in out.splitlines():
        if line.startswith(" "):
            results[-1][-1] += " " + line.strip()
        else:
            parts = line.split()
            repo, name, version = parts[0], parts[1], parts[2]
            desc = " ".join(parts[3:])
            results.append([repo, name, version, desc])
    return results

def info(package, extra_args=None):
    out = _run(["-Qi", package], extra_args=extra_args)
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

def list_installed(extra_args=None):
    out = _run(["-Qe"], extra_args=extra_args)
    return [tuple(line.split()) for line in out.splitlines()]

def list_outdated(extra_args=None):
    out = _run(["-Qu"], extra_args=extra_args)
    return [tuple(line.split()[:2]) for line in out.splitlines()]

def list_files(package, extra_args=None):
    out = _run(["-Ql", package], extra_args=extra_args)
    return [line.split(None, 1)[1] for line in out.splitlines()]

def owns(file_path, extra_args=None):
    out = _run(["-Qo", file_path], extra_args=extra_args)
    parts = out.split()
    return parts[1] if len(parts) > 1 else None

def is_installed(package, extra_args=None):
    try:
        _run(["-Qi", package], extra_args=extra_args)
        return True
    except PacmanError:
        return False

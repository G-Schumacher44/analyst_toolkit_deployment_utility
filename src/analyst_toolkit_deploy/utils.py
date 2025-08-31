from __future__ import annotations

import os
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Iterable, Optional

import yaml


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    gitkeep = p / ".gitkeep"
    if not gitkeep.exists():
        try:
            gitkeep.write_text("")
        except Exception:
            pass


def copy_file(src: Path, dst: Path, overwrite: bool = True) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return
    shutil.copy2(src, dst)


def update_yaml_key(path: Path, key: str, value) -> None:
    if not path.exists():
        return
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        data = {}
    data[key] = value
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def run(cmd: Iterable[str], cwd: Optional[Path] = None, env: Optional[dict] = None, check: bool = True) -> int:
    proc = subprocess.run(list(cmd), cwd=str(cwd) if cwd else None, env=env)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.returncode


def conda_exists() -> bool:
    return shutil.which("conda") is not None


def register_ipykernel(name: str, display_name: str, python_exec: Path) -> None:
    run([
        str(python_exec),
        "-m",
        "ipykernel",
        "install",
        "--user",
        "--name",
        name,
        "--display-name",
        display_name,
    ], check=False)


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()

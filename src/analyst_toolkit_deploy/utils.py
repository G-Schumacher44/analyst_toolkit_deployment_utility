from __future__ import annotations

import shutil
import sys
import subprocess
from pathlib import Path
from typing import Iterable, Optional

import yaml


def ensure_dir(p: Path) -> None:
    """Create a directory (and parents) if missing, and drop a .gitkeep.

    Ensures the path exists even for nested folders and places an empty
    `.gitkeep` so otherwise-empty folders remain visible in Git. Failure to
    write `.gitkeep` is non-fatal and silently ignored.
    """
    p.mkdir(parents=True, exist_ok=True)
    gitkeep = p / ".gitkeep"
    if not gitkeep.exists():
        try:
            gitkeep.write_text("")
        except Exception:
            # Folder exists; keeping .gitkeep is best-effort only.
            pass


def copy_file(src: Path, dst: Path, overwrite: bool = True) -> None:
    """Copy a file with parent creation and overwrite control.

    If `overwrite` is False and the destination exists, the copy is skipped.
    Uses `shutil.copy2` to preserve metadata where possible.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return
    shutil.copy2(src, dst)


def update_yaml_key(path: Path, key: str, value) -> None:
    """Update (or insert) a top-level YAML key in-place.

    No-op if the file does not exist. Falls back to an empty mapping on read
    errors to avoid hard failure. Writes human-friendly YAML (no key sorting).
    """
    if not path.exists():
        return
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        data = {}
    data[key] = value
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def run(
    cmd: Iterable[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    check: bool = True,
) -> int:
    """Run a command and optionally raise on non-zero exit.

    - `cmd`: sequence of args (no shell=True), executed as-is.
    - `cwd`: optional working directory.
    - `env`: optional environment mapping.
    - `check`: if True, non-zero exit codes raise RuntimeError.
    """
    proc = subprocess.run(list(cmd), cwd=str(cwd) if cwd else None, env=env)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}"
        )
    return proc.returncode


def conda_exists() -> bool:
    """Return True if `conda` is discoverable on PATH."""
    return shutil.which("conda") is not None


def register_ipykernel(name: str, display_name: str, python_exec: Path) -> None:
    """Register a Jupyter kernel for the given Python executable.

    `name` is a stable, space-free identifier; `display_name` is the
    human-friendly label shown in Jupyter. Keeping them separate avoids
    failures when spaces/special characters are used.
    """
    run(
        [
            str(python_exec),
            "-m",
            "ipykernel",
            "install",
            "--user",
            "--name",
            name,
            "--display-name",
            display_name,
        ],
        check=False,
    )


def is_interactive() -> bool:
    """Best-effort TTY check used to decide whether to prompt the user."""
    return sys.stdin.isatty() and sys.stdout.isatty()

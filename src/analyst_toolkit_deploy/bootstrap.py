"""Project scaffolding utilities for the Deploy package.

Copies templates, wires datasets, persists defaults, and optionally
creates environments and Jupyter kernels. `bootstrap()` orchestrates
the end-to-end flow; helper functions are usable standalone.
"""

from __future__ import annotations

import os
import shutil
from importlib import resources
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from . import infer_configs as ic
from .utils import conda_exists, copy_file, ensure_dir, is_interactive, register_ipykernel, run, update_yaml_key

console = Console()


def _pkg_path(rel: str) -> Optional[Path]:
    """Resolve a resource path inside the installed package for data files."""
    try:
        base = resources.files("analyst_toolkit_deploy")
        target = base.joinpath(rel)
        with resources.as_file(target) as p:
            return Path(p)
    except Exception:
        return None


def _copy_templates(
    target_root: Path,
    force: bool,
    project_name: str,
    vscode_ai: str,
    copy_notebook: bool,
) -> None:
    """Copy templates into target and inject project/license details where applicable."""
    # Ensure dirs
    for p in [
        target_root / "src",
        target_root / "config",
        target_root / "data/raw",
        target_root / "data/processed",
        target_root / "data/features",
        target_root / "exports/joblib",
        target_root / "exports/plots",
        target_root / "exports/reports",
        target_root / "notebooks",
    ]:
        ensure_dir(p)

    # Config YAMLs
    pkg_cfg = _pkg_path("templates/config")
    if pkg_cfg and pkg_cfg.exists():
        for src in pkg_cfg.glob("*.yaml"):
            dst = target_root / "config" / src.name
            copy_file(src, dst, overwrite=force)
    else:
        console.print("[yellow]No packaged templates found; skipping config copy[/yellow]")

    # .env template
    env_tmpl = _pkg_path("templates/.env.template")
    if env_tmpl:
        dst = target_root / ".env"
        if not dst.exists():
            copy_file(env_tmpl, dst, overwrite=True)

    # environment.yml / requirements.txt / .gitignore
    for rel in [
        "templates/environment.yml",
        "templates/requirements.txt",
        "templates/.gitignore",
    ]:
        src = _pkg_path(rel)
        if src and src.exists():
            copy_file(src, target_root / Path(rel).name, overwrite=force)

    # README.md (prefer packaged template; fallback to workspace template)
    readme_dst = target_root / "README.md"
    readme_src = _pkg_path("templates/README.md")
    if not readme_src:
        ws_readme = Path.cwd() / "deploy_toolkit" / "templates" / "README.md"
        if ws_readme.exists():
            readme_src = ws_readme
    if readme_src and readme_src.exists():
        copy_file(readme_src, readme_dst, overwrite=force)
        # Inject project name into README title
        try:
            import re

            effective_name = project_name
            if not effective_name:
                # Derive from target folder name
                base = target_root.name
                effective_name = re.sub(r"[_-]+", " ", base).strip().title() or base
            txt = readme_dst.read_text(encoding="utf-8")
            pattern = r"^## \((?:Title Placeholder)\)"
            if re.search(pattern, txt, flags=re.M):
                txt = re.sub(pattern, f"## {effective_name}", txt, count=1, flags=re.M)
            else:
                # Fallback simple replace once
                txt = txt.replace("## (Title Placeholder)", f"## {effective_name}", 1)
            # Remove optional top banner image block to avoid broken links
            txt = re.sub(
                r"(?s)^<p align=\"center\">\s*<img [^>]+>.*?</p>\n?",
                "",
                txt,
                count=1,
            )
            readme_dst.write_text(txt, encoding="utf-8")
        except Exception:
            pass

    # LICENSE (prefer packaged license; fallback to workspace root LICENSE)
    lic_dst = target_root / "LICENSE"
    lic_src = _pkg_path("templates/LICENSE")
    if not lic_src:
        ws_lic = Path.cwd() / "LICENSE"
        if ws_lic.exists():
            lic_src = ws_lic
    if lic_src and lic_src.exists():
        copy_file(lic_src, lic_dst, overwrite=False)
        # Update year; author injection is opt-in via LICENSE_AUTHOR env var (no default)
        try:
            import re
            from datetime import datetime

            author = os.environ.get("LICENSE_AUTHOR", "").strip()
            year = str(datetime.now().year)
            txt = lic_dst.read_text(encoding="utf-8")
            # Replace or insert year
            if re.search(r"Copyright \(c\) \d{4}", txt):
                txt = re.sub(r"Copyright \(c\) \d{4}", f"Copyright (c) {year}", txt, count=1)
            else:
                txt = re.sub(r"^MIT License\n", f"MIT License\n\nCopyright (c) {year}\n", txt, count=1, flags=re.M)
            # Optionally append author after year if provided
            if author:
                txt = re.sub(r"(Copyright \(c\) \d{4})(\n)", rf"\1 {author}\2", txt, count=1)
            lic_dst.write_text(txt, encoding="utf-8")
        except Exception:
            pass

    # VS Code settings
    vs_settings = _pkg_path("templates/.vscode/settings.json")
    if vs_settings and vs_settings.exists():
        dst = target_root / ".vscode" / "settings.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        copy_file(vs_settings, dst, overwrite=force)
        # Inject AI provider hint as a pseudo-key comment: omitted for simplicity; can be extended.

    # Notebook template (optional)
    if copy_notebook:
        nb = _pkg_path("templates/toolkit_template.ipynb")
        if nb and nb.exists():
            copy_file(nb, target_root / "notebooks" / "toolkit_template.ipynb", overwrite=force)
        else:
            # Fallback: if running from the original bundle, copy notebook from workspace
            workspace_nb = Path.cwd() / "deploy_toolkit" / "templates" / "toolkit_template.ipynb"
            if workspace_nb.exists():
                copy_file(workspace_nb, target_root / "notebooks" / "toolkit_template.ipynb", overwrite=force)
            else:
                console.print("[yellow]Notebook template not found; skipping[/yellow]")
    else:
        console.print("[yellow]Notebook copy disabled via --copy-notebook False[/yellow]")

    # Resource hub documentation (prefer packaged; fallback to workspace tool_kit_resources)
    docs_dst = target_root / "resource_hub"
    docs_dst.mkdir(parents=True, exist_ok=True)
    docs_src = _pkg_path("templates/resource_hub")
    copied = []
    # Copy packaged docs exactly (authoritative templates)
    if docs_src and docs_src.exists():
        for md in sorted(docs_src.glob("*.md")):
            copy_file(md, docs_dst / md.name, overwrite=force)
            copied.append(md.name)
    # Create a landing page if we have >=3 docs and no README in resource_hub
    if len(copied) >= 3:
        hub_readme = docs_dst / "README.md"
        if not hub_readme.exists():
            try:
                links = "\n".join(f"- {name}" for name in sorted(copied))
                hub_readme.write_text(("Resource Hub\n\n" + "Curated documentation for the scaffolded project.\n\n" + links + "\n"), encoding="utf-8")
            except Exception:
                pass

    # Note: We do not copy or rewrite logo images into the scaffold to keep repos lean.


def _wire_dataset(
    target_root: Path,
    dataset: str,
    ingest: str = "copy",
) -> Optional[Path]:
    """Select a CSV and write its path to the run config, with optional ingest."""
    cfg = target_root / "config" / "run_toolkit_config.yaml"
    chosen: Optional[Path] = None

    def set_pipeline(path: Path) -> None:
        """Write dataset path and suggest a timestamped run_id if missing."""
        try:
            rel = path.relative_to(target_root)
            entry = str(rel)
        except Exception:
            entry = str(path)
        update_yaml_key(cfg, "pipeline_entry_path", entry)
        # Suggest run_id if missing
        try:
            import yaml  # local import

            data = yaml.safe_load(cfg.read_text()) or {}
            if not data.get("run_id"):
                stem = path.stem
                from time import strftime

                data["run_id"] = f"{stem}_{strftime('%Y%m%d_%H%M%S')}"
                cfg.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
        except Exception:
            pass

    def ingest_if_needed(src: Path) -> Path:
        """Move/copy CSV into data/raw unless already under that folder."""
        if src.is_absolute() and target_root in src.parents:
            return src
        # if at project root and ingest is not none, move/copy into data/raw
        dest = target_root / "data" / "raw" / src.name
        if ingest == "move":
            shutil.move(str(src), dest)
            return dest
        elif ingest == "copy":
            shutil.copy2(src, dest)
            return dest
        else:
            return src

    if dataset == "auto":
        raw = sorted((target_root / "data" / "raw").glob("*.csv"))
        root_csv = sorted(target_root.glob("*.csv"))
        if len(raw) == 1:
            chosen = raw[0]
        elif len(root_csv) == 1:
            chosen = ingest_if_needed(root_csv[0])
        else:
            console.print("[yellow]Multiple or no CSVs found; skipping dataset wiring[/yellow]")
            return None
    elif dataset == "prompt":
        opts = sorted((target_root / "data" / "raw").glob("*.csv")) + sorted(target_root.glob("*.csv"))
        if not opts:
            console.print("[yellow]No CSVs found to select[/yellow]")
            return None
        if not is_interactive():
            console.print("[yellow]Non-interactive environment: supply --dataset <path>[/yellow]")
            return None
        choice = Prompt.ask(
            "Select dataset index",
            choices=[str(i) for i in range(len(opts))],
            default="0",
        )
        chosen = opts[int(choice)]
        if chosen.parent == target_root and ingest != "none":
            chosen = ingest_if_needed(chosen)
    else:
        p = Path(dataset)
        if not p.is_absolute():
            p = (target_root / p).resolve()
        if p.exists():
            # If ingest is requested and the file is not already under data/raw, ingest it
            if ingest != "none":
                try:
                    p.relative_to(target_root / "data" / "raw")
                    under_raw = True
                except Exception:
                    under_raw = False
                if not under_raw:
                    chosen = ingest_if_needed(p)
                else:
                    chosen = p
            else:
                chosen = p
        else:
            console.print(f"[yellow]Dataset not found: {dataset}[/yellow]")
            return None

    if chosen:
        set_pipeline(chosen)
        try:
            disp = chosen.relative_to(target_root)
        except Exception:
            disp = chosen
        console.print(f"[green]Wired dataset:[/green] {disp}")
    return chosen


def _persist_env_defaults(
    target_root: Path,
    env_name: str,
    kernel_name: str,
    project_name: str,
    vscode_ai: str,
) -> None:
    envf = target_root / ".env"
    envf.touch(exist_ok=True)
    text = envf.read_text(encoding="utf-8") if envf.exists() else ""

    def upsert(key: str, val: str) -> None:
        nonlocal text
        if not val:
            return
        import re

        pattern = re.compile(rf"^{key}=.*$", re.M)
        if pattern.search(text):
            text = pattern.sub(f"{key}={val}", text)
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += f"{key}={val}\n"

    upsert("ENV_NAME", env_name)
    upsert("KERNEL_NAME", kernel_name)
    upsert("PROJECT_NAME", project_name)
    upsert("VSCODE_AI", vscode_ai)
    envf.write_text(text, encoding="utf-8")


def _setup_conda(target_root: Path, env_name: str, kernel_name: str, reuse: bool, force_recreate: bool) -> None:
    if not conda_exists():
        console.print("[red]conda not found in PATH[/red]")
        return
    # Check existence
    exists = False
    try:
        import subprocess

        out = subprocess.check_output(["conda", "env", "list"], text=True)
        exists = any(line.split()[0] == env_name for line in out.splitlines() if line and not line.startswith("#"))
    except Exception:
        pass

    if exists and force_recreate:
        console.print(f"[yellow]Removing existing env: {env_name}[/yellow]")
        run(["conda", "env", "remove", "-y", "-n", env_name], check=False)
        exists = False

    if exists and reuse:
        console.print(f"[green]Reusing conda env:[/green] {env_name}")
    else:
        env_yml = target_root / "environment.yml"
        if env_yml.exists():
            console.print(f"[green]Creating conda env from environment.yml:[/green] {env_name}")
            run(
                ["conda", "env", "create", "-f", str(env_yml), "-n", env_name],
                check=False,
            )
            # fallback to update if create failed
            run(
                ["conda", "env", "update", "-f", str(env_yml), "-n", env_name],
                check=False,
            )
        else:
            console.print(f"[green]Creating conda env:[/green] {env_name}")
            run(
                [
                    "conda",
                    "create",
                    "-y",
                    "-n",
                    env_name,
                    "python=3.10",
                ],
                check=False,
            )
            req = target_root / "requirements.txt"
            if req.exists():
                run(
                    [
                        "conda",
                        "run",
                        "-n",
                        env_name,
                        "python",
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(req),
                    ],
                    check=False,
                )

    # Register kernel
    run(
        [
            "conda",
            "run",
            "-n",
            env_name,
            "python",
            "-m",
            "ipykernel",
            "install",
            "--user",
            "--name",
            env_name,
            "--display-name",
            kernel_name,
        ],
        check=False,
    )


def _setup_venv(target_root: Path, env_name: str, kernel_name: str, force_recreate: bool) -> None:
    venv_dir = target_root / ".venv"
    if force_recreate and venv_dir.exists():
        shutil.rmtree(venv_dir, ignore_errors=True)
    if not venv_dir.exists():
        run(["python", "-m", "venv", str(venv_dir)], check=False)
        bin_dir = "Scripts" if os.name == "nt" else "bin"
        py_exec = venv_dir / bin_dir / ("python.exe" if os.name == "nt" else "python")
        run([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"], check=False)
        req = target_root / "requirements.txt"
        if req.exists():
            run([str(py_exec), "-m", "pip", "install", "-r", str(req)], check=False)
    # Register kernel
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    py_exec = venv_dir / bin_dir / ("python.exe" if os.name == "nt" else "python")
    register_ipykernel(env_name, kernel_name, py_exec)


def bootstrap(
    target: Path,
    env: str = "none",
    name: str = "analyst-toolkit",
    kernel_name: Optional[str] = None,
    dataset: str = "auto",
    ingest: str = "copy",
    copy_notebook: bool = True,
    generate_configs: bool = False,
    project_name: str = "",
    vscode_ai: str = "gemini",
    reuse_env: bool = True,
    force_recreate: bool = False,
    force_copy: bool = True,
    run_smoke: bool = False,
) -> None:
    target = target.resolve()
    kernel_name = kernel_name or f"Python ({name})"

    console.print("[bold]Scaffolding folders and templates[/bold]")
    _copy_templates(target, force_copy, project_name, vscode_ai, copy_notebook)

    console.print("[bold]Wiring dataset (if available)[/bold]")
    chosen = _wire_dataset(target, dataset=dataset, ingest=ingest)

    console.print("[bold]Persisting .env defaults[/bold]")
    _persist_env_defaults(target, name, kernel_name, project_name, vscode_ai)

    # Validate choice-like inputs to keep behavior strict but Typer-compatible
    valid_env = {"conda", "venv", "none"}
    if env not in valid_env:
        console.print(f"[red]Invalid env: {env}. Use one of: {sorted(valid_env)}[/red]")
        return
    valid_ingest = {"move", "copy", "none"}
    if ingest not in valid_ingest:
        console.print(f"[red]Invalid ingest: {ingest}. Use one of: {sorted(valid_ingest)}[/red]")
        return
    valid_ai = {"gemini", "codex", "off"}
    if vscode_ai not in valid_ai:
        console.print(f"[red]Invalid vscode_ai: {vscode_ai}. Use one of: {sorted(valid_ai)}[/red]")
        return

    if env == "conda":
        console.print("[bold]Setting up Conda environment[/bold]")
        _setup_conda(
            target,
            name,
            kernel_name,
            reuse=reuse_env,
            force_recreate=force_recreate,
        )
    elif env == "venv":
        console.print("[bold]Setting up venv[/bold]")
        _setup_venv(target, name, kernel_name, force_recreate=force_recreate)
    else:
        console.print("[yellow]Environment creation skipped (explicit opt-in)[/yellow]")

    if generate_configs:
        console.print("[bold]Generating suggested configs[/bold]")
        try:
            outdir = ic.infer_configs(str(target), input_path=str(chosen) if chosen else None)
            console.print(f"[green]Generated configs:[/green] {Path(outdir).relative_to(target)}")
        except Exception as e:
            console.print(f"[yellow]Skipping config generation:[/yellow] {e}")

    if run_smoke:
        cfg = target / "config" / "run_toolkit_config.yaml"
        console.print("[bold]Smoke test command:[/bold]")
        console.print(f"  python -m analyst_toolkit.run_toolkit_pipeline --config {cfg.relative_to(target)}")

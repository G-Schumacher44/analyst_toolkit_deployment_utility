from __future__ import annotations
"""Typer-powered CLI entrypoints.

Exposes two commands:
- `deploy` – scaffold a project and optionally set up an env/kernel.
- `infer-configs` – scan a CSV and generate suggested YAML configs.

The functions below are thin wrappers around the underlying library
functions to keep command parsing and business logic cleanly separated.
"""

from pathlib import Path
from typing import Optional

import typer
from rich import print

from .bootstrap import bootstrap
from . import infer_configs as ic


app = typer.Typer(add_completion=False, no_args_is_help=True, help="Analyst Toolkit deployment utilities")


@app.command("deploy")
def deploy_cmd(
    target: Path = typer.Option(Path("."), exists=False, file_okay=False, dir_okay=True, help="Project root to scaffold into (will be created)"),
    env: str = typer.Option("none", help="Environment mode: conda|venv|none"),
    name: str = typer.Option("analyst-toolkit", help="Environment name (and default kernel name)"),
    kernel_name: Optional[str] = typer.Option(None, help="Jupyter kernel display name"),
    dataset: str = typer.Option("auto", help="Dataset wiring: auto|prompt|<path>"),
    ingest: str = typer.Option("copy", help="Ingest policy for root CSV: move|copy|none"),
    copy_notebook: bool = typer.Option(True, help="Copy the starter notebook if bundled"),
    generate_configs: bool = typer.Option(False, help="Generate inferred config YAMLs"),
    project_name: str = typer.Option("", help="Project name for README / notebook injection"),
    vscode_ai: str = typer.Option("gemini", help="Inline suggestion provider: gemini|codex|off"),
    reuse_env: bool = typer.Option(True, help="Reuse existing env if found (conda)"),
    force_recreate: bool = typer.Option(False, help="Recreate env (conda/venv) if exists"),
    force_copy: bool = typer.Option(True, help="Overwrite existing template files"),
    run_smoke: bool = typer.Option(False, help="Print recommended smoke test command"),
):
    """Scaffold a project and (optionally) set up env/kernel + configs.

    Parameters are grouped as follows:
    - Target and naming: `target`, `name`, `kernel_name`, `project_name`.
    - Environment controls: `env`, `reuse_env`, `force_recreate`.
    - Dataset wiring: `dataset`, `ingest`.
    - Templates and docs: `copy_notebook`, `force_copy`, `vscode_ai`.
    - Extras: `generate_configs`, `run_smoke`.
    """
    bootstrap(
        target=target,
        env=env,  # explicit opt-in only
        name=name,
        kernel_name=kernel_name,
        dataset=dataset,
        ingest=ingest,
        copy_notebook=copy_notebook,
        generate_configs=generate_configs,
        project_name=project_name,
        vscode_ai=vscode_ai,
        reuse_env=reuse_env,
        force_recreate=force_recreate,
        force_copy=force_copy,
        run_smoke=run_smoke,
    )


@app.command("infer-configs")
def infer_configs_cmd(
    input: Optional[Path] = typer.Option(None, help="Path to input CSV; defaults to config or single CSV under data/raw"),
    outdir: Optional[Path] = typer.Option(None, help="Output directory for generated YAMLs; defaults to config/generated"),
    sample_rows: Optional[int] = typer.Option(None, help="Sample first N rows for speed"),
    max_unique: int = typer.Option(30, help="Max unique values to consider a column categorical"),
    exclude_patterns: str = typer.Option("id|uuid|tag", help="Regex for columns to exclude from categorical/outlier inference"),
    detect_datetimes: bool = typer.Option(True, help="Attempt to infer datetimes from object columns"),
    datetime_hints: Optional[str] = typer.Option(None, help="Comma-separated hints: col:strftime e.g. capture_date:%Y-%m-%d"),
):
    """Inspect a CSV and write suggested config YAMLs under `config/`.

    If `--input` is not supplied, we try to infer the project CSV from
    `config/run_toolkit_config.yaml` or a single CSV under `data/raw/`.
    """
    root = Path.cwd()
    hints = [s.strip() for s in (datetime_hints or "").split(",") if s.strip()]
    out = ic.infer_configs(
        root=str(root),
        input_path=str(input) if input else None,
        outdir=str(outdir) if outdir else None,
        sample_rows=sample_rows,
        max_unique=max_unique,
        exclude_patterns=exclude_patterns,
        detect_datetimes=detect_datetimes,
        datetime_hints=hints,
    )
    print(f"[green]Wrote suggested YAMLs to:[/green] {Path(out).relative_to(root)}")


def main_deploy() -> None:
    # Single-command entrypoint: expose just the deploy command
    typer.run(deploy_cmd)


def main_infer() -> None:
    # Single-command entrypoint: expose just the infer-configs command
    typer.run(infer_configs_cmd)

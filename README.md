<p align="center">
  <img src="logo_img/analyst_toolkit_deploy_banner.png" width="1000"/>
  <br>
  <em>Analyst Toolkit Deployment Utility — Scaffolding + Config Companion</em>
</p>

<p align="center">
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="Status" src="https://img.shields.io/badge/status-active-brightgreen">
  <img alt="Version" src="https://img.shields.io/badge/version-v0.1.2-blueviolet">
  <a href="sandbox_preview/"><img alt="Sandbox Preview" src="https://img.shields.io/badge/artifact-sandbox__preview-blue"></a>
  <a href="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/release.yml"><img alt="Release" src="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/release.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/codespaces/new/G-Schumacher44/analyst_toolkit_deployment_utAdded: Deployment bundle deploy_toolkit.zip with Makefile, templates, and bootstrap script.
Added: README TL;DR and Quick Start while preserving your skeleton layout.
Added: Consistent navigation footers across docs for quick navigation.
Added: .env.example with safe defaults; standardized env name to analyst-toolkit.
Changed: Fixed docs (image paths to repo_img, internal links, typos) and corrected code snippets.
Changed: README now links to deployment, usage, and config guides in tool_kit_resources/.
Removed: Tracked .env, .DS_Store, and large sample CSV to reduce repo bloat.
Infrastructure: .vscode/ added to .gitignore (keep local settings); kept deployment zip in-repo.ility?quickstart=1"><img alt="Open in Codespaces" src="https://github.com/codespaces/badge.svg"></a>
  <a href="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/lint.yml"><img alt="Lint" src="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/lint.yml/badge.svg?branch=main"></a>
</p>

## 📚 Overview

Cross‑platform scaffolding and configuration tools for Analyst Toolkit projects.
Scaffold a ready‑to‑run repo, wire your dataset, optionally create a project environment,
and generate suggested YAML configs for validation and outlier detection 

👀 [`Checkout the Analyst Toolkit`](https://github.com/G-Schumacher44/analyst_toolkit) on GitHub

## 📌 TL;DR

- Install (from source): `python -m pip install -e .`
- Install (from GitHub): `pip install "git+https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility.git@main"`
- Scaffold with dataset + configs:
  - `analyst-deploy --target ./my_project --env none --dataset "/abs/path.csv" --generate-configs`
- Run the toolkit inside `my_project` (ensure the toolkit is installed):
  - `pip install "git+https://github.com/G-Schumacher44/analyst_toolkit.git@main"`
  - `python -m analyst_toolkit.run_toolkit_pipeline --config config/run_toolkit_config.yaml`

## ▶️ Quick Start

1) Install this package
Option A — From GitHub (recommended for users):
```
pip install "git+https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility.git@main"
```
Option B — From source (for contributors):
```
python -m pip install -e .
```
2) Create a new project:
```
analyst-deploy \
  --target ./my_project \
  --env none \
  --dataset "/abs/path/to.csv" \
  --generate-configs
```
3) Optional: create a project environment + kernel inside the scaffold:
```
analyst-deploy --target ./my_project --env conda --name analyst-toolkit
```
4) Open the starter notebook `notebooks/toolkit_template.ipynb` or run the toolkit:
```
# ensure the core toolkit is installed in your active environment
pip install "git+https://github.com/G-Schumacher44/analyst_toolkit.git@main"

python -m analyst_toolkit.run_toolkit_pipeline --config config/run_toolkit_config.yaml
```

5) Programmatic use (optional):
```
from pathlib import Path
from analyst_toolkit_deploy.bootstrap import bootstrap

bootstrap(
    target=Path("./my_project"),
    env="none",
    dataset="/abs/path.csv",
    generate_configs=True,
)
```

## 🗂️ What It Creates

- Folders: `config/`, `data/raw`, `exports/*`, `notebooks/`, `src/` (with `.gitkeep`)
- Templates: module YAMLs, `run_toolkit_config.yaml`, `environment.yml`, `requirements.txt`, `.gitignore`, `.vscode/settings.json`, `.env`
- Notebook: `notebooks/toolkit_template.ipynb`
- Docs: `README.md` (title auto‑set from folder or `--project-name`), `LICENSE` (MIT, year + author injected)


## 🧭 Orientation & Getting Started

<details>
<summary><strong>🧠 Notes from the Dev Team</strong></summary>

I built this deployment utility to solve the first, most tedious problem in any analysis: setting up the project. Before you can even start exploring your data, you're stuck creating folders, managing environments, and writing boilerplate configuration.

This tool automates all of that. In one command, it creates a clean, repeatable workspace, safely handles your dataset, and even gives you smart starting configurations. It's designed to get you from a raw CSV to a fully functional ETL pipeline in seconds.

The goal is simple: let you spend less time on setup and more time doing what matters—finding the stories in your data that drive action.

</details>

<details>
<summary><strong>💻 CLI Commands</strong></summary>


- `analyst-deploy`: scaffold project, wire dataset, optional env/kernel, optional config generation
- `analyst-infer-configs`: generate suggested YAMLs from a CSV
- `python -m analyst_toolkit_deploy`: module entry

Common flags:
- `--target`: project directory to create/populate
- `--dataset`: `auto` | `prompt` | `/path/to.csv`
- `--ingest`: `copy` (default) | `move` | `none`
- `--env`: `none` (default) | `conda` | `venv`
- `--generate-configs`: write suggested YAMLs under `config/generated/`
- `--project-name`: README title; otherwise derived from folder name

</details>

<details>
<summary><strong>🛠 Troubleshooting</strong></summary>

- CLI not found on PATH: use the module form as an alternative:
  - `python -m analyst_toolkit_deploy --help`
- Toolkit not installed when using your existing env (no project env):
  - `pip install "git+https://github.com/G-Schumacher44/analyst_toolkit.git@main"`
- Dataset wiring skipped or wrong file:
  - Prefer absolute CSV paths, or place exactly one CSV in `data/raw/` and use `--dataset auto`.
  - Control ingestion with `--ingest copy|move|none` (default: copy). `none` keeps an absolute path in the config.
- Config suggestions didn’t generate:
  - Ensure `pipeline_entry_path` is set in `config/run_toolkit_config.yaml`, or pass `--input` to `analyst-infer-configs`.
- Jupyter kernel not visible after env creation:
  - Re-run: `python -m ipykernel install --user --name analyst-toolkit --display-name "Python (analyst-toolkit)"` (or conda run equivalent).
- Windows path quirks:
  - Use double quotes around paths; prefer forward slashes or raw strings when scripting.
- Conda/env creation is explicit:
  - Pass `--env conda` or `--env venv` to create a project env; default is `--env none`.

</details>

<details>
<summary>📐 What’s Included</summary>

- CLI: `analyst-deploy`, `analyst-infer-configs`, and `python -m analyst_toolkit_deploy`.
- Templates: per-module YAMLs + `run_toolkit_config.yaml`.
- Notebook: `notebooks/toolkit_template.ipynb` for guided runs.
- Env files: `environment.yml`, `requirements.txt`.
- VS Code: `.vscode/settings.json` (formatting, linting, extraPaths).
- Docs: `resource_hub/` with usage, config, notebook, and deployment guides.

</details>

<details>
<summary><strong>🫆 Version Release Notes</strong></summary>

- v0.1.1
  - Package data: ensure `templates/**` included in wheels; fix Hatch config
  - CLI/runtime: correct venv ipykernel registration (separate kernel name/display)
  - Docs: update repo URLs to `deployment_utility`; fix template README links/stray tag
  - QA: validated build artifacts, metadata, CLI help, and scaffold smoke

- v0.1.0
  - Initial Python-native bootstrap + Typer CLI.
  - Deterministic Resource Hub scaffolding.
  - Dataset wiring + config inference (`config/generated/`).

</details>

<details>
<summary>⚙️ Project Structure</summary>

```
analyst_toolkit_deployment_utility/
├── src/
│   └── analyst_toolkit_deploy/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py                  # Typer CLI
│       ├── bootstrap.py            # Python-native bootstrap
│       ├── infer_configs.py        # CSV → YAML suggestions
│       ├── utils.py
│       └── templates/
│           ├── config/*.yaml       # Scaffolded YAML templates
│           ├── resource_hub/*.md   # Docs copied into projects
│           ├── .vscode/settings.json
│           ├── environment.yml, requirements.txt, .env.template
│           └── toolkit_template.ipynb
├── resource_hub/*.md               # Repo-level docs
├── README.md, LICENSE, pyproject.toml
└── environment.dev.yml             # Dev env for contributors
```

</details>

<details>

<summary>📎 Resource Hub Links</summary>

Additional resources for the [`Analyst Toolkit`](https://github.com/G-Schumacher44/analyst_toolkit) and this deploy utility are provided under [`resource_hub/`](resource_hub/):

- 🔧 [`Deploy Setup Guide`](resource_hub/deployment_setup_guide.md)
- 📘 [`Toolkit README/Usage`](resource_hub/toolkit_readme.md)
- ⚙️ [`Config Guide`](resource_hub/toolkit_config_guide.md)
- 📓 [`Notebook Guide`](resource_hub/notebook_usage_guide.md)
- 🚀 [`Deployment Guide`](resource_hub/deployment_guide.md)
- 🗺️ [`Resource Hub`](resource_hub/resource_hub.md)



</details>

## 📸 Sandbox Preview (Example Artifact)

An example scaffolded project is included under `sandbox_preview/` to showcase the folder structure, docs, notebook, and config templates generated by this utility.

- Open: `sandbox_preview/README.md`
- Explore: `sandbox_preview/notebooks/toolkit_template.ipynb`
- Inspect configs: `sandbox_preview/config/`
- Place a CSV under `sandbox_preview/data/raw/` and run the toolkit command printed in the scaffold’s README or use:
  - `python -m analyst_toolkit.run_toolkit_pipeline --config config/run_toolkit_config.yaml`

Note: The artifact uses `.gitkeep` placeholders so its `data/` and `exports/` folders remain visible without shipping data.

## 🛠 CI/CD and Codespaces

- GitHub Actions: automated build + metadata checks on pushes/PRs. See `.github/workflows/ci.yml`.
- Release workflow: builds artifacts on tags (`v*`) and can publish to TestPyPI/PyPI if secrets are set. See `.github/workflows/release.yml`.
- Codespaces: open in GitHub Codespaces and the devcontainer provisions a conda env from `environment.dev.yml`, installs the package, and registers a Jupyter kernel. See `.devcontainer/`.

## 🤝 On Generative AI Use

Generative AI tools (including models from Google and OpenAI) were used throughout this project as part of an integrated workflow — supporting code generation, documentation refinement, and idea testing. These tools accelerated development, but the logic, structure, and documentation reflect intentional, human-led design. This repository reflects a collaborative process where automation supports clarity and iteration deepens understanding.


This project is licensed under the [MIT License](LICENSE).</file>

---

<p align="center">
  <a href="resource_hub/notebook_usage_guide.md">📓 <b>Notebook Usage</b></a>
  &nbsp;·&nbsp;
  <a href="resource_hub/resource_hub.md">🗺️ <b>Resource Hub</b></a>
  &nbsp;·&nbsp;
  <a href="resource_hub/deployment_guide.md">🚀 <b>Deployment Guide</b></a>
  &nbsp;·&nbsp;
  <a href="resource_hub/deployment_setup_guide.md">📘 <b>Deployer Setup</b></a>
  &nbsp;·&nbsp;
  <a href="resource_hub/toolkit_readme.md">📘 <b>Toolkit Usage</b></a>
</p>

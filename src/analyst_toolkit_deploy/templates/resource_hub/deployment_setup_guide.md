

# 📘 Analyst Toolkit Deployment Utility — Set-up Guide

This guide mirrors the style of the Analyst Toolkit docs and walks through installing the deploy package, scaffolding a project, wiring your dataset, generating config suggestions, and running the toolkit.

---

## ⚙️ Setup

Install (from the deploy package repo root):

```bash
python -m pip install -e .
```

Requirements:
- Python 3.9+
- Conda (optional, recommended) or venv

---

## 🧭 Scaffold a Project

Minimal scaffold (no environment creation):

```bash
analyst-deploy --target ./my_project --env none
```

With dataset + suggested configs (absolute CSV path recommended):

```bash
analyst-deploy \
  --target ./my_project \
  --env none \
  --dataset "/abs/path/to.csv" \
  --generate-configs
```

Ingest policy:
- `--ingest copy` (default): copy CSV to `data/raw/`
- `--ingest move`: move CSV into `data/raw/`
- `--ingest none`: keep an absolute path in config

What’s created:
- Standard folders (`config/`, `data/raw`, `exports/*`, `notebooks/`, `src/`)
- Per‑module YAML templates + `run_toolkit_config.yaml`
- `environment.yml`, `requirements.txt`, `.vscode/settings.json`, `.gitignore`, `.env`
- Bundled starter notebook `notebooks/toolkit_template.ipynb`
- README (title auto‑set) and LICENSE (MIT with year + author)

---

## 🏗️ Create a Project Environment (Optional)

Conda in the scaffold:

```bash
analyst-deploy --target ./my_project --env conda --name analyst-toolkit
```

venv alternative:

```bash
analyst-deploy --target ./my_project --env venv
```

This registers a Jupyter kernel (e.g., “Python (analyst-toolkit)”) for notebooks.

---

## 🧪 Generate/Refresh Config Suggestions

During scaffold (`--generate-configs`) or later:

```bash
analyst-infer-configs --input ./my_project/data/raw/your.csv
```

Useful flags:
- `--sample-rows N` — faster sampling
- `--max-unique` — categorical detection threshold
- `--exclude-patterns` — regex to exclude columns (e.g., `id|uuid|tag`)
- `--detect-datetimes on|off`
- `--datetime-hints col:%Y-%m-%d`

Suggestions land in `config/generated/` and serve as a starting point to refine your curated configs.

---

## 📓 Notebook + CLI Usage

Notebook:
- Open `my_project/notebooks/toolkit_template.ipynb`
- Choose kernel (if created): “Python (analyst-toolkit)”

CLI:

```bash
cd my_project
python -m analyst_toolkit.run_toolkit_pipeline --config config/run_toolkit_config.yaml
```

---

## 🛠 Troubleshooting

- CLI not found or import error:
  - Reinstall: `python -m pip install -e .`
  - Use module form: `python -m analyst_toolkit_deploy --help`
- Dataset wiring failed:
  - Use an absolute path or place one CSV in `data/raw/` and run with `--dataset auto`
- Config generation skipped:
  - Ensure `pipeline_entry_path` is set in `config/run_toolkit_config.yaml` or pass `--input` to `analyst-infer-configs`

___

<p align="center">
  <a href="README.md">🏠 <b>Main README</b></a>
  &nbsp;·&nbsp;
  <a href="deployment_guide.md">🚀 <b>Project Deployment Guide</b></a>
  &nbsp;·&nbsp;
  <a href="deployment_setup_guide.md">🔧 <b>Deployment Setup</b></a>
  &nbsp;·&nbsp;
  <a href="toolkit_readme.md">📘 <b>Toolkit Usage</b></a>
  &nbsp;·&nbsp;
  <a href="notebook_usage_guide.md">📓 <b>Notebook Usage</b></a>
  &nbsp;·&nbsp;
  <a href="toolkit_readme.md">📘 <b>Toolkit README</b></a>
  &nbsp;·&nbsp;
  <a href="toolkit_config_guide.md">⚙️ <b>Config Guide</b></a>
</p>

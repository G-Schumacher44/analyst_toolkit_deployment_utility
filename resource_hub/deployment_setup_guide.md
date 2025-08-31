<p align="center">
  <img src="../logo_img/analyst_toolkit_deploy_banner.png" width="1000"/>
  <br>
  <em>Analyst Toolkit Deployment— Set-Up Guide</em>
</p>
<p align="center">
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="Status" src="https://img.shields.io/badge/status-stable-brightgreen">
  <img alt="Version" src="https://img.shields.io/badge/version-v0.1.0-blueviolet">
</p>


# 📘 Analyst Toolkit Deployment Utility — Set-up Guide

This guide explains how to install the deploy package, scaffold a project, wire your dataset, generate config suggestions, and run the Analyst Toolkit — in the same style as the core Toolkit docs.

---

## ⚙️ Setup

Install (choose one):

Option A — From GitHub (recommended for users):
```bash
pip install "git+https://github.com/<org>/<repo>.git@main"
```

Option B — From source (for contributors):
```bash
python -m pip install -e .
```

Requirements: Python 3.9+, Conda (optional) or venv.

---

## 🧭 Scaffold a Project

Minimal:
```bash
analyst-deploy --target ./my_project --env none
```

With dataset + suggested configs:
```bash
analyst-deploy \
  --target ./my_project \
  --env none \
  --dataset "/abs/path/to.csv" \
  --generate-configs
```

Ingest policy:
- `--ingest copy` (default): copy CSV to `data/raw/`
- `--ingest move`: move CSV to `data/raw/`
- `--ingest none`: keep absolute path in config

Creates: `config/`, `data/raw`, `exports/*`, `notebooks/`, `src/`, YAML templates + `run_toolkit_config.yaml`, `environment.yml`, `requirements.txt`, `.vscode/settings.json`, `.gitignore`, `.env`, README (auto title), LICENSE (MIT, year+author), and a bundled starter notebook.

---

## 🏗️ Project Environment (Optional)

Conda:
```bash
analyst-deploy --target ./my_project --env conda --name analyst-toolkit
```

venv:
```bash
analyst-deploy --target ./my_project --env venv
```

Registers a Jupyter kernel for notebooks.

---

## 🧪 Generate/Refresh Config Suggestions

```bash
analyst-infer-configs --input ./my_project/data/raw/your.csv
```

Options: `--sample-rows`, `--max-unique`, `--exclude-patterns`, `--detect-datetimes`, `--datetime-hints col:%Y-%m-%d`.

Results go to `config/generated/`.

---

## 📓 Notebook + CLI Usage

Notebook: `my_project/notebooks/toolkit_template.ipynb` (choose project kernel if created)

CLI:
```bash
cd my_project
python -m analyst_toolkit.run_toolkit_pipeline --config config/run_toolkit_config.yaml
```

---

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

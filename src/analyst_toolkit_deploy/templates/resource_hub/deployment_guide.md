
# 🚀 Deployment Guide (Notebook‑First)

This guide shows how to unzip the deployment bundle, scaffold a project, auto‑ingest a dataset, infer starter configs locally (no AI, no network), and launch the notebook for Diagnostics and Validation.

---

## ✅ Prerequisites

- Conda installed and initialized in your shell (`conda --version`)
- Make available (`make --version`)
- Network access if you’re not using offline installs

---

## 🧩 What the Bundle Contains

- `Makefile` (at repo root): convenient targets for setup, wiring data, config inference, packaging
- `deploy_toolkit/templates/**`: configuration, env, VS Code, and notebook templates
- `deploy_toolkit/scripts/bootstrap.sh`: notebook‑first bootstrapper
- `deploy_toolkit/tool_kit_resources/**`: docs (this guide, usage, config)

---

## ⚡ Quick Start

1) Unzip the bundle at your project root (Makefile should be at `./Makefile`).
2) Add your CSV at repo root (e.g., `./my_data.csv`) or `./data/raw/`.
3) Activate Conda base:

```bash
conda activate base
```

4) Run setup (builds env, scaffolds repo, infers configs, wires dataset):

```bash
make setup PROJECT_NAME=<your_project_name>
```

Sample initial setup commands:

```bash
# Most common (auto-discovers a single CSV at root or data/raw and copies it into data/raw)
make setup PROJECT_NAME=my_project DATASET=auto

# Prompt to select when multiple CSVs are present
make setup PROJECT_NAME=my_project DATASET=prompt

# Explicit env/kernel names (optional override)
make setup ENV=deploy_toolkit KERNEL_NAME="Python (deploy_toolkit)" PROJECT_NAME=my_project DATASET=auto
```

Defaults in setup:
- `TARGET=.` (repo root)
- `ENV=<folder_name>`; `KERNEL_NAME="Python (<ENV>)"`
- `DATASET=auto` (uses single CSV; prompts if multiple)
- `INGEST=copy` (copies a root CSV into `data/raw/`)
- `GENERATE=1` (writes `config/generated/*`)

5) Launch the starter notebook:

```bash
conda activate <ENV>
make notebook
```

Then select kernel “Python (<ENV>)” and Run All.

---

## 🔩 What Setup Produces

- Scaffolds: `config/`, `data/{raw,processed,features}`, `exports/{joblib,plots,reports}`, `notebooks/`, `.vscode/`
- Copies: `.env`, `.gitignore`, `environment.yml`, `requirements.txt`, `README.md`
- Notebook: `notebooks/toolkit_template.ipynb` (titled with `PROJECT_NAME`)
- Wiring: `config/run_toolkit_config.yaml:pipeline_entry_path` set to your CSV
- Inference (local, privacy‑safe): `config/generated/*` (validation, certification, outliers)
- Env + kernel: Conda env `<ENV>`, kernel “Python (<ENV>)”

---

## 🗂️ Data Ingestion Behavior

- If `data/raw/` contains exactly one CSV → uses that automatically
- Else, if the project root contains exactly one CSV → copies (or moves) it into `data/raw/` and wires it
- If multiple CSVs are found (root or `data/raw/`) → prompts to select (unless `DATASET=/path.csv` is provided)
- Control ingestion with `INGEST=copy|move|none` (default `copy`)

Privacy: Inference/config generation is local Python code; no AI models or network calls.

---

## 🧪 Notebook‑First Flow

1) Run M01 Diagnostics — inspect schema, nulls, cardinality, skew
2) Run M02 Validation (soft) — tune expected columns/types/ranges in YAML
3) Iterate configs, re‑run cells
4) Enable downstream modules when ready (normalization → duplicates → outliers → handling → imputation → final audit → certification strict)

---

## 🛠️ Make Targets

Common targets:

- Setup (alias for full bootstrap):
  ```bash
  make setup PROJECT_NAME=<name>
  ```

- Wire dataset later (after setup):
  ```bash
  make wire-data DATASET=auto        # auto when exactly one CSV
  make wire-data DATASET=prompt      # interactive selection
  make wire-data DATASET=/full/path.csv
  ```

- Regenerate config suggestions (local):
  ```bash
  make configs INPUT=data/raw/your.csv MAX_UNIQUE=30 SAMPLE_ROWS=50000
  ```

- Launch notebook:
  ```bash
  conda activate <ENV>
  make notebook
  ```

- Package deployable zip:
  ```bash
  make package
  ```

- Clean any prior scaffolds inside `deploy_toolkit/` (keeps templates/scripts/resources):
  ```bash
  make clean-deploy-scaffold
  ```

---

## ⚙️ Variables

These can be supplied to any `make` command:

- `TARGET`: project root (default `.`)
- `ENV`: Conda environment (default = folder name)
- `KERNEL_NAME`: Jupyter kernel (default `Python (<ENV>)`)
- `DATASET`: `auto|prompt|/path.csv` (default `auto`)
- `INGEST`: `copy|move|none` (default `copy`) — how to ingest a root CSV into `data/raw/`
- `GENERATE`: `1|0` (default `1`) — write `config/generated/*`
- `OFFLINE`: `1|0` — skip network expectations
- `VSCODE_AI`: `gemini|codex|off` — inline suggestions provider in VS Code
- `PROJECT_NAME`: used in README + notebook title

---

## 🧯 Troubleshooting

- Conda not initialized: `source "$(conda info --base)/etc/profile.d/conda.sh"`
- Script not executable: `chmod +x deploy_toolkit/scripts/bootstrap.sh`
- Multiple CSVs: use `DATASET=prompt` or pass a path with `DATASET=/path/to.csv`
- Notebook won’t open via `make notebook`: ensure Jupyter is installed in `<ENV>` or run `jupyter lab notebooks/toolkit_template.ipynb`

---

## 🔒 Privacy Notes

- Config inference is fully local: no data leaves your machine
- The toolkit avoids logging raw rows; outputs are summaries, reports, and dashboards
- `.gitignore` excludes `data/**` and `exports/**` by default

___

<p align="center">
  <a href="README.md">🏠 <b>Main README</b></a>
  &nbsp;·&nbsp;
  <a href="deployment_guide.md">🚀 <b>Project Deployment Guide</b></a>
  &nbsp;·&nbsp;
  <a href="deploment_setup_guide.md">🔧 <b>Deployment  Setup</b></a>
  &nbsp;·&nbsp;
  <a href="toolkit_usage_guide">📘 <b>Toolkit Usage</b></a>
  &nbsp;·&nbsp;
  <a href="notebook_usage_guide.md">📓 <b>Notebook Usage</b></a>
  &nbsp;·&nbsp;
  <a href="toolkit_readme.md">📘 <b>Toolkit README</b></a>
  &nbsp;·&nbsp;
  <a href="toolkit_config_guide.md">⚙️ <b>Config Guide</b></a>
</p>
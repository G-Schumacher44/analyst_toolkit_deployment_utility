<p align="center">
  <img src="logo_img/analyst_toolkit_deploy_banner.png" width="1000"/>
  <br>
  <em>Analyst Toolkit Deployment Utility — Scaffolding + Config Companion</em>
</p>

<p align="center">
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="Status" src="https://img.shields.io/badge/status-active-brightgreen">
  <img alt="Version" src="https://img.shields.io/badge/version-v0.2.2-blueviolet">
  <a href="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/codespaces/new/G-Schumacher44/analyst_toolkit_deployment_utility?quickstart=1"><img alt="Open in Codespaces" src="https://github.com/codespaces/badge.svg"></a>
</p>

## 📚 Overview

This utility provides cross-platform tools to scaffold and configure projects for the **Analyst Toolkit**.
In a single command, you can:
- Create a standardized, ready-to-run project structure.
- Safely ingest your dataset.
- Generate intelligent starter YAML configurations for the toolkit's modules.

👀 [`Checkout the Analyst Toolkit`](https://github.com/G-Schumacher44/analyst_toolkit) on GitHub

---

## ▶️ Quick Start: From CSV to Notebook in 60 Seconds

1.  **Prepare Your Workspace**
    Create a new folder for your project and place your dataset inside it.
    ```bash
    mkdir my-new-analysis
    mv ~/Downloads/my_data.csv ./my-new-analysis/
    ```

2.  **Install the Deployment Utility**
    In your terminal, install the utility using `pip`.
    ```bash
    pip install "git+https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility.git@v0.2.4"
    ```

3.  **Scaffold Your Project**
    Run a single command to create the project structure, ingest your data, and generate starter configs.
    ```bash
    analyst-deploy --target ./my-new-analysis --dataset ./my-new-analysis/my_data.csv --generate-configs
    ```

4.  **Start Analyzing**
    Navigate into your new project, install the core toolkit, and launch the notebook.
    ```bash
    cd my-new-analysis
    pip install "git+https://github.com/G-Schumacher44/analyst_toolkit.git@v0.2.4"
    jupyter lab notebooks/toolkit_template.ipynb
    ```

---

## 🗂️ What It Creates

The `analyst-deploy` command builds a complete, best-practice project structure for you:

- **`config/`**: Contains all YAML configuration files for controlling the pipeline.
- **`data/raw/`**: Your raw dataset is copied here.
- **`notebooks/`**: Includes a pre-configured `toolkit_template.ipynb` to guide your analysis.
- **`exports/`**: Where all reports, plots, and cleaned data will be saved.
- **`resource_hub/`**: A complete set of documentation and user guides.
- **And more**: `src/`, `.gitignore`, `LICENSE`, and a project-specific `README.md`.

---

<details>
<summary><strong>🧠 Why Use This Utility?</strong></summary>

This tool automates the most tedious part of any analysis: project setup. It's designed to get you from a raw CSV to a fully functional, reproducible ETL pipeline in seconds.

- **Speed**: Go from zero to a complete project with one command.
- **Best Practices**: Enforces a clean separation of code, configuration, and data.
- **Reproducibility**: Creates a standardized environment that's easy to share and re-run.
- **Security**: All data analysis for config generation is done 100% locally. Your data never leaves your machine.

The goal is simple: let you spend less time on setup and more time finding the stories in your data.
</details>

<details>
<summary><strong>🫆 Version Release Notes</strong></summary>

**v0.2.2**
  - **Major Documentation Overhaul**: Complete rewrite of all documentation for clarity and accuracy. Introduced a `USER_GUIDE.md` for users and a `DEVELOPMENT.md` for contributors, centralizing all guides in `resource_hub`.
  - **Modernized Project Scaffolding**: The `toolkit_template.ipynb` included in new projects is now fully refactored to use the modern, direct-call API of the `analyst_toolkit v0.2.0`.
  - **Enhanced Reproducibility**: Added a `Dockerfile` for running the utility in an isolated environment and a fully automated `.devcontainer` setup for a one-click development experience in GitHub Codespaces.
  - **Improved Packaging**: Updated `pyproject.toml` with standard classifiers and keywords for better discoverability on PyPI. Removed redundant legacy configuration files.


- v0.1.2
  - Docs: Synchronized all `resource_hub` documentation between the root repository and the deployable templates.
  - Docs: Added explanatory notes to guides to clarify the purpose of the advanced `run_module` helper function in the notebook template.
  - Build: Refined `pyproject.toml` to explicitly include the `templates` directory in the wheel, improving build robustness and clarity.
  - QA: Corrected various links and improved consistency across all documentation files.

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
<summary><strong>💻 Command Reference</strong></summary>

This utility provides two main CLI commands:

- **`analyst-deploy`**: The primary command for scaffolding a new project.
  - `--target`: The directory to create the project in. (Required)
  - `--dataset`: Path to your CSV. Use `auto` to find a single CSV in the target directory.
  - `--generate-configs`: Analyzes your dataset to create starter YAMLs.
  - `--env <none|conda|venv>`: Optionally create a project-specific environment.
  - `--project-name`: Sets the title in the generated `README.md`.

- **`analyst-infer-configs`**: Use this to generate or refresh configs for an existing project.
  - `--input`: Path to the source CSV file.
  - `--outdir`: Directory to save the generated YAML files (e.g., `config/generated`).

> For a complete list of options and programmatic usage, see the full **User Guide**.

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

**For this Deployment Utility:**

- 🔧 [**User Guide**:](resource_hub/USER_GUIDE.md) How to install and use this tool to create new projects.
- 👨‍💻 [**Developer Guide**:](resource_hub/DEVELOPMENT.md) How to set up a development environment and contribute.

**Core Analyst Toolkit Documentation (templates):**

The following guides for the core `analyst_toolkit` are included in the `resource_hub/` directory and are copied into every new project you create.

- 📘 [`Toolkit README`](resource_hub/toolkit_readme.md)
- ⚙️ [`Config Guide`](resource_hub/toolkit_config_guide.md)
- 📓 [`Notebook Guide`](resource_hub/toolkit_notebook_guide.md)



</details>

<details>
<summary><strong>👨‍💻 For Developers & Contributors</strong></summary>

Interested in contributing to the deployment utility? Our **Developer Guide** has everything you need to get started, including setup instructions and an overview of the codebase.

</details>

____

## 🔒 Privacy Notes

- Config inference is fully local: no data leaves your machine.
- The toolkit avoids logging raw rows; outputs are summaries, reports, and dashboards.
- `.gitignore` excludes `data/**` and `exports/**` by default.

---


## 🤝 On Generative AI Use

Generative AI tools (including models from Google and OpenAI) were used throughout this project as part of an integrated workflow — supporting code generation, documentation refinement, and idea testing. These tools accelerated development, but the logic, structure, and documentation reflect intentional, human-led design. This repository reflects a collaborative process where automation supports clarity and iteration deepens understanding.

---


## 📦 Licensing

This project is licensed under the MIT License.

---

<p align="center">
  <a href="USER_GUIDE.md">📘 <b>User Guide</b></a>
  &nbsp;·&nbsp;
  <a href="DEVELOPMENT.md">👨‍💻 <b>Developer Guide</b></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/G-Schumacher44/analyst_toolkit">🔬 <b>Analyst Toolkit Repo</b></a>
</p>
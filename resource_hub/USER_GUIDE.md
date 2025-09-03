<p align="center">
  <img src="../logo_img/analyst_toolkit_deploy_banner.png" width="1000"/>
  <br>
  <em>Analyst Toolkit Deployment Utility — User Guide</em>
</p>

# 📘 User Guide

Welcome! This guide provides a complete walkthrough for using the **Analyst Toolkit Deployment Utility**. You will learn how to:

1.  **Install** the utility.
2.  **Create** a new, standardized analysis project from a CSV file.
3.  **Understand** the recommended workflow for data analysis using the generated project.
4.  **Use** the advanced features and programmatic API.

---

## Part 1: Installation

First, install the utility from GitHub using `pip`. This command will download and install the latest version.

```bash
pip install "git+https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility.git@v0.2.3"
```

> **Note**: This utility requires Python 3.9 or higher.

---

## Part 2: Creating Your First Project

The primary goal of this utility is to get you from a raw dataset to a ready-to-analyze project in a single command.

#### Step 1: Prepare Your Workspace

Create a new, empty folder for your project and place your dataset inside it. For this example, we'll assume your dataset is named `my_data.csv`.

```bash
# Create the project directory
mkdir my-new-analysis

# Move your dataset into the new directory
mv ~/Downloads/my_data.csv ./my-new-analysis/
```

> **Note for Windows Users**: The commands above are for macOS/Linux. The Windows equivalents are `mkdir my-new-analysis` and `move %USERPROFILE%\Downloads\my_data.csv .\my-new-analysis\`. The `analyst-deploy` command itself works the same on all platforms.

#### Step 2: Scaffold the Project

Now, run the `analyst-deploy` command. This single command will:
-   Create the standard folder structure (`config/`, `data/`, `notebooks/`, etc.) inside `my-new-analysis`.
-   Copy your dataset into the `data/raw/` directory.
-   Analyze your dataset to generate intelligent starter YAML configurations.

```bash
analyst-deploy --target ./my-new-analysis --dataset ./my-new-analysis/my_data.csv --generate-configs
```

Your project is now fully scaffolded!

---

## Part 3: The Analyst Workflow

Once your project is created, you're ready to start your analysis.

#### Step 1: Navigate and Install the Core Toolkit

The deployment utility sets up the project structure, but the analysis is performed by the `analyst_toolkit`. Navigate into your new project directory and install the toolkit.

```bash
cd my-new-analysis

# Install the core toolkit needed to run the pipeline
pip install "git+https://github.com/G-Schumacher44/analyst_toolkit.git@v0.2.0"
```

#### Step 2: Launch the Notebook

The recommended way to work is through the pre-configured Jupyter Notebook.

```bash
jupyter lab notebooks/toolkit_template.ipynb
```

#### Step 3: Iterate and Analyze

The notebook is designed for an iterative, cell-by-cell workflow that separates configuration from code:

1.  **Run a module cell** (e.g., the "M01 - Diagnostics" cell).
2.  **Inspect the output dashboard** to understand the results.
3.  **Edit the corresponding YAML file** in the `config/` directory to refine the rules (e.g., add an expected column in `validation_config_template.yaml`).
4.  **Re-run the cell** to apply your new configuration.

This loop allows you to build a robust, auditable data pipeline without ever modifying the notebook's Python code.

---

## Part 4: Advanced Usage

<details>
<summary><strong>💻 Full Command Reference</strong></summary>

This utility provides two main CLI commands with several options for customization.

#### `analyst-deploy`

The primary command for scaffolding a new project.

-   `--target <path>`: **(Required)** The directory to create the project in.
-   `--dataset <path|auto>`: Path to your source CSV. Use `auto` to automatically find a single CSV in the target directory.
-   `--generate-configs`: If present, analyzes the dataset to create starter YAMLs in `config/generated/`.
-   `--ingest <copy|move|none>`: How to handle the dataset. `copy` is the default. `none` will use an absolute path in the config without moving the file.
-   `--env <none|conda|venv>`: Optionally create and register a dedicated project environment. `none` is the default.
-   `--name <env_name>`: The name for the Conda/venv environment if `--env` is used.
-   `--project-name <"My Project">`: Sets the title in the generated `README.md`. Defaults to the target folder name.

#### `analyst-infer-configs`

Use this to generate or refresh configs for an existing project.

-   `--input <path>`: **(Required)** Path to the source CSV file.
-   `--outdir <path>`: Directory to save the generated YAML files (defaults to `config/generated`).
-   `--sample-rows <int>`: Number of rows to sample for faster analysis.
-   `--max-unique <int>`: The threshold for treating a column as categorical.

</details>

<details>
<summary><strong>🐍 Programmatic Usage (for Automation)</strong></summary>

For advanced use cases, such as automating project creation in a larger script, you can import and use the core functions directly.

```python
from pathlib import Path
from analyst_toolkit_deploy.bootstrap import bootstrap
from analyst_toolkit_deploy.infer_configs import infer_configs_from_csv

# Define project parameters
project_dir = Path("./my_automated_project")
dataset_path = Path("/path/to/my_data.csv")

# 1. Scaffold the project structure
bootstrap(
    target=project_dir,
    dataset=str(dataset_path),
    project_name="My Automated Project"
)

# 2. Generate starter configs
infer_configs_from_csv(
    input_path=project_dir / "data" / "raw" / dataset_path.name,
    outdir=project_dir / "config" / "generated"
)

print(f"Project created at: {project_dir}")
```

</details>

---

<p align="center">
  <a href="../README.md">🏠 <b>Back to Main README</b></a>
  &nbsp;·&nbsp;
  <a href="DEVELOPMENT.md">👨‍💻 <b>Developer Guide</b></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/G-Schumacher44/analyst_toolkit">🔬 <b>Analyst Toolkit Repo</b></a>
</p>
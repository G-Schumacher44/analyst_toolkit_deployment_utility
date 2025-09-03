<p align="center">
  <img src="../logo_img/analyst_toolkit_deploy_banner.png" width="1000"/>
  <br>
  <em>Analyst Toolkit — Developer & Contributor Guide</em>
</p>

# 👨‍💻 Developer & Contributor Guide

This guide is for developers who want to contribute to the Analyst Toolkit Deployment Utility. It covers setting up a development environment, understanding the project structure, and following our contribution guidelines.

---

## ⚙️ Setting Up for Development

To get started, clone the repository and set up an editable installation.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/G-Schumacher44/analyst_toolkit_deployment_utility.git
    cd analyst_toolkit_deployment_utility
    ```

2.  **Create a Development Environment**
    We recommend using Conda to manage environments. A development environment file is provided.
    ```bash
    conda env create -f environment.dev.yml
    conda activate analyst-toolkit-dev
    ```

3.  **Install in Editable Mode**
    This allows you to make changes to the source code and have them immediately reflected when you run the CLI.
    ```bash
    pip install -e .
    ```

4.  **Verify Installation**
    Check that the CLI commands are available.
    ```bash
    analyst-deploy --help
    analyst-infer-configs --help
    ```

---

## 📂 Project Structure

The key components of the utility are located in the `src/analyst_toolkit_deploy/` directory.

-   **`cli.py`**: Defines the Typer-based command-line interface (`analyst-deploy` and `analyst-infer-configs`).
-   **`bootstrap.py`**: Contains the core logic for scaffolding a new project directory.
-   **`infer_configs.py`**: Contains the logic for analyzing a dataset and generating starter YAML files.
-   **`templates/`**: This is a critical directory. It contains all the files and folders (like `toolkit_template.ipynb`, YAML configs, and the `resource_hub` docs) that are copied into a new project during scaffolding.

---

## ✅ Code Style & Linting

This project uses `black`, `isort`, and `flake8` to maintain a consistent code style. Before committing, please format and lint your code. The configurations can be found in `pyproject.toml`.

---

## 🤝 How to Contribute

We welcome contributions! Please follow these steps:

1.  **Fork the repository** on GitHub.
2.  Create a **new branch** for your feature or bug fix.
3.  Make your changes and **commit them** with a clear, descriptive message.
4.  **Push** your branch to your fork.
5.  Open a **Pull Request** against the `main` branch of the original repository.

Thank you for helping improve the Analyst Toolkit ecosystem!

---

<p align="center">
  <a href="../README.md">🏠 <b>Back to Main README</b></a>
  &nbsp;·&nbsp;
  <a href="USER_GUIDE.md">📘 <b>User Guide</b></a>
</p>
#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="analyst_toolkit_deploy"

if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  echo "Updating existing conda env: $ENV_NAME"
  conda env update -n "$ENV_NAME" -f environment.dev.yml || true
else
  echo "Creating conda env: $ENV_NAME"
  conda env create -f environment.dev.yml || conda create -y -n "$ENV_NAME" python=3.10
fi

echo "Installing package in editable mode"
conda run -n "$ENV_NAME" python -m pip install -e .

echo "Registering Jupyter kernel"
conda run -n "$ENV_NAME" python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python ($ENV_NAME)"

echo "Done. Activate with: conda activate $ENV_NAME"


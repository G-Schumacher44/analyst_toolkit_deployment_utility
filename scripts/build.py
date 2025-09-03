import sys
from pathlib import Path
from analyst_toolkit_deploy.bootstrap import bootstrap

# 1. Define the target directory for your new project.
#    This folder will be created by the script.
target_dir = Path(".")

# 2. Provide the absolute path to your dataset.
#    The utility will copy it into the project and configure the pipeline.
#    IMPORTANT: Replace this with the actual path to your CSV file.
dataset_file_path = Path("./synthetic_penguins_v3.5.csv")

# --- Improvement: Add a pre-flight check for the dataset file ---
if not dataset_file_path.is_file():
    print(f"❌ Error: Dataset file not found at '{dataset_file_path}'")
    print("Please update the 'dataset_file_path' variable in this script to a valid file path.")
    sys.exit(1)  # Exit the script with an error code

print(f"🚀 Scaffolding project at: {target_dir.resolve()}")
print(f"📊 Wiring up dataset: {dataset_file_path}")

# 3. Call the bootstrap function to create the project structure.
bootstrap(
    target=target_dir,
    dataset=str(dataset_file_path),
    generate_configs=True,  # Automatically creates starter YAML configs from your data.
    env="none"              # Skips creating a new Conda/venv environment for now.
)

print(f"\n✅ Project '{target_dir.name}' created successfully!")

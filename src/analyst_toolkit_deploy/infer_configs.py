"""CSV / Parquet / GCS inspection utilities to build suggested YAML configs.

Reads a sample (or full) dataset, infers schema information, categorical values,
and numeric ranges, then returns data-enriched YAML config strings for each
requested module.

Supports three input types:
  - gs://bucket/path   → GCS pull (parquet or CSV)
  - path/to/file.parquet → pd.read_parquet()
  - path/to/file.csv   → pd.read_csv() (original behavior)

Returns dict[str, str]: module_name → YAML string.
Writes to outdir if provided (CLI path).

All 9 module configs are supported:
  Inferred from data: validation, certification, outliers
  Enriched templates: diagnostics, normalization, duplicates,
                      handling, imputation, final_audit
"""

from __future__ import annotations

import glob
import os
import re
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml


# ---------------------------------------------------------------------------
# Internal I/O helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: str) -> Dict[str, Any]:
    """Safe-load YAML file into a dict; return empty mapping on null."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _write_yaml(path: str, data: Dict[str, Any]) -> None:
    """Write a dict to YAML with stable, readable formatting."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def _load_input(path: str, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """Dispatch on path type and return a DataFrame.

    Args:
        path: Local CSV/parquet path or gs:// URI.
        sample_rows: If set, read only the first N rows.

    Returns:
        pd.DataFrame
    """
    read_kwargs: Dict[str, Any] = {}
    if sample_rows is not None:
        read_kwargs["nrows"] = int(sample_rows)

    if path.startswith("gs://"):
        return _load_from_gcs(path, sample_rows=sample_rows)
    elif path.endswith(".parquet"):
        df = pd.read_parquet(path)
        if sample_rows:
            df = df.head(sample_rows)
        return df
    else:
        return pd.read_csv(path, low_memory=False, **read_kwargs)


def _load_from_gcs(gcs_path: str, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """Pull a dataset from GCS into a DataFrame.

    Checks for _MANIFEST.json at the partition path to get the file list;
    otherwise globs *.parquet then *.csv files.
    """
    import json
    import tempfile
    from pathlib import Path as _Path

    try:
        from google.cloud import storage
    except ImportError:
        raise ImportError(
            "google-cloud-storage is required for GCS input. "
            "Install: pip install google-cloud-storage"
        )

    stripped = gcs_path.removeprefix("gs://")
    bucket_name, _, prefix = stripped.partition("/")
    prefix = prefix.rstrip("/")

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Direct file path — skip manifest/glob logic
    if prefix.endswith(".parquet") or prefix.endswith(".csv"):
        blobs = [bucket.blob(prefix)]
    else:
        manifest_blob = bucket.blob(f"{prefix}/_MANIFEST.json")
        if manifest_blob.exists():
            manifest = json.loads(manifest_blob.download_as_text())
            raw_files = manifest.get("files", [])
            # files entries may be bare strings or dicts with a "path" key
            file_names = [f["path"] if isinstance(f, dict) else f for f in raw_files]
            blobs = [bucket.blob(f"{prefix}/{f}") for f in file_names]
        else:
            all_blobs = list(client.list_blobs(bucket_name, prefix=f"{prefix}/"))
            blobs = [b for b in all_blobs if b.name.endswith(".parquet") or b.name.endswith(".csv")]

    if not blobs:
        raise FileNotFoundError(f"No data files found at: {gcs_path}")

    frames = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for blob in blobs:
            local = _Path(tmpdir) / _Path(blob.name).name
            blob.download_to_filename(str(local))
            if str(local).endswith(".parquet"):
                frames.append(pd.read_parquet(local))
            else:
                frames.append(pd.read_csv(local, low_memory=False))

    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    if sample_rows:
        df = df.head(sample_rows)
    return df


def _find_entry_csv(root: str) -> str:
    """Infer the input CSV from config or a single file under data/raw.

    Preference order:
    1) `config/run_toolkit_config.yaml` → `pipeline_entry_path`.
    2) Exactly one `*.csv` under `data/raw/`.
    Otherwise, raise with a clear instruction.
    """
    cfg_path = os.path.join(root, "config", "run_toolkit_config.yaml")
    if os.path.exists(cfg_path):
        cfg = _load_yaml(cfg_path)
        p = (cfg or {}).get("pipeline_entry_path")
        if p:
            p_abs = os.path.join(root, p) if not os.path.isabs(p) else p
            if os.path.exists(p_abs):
                return p_abs
    candidates = sorted(glob.glob(os.path.join(root, "data", "raw", "*.csv")))
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError(
        "Could not determine entry CSV. Set --input or pipeline_entry_path in "
        "config/run_toolkit_config.yaml or place exactly one CSV in data/raw/."
    )



# ---------------------------------------------------------------------------
# Inference helpers (unchanged from v0.2.5)
# ---------------------------------------------------------------------------

def infer_types(df: pd.DataFrame, detect_datetimes: bool = True) -> Dict[str, str]:
    """Map each column to a simple dtype label; optionally detect datetimes."""
    types: Dict[str, str] = {}
    for col in df.columns:
        s = df[col]
        dtype = str(s.dtype)
        if detect_datetimes and dtype == "object":
            sample = s.dropna().astype(str).head(500)
            if not sample.empty:
                parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
                if parsed.notna().mean() >= 0.9:
                    types[col] = "datetime64[ns]"
                    continue
        types[col] = dtype
    return types


def infer_categoricals(
    df: pd.DataFrame,
    max_unique: int = 30,
    top_n: int = 30,
    exclude_patterns: List[re.Pattern] | None = None,
) -> Dict[str, list]:
    """Return a map of likely-categorical columns to a small set of values."""
    cats: Dict[str, list] = {}
    for col in df.columns:
        s = df[col]
        if exclude_patterns and any(p.search(col) for p in exclude_patterns):
            continue
        if s.dtype == "object" or str(s.dtype).startswith("category") or s.nunique(dropna=True) <= max_unique:
            vals = s.dropna().astype(str).value_counts().index.tolist()[:top_n]
            if vals:
                cats[col] = sorted(list(set(vals)))
    return cats


def infer_numeric_ranges(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Compute min/max ranges for numeric columns (NaNs ignored)."""
    ranges: Dict[str, Dict[str, float]] = {}
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            s_clean = s.dropna()
            if s_clean.empty:
                continue
            ranges[col] = {"min": float(s_clean.min()), "max": float(s_clean.max())}
    return ranges


# ---------------------------------------------------------------------------
# Config builders — data-inferred (validation, certification, outliers)
# ---------------------------------------------------------------------------

def build_validation_config(input_path_rel: str, cols, types, cats, ranges, fail_on_error: bool) -> Dict[str, Any]:
    """Assemble a validation/certification config structure from inference."""
    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "validation": {
            "input_path": input_path_rel,
            "schema_validation": {
                "run": True,
                "fail_on_error": bool(fail_on_error),
                "rules": {
                    "expected_columns": list(cols),
                    "expected_types": types,
                    "categorical_values": cats,
                    "numeric_ranges": ranges,
                },
            },
            "settings": {
                "checkpoint": False,
                "export": True,
                "as_csv": False,
                "export_path": "exports/reports/validation/validation_report.xlsx",
                "show_inline": True,
            },
        },
    }


def build_outlier_config(input_path_rel: str, numeric_cols) -> Dict[str, Any]:
    """Assemble a simple outlier detection config for numeric columns."""
    detection_specs = {c: {"method": "iqr", "iqr_multiplier": 1.5} for c in numeric_cols}
    detection_specs["__default__"] = {"method": "iqr", "iqr_multiplier": 2.0}
    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "outlier_detection": {
            "run": True,
            "input_path": input_path_rel,
            "detection_specs": detection_specs,
            "exclude_columns": [],
            "append_flags": True,
            "plotting": {
                "run": True,
                "plot_save_dir": "exports/plots/outliers/{run_id}",
                "plot_types": ["box", "hist"],
                "show_plots_inline": True,
            },
            "export": {
                "run": True,
                "export_dir": "exports/reports/outliers/detection/",
                "as_csv": False,
            },
            "checkpoint": {
                "run": True,
                "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m05_outliers_flagged.joblib",
            },
        },
    }


# ---------------------------------------------------------------------------
# Enriched template builders — 6 judgment-gap configs
# ---------------------------------------------------------------------------

def build_diag_config(df: pd.DataFrame, input_path_rel: str, types: Dict[str, str]) -> Dict[str, Any]:
    """Diagnostics config — fully inferred from dataset schema."""
    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "diagnostics": {
            "input_path": input_path_rel,
            "profile": {
                "run": True,
                "settings": {
                    "export": True,
                    "as_csv": False,
                    "export_path": "exports/reports/diagnostics/diagnostics_summary.xlsx",
                    "checkpoint": False,
                    "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m02_diag_checkpoint.joblib",
                    "show_inline": True,
                    "include_samples": True,
                    "include_metadata": True,
                    "encoding": "utf-8",
                    "max_rows": 5,
                    "high_cardinality_threshold": 15,
                    "quality_checks": {
                        "skew_threshold": 2.0,
                        "expected_dtypes": types,
                    },
                },
            },
            "plotting": {
                "run": True,
                "save_dir": "exports/plots/diagnostics/",
            },
        },
    }


def build_normalization_config(
    df: pd.DataFrame,
    input_path_rel: str,
    cats: Dict[str, list],
    types: Dict[str, str],
    numeric_cols: List[str],
) -> Dict[str, Any]:
    """Normalization config — scaffold from inferred schema; value_mappings left empty for human/LLM."""
    string_cat_cols = [
        c for c in cats
        if str(df[c].dtype) == "object" or str(df[c].dtype).startswith("category")
    ]
    datetime_cols = {
        col: {"format": "%Y-%m-%d", "errors": "coerce", "utc": False, "make_naive": True}
        for col, dtype in types.items()
        if "datetime" in dtype
    }
    coerce_dtypes = {c: types[c] for c in numeric_cols if c in types}

    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "normalization": {
            "run": True,
            "rules": {
                "rename_columns": {},
                "standardize_text_columns": string_cat_cols,
                "value_mappings": {col: {} for col in string_cat_cols},
                "fuzzy_matching": {
                    "run": False,
                    "settings": {},
                },
                "parse_datetimes": datetime_cols,
                "preview_columns": string_cat_cols,
                "coerce_dtypes": coerce_dtypes,
            },
            "settings": {
                "show_inline": True,
                "export": True,
                "as_csv": False,
                "export_path": "exports/reports/normalization/normalization_report.xlsx",
                "checkpoint": {
                    "run": True,
                    "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m03_df_normalized.joblib",
                },
            },
        },
    }


def build_dups_config(df: pd.DataFrame, input_path_rel: str, exclude_re: list) -> Dict[str, Any]:
    """Duplicates config — fully inferred; subset_columns pre-populated, user/LLM trims."""
    subset_cols = [
        c for c in df.columns
        if not pd.api.types.is_numeric_dtype(df[c])
        and not any(p.search(c) for p in exclude_re)
    ]
    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "duplicates": {
            "run": True,
            "input_path": input_path_rel,
            "subset_columns": subset_cols,
            "keep": "first",
            "mode": "remove",
            "settings": {
                "checkpoint": True,
                "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m04_dupes_checkpoint.joblib",
                "export": True,
                "export_path": "exports/reports/duplicates/duplicates_report.xlsx",
                "export_format": "xlsx",
                "show_inline": True,
                "plotting": {
                    "run": True,
                    "save_dir": "exports/plots/duplicates/",
                },
            },
        },
    }


def build_handling_config(input_path_rel: str, numeric_cols: List[str]) -> Dict[str, Any]:
    """Outlier handling config — one entry per numeric col, defaulting to median."""
    handling_specs: Dict[str, Any] = {"__global__": {"strategy": "none"}}
    for col in numeric_cols:
        handling_specs[col] = {"strategy": "median"}
    handling_specs["__default__"] = {"strategy": "clip"}

    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "outlier_handling": {
            "run": True,
            "input_df_path": "exports/joblib/{run_id}_m05_outliers_flagged.joblib",
            "detection_results_path": "exports/joblib/{run_id}_m05_detection_results.joblib",
            "handling_specs": handling_specs,
            "settings": {
                "show_inline": True,
                "export": {
                    "run": True,
                    "export_path": "exports/reports/outliers/handling/outlier_handling_report.xlsx",
                    "as_csv": False,
                },
                "checkpoint": {
                    "run": True,
                    "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m06_df_handled.joblib",
                },
            },
        },
    }


def build_imputation_config(df: pd.DataFrame, input_path_rel: str) -> Dict[str, Any]:
    """Imputation config — strategy auto-selected per column dtype; only null cols included."""
    strategies: Dict[str, Any] = {}
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                strategies[col] = "median"
            elif "datetime" in str(df[col].dtype):
                strategies[col] = {"strategy": "constant", "value": "1900-01-01"}
            else:
                strategies[col] = "mode"

    return {
        "notebook": True,
        "run_id": "",
        "logging": "auto",
        "imputation": {
            "run": True,
            "input_path": "exports/joblib/{run_id}_m06_df_handled.joblib",
            "rules": {
                "strategies": strategies,
            },
            "settings": {
                "show_inline": True,
                "export": {
                    "run": True,
                    "as_csv": False,
                    "export_path": "exports/reports/imputation/imputation_report.xlsx",
                },
                "plotting": {
                    "run": True,
                    "save_dir": "exports/plots/imputation/",
                },
                "checkpoint": {
                    "run": True,
                    "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m07_df_imputed.joblib",
                },
            },
        },
    }


def build_final_audit_config(
    df: pd.DataFrame,
    input_path_rel: str,
    types: Dict[str, str],
    cats: Dict[str, list],
) -> Dict[str, Any]:
    """Final audit config — fully inferred; drop_columns and disallowed_nulls are best-effort."""
    # Columns M05 appends as outlier flags — drop them before certification
    outlier_flag_cols = [c for c in df.columns if c.endswith(("_iqr_outlier", "_zscore_outlier"))]
    # Columns with no nulls in the sample are candidates for disallowed_null_columns
    no_null_cols = [c for c in df.columns if not df[c].isnull().any()]

    return {
        "run_id": "",
        "notebook": True,
        "logging": "auto",
        "final_audit": {
            "run": True,
            "input_df_path": "exports/joblib/{run_id}/{run_id}_m07_df_imputed.joblib",
            "raw_data_path": input_path_rel,
            "final_edits": {
                "run": True,
                "drop_columns": outlier_flag_cols,
                "rename_columns": {},
                "coerce_dtypes": {},
            },
            "certification": {
                "run": True,
                "fail_on_error": True,
                "rules": {
                    "expected_columns": list(df.columns),
                    "expected_types": types,
                    "categorical_values": cats,
                    "disallowed_null_columns": no_null_cols,
                },
            },
            "settings": {
                "show_inline": True,
                "export_report": True,
                "paths": {
                    "report_excel": "exports/reports/final_audit/{run_id}_FinalAuditReport.xlsx",
                    "report_joblib": "exports/reports/final_audit/{run_id}_FinalAuditReport.joblib",
                    "checkpoint_csv": "data/processed/{run_id}_certified.csv",
                    "checkpoint_joblib": "exports/joblib/{run_id}/{run_id}_certified.joblib",
                    "plot_save_dir": "exports/plots/final_audit/{run_id}/",
                },
            },
        },
    }


def build_master_config(modules_generated: list, outdir_rel: str = "config/generated") -> Dict[str, Any]:
    """Generate a master run_toolkit_config.yaml referencing all modules."""
    _module_config_map = {
        "validation": ("validation", f"{outdir_rel}/validation_config_autofill.yaml"),
        "certification": ("validation", f"{outdir_rel}/certification_config_autofill.yaml"),
        "outliers": ("outlier_detection", f"{outdir_rel}/outlier_config_autofill.yaml"),
        "diagnostics": ("diagnostics", f"{outdir_rel}/diag_config_autofill.yaml"),
        "normalization": ("normalization", f"{outdir_rel}/normalization_config_autofill.yaml"),
        "duplicates": ("duplicates", f"{outdir_rel}/dups_config_autofill.yaml"),
        "handling": ("outlier_handling", f"{outdir_rel}/handling_config_autofill.yaml"),
        "imputation": ("imputation", f"{outdir_rel}/imputation_config_autofill.yaml"),
        "final_audit": ("final_audit", f"{outdir_rel}/final_audit_config_autofill.yaml"),
    }

    modules_section: Dict[str, Any] = {}
    for module_name, (section_key, config_path) in _module_config_map.items():
        is_generated = module_name in modules_generated
        modules_section[module_name] = {
            "run": is_generated,
            "config_path": config_path,
        }

    return {
        "run_id": "run_001",
        "notebook": False,
        "pipeline_entry_path": "data/raw/",
        "modules": modules_section,
    }


# ---------------------------------------------------------------------------
# Map from module name → builder function tag
# ---------------------------------------------------------------------------

_INFERRED_MODULES = {"validation", "certification", "outliers"}

_ALL_MODULES = {
    "validation", "certification", "outliers",
    "diagnostics", "normalization", "duplicates",
    "handling", "imputation", "final_audit",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def infer_configs(
    root: str | None,
    input_path: str | None = None,
    modules: List[str] | None = None,
    outdir: str | None = None,
    sample_rows: int | None = None,
    max_unique: int = 30,
    exclude_patterns: str = "id|uuid|tag",
    detect_datetimes: bool = True,
    datetime_hints: List[str] | None = None,
) -> Dict[str, str]:
    """Inspect a dataset and generate YAML config strings for each module.

    Args:
        root: Project root directory. Required for local CSV discovery when
              input_path is not supplied. Pass None when providing input_path directly.
        input_path: Path to input data (local CSV/parquet or gs:// URI).
                    If None, discovered from root via _find_entry_csv().
        modules: Module names to generate. None = all inferrable modules.
                 Supported: validation, certification, outliers, diagnostics,
                 normalization, duplicates, handling, imputation, final_audit.
        outdir: If provided, write each YAML string to this directory as
                {module}_config_autofill.yaml. Always returns the dict.
        sample_rows: Read only the first N rows for speed.
        max_unique: Max unique values to consider a column categorical.
        exclude_patterns: Regex string for columns to skip in inference.
        detect_datetimes: Attempt datetime inference for object columns.
        datetime_hints: Per-column format hints, e.g. ["capture_date:%Y-%m-%d"].

    Returns:
        dict[str, str]: module_name → YAML string.
    """
    # Resolve modules list
    requested = set(modules) if modules else _ALL_MODULES
    unknown = requested - _ALL_MODULES
    if unknown:
        raise ValueError(f"Unknown module(s): {unknown}. Valid: {_ALL_MODULES}")

    # Resolve input path
    if input_path:
        resolved_input = input_path
        rel_path = input_path  # For GCS/remote paths, use as-is in configs
    else:
        if not root:
            raise ValueError("Either 'root' or 'input_path' must be provided.")
        root = os.path.abspath(root)
        resolved_input = _find_entry_csv(root)
        rel_path = os.path.relpath(resolved_input, root)

    # Load data
    df = _load_input(resolved_input, sample_rows=sample_rows)

    # Apply datetime hints
    datetime_hints = datetime_hints or []
    hinted_types: Dict[str, str] = {}
    for hint in datetime_hints:
        if ":" not in hint:
            continue
        col, fmt = hint.split(":", 1)
        col, fmt = col.strip(), fmt.strip()
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
                hinted_types[col] = "datetime64[ns]"
            except Exception:
                pass

    # Core inference
    cols = list(df.columns)
    types = infer_types(df, detect_datetimes=detect_datetimes)
    types.update(hinted_types)
    exclude_re = [re.compile(exclude_patterns)] if exclude_patterns else []
    cats = infer_categoricals(df, max_unique=max_unique, exclude_patterns=exclude_re)
    ranges = infer_numeric_ranges(df)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    numeric_cols = [c for c in numeric_cols if not any(p.search(c) for p in exclude_re)]

    # Build configs
    configs: Dict[str, str] = {}

    if "validation" in requested:
        data = build_validation_config(rel_path, cols, types, cats, ranges, fail_on_error=False)
        configs["validation"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "certification" in requested:
        data = build_validation_config(rel_path, cols, types, cats, ranges, fail_on_error=True)
        configs["certification"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "outliers" in requested:
        data = build_outlier_config(rel_path, numeric_cols)
        configs["outliers"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "diagnostics" in requested:
        data = build_diag_config(df, rel_path, types)
        configs["diagnostics"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "normalization" in requested:
        data = build_normalization_config(df, rel_path, cats, types, numeric_cols)
        configs["normalization"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "duplicates" in requested:
        data = build_dups_config(df, rel_path, exclude_re)
        configs["duplicates"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "handling" in requested:
        data = build_handling_config(rel_path, numeric_cols)
        configs["handling"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "imputation" in requested:
        data = build_imputation_config(df, rel_path)
        configs["imputation"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    if "final_audit" in requested:
        data = build_final_audit_config(df, rel_path, types, cats)
        configs["final_audit"] = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    # Write to disk if outdir provided
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        for module_name, yaml_str in configs.items():
            fname = f"{module_name}_config_autofill.yaml"
            fpath = os.path.join(outdir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(yaml_str)

        # Also write master run_toolkit_config.yaml
        master_cfg = build_master_config(
            modules_generated=list(configs.keys()),
            outdir_rel=outdir,
        )
        master_path = os.path.join(outdir, "run_toolkit_config.yaml")
        with open(master_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(master_cfg, f, sort_keys=False, allow_unicode=True)

    return configs

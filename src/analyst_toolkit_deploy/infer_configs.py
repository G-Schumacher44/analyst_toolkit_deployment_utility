from __future__ import annotations

import os
import re
import glob
from typing import Dict, Any, List

import pandas as pd
import yaml


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _write_yaml(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def _find_entry_csv(root: str) -> str:
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
        "Could not determine entry CSV. Set --input or pipeline_entry_path in config/run_toolkit_config.yaml or place exactly one CSV in data/raw/."
    )


def infer_types(df: pd.DataFrame, detect_datetimes: bool = True) -> Dict[str, str]:
    types: Dict[str, str] = {}
    for col in df.columns:
        s = df[col]
        dtype = str(s.dtype)
        if detect_datetimes and dtype == "object":
            sample = s.dropna().astype(str).head(500)
            if not sample.empty:
                parsed = pd.to_datetime(
                    sample, errors="coerce", infer_datetime_format=True
                )
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
    cats: Dict[str, list] = {}
    for col in df.columns:
        s = df[col]
        if exclude_patterns and any(p.search(col) for p in exclude_patterns):
            continue
        if s.dtype == "object" or str(s.dtype).startswith("category") or s.nunique(dropna=True) <= max_unique:
            vals = s.dropna().astype(str).value_counts().index.tolist()[: top_n]
            if vals:
                cats[col] = sorted(list(set(vals)))
    return cats


def infer_numeric_ranges(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    ranges: Dict[str, Dict[str, float]] = {}
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            s_clean = s.dropna()
            if s_clean.empty:
                continue
            ranges[col] = {"min": float(s_clean.min()), "max": float(s_clean.max())}
    return ranges


def build_validation_config(input_path_rel: str, cols, types, cats, ranges, fail_on_error: bool) -> Dict[str, Any]:
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
            "export": {"run": True, "export_dir": "exports/reports/outliers/detection/", "as_csv": False},
            "checkpoint": {"run": True, "checkpoint_path": "exports/joblib/{run_id}/{run_id}_m05_outliers_flagged.joblib"},
        },
    }


def infer_configs(
    root: str,
    input_path: str | None = None,
    outdir: str | None = None,
    sample_rows: int | None = None,
    max_unique: int = 30,
    exclude_patterns: str = "id|uuid|tag",
    detect_datetimes: bool = True,
    datetime_hints: List[str] | None = None,
) -> str:
    root = os.path.abspath(root)
    input_csv = input_path or _find_entry_csv(root)
    rel_path = os.path.relpath(input_csv, root)

    read_kwargs = dict(low_memory=False)
    if sample_rows:
        read_kwargs["nrows"] = sample_rows
    df = pd.read_csv(input_csv, **read_kwargs)
    # Apply hints
    datetime_hints = datetime_hints or []
    hinted_types = {}
    for hint in datetime_hints:
        if ":" not in hint:
            continue
        col, fmt = hint.split(":", 1)
        col = col.strip()
        fmt = fmt.strip()
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
                hinted_types[col] = "datetime64[ns]"
            except Exception:
                pass

    cols = list(df.columns)
    types = infer_types(df, detect_datetimes=detect_datetimes)
    types.update(hinted_types)
    exclude_re = [re.compile(exclude_patterns)] if exclude_patterns else []
    cats = infer_categoricals(df, max_unique=max_unique, exclude_patterns=exclude_re)
    ranges = infer_numeric_ranges(df)

    validation = build_validation_config(rel_path, cols, types, cats, ranges, fail_on_error=False)
    certification = build_validation_config(rel_path, cols, types, cats, ranges, fail_on_error=True)
    numeric_cols = [
        c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
    ]
    numeric_cols = [
        c for c in numeric_cols if not any(p.search(c) for p in exclude_re)
    ]
    outliers = build_outlier_config(rel_path, numeric_cols)

    out_dir = outdir or os.path.join(root, "config", "generated")
    os.makedirs(out_dir, exist_ok=True)
    _write_yaml(os.path.join(out_dir, "validation_config_autofill.yaml"), validation)
    _write_yaml(os.path.join(out_dir, "certification_config_autofill.yaml"), certification)
    _write_yaml(os.path.join(out_dir, "outlier_config_autofill.yaml"), outliers)
    return out_dir

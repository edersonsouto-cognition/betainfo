"""Data processing helpers for CSV and JSON files.

Provides convenience wrappers around pandas for reading/writing structured data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Write a DataFrame to a CSV file."""
    df.to_csv(path, index=False)


def load_json(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON array from a file."""
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array, got {type(data).__name__}")
    return data


def save_json(data: list[dict[str, Any]], path: str | Path) -> None:
    """Write a list of dicts to a JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def summarize_csv(path: str | Path) -> dict[str, Any]:
    """Return a quick summary (shape, columns, dtypes) of a CSV file."""
    df = load_csv(path)
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {col: str(dt) for col, dt in df.dtypes.items()},
    }


def filter_csv(
    path: str | Path,
    column: str,
    value: Any,
) -> pd.DataFrame:
    """Filter a CSV to rows where ``column == value``."""
    df = load_csv(path)
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in {list(df.columns)}")
    return df[df[column] == value]


def aggregate_csv(
    path: str | Path,
    group_by: str,
    agg_column: str,
    agg_func: str = "sum",
) -> pd.DataFrame:
    """Group a CSV by a column and aggregate another column."""
    df = load_csv(path)
    if group_by not in df.columns:
        raise KeyError(f"Column '{group_by}' not in {list(df.columns)}")
    if agg_column not in df.columns:
        raise KeyError(f"Column '{agg_column}' not in {list(df.columns)}")
    return df.groupby(group_by)[agg_column].agg(agg_func).reset_index()

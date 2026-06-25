"""Tests for the data_processor module."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.utils.data_processor import (
    aggregate_csv,
    filter_csv,
    load_csv,
    load_json,
    save_csv,
    save_json,
    summarize_csv,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SALES_CSV = DATA_DIR / "sales_data.csv"


class TestLoadCSV:
    def test_loads_sales_data(self) -> None:
        df = load_csv(SALES_CSV)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 24
        assert "product" in df.columns


class TestSaveCSV:
    def test_round_trip(self, tmp_path: Path) -> None:
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        path = tmp_path / "out.csv"
        save_csv(df, path)
        loaded = load_csv(path)
        assert list(loaded.columns) == ["a", "b"]
        assert len(loaded) == 2


class TestLoadJSON:
    def test_loads_sample_tasks(self) -> None:
        data = load_json(DATA_DIR / "sample_tasks.json")
        assert isinstance(data, list)
        assert len(data) == 6

    def test_rejects_non_array(self, tmp_path: Path) -> None:
        path = tmp_path / "obj.json"
        path.write_text('{"key": "value"}')
        with pytest.raises(ValueError, match="JSON array"):
            load_json(path)


class TestSaveJSON:
    def test_round_trip(self, tmp_path: Path) -> None:
        data = [{"x": 1}, {"x": 2}]
        path = tmp_path / "out.json"
        save_json(data, path)
        loaded = json.loads(path.read_text())
        assert loaded == data


class TestSummarizeCSV:
    def test_summary_shape(self) -> None:
        summary = summarize_csv(SALES_CSV)
        assert summary["rows"] == 24
        assert summary["columns"] == 7
        assert "product" in summary["column_names"]


class TestFilterCSV:
    def test_filter_by_region(self) -> None:
        df = filter_csv(SALES_CSV, "region", "North")
        assert len(df) > 0
        assert all(df["region"] == "North")

    def test_missing_column_raises(self) -> None:
        with pytest.raises(KeyError):
            filter_csv(SALES_CSV, "nonexistent", "val")


class TestAggregateCSV:
    def test_sum_by_region(self) -> None:
        df = aggregate_csv(SALES_CSV, "region", "quantity", "sum")
        assert "region" in df.columns
        assert "quantity" in df.columns
        assert len(df) == 4

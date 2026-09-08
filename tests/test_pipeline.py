"""Tests for the universal data processing pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from dpa.pipeline import (
    build_dataset_table,
    compute_statistics,
    extract_metadata,
    render_visualization,
    run_pipeline,
)
from tests.fixtures import write_csv


def test_extract_metadata_fields(tmp_path: Path):
    path = tmp_path / "P01_Condition_deviceA.csv"
    path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    meta = extract_metadata(path)
    assert meta["participant"] == "P01"
    assert meta["category"] == "Condition"
    assert meta["device"] == "deviceA"
    assert meta["rows"] == 2
    assert meta["file_size"] > 0


def test_build_dataset_table_and_statistics(tmp_path: Path):
    write_csv(tmp_path, "P01_A_dev1.csv", ["c1", "c2"], 3)
    write_csv(tmp_path, "P02_B_dev2.csv", ["c1"], 4)

    table = build_dataset_table(list(tmp_path.glob("*.csv")))
    assert len(table) == 2
    assert table["rows"].sum() == 7

    stats = compute_statistics(table)
    assert stats["total_files"] == 2
    assert stats["total_participants"] == 2
    assert stats["devices"] == 2


def test_run_pipeline_produces_report(tmp_path: Path):
    write_csv(tmp_path, "P01_A_dev1.csv", ["c1", "c2"], 3)

    out = tmp_path / "report.xlsx"
    result = run_pipeline(tmp_path, output=out, visualize=False)
    assert result["files"] == 1
    assert out.exists()
    assert isinstance(result["dataset"], pd.DataFrame)


def test_run_pipeline_missing_folder(tmp_path: Path):
    with pytest.raises(NotADirectoryError):
        run_pipeline(tmp_path / "nope", output="x.xlsx", visualize=False)


def test_render_visualization(tmp_path: Path):
    df = pd.DataFrame(
        {"device": ["d1", "d2", "d1"], "rows": [10, 20, 30]}
    )
    out = tmp_path / "summary.png"
    render_visualization(df, out)
    assert out.exists()
    assert out.stat().st_size > 0

"""Tests for the metadata generator."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd
import pytest

from dpa.metadata_generator import (
    detect_input_type,
    format_date,
    generate_metadata,
    list_files_from_folder,
    list_files_from_zip,
)


def test_list_files_from_folder_recursive(tmp_path: Path):
    (tmp_path / "d" / "e").mkdir(parents=True)
    (tmp_path / "d" / "a.csv").write_text("x\n1\n", encoding="utf-8")
    (tmp_path / "d" / "e" / "b.csv").write_text("y\n2\n", encoding="utf-8")

    files = list_files_from_folder(tmp_path / "d")
    assert sorted(files) == ["a.csv", "e/b.csv"]


def test_list_files_from_zip(tmp_path: Path):
    zip_path = tmp_path / "ds.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("a.csv", "x\n1\n")
        zf.writestr("folder/b.csv", "y\n2\n")

    files = list_files_from_zip(zip_path)
    assert sorted(files) == ["a.csv", "folder/b.csv"]


def test_detect_input_type_folder(tmp_path: Path):
    (tmp_path / "a.csv").write_text("x\n1\n", encoding="utf-8")
    assert detect_input_type(tmp_path) == ["a.csv"]


def test_detect_input_type_zip(tmp_path: Path):
    zip_path = tmp_path / "ds.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("a.csv", "x\n1\n")
    assert detect_input_type(zip_path) == ["a.csv"]


def test_detect_input_type_invalid(tmp_path: Path):
    with pytest.raises(ValueError):
        detect_input_type(tmp_path / "missing")


def test_format_date_multiple_formats():
    assert format_date("2024-03-01") == "01/03/2024"
    assert format_date("20240301") == "01/03/2024"
    assert format_date("01/03/2024") == "01/03/2024"
    assert format_date("not-a-date") == "not-a-date"


def test_generate_metadata_structure():
    df = generate_metadata(
        ["a.csv", "b.csv"],
        repository_url="https://repo",
        project_name="proj",
        source="src",
        generation_date="01/03/2024",
        volunteer_id="V1",
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]["url_filename"] == "https://repo/a.csv"
    assert df.iloc[0]["volunteer_id"] == "V1"

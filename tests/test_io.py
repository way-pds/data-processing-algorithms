"""Tests for the shared I/O helpers."""

from __future__ import annotations

from pathlib import Path

from dpa.core.io import count_csv_rows, find_csv_files, find_files, read_dataset


def test_find_csv_files_recursive(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "x.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (tmp_path / "b" / "y.csv").write_text("a,c\n3,4\n", encoding="utf-8")
    (tmp_path / "b" / "z.txt").write_text("ignored", encoding="utf-8")

    files = find_csv_files(tmp_path)
    assert len(files) == 2
    assert all(f.suffix == ".csv" for f in files)


def test_find_files_with_custom_extensions(tmp_path: Path):
    (tmp_path / "data.json").write_text("{}", encoding="utf-8")
    files = find_files(tmp_path, [".json"])
    assert len(files) == 1
    assert files[0].suffix == ".json"


def test_count_csv_rows_excludes_header(tmp_path: Path):
    path = tmp_path / "d.csv"
    path.write_text("c1,c2\n1,2\n3,4\n5,6\n", encoding="utf-8")
    assert count_csv_rows(path) == 3


def test_count_csv_rows_unreadable_returns_nan(tmp_path: Path):
    # Opening a directory (not a file) should fail and yield NaN.
    result = count_csv_rows(tmp_path)
    assert result != result  # NaN


def test_read_dataset_returns_none_on_error(tmp_path: Path):
    path = tmp_path / "broken.csv"
    path.write_bytes(b"\xff\xfe invalid \x00\x01")
    assert read_dataset(path) is None


def test_read_dataset_ok(tmp_path: Path):
    path = tmp_path / "ok.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    df = read_dataset(path)
    assert df is not None
    assert list(df.columns) == ["a", "b"]

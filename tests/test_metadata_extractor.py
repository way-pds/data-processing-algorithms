"""Tests for the dataset metadata extractor."""

from __future__ import annotations

from dpa.metadata_extractor import build_file_record, build_metadata_table, scan_dataset


def test_scan_dataset_finds_all_files(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.csv").write_text("x\n1\n", encoding="utf-8")
    (tmp_path / "sub" / "b.csv").write_text("y\n2\n", encoding="utf-8")
    (tmp_path / "sub" / "c.txt").write_text("z", encoding="utf-8")

    files = scan_dataset(tmp_path)
    names = {f.name for f in files}
    assert names == {"a.csv", "b.csv", "c.txt"}


def test_build_file_record_parses_filename(tmp_path):
    file = tmp_path / "P01_Condition_VivaSensing_Right.csv"
    file.write_text("a,b\n1,2\n", encoding="utf-8")
    rec = build_file_record(file)
    assert rec["participant"] == "P01"
    assert rec["category"] == "Condition"
    assert rec["device"] == "VivaSensing"
    assert rec["extension"] == ".csv"
    assert rec["file_size"] > 0
    assert rec["pattern_valid"] is True


def test_build_file_record_short_name(tmp_path):
    file = tmp_path / "plain.csv"
    file.write_text("a\n1\n", encoding="utf-8")
    rec = build_file_record(file)
    assert rec["participant"] == "plain"
    assert rec["device"] is None


def test_build_metadata_table(tmp_path):
    (tmp_path / "P01_C_Dev.csv").write_text("a\n1\n", encoding="utf-8")
    files = scan_dataset(tmp_path)
    df = build_metadata_table(files)
    assert "file_name" in df.columns
    assert len(df) == 1

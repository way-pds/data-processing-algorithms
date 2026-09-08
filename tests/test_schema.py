"""Tests for the schema validator."""

from __future__ import annotations

from dpa.schema import resolve_expected_columns, run_validation, validate_file

SCHEMAS = {
    "deviceA": {"type1": ["col1", "col2", "col3"]},
    "deviceB": ["sensor1", "sensor2"],
}


def test_resolve_expected_columns_nested():
    assert resolve_expected_columns(SCHEMAS, "deviceA", "type1") == ["col1", "col2", "col3"]
    assert resolve_expected_columns(SCHEMAS, "deviceA", "other") == ["col1", "col2", "col3"]


def test_resolve_expected_columns_flat():
    assert resolve_expected_columns(SCHEMAS, "deviceB", None) == ["sensor1", "sensor2"]


def test_resolve_expected_columns_unknown():
    assert resolve_expected_columns(SCHEMAS, "ghost", None) is None


def test_validate_file_missing_columns(tmp_path):
    # participant_category_deviceA
    path = tmp_path / "P01_Condition_deviceA.csv"
    path.write_text("col1,col2\n1,2\n", encoding="utf-8")
    result = validate_file(path, SCHEMAS)
    assert "error" not in result
    assert result["missing_columns"] == ["col3"]
    assert result["valid"] is False


def test_validate_file_complete(tmp_path):
    path = tmp_path / "P01_Condition_deviceA.csv"
    path.write_text("col1,col2,col3\n1,2,3\n", encoding="utf-8")
    result = validate_file(path, SCHEMAS)
    assert result["valid"] is True
    assert result["missing_columns"] == []


def test_validate_file_unknown_schema(tmp_path):
    path = tmp_path / "P01_Condition_ghost.csv"
    path.write_text("a\n1\n", encoding="utf-8")
    result = validate_file(path, SCHEMAS)
    assert result["error"] == "unknown_schema"


def test_run_validation_partitions_report_and_errors(tmp_path):
    (tmp_path / "P01_Condition_deviceA.csv").write_text("col1,col2\n1,2\n", encoding="utf-8")
    (tmp_path / "P01_Condition_ghost.csv").write_text("a\n1\n", encoding="utf-8")

    report, errors = run_validation(tmp_path, SCHEMAS)
    assert len(report) == 1
    assert len(errors) == 1
    assert errors.iloc[0]["error"] == "unknown_schema"

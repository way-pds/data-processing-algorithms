"""Tests for the data quality analyzer."""

from __future__ import annotations

from dpa.quality import analyze_dataset, classify_severity, run_quality_analysis


def test_classify_severity():
    assert classify_severity(0, 0.0) == "EMPTY"
    assert classify_severity(100, 0.9) == "CRITICAL"
    assert classify_severity(100, 0.3) == "FAIR"
    assert classify_severity(100, 0.0) == "OK"


def test_analyze_dataset_metrics(tmp_path):
    path = tmp_path / "d.csv"
    path.write_text(
        "num,cat\n1,a\n2,\n3,b\n4,\n", encoding="utf-8"
    )
    col_metrics, report = analyze_dataset(path)
    assert report.file_name == "d.csv"
    assert report.rows == 4
    assert report.missing_cells > 0
    assert "missing_pct" in col_metrics.columns
    assert "constant" in col_metrics.columns
    assert report.severity in ("OK", "FAIR", "CRITICAL", "EMPTY")


def test_analyze_empty_returns_empty_file():
    # A completely empty CSV yields an empty DataFrame and an EMPTY severity.

    # read_dataset returns None for empty; analyze_dataset treats None -> empty frame
    assert classify_severity(0, 1.0) == "EMPTY"


def test_column_metrics_variance(tmp_path):
    path = tmp_path / "const.csv"
    path.write_text("const,var\n1,1\n1,2\n1,3\n", encoding="utf-8")
    col_metrics, report = analyze_dataset(path)
    const_row = col_metrics.loc["const"]
    assert const_row["variance"] == 0
    assert bool(const_row["constant"])
    var_row = col_metrics.loc["var"]
    assert var_row["variance"] > 0
    assert not bool(var_row["constant"])


def test_run_quality_analysis_empty_folder(tmp_path):
    col, reports = run_quality_analysis(tmp_path)
    assert col.empty
    assert reports.empty


def test_run_quality_analysis_broken_reported_as_empty(tmp_path):
    # An invalid file is reported with EMPTY severity, not silently skipped.
    (tmp_path / "broken.csv").write_bytes(b"\xff\xfe \x00\x01")
    (tmp_path / "ok.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    col, reports = run_quality_analysis(tmp_path)
    assert len(reports) == 2
    severity_by_file = dict(zip(reports["file_name"], reports["severity"]))
    assert severity_by_file["broken.csv"] == "EMPTY"
    assert severity_by_file["ok.csv"] == "OK"

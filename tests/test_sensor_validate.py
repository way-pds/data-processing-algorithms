"""Tests for the sensor dataset validator."""

from __future__ import annotations

import pandas as pd

from dpa.sensor_validate import (
    analyze_dataset,
    detect_signal_breaks,
    normalize_device,
    validate_file_quantity,
    validate_line_counts,
)
from tests.fixtures import write_sensor_csv

EXPECTED_FILES = {"accelerometer": 1, "bia": 2, "ecg": 2, "ppg": 1}
EXPECTED_LINES = {"accelerometer": 100, "bia": 20, "ecg": 40, "ppg": 50}


def test_normalize_device():
    assert normalize_device("bia1") == "bia"
    assert normalize_device("bia2") == "bia"
    assert normalize_device("ecg2") == "ecg"
    assert normalize_device("accelerometer") == "accelerometer"
    assert normalize_device("") == ""


def test_validate_file_quantity_with_multi_index(tmp_path):
    # bia1 and bia2 should both count toward the single "bia" bucket.
    write_sensor_csv(tmp_path, "bia1.csv", "time", 5, 100)
    write_sensor_csv(tmp_path, "bia2.csv", "time", 5, 100)
    write_sensor_csv(tmp_path, "accelerometer.csv", "time", 5, 100)

    meta = pd.DataFrame(
        {
            "normalized_device": ["bia", "bia", "accelerometer"],
            "device": ["bia1", "bia2", "accelerometer"],
            "line_count": [5, 5, 5],
        }
    )
    quantity = validate_file_quantity(meta, EXPECTED_FILES)
    assert quantity["bia"] is True
    assert quantity["accelerometer"] is True
    assert quantity["ecg"] is False


def test_validate_line_counts_uses_min(tmp_path):
    # bia1 meets min, bia2 falls short -> overall False (uses min).
    meta = pd.DataFrame(
        {
            "device": ["bia1", "bia2"],
            "line_count": [30, 10],
        }
    )
    result = validate_line_counts(meta, {"bia": 20})
    assert result["bia"] is False

    meta2 = pd.DataFrame({"device": ["bia1", "bia2"], "line_count": [30, 25]})
    result2 = validate_line_counts(meta2, {"bia": 20})
    assert result2["bia"] is True


def test_analyze_dataset_integration(tmp_path):
    write_sensor_csv(tmp_path, "accelerometer.csv", "time", 200, 1)
    write_sensor_csv(tmp_path, "bia1.csv", "time", 30, 1)
    write_sensor_csv(tmp_path, "bia2.csv", "time", 30, 1)

    results = analyze_dataset(tmp_path, EXPECTED_FILES, EXPECTED_LINES)
    assert results.file_validation["bia"] is True
    assert results.file_validation["accelerometer"] is True
    assert results.line_validation["bia"] is True
    assert isinstance(results.metadata, pd.DataFrame)


def test_detect_signal_breaks(tmp_path):
    path = tmp_path / "signal.csv"
    # 10 samples every 100ms, then a big gap of ~5 seconds.
    path.write_text(
        "time\n"
        "2024-01-01 00:00:00.000\n"
        "2024-01-01 00:00:00.100\n"
        "2024-01-01 00:00:00.200\n"
        "2024-01-01 00:00:05.000\n",
        encoding="utf-8",
    )
    df = pd.read_csv(path)
    breaks = detect_signal_breaks(df, "time", max_gap_seconds=0.1)
    assert len(breaks) == 1


def test_detect_signal_breaks_missing_column():
    df = pd.DataFrame({"x": [1, 2, 3]})
    assert detect_signal_breaks(df, "time", max_gap_seconds=0.1).empty

"""Tests for the sampling frequency analyzer."""

from __future__ import annotations

import numpy as np
import pandas as pd

from dpa.frequency import (
    calculate_sampling_frequency,
    extract_device_type,
    extract_file_type,
)


def test_calculate_sampling_frequency_known_rate():
    # 1000 samples at 10 ms => 100 Hz
    start = 1_600_000_000_000
    timestamps = [start + i * 10 for i in range(1000)]
    df = pd.DataFrame({"Timestamp": timestamps})
    mean, std = calculate_sampling_frequency(df, "Timestamp", "ms")
    assert mean is not None
    assert np.isclose(mean, 100.0, atol=1e-6)
    assert std is not None and std < 1e-6


def test_calculate_sampling_frequency_missing_column():
    df = pd.DataFrame({"other": [1, 2, 3]})
    mean, std = calculate_sampling_frequency(df, "Timestamp", "ms")
    assert mean is None and std is None


def test_calculate_sampling_frequency_unit_none_parses_dates():
    # String-formatted timestamps with unit=None should be parsed as datetimes.
    df = pd.DataFrame(
        {
            "time": [
                "2024-01-01 00:00:00",
                "2024-01-01 00:00:01",
                "2024-01-01 00:00:02",
            ]
        }
    )
    mean, std = calculate_sampling_frequency(df, "time", None)
    assert mean is not None
    assert np.isclose(mean, 1.0, atol=1e-6)


def test_extract_device_type():
    assert extract_device_type(__import__("pathlib").Path("P01_C_VivaSensing-Acc.csv")) == "VivaSensing"
    assert extract_device_type(__import__("pathlib").Path("short.csv")) is None


def test_extract_file_type():
    assert extract_file_type(__import__("pathlib").Path("P01_C_VivaSensing-Acc.csv")) == "Acc"
    assert extract_file_type(__import__("pathlib").Path("P01_C_VivaSensing.csv")) == "Acc"

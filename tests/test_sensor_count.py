"""Tests for the sensor data counter."""

from __future__ import annotations

from dpa.sensor_count import analyze_sensor_data, count_valid_data
from tests.fixtures import write_csv


def test_count_valid_data():

    import pandas as pd

    df = pd.DataFrame({"Acc_X": [1, 2, None], "Acc_Y": [1, None, None]})
    counts = count_valid_data(df, ["Acc_X", "Acc_Y"])
    assert counts == {"Acc_X": 2, "Acc_Y": 1}


def test_count_valid_data_missing_column():
    from pandas import DataFrame

    df = DataFrame({"other": [1, 2]})
    assert count_valid_data(df, ["Acc_X"]) == {}


def test_analyze_sensor_data(tmp_path):
    write_csv(tmp_path, "p.csv", ["Acc_X", "Acc_Y", "Acc_Z"], 5)
    result = analyze_sensor_data(tmp_path)
    assert len(result) == 1
    assert result.iloc[0]["Acc_X"] == 5
    assert result.iloc[0]["Acc_Y"] == 5

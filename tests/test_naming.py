"""Tests for filename metadata parsing."""

from __future__ import annotations

from pathlib import Path

from dpa.core.naming import FileNameInfo, parse_filename


def test_full_pattern():
    info = parse_filename("P01_Condition_VivaSensing_Right_Dom_20240301.csv")
    assert info.participant == "P01"
    assert info.category == "Condition"
    assert info.device == "VivaSensing"
    assert info.extra_1 == "Right"
    assert info.extra_2 == "Dom"
    assert info.date == "20240301"
    assert info.pattern_valid is True


def test_short_name_degrades_gracefully():
    info = parse_filename("just_a_name.csv")
    assert info.participant == "just"
    assert info.category == "a"
    assert info.device == "name"
    assert info.extra_1 is None
    assert info.pattern_valid is True


def test_single_token():
    info = parse_filename("onlyone.csv")
    assert info.participant == "onlyone"
    assert info.device is None
    assert info.pattern_valid is False


def test_accepts_pathlike():
    info = parse_filename(Path("dir") / "p1_cat_dev.csv")
    assert info.participant == "p1"


def test_dataclass_defaults():
    info = FileNameInfo()
    assert info.pattern_valid is False

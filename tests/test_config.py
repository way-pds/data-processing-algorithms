"""Tests for configuration loading."""

from __future__ import annotations

from pathlib import Path

from dpa.core.config import DEFAULT_CONFIG, load_config


def test_defaults_loaded_when_no_path():
    cfg = load_config(None)
    assert "devices" in cfg
    assert "schemas" in cfg
    assert cfg["devices"]["VivaSensing"]["timestamp"] == "Timestamp"


def test_missing_file_falls_back_to_defaults(tmp_path: Path):
    cfg = load_config(tmp_path / "nope.yaml")
    assert cfg == DEFAULT_CONFIG


def test_partial_override_merges(tmp_path: Path):
    cfg_path = tmp_path / "custom.yaml"
    cfg_path.write_text(
        '---\ndevices:\n  VivaSensing:\n    timestamp: "TSX"\n', encoding="utf-8"
    )
    cfg = load_config(cfg_path)
    # Overridden value
    assert cfg["devices"]["VivaSensing"]["timestamp"] == "TSX"
    # Untouched sibling preserved
    assert cfg["devices"]["COLA"]["timestamp"] == "Timestamp_Sensor(us)"
    # Untouched top-level section preserved
    assert "sensor_columns" in cfg


def test_defaults_not_mutated_after_load():
    cfg = load_config(None)
    cfg["devices"]["TANITA"]["unit"] = "changed"
    assert DEFAULT_CONFIG["devices"]["TANITA"]["unit"] is None

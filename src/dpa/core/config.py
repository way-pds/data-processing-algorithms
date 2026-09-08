"""Configuration loading utilities.

Device, sensor, and schema definitions are kept external (YAML) rather than
hardcoded so the tools can be reused across projects without code changes.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Fallback configuration tree used when no external file is provided.
DEFAULT_CONFIG: dict[str, Any] = {
    "devices": {
        "VivaSensing": {"timestamp": "Timestamp", "unit": "ms"},
        "COLA": {"timestamp": "Timestamp_Sensor(us)", "unit": "us"},
        "BIA": {"timestamp": "TimeStamp", "unit": "ms"},
        "TANITA": {"timestamp": "time", "unit": None},
        "psgSleepStaging": {"timestamp": "Timestamp_ms", "unit": "ms"},
    },
    "sensor_columns": {
        "accelerometer": ["Acc_X", "Acc_Y", "Acc_Z"],
        "gyroscope": ["Gyr_X", "Gyr_Y", "Gyr_Z"],
        "magnetometer": ["Mag_X", "Mag_Y", "Mag_Z"],
        "heart_rate": ["HR"],
    },
    "expected_files": {
        "accelerometer": 1,
        "ppg": 1,
        "bia": 2,
        "ecg": 2,
    },
    "expected_lines": {
        "accelerometer": 42000,
        "bia": 150,
        "ecg": 1500,
        "ppg": 85000,
    },
    "schemas": {
        "deviceA": {"type1": ["col1", "col2", "col3"]},
        "deviceB": {"type2": ["sensor1", "sensor2"]},
        "deviceC": {"type3": ["value", "timestamp"]},
    },
}


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from a YAML file, falling back to defaults.

    The external file, when provided, is merged over the defaults so that a
    partial configuration only overrides the keys it defines.

    Args:
        path: Optional path to a YAML configuration file.

    Returns:
        A dictionary with the merged configuration.
    """
    cfg = _deep_copy(DEFAULT_CONFIG)

    if path is None:
        return cfg

    config_path = Path(path)
    if not config_path.is_file():
        logger.warning("Config file not found (%s); using defaults.", config_path)
        return cfg

    with config_path.open("r", encoding="utf-8") as fh:
        loaded = yaml.safe_load(fh) or {}

    if not isinstance(loaded, Mapping):
        logger.warning("Config file must contain a mapping; using defaults.")
        return cfg

    _deep_merge(cfg, dict(loaded))
    return cfg


def _deep_copy(value: Any) -> Any:
    """Recursively copy a nested structure of dict/list/scalars."""
    if isinstance(value, dict):
        return {k: _deep_copy(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy(v) for v in value]
    return value


def _deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> None:
    """Recursively merge *override* into *base* (mutating base)."""
    for key, value in override.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, Mapping)
        ):
            _deep_merge(base[key], dict(value))
        else:
            base[key] = _deep_copy(value)

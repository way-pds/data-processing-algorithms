"""Generate a small synthetic dataset to demonstrate every dpa tool.

Run from the repository root:

    python examples/generate_demo_data.py          # writes into examples/data
    python examples/demo.py                        # runs every tool on the demo data
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def _make_device_dir(base: Path, name: str) -> Path:
    path = base / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_sensor_csv(path: Path, timestamps: np.ndarray, value_name: str) -> None:
    df = pd.DataFrame({value_name: np.round(np.sin(np.arange(len(timestamps)) / 10), 4)})
    df.insert(0, "time_ms", timestamps.astype(int))
    df.to_csv(path, index=False)


def _samples(fs_hz: float, seconds: float) -> np.ndarray:
    """Return a monotonically increasing millisecond timestamp vector."""
    n = int(fs_hz * seconds)
    ms = np.round(1000.0 / fs_hz)
    return 1_600_000_000_000 + np.arange(n) * ms


def generate(base: str | Path = "examples/data") -> None:
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)

    # --- Sampling frequency analyzer: two devices with a known rate ---
    viva = _make_device_dir(base, "project_alpha")
    _write_sensor_csv(viva / "P01_Condition_VivaSensing-Acc.csv", _samples(100, 5), "acc")
    _write_sensor_csv(viva / "P02_Condition_VivaSensing-Acc.csv", _samples(100, 5), "acc")

    # --- Sensor validator: expected sensor set for one participant ---
    sensor_dir = _make_device_dir(base, "sensors")
    _write_sensor_csv(sensor_dir / "subject_01" / "accelerometer.csv", _samples(100, 2), "acc")
    _write_sensor_csv(sensor_dir / "subject_01" / "bia1.csv", _samples(20, 2), "bia")
    _write_sensor_csv(sensor_dir / "subject_01" / "bia2.csv", _samples(20, 2), "bia")
    _write_sensor_csv(sensor_dir / "subject_01" / "ecg1.csv", _samples(500, 3), "ecg")
    _write_sensor_csv(sensor_dir / "subject_01" / "ecg2.csv", _samples(500, 3), "ecg")

    # --- Schema validator: files with an expected set of columns ---
    schema_dir = _make_device_dir(base, "schemas")
    pd.DataFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
            # note: col3 intentionally missing to demonstrate a schema violation
        }
    ).to_csv(schema_dir / "deviceA.csv", index=False)
    pd.DataFrame({"sensor1": [1, 2], "sensor2": [3, 4]}).to_csv(
        schema_dir / "deviceB.csv", index=False
    )

    # --- Quality analyzer: a healthy and a degraded dataset ---
    quality_dir = _make_device_dir(base, "quality")
    pd.DataFrame(
        {
            "id": range(50),
            "value": np.random.default_rng(7).normal(size=50),
            "label": ["ok"] * 50,
        }
    ).to_csv(quality_dir / "good.csv", index=False)
    pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "value": [None] * 5,  # entirely null column -> constant
        }
    ).to_csv(quality_dir / "bad.csv", index=False)

    logging.info("Demo data written to %s", base.resolve())


if __name__ == "__main__":
    generate()

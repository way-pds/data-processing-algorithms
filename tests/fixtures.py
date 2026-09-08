"""Reusable test helpers for building synthetic datasets in temporary folders."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd


def write_csv(directory: Path, name: str, columns: Sequence[str], rows: int) -> Path:
    """Write a simple CSV with the given columns and number of rows."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    df = pd.DataFrame(
        {col: list(range(rows)) for col in columns},
        index=pd.RangeIndex(rows).rename("id"),
    )
    df.to_csv(path, index=False)
    return path


def write_sensor_csv(directory: Path, name: str, column: str, n_rows: int, step_ms: int) -> Path:
    """Write a sensor CSV with a millisecond timestamp column."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    start = 1_600_000_000_000  # ms epoch
    timestamps = [start + (i * step_ms) for i in range(n_rows)]
    df = pd.DataFrame({column: timestamps, "value": list(range(n_rows))})
    df.to_csv(path, index=False)
    return path

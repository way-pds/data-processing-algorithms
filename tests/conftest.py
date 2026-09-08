"""Pytest fixtures shared across the test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures import write_csv, write_sensor_csv


@pytest.fixture
def make_csv(tmp_path: Path):
    """Factory that writes a CSV into an isolated temp folder and returns its path."""

    def _make(name: str, columns: list[str], rows: int) -> Path:
        return write_csv(tmp_path, name, columns, rows)

    return _make


@pytest.fixture
def make_sensor_csv(tmp_path: Path):
    """Factory that writes a timestamped sensor CSV."""

    def _make(name: str, column: str, n_rows: int, step_ms: int) -> Path:
        return write_sensor_csv(tmp_path, name, column, n_rows, step_ms)

    return _make

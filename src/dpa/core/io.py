"""File discovery and dataset reading helpers shared across modules."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: tuple[str, ...] = (".csv", ".txt")


def find_files(
    folder: str | Path,
    extensions: Sequence[str] | None = None,
) -> list[Path]:
    """Recursively find files with the given extensions.

    Args:
        folder: Root folder to scan recursively.
        extensions: Tuple/list of extensions (e.g. ``(".csv",)``). Defaults to
            the package-wide supported extensions.

    Returns:
        Sorted list of matching file paths.
    """
    base = Path(folder)
    exts: Sequence[str] = extensions or SUPPORTED_EXTENSIONS
    found: list[Path] = []
    for ext in exts:
        found.extend(base.rglob(f"*{ext}"))
    return sorted(found)


def find_csv_files(folder: str | Path) -> list[Path]:
    """Recursively find all ``.csv`` files under *folder*."""
    return find_files(folder, [".csv"])


def read_dataset(file: str | Path) -> pd.DataFrame | None:
    """Read a CSV file into a DataFrame, returning ``None`` on failure.

    Errors are logged instead of raised so batch processing over many files
    can continue past a single broken file.
    """
    try:
        return pd.read_csv(file, low_memory=False)
    except Exception as exc:  # noqa: BLE001 - batch tools tolerate single-file failures
        logger.warning("Could not read %s: %s", file, exc)
        return None


def count_csv_rows(file: str | Path) -> int | float:
    """Count data rows in a CSV file efficiently (header excluded).

    Returns ``float("nan")`` when the file cannot be read, mirroring the
    prior behavior of the validation pipeline.
    """
    path = Path(file)
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
            total = sum(1 for _ in fh)
        return max(total - 1, 0)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not count rows in %s: %s", path, exc)
        return float("nan")

"""Sampling Frequency Analyzer.

Scans sensor datasets, identifies device types, and computes mean and standard
deviation of the sampling frequency for each device.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, cast

import pandas as pd

from dpa.core.config import load_config
from dpa.core.io import find_csv_files, read_dataset

logger = logging.getLogger(__name__)


def extract_device_type(file: Path) -> str | None:
    """Extract the device type token from a file name.

    The device token is the third underscore-separated field, optionally
    suffixed with a ``-<file_type>`` qualifier (e.g. ``VivaSensing-Acc``).
    """
    parts = file.stem.split("_")
    if len(parts) < 3:
        return None
    return parts[2].split("-")[0]


def extract_file_type(file: Path) -> str:
    """Extract the file-type qualifier from the device token, defaulting to ``Acc``."""
    parts = file.stem.split("_")
    if len(parts) < 3:
        return "Acc"
    device_info = parts[2].split("-")
    return device_info[1] if len(device_info) > 1 else "Acc"


def extract_metadata(file: Path) -> dict[str, object]:
    """Extract project, device type, and file type from a file path/name."""
    project: str | None
    try:
        project = file.parents[1].name if len(file.parents) > 1 else None
    except IndexError:
        project = None

    return {
        "file": file,
        "file_name": file.name,
        "project": project,
        "device_type": extract_device_type(file),
        "file_type": extract_file_type(file),
    }


def calculate_sampling_frequency(
    df: pd.DataFrame,
    timestamp_column: str,
    unit: Literal["D", "s", "ms", "us", "ns"] | None,
) -> tuple[float | None, float | None]:
    """Compute mean/std of the sampling frequency for a device DataFrame.

    The frequency is the reciprocal of the timestamp delta. Returns
    ``(mean, std)`` of the empirical sampling frequency, or ``(None, None)``
    when the timestamp column is missing or no valid delta exists.

    Args:
        df: The sensor DataFrame.
        timestamp_column: Name of the timestamp column.
        unit: Pandas timestamp unit (``"s"``, ``"ms"``, ``"us"`` ...) or
            ``None`` to attempt automatic (formatted-string) parsing.
    """
    if timestamp_column not in df.columns:
        return None, None

    try:
        if unit:
            time = pd.to_datetime(df[timestamp_column], unit=unit)
        else:
            time = pd.to_datetime(df[timestamp_column], errors="coerce")
    except (ValueError, TypeError) as exc:
        logger.warning("Could not parse timestamps in column %r: %s", timestamp_column, exc)
        return None, None

    diff = time.diff().dt.total_seconds()

    positive = diff[diff > 0]
    if positive.empty:
        return None, None

    freq = 1.0 / positive
    return float(freq.mean()), float(freq.std())


def analyze_dataset(
    folder: str | Path,
    device_config: dict[str, dict[str, object]] | None = None,
) -> pd.DataFrame:
    """Analyze all recognized device CSV files under *folder*.

    Returns a DataFrame with one row per file and computed frequency metrics.
    """
    cfg = device_config or load_config().get("devices", {})
    files = find_csv_files(folder)

    records: list[dict[str, object]] = []
    for file in files:
        meta = extract_metadata(file)
        device = extract_device_type(file)

        if device is None or device not in cfg:
            continue

        dev_cfg = cfg[device]
        df = read_dataset(file)
        if df is None:
            meta["frequency_mean"] = None
            meta["frequency_std"] = None
            records.append(meta)
            continue

        unit_value = dev_cfg.get("unit")
        unit_arg = (
            cast(Literal["D", "s", "ms", "us", "ns"], unit_value) if unit_value else None
        )

        mean, std = calculate_sampling_frequency(
            df,
            str(dev_cfg.get("timestamp", "")),
            unit_arg,
        )
        meta["frequency_mean"] = mean
        meta["frequency_std"] = std
        records.append(meta)

    return pd.DataFrame(records)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze sensor sampling frequency.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-c", "--config", default=None, help="Optional YAML configuration file.")
    parser.add_argument("-o", "--output", default="frequency_report.xlsx", help="Output report path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def _summarize(result: pd.DataFrame) -> str:
    """Format a compact grouped summary of the frequency analysis."""
    summary: list[str] = []
    if result.empty:
        return "No recognized device files found."

    grouped = result.groupby(["device_type", "file_type"])
    for (device, ftype), group in grouped:
        means = group["frequency_mean"].dropna()
        if means.empty:
            summary.append(f"{device}/{ftype}: 0 files with measurable frequency")
            continue
        summary.append(
            f"{device}/{ftype}: {len(group)} file(s), "
            f"mean={means.mean():.2f} Hz, std={means.std():.2f} Hz"
        )
    return "\n".join(summary)


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )

    cfg = load_config(args.config)
    result = analyze_dataset(args.folder, cfg.get("devices", {}))

    print("\n".join(_summarize(result).split("\n")))
    print()

    if not result.empty:
        result.to_excel(args.output, index=False)
        print(f"Frequency report saved to: {args.output}")


if __name__ == "__main__":
    main()

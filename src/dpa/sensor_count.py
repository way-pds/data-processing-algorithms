"""Sensor Data Counter.

Scans CSV datasets and counts the number of valid (non-null) observations per
sensor column, producing a summary of data completeness by sensor type.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Mapping, Sequence
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from dpa.core.config import load_config
from dpa.core.io import find_csv_files, read_dataset

logger = logging.getLogger(__name__)


def count_valid_data(df: pd.DataFrame, columns: Sequence[str]) -> dict[str, int]:
    """Count non-null values for each requested column present in *df*."""
    return {col: int(df[col].notna().sum()) for col in columns if col in df.columns}


def analyze_sensor_data(
    folder: str | Path,
    sensor_columns: Mapping[str, Sequence[str]] | None = None,
) -> pd.DataFrame:
    """Count valid observations per sensor column across all CSV files.

    Args:
        folder: Dataset folder to scan.
        sensor_columns: Mapping of ``sensor_name -> [columns]``. Defaults to
            the package configuration.

    Returns:
        A DataFrame with one row per file and one column per sensor field.
    """
    cfg = sensor_columns or load_config().get("sensor_columns", {})
    files = find_csv_files(folder)
    results: list[dict[str, object]] = []

    for file in tqdm(files, desc="Counting sensor data", unit="file"):
        df = read_dataset(file)
        row: dict[str, object] = {"file": file.name}
        if df is not None:
            for columns in cfg.values():
                counts = count_valid_data(df, columns)
                for col, value in counts.items():
                    row[col] = value
        results.append(row)

    return pd.DataFrame(results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Count valid sensor data points in CSV datasets.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-c", "--config", default=None, help="Optional YAML configuration file.")
    parser.add_argument("-o", "--output", default="sensor_data_count.xlsx", help="Output report path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )

    cfg = load_config(args.config)
    dataset = analyze_sensor_data(args.folder, cfg.get("sensor_columns", {}))

    numeric_cols = [c for c in dataset.columns if c != "file"]
    print("\nSummary of available data:\n")
    if numeric_cols:
        totals = dataset[numeric_cols].sum(numeric_only=True)
        for col in numeric_cols:
            print(f"  {col}: {int(totals[col])} valid points")
    else:
        print("  No sensor columns found.")

    if not dataset.empty:
        dataset.to_excel(args.output, index=False)
        print(f"\nSensor data count saved to: {args.output}")


if __name__ == "__main__":
    main()

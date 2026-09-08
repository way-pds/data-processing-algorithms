"""Dataset Quality Analyzer.

Runs automated data-quality checks on CSV datasets and produces an Excel/CSV
report with per-column metrics and dataset-level diagnostics.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from dpa.core.io import find_csv_files, read_dataset

logger = logging.getLogger(__name__)


@dataclass
class DatasetReport:
    """Container for the per-file quality analysis results."""

    file_name: str
    rows: int
    columns: int
    missing_cells: int
    total_cells: int
    duplicate_rows: int
    empty_columns: int
    numeric_columns: int
    constant_columns: int
    severity: str


def classify_severity(rows: int, missing_ratio: float) -> str:
    """Classify a dataset into a quality category/severity label.

    Args:
        rows: Number of data rows.
        missing_ratio: Fraction of missing cells (0..1).

    Returns:
        One of ``EMPTY``, ``CRITICAL``, ``FAIR``, or ``OK``.
    """
    if rows == 0:
        return "EMPTY"
    if missing_ratio > 0.5:
        return "CRITICAL"
    if missing_ratio > 0.2:
        return "FAIR"
    return "OK"


def column_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-column quality metrics for a DataFrame."""
    metrics = pd.DataFrame(
        {
            "missing_values": df.isnull().sum(),
            "missing_pct": df.isnull().mean() * 100,
            "unique_values": df.nunique(),
            "dtype": df.dtypes.astype(str),
        }
    )
    numeric = df.select_dtypes(include=[np.number])
    if not numeric.empty:
        metrics["variance"] = numeric.var()
        metrics["mean"] = numeric.mean()
        metrics["min"] = numeric.min()
        metrics["max"] = numeric.max()

    # Detect constant (zero-variance / zero-unique) numeric columns.
    metrics["constant"] = metrics.get("variance", pd.Series(dtype=float)).fillna(0) == 0
    return metrics


def analyze_dataset(file: Path) -> tuple[pd.DataFrame, DatasetReport]:
    """Analyze a single CSV file, returning (column_metrics, dataset_report)."""
    df = read_dataset(file)
    if df is None:
        df = pd.DataFrame()

    row_count = len(df)
    total_cells = int(df.size)
    missing_cells = int(df.isnull().sum().sum()) if not df.empty else 0
    missing_ratio = missing_cells / total_cells if total_cells else 1.0
    duplicate_rows = int(df.duplicated().sum()) if not df.empty else 0

    col_metrics = column_metrics(df)
    if not col_metrics.empty:
        col_metrics["file_name"] = file.name

    severity = classify_severity(row_count, missing_ratio)

    report = DatasetReport(
        file_name=file.name,
        rows=row_count,
        columns=df.shape[1] if not df.empty else 0,
        missing_cells=missing_cells,
        total_cells=total_cells,
        duplicate_rows=duplicate_rows,
        empty_columns=int((col_metrics["missing_values"] == row_count).sum()) if row_count else df.shape[1],
        numeric_columns=int(df.select_dtypes(include=[np.number]).shape[1]) if not df.empty else 0,
        constant_columns=int(col_metrics["constant"].sum()) if not col_metrics.empty else 0,
        severity=severity,
    )
    return col_metrics, report


def run_quality_analysis(folder: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Analyze every CSV under *folder*.

    Returns a tuple ``(column_metrics, dataset_reports)`` of DataFrames. Files
    that cannot be read are skipped (and logged) rather than aborting the run.
    """
    files = find_csv_files(folder)

    column_frames: list[pd.DataFrame] = []
    report_rows: list[dict[str, object]] = []

    for file in tqdm(files, desc="Analyzing datasets", unit="file"):
        try:
            col_metrics, report = analyze_dataset(file)
        except Exception as exc:  # noqa: BLE001 - continue past broken files
            logger.warning("Skipping %s: %s", file, exc)
            continue

        if not col_metrics.empty:
            column_frames.append(col_metrics)
        report_rows.append(vars(report))

    column_metrics = pd.concat(column_frames, ignore_index=True) if column_frames else pd.DataFrame()
    dataset_reports = pd.DataFrame(report_rows)
    return column_metrics, dataset_reports


def export_report(
    column_metrics: pd.DataFrame,
    dataset_reports: pd.DataFrame,
    output: str | Path = "data_quality_report.xlsx",
) -> None:
    """Export both tables to an Excel workbook (or CSV if extension matches)."""
    out = Path(output)
    if out.suffix.lower() in (".csv", ".txt"):
        dataset_reports.to_csv(out, index=False, sep=";")
        logger.info("Quality report saved to %s", out)
        return

    if out.suffix.lower() not in (".xlsx", ".xls"):
        out = out.with_suffix(".xlsx")

    with pd.ExcelWriter(out) as writer:
        dataset_reports.to_excel(writer, sheet_name="datasets", index=False)
        column_metrics.to_excel(writer, sheet_name="column_metrics", index=False)
    logger.info("Quality report saved to %s", out)
    print(f"Quality report saved to: {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze data quality of CSV datasets.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-o", "--output", default="data_quality_report.xlsx", help="Output report path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )

    column_metrics, dataset_reports = run_quality_analysis(args.folder)

    if not dataset_reports.empty:
        summary = (
            dataset_reports["severity"]
            .value_counts()
            .reindex(["OK", "FAIR", "CRITICAL", "EMPTY"], fill_value=0)
        )
        print("\nQuality summary:")
        print(f"  Files analyzed : {len(dataset_reports)}")
        print(f"  OK             : {int(summary.get('OK', 0))}")
        print(f"  FAIR           : {int(summary.get('FAIR', 0))}")
        print(f"  CRITICAL       : {int(summary.get('CRITICAL', 0))}")
        print(f"  EMPTY          : {int(summary.get('EMPTY', 0))}")

    export_report(column_metrics, dataset_reports, args.output)


if __name__ == "__main__":
    main()

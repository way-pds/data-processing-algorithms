"""Universal Data Processing Pipeline.

Scans directories of dataset files, extracts metadata, computes statistics,
generates an Excel report, and optionally renders summary visualizations.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless rendering

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from dpa.core.io import count_csv_rows, find_csv_files  # noqa: E402
from dpa.core.naming import FileNameInfo, parse_filename  # noqa: E402

logger = logging.getLogger(__name__)


def extract_metadata(file: Path) -> dict[str, object]:
    """Extract metadata (participant, device, size, rows) from a file path."""
    info: FileNameInfo = parse_filename(file)
    try:
        size = file.stat().st_size
    except OSError as exc:  # pragma: no cover - defensive
        logger.warning("Could not stat %s: %s", file, exc)
        size = -1

    return {
        "filename": file.name,
        "file_path": str(file),
        "file_size": size,
        "participant": info.participant,
        "category": info.category,
        "device": info.device,
        "extra_1": info.extra_1,
        "extra_2": info.extra_2,
        "date": info.date,
        "pattern_valid": info.pattern_valid,
        "rows": count_csv_rows(file),
    }


def build_dataset_table(files: Sequence[Path]) -> pd.DataFrame:
    """Build the dataset metadata/statistics table for a list of files."""
    return pd.DataFrame([extract_metadata(f) for f in files])


def compute_statistics(df: pd.DataFrame) -> dict[str, object]:
    """Compute high-level dataset statistics."""
    stats: dict[str, object] = {"total_files": len(df)}

    if "participant" in df.columns:
        stats["total_participants"] = int(df["participant"].nunique())
    if "device" in df.columns:
        stats["devices"] = int(df["device"].nunique())
    if "category" in df.columns:
        stats["categories"] = int(df["category"].nunique())
    if "rows" in df.columns and not df["rows"].isna().all():
        stats["total_rows"] = int(pd.to_numeric(df["rows"], errors="coerce").sum())
    return stats


def export_report(df: pd.DataFrame, output_file: str | Path) -> None:
    """Export the dataset table and grouped metrics to an Excel workbook."""
    out = Path(output_file)
    if out.suffix.lower() not in (".xlsx", ".xls"):
        out = out.with_suffix(".xlsx")

    with pd.ExcelWriter(out) as writer:
        df.to_excel(writer, sheet_name="dataset", index=False)

        if "device" in df.columns:
            device_metrics = (
                df.groupby("device")[["file_size", "rows"]].agg(["mean", "std", "sum"])
            )
            device_metrics.to_excel(writer, sheet_name="device_metrics")

        if "participant" in df.columns:
            participant_metrics = (
                df.groupby("participant")[["file_size", "rows"]].agg(
                    ["mean", "std", "sum", "count"]
                )
            )
            participant_metrics.to_excel(writer, sheet_name="participant_metrics")

    logger.info("Report generated: %s", out)
    print(f"Report generated: {out}")


def render_visualization(
    df: pd.DataFrame,
    output_file: str | Path = "pipeline_summary.png",
) -> None:
    """Render a summary chart (files or rows per device) to a PNG file."""
    if df.empty or "device" not in df.columns:
        logger.info("No visualization produced (no usable device data).")
        return

    out = Path(output_file)
    if out.suffix.lower() not in (".png", ".jpg", ".jpeg", ".svg"):
        out = out.with_suffix(".png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    devices = df["device"].fillna("unknown")

    counts = devices.value_counts()
    counts.plot(kind="bar", ax=axes[0], color="#4C72B0")
    axes[0].set_title("Files per device")
    axes[0].set_ylabel("Count")

    if "rows" in df.columns:
        numeric_rows = pd.to_numeric(df["rows"], errors="coerce").fillna(0)
        rows_by_device = (
            df.assign(rows=numeric_rows).groupby(df["device"].fillna("unknown"))["rows"].sum()
        )
        rows_by_device.plot(kind="bar", ax=axes[1], color="#55A868")
        axes[1].set_title("Total rows per device")
        axes[1].set_ylabel("Rows")
    else:
        axes[1].axis("off")

    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Visualization saved to %s", out)
    print(f"Visualization saved to: {out}")


def run_pipeline(
    folder_path: str | Path,
    output: str | Path = "report.xlsx",
    visualize: bool = True,
    chart_output: str | Path = "pipeline_summary.png",
) -> dict[str, object]:
    """Run the full pipeline and return the computed statistics."""
    folder = Path(folder_path)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    logger.info("Scanning folder: %s", folder)
    print("Scanning folder:", folder)

    files = find_csv_files(folder)
    print("Files found:", len(files))

    df = build_dataset_table(files)
    stats = compute_statistics(df)
    print("Statistics:", stats)

    export_report(df, output)

    if visualize:
        render_visualization(df, chart_output)

    return {"dataset": df, "statistics": stats, "files": len(files)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the universal data processing pipeline.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-o", "--output", default="report.xlsx", help="Output Excel report path.")
    parser.add_argument("--no-visualization", action="store_true", help="Skip chart generation.")
    parser.add_argument("-c", "--chart", default="pipeline_summary.png", help="Output chart path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )
    run_pipeline(
        args.folder,
        output=args.output,
        visualize=not args.no_visualization,
        chart_output=args.chart,
    )


if __name__ == "__main__":
    main()

"""Dataset Metadata Extractor.

Scans a directory tree, parses file names into structured metadata, and
exports a metadata table (CSV or Excel) describing every file found.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from dpa.core.io import find_files
from dpa.core.naming import FileNameInfo, parse_filename

logger = logging.getLogger(__name__)


def build_file_record(file: Path) -> dict[str, object]:
    """Build a single metadata record from a file path."""
    info: FileNameInfo = parse_filename(file)
    try:
        size = file.stat().st_size
    except OSError as exc:  # pragma: no cover - defensive
        logger.warning("Could not stat %s: %s", file, exc)
        size = -1

    return {
        "file_name": file.name,
        "file_path": str(file),
        "file_size": size,
        "extension": file.suffix,
        "participant": info.participant,
        "category": info.category,
        "device": info.device,
        "extra_1": info.extra_1,
        "extra_2": info.extra_2,
        "date": info.date,
        "pattern_valid": info.pattern_valid,
    }


def build_metadata_table(files: Sequence[Path]) -> pd.DataFrame:
    """Build a metadata DataFrame from a list of file paths."""
    return pd.DataFrame([build_file_record(f) for f in files])


def scan_dataset(folder: str | Path) -> list[Path]:
    """Recursively collect all regular files under *folder*."""
    base = Path(folder)
    return [f for f in find_files(base, [".", ""]) if f.is_file()]


def export_metadata(
    df: pd.DataFrame,
    output: str | Path = "dataset_metadata.xlsx",
    fmt: str = "auto",
) -> None:
    """Export the metadata table to the requested format.

    Supported ``fmt`` values: ``"csv"``, ``"excel"``, or ``"auto"`` (inferred
    from the output file extension, defaulting to Excel).
    """
    out = Path(output)
    extension = out.suffix.lower()
    if fmt == "auto":
        fmt = "excel" if extension in (".xlsx", ".xls") else "csv"
    if extension not in (".xlsx", ".xls") and fmt == "excel":
        out = out.with_suffix(".xlsx")

    if fmt == "csv":
        df.to_csv(out, index=False, sep=";")
    else:
        df.to_excel(out, index=False)

    logger.info("Metadata file generated: %s", out)
    print(f"Metadata file generated: {out}")


def run_extractor(folder: str | Path, output: str | Path = "dataset_metadata.xlsx") -> pd.DataFrame:
    """Run the full extraction pipeline and return the metadata table."""
    files = scan_dataset(folder)
    logger.info("Files found: %d", len(files))
    print(f"Files found: {len(files)}")
    df = build_metadata_table(files)
    export_metadata(df, output)
    return df


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract metadata from dataset files.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-o", "--output", default="dataset_metadata.xlsx", help="Output file.")
    parser.add_argument("-f", "--format", choices=["auto", "csv", "excel"], default="auto")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )
    out = Path(args.output)
    if args.format != "auto":
        out = out.with_suffix(".csv" if args.format == "csv" else ".xlsx")
    run_extractor(args.folder, out)


if __name__ == "__main__":
    main()

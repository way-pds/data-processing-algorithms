"""Generate structured metadata from datasets stored in folders or ZIP files.

Scans local folders or ZIP archives, lists their contents, and produces a
standardized metadata table (CSV) suitable for data cataloging and ingestion
pipelines.
"""

from __future__ import annotations

import argparse
import logging
import zipfile
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_DATE_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y%m%d",
    "%d-%m-%Y",
    "%Y/%m/%d",
)


def list_files_from_folder(folder_path: str | Path) -> list[str]:
    """Recursively list all file paths inside a folder (POSIX relative)."""
    base = Path(folder_path).resolve()
    if not base.is_dir():
        raise ValueError(f"Not a directory: {folder_path}")
    return [p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()]


def list_files_from_zip(zip_path: str | Path) -> list[str]:
    """List file paths contained in a ZIP archive."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        return [info.filename for info in zip_ref.infolist() if not info.is_dir()]


def detect_input_type(input_path: str | Path) -> list[str]:
    """Detect whether the input is a folder or ZIP and list its files."""
    path = Path(input_path)

    if path.is_file() and path.suffix.lower() == ".zip":
        return list_files_from_zip(path)
    if path.is_dir():
        return list_files_from_folder(path)

    raise ValueError("Input must be a folder or a ZIP file")


def format_date(date_string: str) -> str:
    """Convert a date in several common formats to ``DD/MM/YYYY``.

    Returns the original string unchanged if no known format matches.
    """
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return date_string


def generate_metadata(
    file_list: Sequence[str],
    repository_url: str,
    project_name: str,
    source: str,
    generation_date: str,
    volunteer_id: str | None = None,
) -> pd.DataFrame:
    """Create a metadata DataFrame from a list of relative file paths."""
    return pd.DataFrame(
        [
            {
                "generation_date": generation_date,
                "source": source,
                "project_name": project_name,
                "volunteer_id": volunteer_id,
                "url_filename": f"{repository_url}/{file}",
            }
            for file in file_list
        ]
    )


def export_metadata(df: pd.DataFrame, output_path: str | Path) -> None:
    """Export the metadata table to CSV (semicolon-separated) at *output_path*."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, sep=";")
    logger.info("Metadata saved to %s", out)
    print(f"Metadata saved to {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate metadata from a folder or ZIP.")
    parser.add_argument("input", nargs="?", default="data/input", help="Dataset folder or ZIP file.")
    parser.add_argument("-r", "--repository", default="https://repository-url", help="Base repository URL.")
    parser.add_argument("-p", "--project", default="example_project", help="Project name.")
    parser.add_argument("-s", "--source", default="sensor_data", help="Data source.")
    parser.add_argument("-d", "--date", default=None, help="Generation date (any supported format).")
    parser.add_argument("-i", "--volunteer-id", default=None, help="Volunteer/subject identifier.")
    parser.add_argument("-o", "--output", default="output/metadata.csv", help="Output CSV path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )

    generation_date = format_date(args.date or datetime.now().strftime("%Y-%m-%d"))

    files = detect_input_type(args.input)
    df = generate_metadata(
        files,
        repository_url=args.repository,
        project_name=args.project,
        source=args.source,
        generation_date=generation_date,
        volunteer_id=args.volunteer_id,
    )
    export_metadata(df, args.output)


if __name__ == "__main__":
    main()

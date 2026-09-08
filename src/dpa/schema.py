"""Dataset Schema Validator.

Validates the structure of CSV datasets against expected schemas, reporting
missing columns, empty files, and unknown schemas.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError
from tqdm import tqdm

from dpa.core.config import load_config
from dpa.core.io import find_csv_files
from dpa.core.naming import parse_filename

logger = logging.getLogger(__name__)


def resolve_expected_columns(
    schemas: dict[str, Any],
    device: str | None,
    subtype: str | None,
) -> list[str] | None:
    """Resolve the expected columns for a device/subtype against *schemas*.

    A schema value may be either a flat list of columns or a nested mapping of
    ``subtype -> [columns]``. Returns ``None`` when no matching schema exists.
    """
    if not device or device not in schemas:
        return None

    value = schemas[device]

    if isinstance(value, (list, tuple)):
        return [str(c) for c in value]

    if isinstance(value, dict):
        if subtype and subtype in value:
            return [str(c) for c in value[subtype]]
        flattened: list[str] = []
        for entry in value.values():
            if isinstance(entry, (list, tuple)):
                flattened.extend(str(c) for c in entry)
        return flattened or None

    return None


def validate_file(file: Path, schemas: dict[str, Any]) -> dict[str, Any]:
    """Validate a single CSV file against the schema configuration."""
    try:
        df = pd.read_csv(file, low_memory=False)
    except EmptyDataError:
        return {"file": file.name, "error": "empty_file"}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not parse %s: %s", file, exc)
        return {"file": file.name, "error": "parse_error"}

    info = parse_filename(file)
    expected = resolve_expected_columns(schemas, info.device, info.category)

    if expected is None:
        return {
            "file": file.name,
            "error": "unknown_schema",
            "device": info.device,
            "rows": len(df),
        }

    missing = sorted(set(expected) - set(df.columns))
    return {
        "file": file.name,
        "device": info.device,
        "rows": len(df),
        "missing_columns": missing,
        "columns_found": list(df.columns),
        "valid": not missing,
    }


def run_validation(folder: str | Path, schemas: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate every CSV under *folder*.

    Returns ``(report, errors)`` DataFrames. Report rows describe valid files;
    error rows describe files that could not be validated.
    """
    files = find_csv_files(folder)
    reports: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for file in tqdm(files, desc="Validating schemas", unit="file"):
        result = validate_file(file, schemas)
        if result.get("error"):
            errors.append(
                {
                    "file": result["file"],
                    "error": result["error"],
                    "device": result.get("device"),
                }
            )
        else:
            reports.append(
                {
                    "file": result["file"],
                    "device": result.get("device"),
                    "rows": result["rows"],
                    "missing_columns": result["missing_columns"],
                    "valid": result["valid"],
                }
            )

    return pd.DataFrame(reports), pd.DataFrame(errors)


def export_results(
    report: pd.DataFrame,
    errors: pd.DataFrame,
    output: str | Path = "schema_validation_report.xlsx",
) -> None:
    """Export the validation report and errors to an Excel workbook."""
    out = Path(output)
    if out.suffix.lower() not in (".xlsx", ".xls"):
        out = out.with_suffix(".xlsx")
    with pd.ExcelWriter(out) as writer:
        report.to_excel(writer, sheet_name="report", index=False)
        errors.to_excel(writer, sheet_name="errors", index=False)
    logger.info("Validation report saved to %s", out)
    print(f"Validation report saved to: {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate dataset schemas against configuration.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-c", "--config", default=None, help="Optional YAML configuration file.")
    parser.add_argument("-o", "--output", default="schema_validation_report.xlsx", help="Output report path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )

    cfg = load_config(args.config)
    report, errors = run_validation(args.folder, cfg.get("schemas", {}))

    if not errors.empty:
        print(f"\n{len(errors)} file(s) could not be validated.")
    if not report.empty:
        invalid = report[report["valid"] == False]  # noqa: E712
        print(f"{len(invalid)} file(s) have missing columns.")

    export_results(report, errors, args.output)


if __name__ == "__main__":
    main()

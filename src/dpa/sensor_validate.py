"""Sensor Dataset Validator.

Validates sensor-based datasets: checks that the expected number of files and
the minimum number of lines per sensor are present, and detects signal
interruptions (timestamp gaps).
"""

from __future__ import annotations

import argparse
import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from dpa.core.config import load_config
from dpa.core.io import find_csv_files, read_dataset

logger = logging.getLogger(__name__)


@dataclass
class SensorValidationResult:
    """Result of the sensor dataset validation pipeline."""

    metadata: pd.DataFrame
    file_validation: dict[str, bool]
    line_validation: dict[str, bool]
    signal_breaks: pd.DataFrame = field(default_factory=pd.DataFrame)


def normalize_device(device: str | None) -> str:
    """Normalize a device token, stripping trailing file indices.

    ``"bia1"`` and ``"bia2"`` both normalize to ``"bia"``; ``"ecg2"`` to
    ``"ecg"``; ``"accelerometer"`` is unchanged.
    """
    if not device:
        return ""
    return re.sub(r"\d+$", "", device.lower())


def count_lines(df: pd.DataFrame) -> int | None:
    """Return the number of data rows, or ``None`` if the frame is invalid."""
    row_count = len(df)
    return row_count


def build_metadata_table(folder: str | Path) -> pd.DataFrame:
    """Collect per-file metadata (device, folder, line count)."""
    files = find_csv_files(folder)
    records: list[dict[str, object]] = []

    for file in tqdm(files, desc="Collecting metadata", unit="file"):
        df = read_dataset(file)
        records.append(
            {
                "file": str(file),
                "file_name": file.name,
                "device": file.stem.lower(),
                "normalized_device": normalize_device(file.stem),
                "folder": file.parent.name,
                "line_count": count_lines(df) if df is not None else None,
            }
        )

    return pd.DataFrame(records)


def validate_file_quantity(
    df: pd.DataFrame,
    expected_files: Mapping[str, int],
) -> dict[str, bool]:
    """Check that each sensor has its expected number of files."""
    counts = df.groupby("normalized_device").size()
    return {
        device: int(counts.get(device, 0)) == expected
        for device, expected in expected_files.items()
    }


def validate_line_counts(
    df: pd.DataFrame,
    expected_lines: Mapping[str, int],
) -> dict[str, bool]:
    """Check that each sensor's files meet a minimum line count.

    Files are matched to a sensor by prefix (e.g. both ``bia1`` and ``bia2``
    are validated against the ``bia`` threshold) and the check passes when the
    *minimum* observed line count meets the expected threshold.
    """
    validation: dict[str, bool] = {}
    for sensor, threshold in expected_lines.items():
        subset = df[df["device"].str.startswith(sensor)]
        if subset.empty or subset["line_count"].isna().all():
            validation[sensor] = False
            continue
        validation[sensor] = int(subset["line_count"].min()) >= threshold
    return validation


def detect_signal_breaks(
    df: pd.DataFrame,
    time_column: str = "time",
    max_gap_seconds: float = 0.1,
) -> pd.DataFrame:
    """Return rows in *df* where the timestamp gap exceeds *max_gap_seconds*.

    Returns an empty DataFrame when the time column is missing or no gaps are
    found.
    """
    if time_column not in df.columns:
        return df.iloc[0:0]

    time = pd.to_datetime(df[time_column], errors="coerce")
    diff = time.diff()
    mask = (diff > pd.Timedelta(seconds=max_gap_seconds)) & diff.notna()
    return df[mask]


def analyze_dataset(
    folder: str | Path,
    expected_files: Mapping[str, int],
    expected_lines: Mapping[str, int],
    check_breaks: bool = False,
) -> SensorValidationResult:
    """Run the sensor validation pipeline over *folder*.

    Args:
        folder: Dataset folder to scan.
        expected_files: Sensor -> expected file count.
        expected_lines: Sensor -> minimum expected line count.
        check_breaks: When True, also scan each file for signal interruptions.

    Returns:
        A :class:`SensorValidationResult` with metadata and validation maps.
    """
    metadata = build_metadata_table(folder)
    file_validation = validate_file_quantity(metadata, expected_files)
    line_validation = validate_line_counts(metadata, expected_lines)

    signal_breaks = pd.DataFrame()
    if check_breaks:
        break_frames: list[pd.DataFrame] = []
        for file in pathlib_rows(metadata):
            df = read_dataset(file)
            if df is None:
                continue
            breaks = detect_signal_breaks(df)
            if not breaks.empty:
                breaks = breaks.copy()
                breaks["file"] = Path(file).name
                break_frames.append(breaks)
        if break_frames:
            signal_breaks = pd.concat(break_frames, ignore_index=True)

    return SensorValidationResult(
        metadata=metadata,
        file_validation=file_validation,
        line_validation=line_validation,
        signal_breaks=signal_breaks,
    )


def pathlib_rows(metadata: pd.DataFrame) -> list[str]:
    """Return the stored file paths from a metadata DataFrame."""
    if metadata.empty or "file" not in metadata.columns:
        return []
    return [str(p) for p in metadata["file"].tolist()]


def _format_results(results: SensorValidationResult) -> str:
    lines: list[str] = ["File validation:"]
    for device, ok in results.file_validation.items():
        lines.append(f"  {device}: {ok}")
    lines.append("Line validation:")
    for device, ok in results.line_validation.items():
        lines.append(f"  {device}: {ok}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate sensor dataset completeness.")
    parser.add_argument("folder", nargs="?", default="data", help="Dataset folder to scan.")
    parser.add_argument("-c", "--config", default=None, help="Optional YAML configuration file.")
    parser.add_argument("--check-breaks", action="store_true", help="Detect signal interruptions.")
    parser.add_argument("-o", "--output", default="sensor_validation_report.xlsx", help="Output report path.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
    )

    cfg = load_config(args.config)
    results = analyze_dataset(
        args.folder,
        cfg.get("expected_files", {}),
        cfg.get("expected_lines", {}),
        check_breaks=args.check_breaks,
    )

    print("\n" + _format_results(results))

    if not results.metadata.empty:
        with pd.ExcelWriter(args.output) as writer:
            results.metadata.to_excel(writer, sheet_name="metadata", index=False)

            validation = pd.concat(
                [
                    pd.DataFrame(
                        {
                            "check": list(results.file_validation.keys()),
                            "type": "file_quantity",
                            "valid": list(results.file_validation.values()),
                        }
                    ),
                    pd.DataFrame(
                        {
                            "check": list(results.line_validation.keys()),
                            "type": "line_count",
                            "valid": list(results.line_validation.values()),
                        }
                    ),
                ],
                ignore_index=True,
            )
            validation.to_excel(writer, sheet_name="validation", index=False)

            if args.check_breaks and not results.signal_breaks.empty:
                results.signal_breaks.to_excel(
                    writer, sheet_name="signal_breaks", index=False
                )
        print(f"Sensor validation report saved to: {args.output}")


if __name__ == "__main__":
    main()

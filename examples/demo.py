"""Run every dpa tool against synthetic demo data.

Usage
-----
    python examples/generate_demo_data.py   # create the demo data first
    python examples/demo.py                 # then run this script

Both scripts should be executed from the repository root.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from dpa.core.config import load_config
from dpa.frequency import analyze_dataset as frequency_analyze
from dpa.metadata_extractor import run_extractor
from dpa.metadata_generator import generate_metadata
from dpa.pipeline import run_pipeline
from dpa.quality import run_quality_analysis
from dpa.schema import run_validation
from dpa.sensor_count import analyze_sensor_data
from dpa.sensor_validate import analyze_dataset as sensor_validate

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("demo")

DATA_DIR = Path("examples/data")


def _banner(title: str) -> None:
    log.info("=" * 60)
    log.info("  %s", title)
    log.info("=" * 60)


def demo_frequency() -> None:
    _banner("Sampling Frequency Analysis")
    cfg = load_config(Path("config/devices.yaml"))
    devices = cfg.get("devices", {})
    report = frequency_analyze(DATA_DIR, config=devices)
    log.info("Frequency report:\n%s", report.to_string(index=False))


def demo_metadata_extractor() -> None:
    _banner("Metadata Extractor")
    out = DATA_DIR / "_metadata_extracted.xlsx"
    df = run_extractor(DATA_DIR, output=out)
    log.info("Extracted %d rows of metadata", len(df))
    log.info("Columns: %s", list(df.columns))


def demo_metadata_generator() -> None:
    _banner("Metadata Generator")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "metadata.csv"
        df = generate_metadata(
            input_path=DATA_DIR,
            repository="https://github.com/way-pds/data-processing-algorithms",
            project="demo_project",
            source="sensor_data",
            output_path=out,
            volunteer_id="demo_subject",
        )
        log.info("Generated %d metadata rows", len(df))
        log.info("Sample:\n%s", df.head().to_string(index=False))


def demo_schema_validation() -> None:
    _banner("Schema Validation")
    cfg = load_config(Path("config/devices.yaml"))
    schemas = cfg.get("schemas", {})
    summary, details = run_validation(DATA_DIR, schemas)
    log.info("Schema summary:\n%s", summary.to_string(index=False))


def demo_sensor_validate() -> None:
    _banner("Sensor Dataset Validation")
    cfg = load_config(Path("config/devices.yaml"))
    expected_files = cfg.get("expected_files", {})
    expected_lines = cfg.get("expected_lines", {})
    results = sensor_validate(DATA_DIR, expected_files, expected_lines)
    log.info("File validation: %s", results.file_validation)
    log.info("Line validation: %s", results.line_validation)


def demo_sensor_count() -> None:
    _banner("Sensor Data Count")
    cfg = load_config(Path("config/devices.yaml"))
    sensor_columns = cfg.get("sensor_columns", {})
    report = analyze_sensor_data(DATA_DIR, sensor_columns=sensor_columns)
    log.info("Sensor count report:\n%s", report.to_string(index=False))


def demo_quality() -> None:
    _banner("Data Quality Analysis")
    report_df, summary_df = run_quality_analysis(DATA_DIR)
    log.info("Quality report (%d rows):\n%s", len(report_df), report_df.to_string(index=False))


def demo_pipeline() -> None:
    _banner("End-to-End Pipeline")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pipeline_report.xlsx"
        chart = Path(tmp) / "pipeline_summary.png"
        report = run_pipeline(DATA_DIR, output_file=out, chart_file=chart)
        log.info("Pipeline report (%d rows)", len(report))
        if chart.exists():
            log.info("Chart saved to %s", chart)


def main() -> None:
    log.info("Demo data directory: %s", DATA_DIR.resolve())
    if not DATA_DIR.exists():
        log.error("Run 'python examples/generate_demo_data.py' first.")
        return

    demo_frequency()
    demo_metadata_extractor()
    demo_metadata_generator()
    demo_schema_validation()
    demo_sensor_validate()
    demo_sensor_count()
    demo_quality()
    demo_pipeline()

    _banner("All demos completed successfully!")


if __name__ == "__main__":
    main()

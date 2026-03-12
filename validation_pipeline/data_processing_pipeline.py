"""
Universal Data Processing Pipeline

This script scans directories containing dataset files,
extracts metadata, computes statistics, and generates
structured reports.

Author: Wayne Pereira da Silva
"""

from pathlib import Path
import pandas as pd
import numpy as np


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SUPPORTED_EXTENSIONS = [".csv"]


# --------------------------------------------------
# FILE DISCOVERY
# --------------------------------------------------

def find_files(folder: Path, extensions=None):
    """
    Recursively find files with given extensions.
    """
    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS

    files = []
    for ext in extensions:
        files.extend(folder.rglob(f"*{ext}"))

    return files


# --------------------------------------------------
# METADATA EXTRACTION
# --------------------------------------------------

def extract_metadata(file_path: Path):
    """
    Extract metadata from filename based on underscore pattern.
    """

    name_parts = file_path.stem.split("_")

    metadata = {
        "filename": file_path.name,
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size
    }

    try:
        metadata.update({
            "participant": name_parts[0].lower(),
            "category": name_parts[1].lower(),
            "device": name_parts[2].lower(),
            "extra_1": name_parts[3] if len(name_parts) > 3 else None,
            "extra_2": name_parts[4] if len(name_parts) > 4 else None,
            "date": name_parts[5] if len(name_parts) > 5 else None
        })
    except Exception:
        metadata["pattern_valid"] = False
        return metadata

    metadata["pattern_valid"] = True

    return metadata


# --------------------------------------------------
# ROW COUNT
# --------------------------------------------------

def count_rows(file_path: Path):
    """
    Count rows in CSV files.
    """

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1
    except Exception:
        return np.nan


# --------------------------------------------------
# BUILD DATAFRAME
# --------------------------------------------------

def build_dataset_table(files):

    records = []

    for f in files:

        meta = extract_metadata(f)
        meta["rows"] = count_rows(f)

        records.append(meta)

    df = pd.DataFrame(records)

    return df


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

def compute_statistics(df):

    stats = {}

    stats["total_files"] = len(df)
    stats["total_participants"] = df["participant"].nunique()

    if "device" in df.columns:
        stats["devices"] = df["device"].nunique()

    return stats


# --------------------------------------------------
# REPORT GENERATION
# --------------------------------------------------

def export_report(df, output_file):

    with pd.ExcelWriter(output_file) as writer:

        df.to_excel(writer, sheet_name="dataset", index=False)

        if "device" in df.columns:

            device_metrics = (
                df.groupby("device")[["file_size", "rows"]]
                .agg(["mean", "std", "sum"])
            )

            device_metrics.to_excel(writer, sheet_name="device_metrics")

        if "participant" in df.columns:

            participant_metrics = (
                df.groupby("participant")[["file_size", "rows"]]
                .agg(["mean", "std", "sum", "count"])
            )

            participant_metrics.to_excel(writer, sheet_name="participant_metrics")


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def run_pipeline(folder_path, output="report.xlsx"):

    folder = Path(folder_path)

    print("Scanning folder:", folder)

    files = find_files(folder)

    print("Files found:", len(files))

    df = build_dataset_table(files)

    stats = compute_statistics(df)

    print("Statistics:", stats)

    export_report(df, output)

    print("Report generated:", output)


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    folder = input("Enter dataset folder path: ")

    run_pipeline(folder)
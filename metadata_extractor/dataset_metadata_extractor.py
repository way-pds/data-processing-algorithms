"""
Dataset Metadata Extractor

Scans dataset directories and generates a structured
metadata table describing all files.

Author: Wayne Pereira da Silva
"""

from pathlib import Path
import pandas as pd


# --------------------------------------------------
# FILE SCAN
# --------------------------------------------------

def scan_dataset(folder):

    folder = Path(folder)

    files = list(folder.rglob("*"))

    files = [f for f in files if f.is_file()]

    return files


# --------------------------------------------------
# METADATA EXTRACTION
# --------------------------------------------------

def extract_file_info(file):

    info = {}

    info["file_name"] = file.name
    info["file_path"] = str(file)
    info["file_size"] = file.stat().st_size
    info["extension"] = file.suffix

    try:

        parts = file.stem.split("_")

        info["participant"] = parts[0] if len(parts) > 0 else None
        info["category"] = parts[1] if len(parts) > 1 else None
        info["device"] = parts[2] if len(parts) > 2 else None
        info["date"] = parts[3] if len(parts) > 3 else None

    except Exception:

        info["participant"] = None

    return info


# --------------------------------------------------
# BUILD TABLE
# --------------------------------------------------

def build_metadata_table(files):

    records = []

    for f in files:

        records.append(extract_file_info(f))

    df = pd.DataFrame(records)

    return df


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

def export_metadata(df, output="dataset_metadata.xlsx"):

    df.to_excel(output, index=False)

    print("Metadata file generated:", output)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def run_extractor(folder):

    files = scan_dataset(folder)

    print("Files found:", len(files))

    df = build_metadata_table(files)

    export_metadata(df)


if __name__ == "__main__":

    folder = input("Dataset folder path: ")

    run_extractor(folder)
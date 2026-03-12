"""
Dataset Quality Analyzer

Performs automated quality analysis on CSV datasets.

Author: Wayne Pereira da Silva
"""

from pathlib import Path
import pandas as pd
from tqdm import tqdm


# --------------------------------------------------
# FILE DISCOVERY
# --------------------------------------------------

def find_csv_files(folder):

    folder = Path(folder)

    return list(folder.rglob("*.csv"))


# --------------------------------------------------
# QUALITY METRICS
# --------------------------------------------------

def analyze_dataset(file):

    df = pd.read_csv(file, low_memory=False)

    stats = pd.concat(
        [
            df.isnull().sum().to_frame("missing_values"),
            df.select_dtypes("number").var().to_frame("variance"),
            df.nunique().to_frame("unique_values")
        ],
        axis=1
    )

    stats["file_name"] = file.name

    return stats


# --------------------------------------------------
# PIPELINE
# --------------------------------------------------

def run_quality_analysis(folder):

    files = find_csv_files(folder)

    results = []

    for file in tqdm(files):

        try:

            stats = analyze_dataset(file)

            results.append(stats)

        except Exception:

            continue

    results = pd.concat(results)

    return results


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

def export_report(results):

    with pd.ExcelWriter("data_quality_report.xlsx") as writer:

        results.to_excel(writer, sheet_name="quality_metrics")


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    folder = input("Dataset folder: ")

    results = run_quality_analysis(folder)

    export_report(results)

    print("Quality analysis completed.")
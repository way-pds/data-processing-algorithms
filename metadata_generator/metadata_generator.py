"""
metadata_generator.py

Generate metadata from datasets stored in folders or ZIP files.
The script extracts file paths and builds structured metadata
for data cataloging and repository ingestion.

Author: Your Name
"""

from pathlib import Path
import zipfile
import pandas as pd
from datetime import datetime
from io import BytesIO


def list_files_from_folder(folder_path: str) -> list:
    """
    Recursively list all files inside a folder.
    """
    base = Path(folder_path).resolve()
    files = [p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()]
    return files


def list_files_from_zip(zip_path: str) -> list:
    """
    List files contained in a ZIP archive.
    """
    files = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for info in zip_ref.infolist():
            if not info.is_dir():
                files.append(info.filename)
    return files


def detect_input_type(input_path: str) -> list:
    """
    Detect if input is a folder or ZIP and extract file paths.
    """
    path = Path(input_path)

    if path.is_file() and path.suffix == ".zip":
        return list_files_from_zip(input_path)

    elif path.is_dir():
        return list_files_from_folder(input_path)

    else:
        raise ValueError("Input must be a folder or ZIP file")


def generate_metadata(file_list: list,
                      repository_url: str,
                      project_name: str,
                      source: str,
                      generation_date: str) -> pd.DataFrame:
    """
    Create metadata DataFrame.
    """

    metadata = []

    for file in file_list:
        metadata.append({
            "generation_date": generation_date,
            "source": source,
            "project_name": project_name,
            "volunteer_id": None,
            "url_filename": f"{repository_url}/{file}"
        })

    df = pd.DataFrame(metadata)

    return df


def format_date(date_string: str) -> str:
    """
    Convert multiple date formats to DD/MM/YYYY.
    """

    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y",
        "%Y%m%d", "%d-%m-%Y", "%Y/%m/%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue

    return date_string


def export_metadata(df: pd.DataFrame, output_path: str):

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False, sep=";")

    print(f"Metadata saved to {output_path}")


def main():

    input_path = "data/input"
    repository = "https://repository-url"
    project = "example_project"
    source = "sensor_data"
    generation_date = "20240301"

    files = detect_input_type(input_path)

    df = generate_metadata(
        files,
        repository,
        project,
        source,
        generation_date
    )

    export_metadata(df, "output/metadata.csv")


if __name__ == "__main__":
    main()
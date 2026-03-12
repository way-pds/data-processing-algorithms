"""
Dataset Schema Validator

Validates dataset structure by comparing CSV columns
with expected schema definitions.

Author: Wayne Pereira da Silva
"""

from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
from tqdm import tqdm


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

PROJECTS = {
    "project1": {"devices": ["deviceA", "deviceB"]},
    "project2": {"devices": ["deviceC"]}
}

DEVICES = {
    "deviceA": {
        "type1": ["col1", "col2", "col3"]
    },
    "deviceB": {
        "type2": ["sensor1", "sensor2"]
    },
    "deviceC": {
        "type3": ["value", "timestamp"]
    }
}


# --------------------------------------------------
# FILE DISCOVERY
# --------------------------------------------------

def find_csv_files(folder):

    folder = Path(folder)

    return list(folder.rglob("*.csv"))


# --------------------------------------------------
# DEVICE RESOLUTION
# --------------------------------------------------

def find_devices(project):

    if project not in PROJECTS:
        return []

    return PROJECTS[project]["devices"]


# --------------------------------------------------
# SCHEMA VALIDATION
# --------------------------------------------------

def validate_file(file):

    try:
        df = pd.read_csv(file, low_memory=False)
    except EmptyDataError:
        return {"error": "empty_file"}

    project = file.parents[1].name.lower()

    devices = find_devices(project)

    type_ = file.stem.split("_")[2]

    expected_columns = None

    for device in devices:
        if device in DEVICES and type_ in DEVICES[device]:
            expected_columns = DEVICES[device][type_]
            break

    if expected_columns is None:
        return {"error": "unknown_schema"}

    missing_columns = list(set(expected_columns) - set(df.columns))

    return {
        "missing_columns": missing_columns,
        "columns_found": list(df.columns),
        "rows": len(df)
    }


# --------------------------------------------------
# PIPELINE
# --------------------------------------------------

def run_validation(folder):

    files = find_csv_files(folder)

    reports = []
    errors = []

    for file in tqdm(files):

        result = validate_file(file)

        if "error" in result:

            errors.append({
                "file": file.name,
                "error": result["error"]
            })

        else:

            reports.append({
                "file": file.name,
                "rows": result["rows"],
                "missing_columns": result["missing_columns"]
            })

    return pd.DataFrame(reports), pd.DataFrame(errors)


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

def export_results(report, errors):

    with pd.ExcelWriter("schema_validation_report.xlsx") as writer:

        report.to_excel(writer, sheet_name="report", index=False)
        errors.to_excel(writer, sheet_name="errors", index=False)


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    folder = input("Dataset folder: ")

    report, errors = run_validation(folder)

    export_results(report, errors)

    print("Validation completed.")
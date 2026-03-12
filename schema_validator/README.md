# Dataset Schema Validator

This project implements a Python algorithm for validating the structure of datasets based on predefined schemas.

The script scans a dataset directory, identifies CSV files, and verifies whether the columns present in each file match the expected schema defined for each device or data source.

## Features

- Recursive dataset scanning
- Schema validation based on predefined device structures
- Detection of:
  - Missing columns
  - Non-standard datasets
  - Empty files
- Automatic error report generation
- Summary statistics for each dataset

## Use Case

The algorithm was originally designed to validate research datasets collected from multiple devices such as wearable sensors, health trackers, and physiological measurement systems.

However, the structure can be adapted to any project requiring **dataset schema validation**.

## Technologies

- Python
- Pandas
- Pathlib
- TQDM

## Output

The algorithm generates:

- dataset validation report
- error log
- summary statistics

All exported automatically to Excel.

## Example

```bash
python schema_validator.py --folder path/to/dataset
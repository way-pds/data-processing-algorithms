# Dataset Quality Analyzer

This project implements an automated data quality analysis pipeline for structured datasets.

The algorithm analyzes CSV files and generates metrics that help identify potential data issues.

## Data Quality Checks

The script performs:

- Missing value analysis
- Variance calculation
- Unique value count
- Dataset consistency checks
- Column validation
- Dataset categorization

## Features

- Automated dataset scanning
- Statistical analysis of datasets
- Detection of abnormal files
- Generation of analytical reports
- Export to Excel

## Output

The algorithm produces an Excel report containing:

- dataset metadata
- column statistics
- dataset distribution
- detected errors

## Example

```bash
python data_quality_analysis.py --folder path/to/data
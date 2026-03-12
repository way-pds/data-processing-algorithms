# Metadata Generator

Python tool for generating structured metadata from datasets stored in folders or ZIP files.

This project automates the extraction of file paths and generates standardized metadata for data cataloging, data engineering workflows, and repository ingestion pipelines.

---

## Overview

In many data engineering and research workflows, datasets arrive in folders or compressed archives without structured metadata. This script scans those datasets, extracts file paths, and generates standardized metadata describing the dataset contents.

The generated metadata can be used for:

* Data cataloging
* Data lake ingestion
* Dataset documentation
* Automated pipelines
* Repository uploads

---

## Features

* Supports datasets stored in:

  * Local folders
  * ZIP archives
* Recursively scans directory structures
* Extracts dataset file paths
* Generates structured metadata
* Handles multiple date formats
* Exports metadata to CSV
* Modular and reusable Python functions

---

## Project Structure

metadata-generator/

│

├── metadata_generator.py

├── README.md

├── requirements.txt

│

├── data

│   └── input

│

└── output

```
└── metadata.csv
```

---

## Requirements

Python 3.8+

Install the required dependencies:

pip install pandas

---

## Installation

Clone the repository:

git clone https://github.com/yourusername/metadata-generator.git

cd metadata-generator

Install dependencies:

pip install -r requirements.txt

---

## Usage

Open the script and configure the following parameters:

input_path = "data/input"

repository = "https://repository-url"

project = "example_project"

source = "sensor_data"

generation_date = "20240301"

Run the script:

python metadata_generator.py

---

## Input

The script accepts two types of input:

### 1. Folder

Example:

data/input/

```
subject_01/

    file1.csv

    file2.csv
```

### 2. ZIP file

Example:

dataset.zip

The script automatically detects the input type.

---

## Output

The script generates a CSV file containing dataset metadata.

Example output file:

output/metadata.csv

Example table structure:

generation_date;source;project_name;volunteer_id;url_filename

01/03/2024;sensor_data;example_project;None;https://repository-url/file1.csv

---

## Metadata Fields

| Field           | Description                               |
| --------------- | ----------------------------------------- |
| generation_date | Date when the dataset was generated       |
| source          | Origin of the dataset                     |
| project_name    | Project associated with the dataset       |
| volunteer_id    | Identifier for the subject (if available) |
| url_filename    | Final path or repository URL of the file  |

---

## Code Structure

The script is organized into reusable functions:

list_files_from_folder()

Recursively scans a directory and returns file paths.

list_files_from_zip()

Reads files from ZIP archives.

detect_input_type()

Determines whether the input is a folder or ZIP file.

generate_metadata()

Creates a structured metadata table using pandas.

format_date()

Standardizes different date formats.

export_metadata()

Exports the metadata table to CSV.

---

## Example Workflow

1. Receive dataset folder or ZIP file
2. Scan files automatically
3. Extract file paths
4. Generate metadata table
5. Export metadata CSV

---

## Applications

This tool can be used in several contexts:

Data Engineering

* Dataset ingestion pipelines
* Data lake organization
* Metadata automation

Research Data Management

* Scientific dataset documentation
* Data sharing workflows

Machine Learning

* Dataset cataloging
* Training data organization

---

## Future Improvements

Possible extensions for this project:

* CLI argument support
* Integration with cloud storage
* Automatic metadata validation
* Support for additional archive formats
* REST API integration
* Automatic repository upload

---

## Author

Your Name

Mathematics & Computational Science — UNICAMP
Data Science and Data Engineering projects

---

## License

MIT License

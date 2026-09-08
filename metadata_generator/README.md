# Metadata Generator

> Module: `src/dpa/metadata_generator.py` · CLI: `dpa-metadata-generator`

Generates repository-ready metadata from dataset folders or ZIP archives.

## Features

- Automatic detection of folder vs. ZIP input
- Recursive directory scanning
- Standardized date formatting
- Configurable project, source, repository URL, and volunteer ID
- CSV export

## Usage

```bash
dpa-metadata-generator data/input/ \
  -r https://repo.url \
  -p my_project \
  -s sensor_data \
  -d "2026-01-01" \
  -i subject01 \
  -o metadata.csv
```

## Programmatic

```python
from dpa.metadata_generator import generate_metadata

df = generate_metadata(
    input_path="data/input",
    repository="https://repo.url",
    project="my_project",
    source="sensor_data",
    output_path="metadata.csv",
    volunteer_id="subject01",
)
```

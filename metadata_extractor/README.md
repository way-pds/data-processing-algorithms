# Dataset Metadata Extractor

> Module: `src/dpa/metadata_extractor.py` · CLI: `dpa-metadata-extractor`

Extracts structured metadata from dataset filenames.

## Features

- Automatic CSV dataset discovery
- Metadata extraction from filenames (research, participant, device, category, side, dominance, moment, date)
- File size and row count
- Export to Excel or CSV

## Usage

```bash
dpa-metadata-extractor path/to/data -o metadata.xlsx -f excel -v
```

## Programmatic

```python
from dpa.metadata_extractor import run_extractor

df = run_extractor("data/", output="metadata.xlsx")
```

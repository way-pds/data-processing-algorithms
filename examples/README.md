# Examples

## Quick Demo

```bash
# From the repository root:
python examples/generate_demo_data.py   # creates synthetic CSVs in examples/data/
python examples/demo.py                 # runs every dpa tool on the demo data
```

## What the Demo Covers

| Tool | What it does |
|------|-------------|
| `dpa-frequency` | Analyzes sampling frequency of synthetic sensor CSVs |
| `dpa-metadata-extractor` | Extracts metadata from filenames |
| `dpa-metadata-generator` | Generates repository-ready metadata |
| `dpa-schema` | Validates column schemas against config |
| `dpa-sensor-validate` | Validates file/line counts for sensors |
| `dpa-sensor-count` | Counts valid data points per sensor |
| `dpa-quality` | Runs data quality checks |
| `dpa-pipeline` | Full end-to-end pipeline with charts |

All output is logged to stdout. Temporary files are cleaned up automatically.

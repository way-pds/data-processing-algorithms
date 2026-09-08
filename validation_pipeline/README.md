# Dataset Validation Pipeline

> Module: `src/dpa/pipeline.py` · CLI: `dpa-pipeline`

End-to-end data processing pipeline: metadata extraction, statistics, and visualization.

## Pipeline Steps

1. Scan folder for CSV files
2. Extract metadata from filenames
3. Compute per-device and per-participant statistics
4. Generate summary charts (matplotlib)
5. Export Excel report

## Usage

```bash
dpa-pipeline path/to/data -o report.xlsx -c summary.png -v

# Skip chart generation
dpa-pipeline path/to/data --no-visualization
```

## Programmatic

```python
from dpa.pipeline import run_pipeline

report = run_pipeline("data/", output_file="report.xlsx", chart_file="chart.png")
```

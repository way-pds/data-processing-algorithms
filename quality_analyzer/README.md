# Dataset Quality Analyzer

> Module: `src/dpa/quality.py` · CLI: `dpa-quality`

Performs automated data quality analysis on CSV datasets.

## Quality Checks

- Missing value ratio per column
- Duplicate row detection
- Constant (zero-variance) column detection
- Severity classification (high / medium / low)

## Usage

```bash
dpa-quality path/to/data -o quality_report.xlsx -v
```

## Programmatic

```python
from dpa.quality import run_quality_analysis

report_df, summary_df = run_quality_analysis("data/")
```

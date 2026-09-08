# Sampling Frequency Analyzer

> Module: `src/dpa/frequency.py` · CLI: `dpa-frequency`

Analyzes the sampling frequency of sensor datasets stored in CSV files.

## Features

- Recursive dataset discovery with configurable device definitions
- Metadata extraction from structured filenames
- Sampling frequency statistics (mean, std, Hz)
- External YAML configuration for device timestamps and units
- Excel report export

## Usage

```bash
# Default (scans ./data)
dpa-frequency

# Custom folder + config
dpa-frequency path/to/data --config config/devices.yaml -o report.xlsx -v
```

## Configuration

Device-to-timestamp mappings are defined in `config/devices.yaml`:

```yaml
devices:
  VivaSensing:
    timestamp: "Timestamp"
    unit: "ms"
  TANITA:
    timestamp: "time"
    unit: null          # auto-detect unit
```

## Programmatic

```python
from dpa.frequency import analyze_dataset
from dpa.core.config import load_config

cfg = load_config("config/devices.yaml")
report = analyze_dataset("data/", config=cfg["devices"])
```

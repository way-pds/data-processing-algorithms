# Sensor Dataset Validator

> Module: `src/dpa/sensor_validate.py` · CLI: `dpa-sensor-validate`

Validates sensor datasets by file count, line count, and signal continuity.

## Checks

- Expected number of files per sensor type
- Minimum line count per sensor
- Signal break detection (consecutive identical rows)

## Configuration

Expected values are defined in `config/devices.yaml`:

```yaml
expected_files:
  accelerometer: 1
  bia: 2
  ecg: 2
  ppg: 1

expected_lines:
  accelerometer: 42000
  bia: 150
  ecg: 1500
  ppg: 85000
```

## Usage

```bash
dpa-sensor-validate path/to/data --config config/devices.yaml -v
```

## Programmatic

```python
from dpa.sensor_validate import analyze_dataset

results = analyze_dataset("data/", expected_files, expected_lines)
print(results.file_validation)
print(results.line_validation)
print(results.signal_breaks)
```

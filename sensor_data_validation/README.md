# Sensor Data Counter

> Module: `src/dpa/sensor_count.py` · CLI: `dpa-sensor-count`

Counts valid (non-null) data points per sensor column across CSV datasets.

## Supported Sensors

| Sensor | Columns |
|--------|---------|
| Accelerometer | Acc_X, Acc_Y, Acc_Z |
| Gyroscope | Gyr_X, Gyr_Y, Gyr_Z |
| Magnetometer | Mag_X, Mag_Y, Mag_Z |
| Heart Rate | HR |

Column mappings are configurable in `config/devices.yaml`.

## Usage

```bash
dpa-sensor-count path/to/data --config config/devices.yaml -o report.xlsx -v
```

## Programmatic

```python
from dpa.sensor_count import analyze_sensor_data

report = analyze_sensor_data("data/", sensor_columns=sensor_columns)
```

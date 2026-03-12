# Sensor Data Counter

This project provides a Python script for validating and quantifying sensor data in CSV datasets.

The script scans directories containing CSV files, identifies sensor columns, and counts valid data points for each sensor type. This helps evaluate dataset completeness and data availability in sensor-based research or monitoring systems.

## Features

- Recursive search for CSV files
- Automatic detection of sensor columns
- Counting of valid (non-null) data points
- Support for multiple sensor types
- Summary of available sensor data

## Supported Sensors

The script currently supports the following sensor types:

| Sensor | Columns |
|------|------|
| Accelerometer | Acc_X, Acc_Y, Acc_Z |
| Gyroscope | Gyr_X, Gyr_Y, Gyr_Z |
| Magnetometer | Mag_X, Mag_Y, Mag_Z |
| Heart Rate | HR |

The sensor configuration can easily be extended by editing the `SENSOR_COLUMNS` dictionary.

## Requirements

- Python 3.9+
- pandas

Install dependencies:

```bash
pip install pandas
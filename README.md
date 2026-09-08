# Data Processing Algorithms

[![CI](https://github.com/way-pds/data-processing-algorithms/actions/workflows/ci.yml/badge.svg)](https://github.com/way-pds/data-processing-algorithms/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python toolkit for dataset validation, metadata extraction, and data quality analysis — designed for sensor-based research data engineering workflows.

## Quick Start

```bash
# Clone
git clone https://github.com/way-pds/data-processing-algorithms.git
cd data-processing-algorithms

# Install (editable) with dev tools
pip install -e ".[dev]"

# Generate demo data and run every tool
python examples/generate_demo_data.py
python examples/demo.py
```

## Tools

| Command | Module | Description |
|---------|--------|-------------|
| `dpa-frequency` | `frequency.py` | Analyse sensor sampling frequency (mean, std, Hz). |
| `dpa-metadata-extractor` | `metadata_extractor.py` | Extract metadata from structured filenames. |
| `dpa-metadata-generator` | `metadata_generator.py` | Generate repository-ready metadata from folders or ZIPs. |
| `dpa-quality` | `quality.py` | Data quality analysis (missing values, duplicates, constants). |
| `dpa-schema` | `schema.py` | Validate CSV column schemas against a configuration. |
| `dpa-sensor-count` | `sensor_count.py` | Count valid data points per sensor column. |
| `dpa-sensor-validate` | `sensor_validate.py` | Validate sensor file counts, line counts, and detect signal breaks. |
| `dpa-pipeline` | `pipeline.py` | End-to-end pipeline: metadata + statistics + charts. |

Every tool supports `--help`, `-v/--verbose`, and `-o/--output`.

### CLI Examples

```bash
# Sampling frequency on a custom folder with an external config
dpa-frequency data/ --config config/devices.yaml -o report.xlsx -v

# Full pipeline with chart
dpa-pipeline data/ --output report.xlsx --chart summary.png

# Schema validation
dpa-schema data/ --config config/devices.yaml -o schema_report.xlsx

# Metadata extractor (Excel output)
dpa-metadata-extractor data/ -o metadata.xlsx -f excel

# Metadata generator
dpa-metadata-generator data/ -r https://repo.url -p my_project -o metadata.csv

# Sensor validation
dpa-sensor-validate data/ --config config/devices.yaml

# Sensor data count
dpa-sensor-count data/ --config config/devices.yaml

# Data quality
dpa-quality data/ -o quality.xlsx
```

### Programmatic Usage

```python
from dpa.core.config import load_config
from dpa.frequency import analyze_dataset
from dpa.quality import run_quality_analysis
from dpa.pipeline import run_pipeline

# Load external device configuration
cfg = load_config("config/devices.yaml")

# Frequency analysis
freq_report = analyze_dataset("data/", config=cfg["devices"])

# Quality analysis
quality_df, summary_df = run_quality_analysis("data/")

# Full pipeline
report = run_pipeline("data/", output_file="report.xlsx", chart_file="chart.png")
```

## Project Structure

```
data-processing-algorithms/
├── src/dpa/                    # Installable package
│   ├── core/                   # Shared utilities (I/O, config, filename parsing)
│   │   ├── config.py           # YAML config loader with deep-merge defaults
│   │   ├── io.py               # File discovery, CSV reading, row counting
│   │   └── naming.py           # Structured filename parser
│   ├── frequency.py            # Sampling frequency analysis
│   ├── metadata_extractor.py   # Filename-based metadata extraction
│   ├── metadata_generator.py   # Repository metadata generation
│   ├── quality.py              # Data quality checks
│   ├── schema.py               # Schema validation
│   ├── sensor_count.py         # Sensor data point counting
│   ├── sensor_validate.py      # Sensor file/line validation
│   └── pipeline.py             # End-to-end processing pipeline
├── config/
│   └── devices.yaml            # External configuration (devices, schemas, sensors)
├── examples/                   # Demo data generator + runner
├── tests/                      # Pytest test suite (58 tests)
├── .github/workflows/ci.yml    # GitHub Actions CI
├── pyproject.toml              # Package definition + entry points
├── Makefile                    # Dev shortcuts (make test, make lint, make fmt)
├── LICENSE                     # MIT
└── CHANGELOG.md                # Release history
```

## Configuration

Device definitions, sensor columns, expected file/line counts, and schemas are configured in [`config/devices.yaml`](config/devices.yaml). Every tool falls back to built-in defaults when no config file is provided.

Override any subset of values — the config system deep-merges your overrides over the defaults.

## Development

```bash
make install          # Create venv + install package in editable mode
make test             # Run the test suite
make lint             # Run ruff + mypy
make fmt              # Auto-format code with ruff
make coverage         # Run tests with coverage report
```

## Technology Stack

- **Python 3.9+**
- pandas, numpy, PyYAML, tqdm, openpyxl
- pytest + pytest-cov (testing)
- ruff (linting/formatting)
- mypy (static type checking)
- GitHub Actions (CI/CD)

## Author

**Wayne Pereira da Silva**
Applied Mathematics and Computational Science — UNICAMP

## License

[MIT](LICENSE)

# Dataset Schema Validator

> Module: `src/dpa/schema.py` · CLI: `dpa-schema`

Validates CSV column structure against predefined schemas.

## Features

- Device-level schema matching from filename tokens
- Missing column and extra column detection
- Empty file detection
- External YAML schema configuration
- Excel report export

## Usage

```bash
dpa-schema path/to/data --config config/devices.yaml -o schema_report.xlsx -v
```

## Configuration

Schemas are defined in `config/devices.yaml`:

```yaml
schemas:
  deviceA:
    type1: ["col1", "col2", "col3"]
  deviceB:
    type2: ["sensor1", "sensor2"]
```

## Programmatic

```python
from dpa.schema import run_validation
from dpa.core.config import load_config

cfg = load_config("config/devices.yaml")
summary, details = run_validation("data/", cfg["schemas"])
```

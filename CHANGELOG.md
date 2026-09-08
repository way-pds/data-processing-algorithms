# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-08

### Added

- Packaging: `pyproject.toml`, `src/dpa` layout, console entry points (`dpa-*`),
  and a development `Makefile`.
- Automated test suite with `pytest` (58 tests) covering every module, including
  edge cases (empty files, malformed names, timestamp parsing).
- Uniform CLI built on `argparse` for every tool (`--input/--output/--config`,
  `-v/--verbose` logging).
- External YAML configuration (`config/devices.yaml`) replacing hardcoded
  device/sensor/schema dictionaries, merged over sensible defaults.
- Shared core package (`dpa.core`) with file discovery, dataset reading,
  filename parsing, and configuration loading (removes duplicated logic).
- Structured `logging` throughout (replacing `print`) with a CL configurable
  verbosity level.
- Static analysis integrateable into CI: `ruff` lint + `mypy` strict typing.
- GitHub Actions CI workflow that runs lint, format, type-check, and tests
  across Python 3.9–3.12.
- MIT `LICENSE`, this `CHANGELOG`, and synthetic example datasets/demos.

### Fixed

- `frequency_analysis`: crash on devices without a timestamp unit (e.g. TANITA)
  and division-by-zero when adjacent timestamps are equal; guarded the
  `parents[1]` path traversal.
- `sensor_validator`: line-count matching that conflated `bia1`/`bia2` and
  file-quantity validation that compared against the wrong device keys; the
  previously unused signal-break detector is now wired into the pipeline.
- `schema_validator`: `IndexError` on filenames with fewer than three fields.
- `metadata_generator`: `format_date` was defined but never applied; date is now
  normalized and `volunteer_id` is configurable.
- `quality_analyzer`: crash on empty result sets; added documented checks
  (duplicates, empty/constant columns, severity classification).
- `validation_pipeline`: README promised visualizations that did not exist; the
  pipeline now renders summary charts.

### Changed

- Modules reorganized into an installable package under `src/dpa`.
- All tools accept a folder as a positional CLI argument with sensible defaults.

### Removed

- Hardcoded, project-specific configuration scattered across modules.

[unreleased]: https://github.com/way-pds/data-processing-algorithms
[0.1.0]: https://github.com/way-pds/data-processing-algorithms/releases/tag/v0.1.0

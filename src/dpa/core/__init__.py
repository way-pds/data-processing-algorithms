"""Core shared utilities for the dpa package.

This package centralizes the reusable pieces used by every module
(file discovery, filename metadata parsing, dataset reading, and
external configuration loading) to avoid code duplication.
"""

from dpa.core.config import load_config
from dpa.core.io import (
    count_csv_rows,
    find_csv_files,
    find_files,
    read_dataset,
)
from dpa.core.naming import parse_filename

__all__ = [
    "load_config",
    "find_files",
    "find_csv_files",
    "count_csv_rows",
    "read_dataset",
    "parse_filename",
]

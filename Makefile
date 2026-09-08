# Data Processing Algorithms — development Makefile

PYTHON ?= python
VENV ?= .venv
PY := $(VENV)/Scripts/python.exe

.PHONY: help install dev install-dev run lint format typecheck test coverage build clean

help:
	@echo "Targets:"
	@echo "  help          Show this help"
	@echo "  install       Install the package and runtime dependencies"
	@echo "  dev           Install the package in editable mode with dev dependencies"
	@echo "  lint          Run ruff check"
	@echo "  format        Auto-format code with ruff"
	@echo "  typecheck     Run mypy type checking"
	@echo "  test          Run the pytest suite"
	@echo "  coverage      Run pytest with coverage report"
	@echo "  build         Build sdist and wheel"
	@echo "  clean         Remove caches and build artifacts"

install:
	$(PYTHON) -m pip install .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PY) -m dpa.pipeline --help

lint:
	$(PY) -m ruff check src tests

format:
	$(PY) -m ruff check src tests --fix
	$(PY) -m ruff format src tests

typecheck:
	$(PY) -m mypy src

test:
	$(PY) -m pytest

coverage:
	$(PY) -m pytest --cov=dpa --cov-report=term-missing

build:
	$(PY) -m build

clean:
	rm -rf build dist src/*.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

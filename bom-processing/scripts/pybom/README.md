# Bills of Mortality Data Processor (Python)

This is a Python conversion of the R scripts for processing Bills of Mortality data from the Death by Numbers project.

## Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Usage

### Using the Makefile (Recommended)

The project includes a comprehensive Makefile for common tasks:

```bash
# See all available commands
make help

# Run the data processor
make run

# Run tests
make test

# Clean output files
make clean

# Format code
make format

# Check data directory
make check-data

# View project status
make status

# Full development workflow
make dev-run
```

### Using Poetry directly

```bash
# Process the Bills of Mortality data
poetry run python -m bomr.process_bills

# Or with custom directories
poetry run python -m bomr.process_bills --data-dir /path/to/csv/files --output-dir /path/to/output
```

## Features

This Python version provides:

- **Exact functionality** of the R scripts with improved error handling
- **Better type safety** and explicit data processing
- **Rich console output** with progress indicators
- **Modular design** with separate modules for different processing steps
- **Comprehensive logging** for debugging and monitoring
- **CLI interface** with configurable options

## Structure

- `bomr/main.py` - Main processing script (converts 01-bills.R)
- `bomr/helpers.py` - Core helper functions (converts helpers.R)
- `bomr/data_processing.py` - Advanced data processing functions
- `pyproject.toml` - Poetry configuration with dependencies

## Key Improvements over R Version

1. **Missing column handling**: Gracefully handles missing `is_illegible` and `is_missing` columns
2. **Better error messages**: More detailed error reporting and logging
3. **Type safety**: Explicit type handling prevents common data type issues
4. **Modular design**: Easier to test and maintain individual components
5. **Progress indicators**: Visual feedback during long processing operations

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical operations
- typer: CLI interface
- rich: Console output and progress bars
- sqlalchemy: Database operations (future use)
- psycopg2: PostgreSQL adapter (future use)

## Output

The script produces the same CSV files as the R version:
- `bills_weekly.csv` - Processed weekly bills data
- `parishes_unique.csv` - Unique parishes with canonical names
- `week_unique.csv` - Unique weeks with identifiers
- `year_unique.csv` - Unique years
- Various causes CSV files for each source
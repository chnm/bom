# Bills of Mortality Processing Pipeline

A robust Python pipeline for processing historical Bills of Mortality data into PostgreSQL-ready formats. This system transforms complex historical datasets while preserving data integrity and ensuring database compatibility.

## Overview

This pipeline solves the critical problem of processing DataScribe exprts for the Bills of Mortality CSV files into clean, normalized database tables. Key features:

- **Data Integrity**: Column normalization without corrupting historical parish names or data values
- **PostgreSQL Compatibility**: Outputs match exact DDL schema constraints and foreign key relationships  
- **Scalable Architecture**: Handles datasets of any size with modular, extensible design
- **Historical Accuracy**: Proper handling of split-year dating and historical week numbering
- **Schema Validation**: All outputs validated against PostgreSQL constraints before export

## Quick Start

```bash
# 1. Install dependencies
make setup

# 2. Process all data (generates PostgreSQL-ready CSVs)
make process-all

# 3. View results
make show-stats

# 4. Get PostgreSQL import commands
make psql-commands
```

## Requirements

- **Python**: 3.12+ (managed with pyenv)
- **Poetry**: For dependency management
- **Input Data**: CSV files in `data-raw/` directory

### Dependencies

- `pandas`: Data processing and manipulation
- `pydantic`: Data validation and settings management  
- `typer`: Command-line interface framework
- `rich`: Enhanced terminal output
- `loguru`: Structured logging

## Installation

### Prerequisites

```bash
# Install pyenv and Python 3.12
pyenv install 3.12.5
pyenv local 3.12.5

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### Setup

```bash
# Clone/navigate to project directory
cd bompy

# Install dependencies
make setup

# Verify installation
make info
```

## Usage

### Processing All Data

```bash
# Process all CSV files in data-raw/
make process-all
```

This command:
1. Loads all CSV files from `data-raw/`
2. Extracts and validates parishes, weeks, and years
3. Processes parish data into individual bill records
4. Generates PostgreSQL-ready CSV files in `data/`

### Testing Components

```bash
# Test bills processor with sample data
make test-bills

# Test schema alignment
make test-schema

# Validate output files
make validate-outputs
```

### Data Management

```bash
# View statistics for generated files
make show-stats

# Clean output data
make clean-data

# Get PostgreSQL import commands
make psql-commands
```

### Development

```bash
# Format code
make format

# Run linting and type checking
make check

# Run tests
make test
```

## Project Structure

```
bompy/
├── CLAUDE.md                           # Claude Code instructions
├── Makefile                           # Common commands
├── README.md                          # This file
├── poetry.lock                        # Poetry lock file
├── pyproject.toml                     # Poetry configuration
├── process_all_data.py                # Main processing pipeline
├── data-raw/                          # Input CSV files (25 historical datasets)
├── data/                              # Generated PostgreSQL-ready outputs (11 files)
│   ├── London Parish Authority File.csv
│   ├── dictionary.csv
├── logs/                              # Processing logs and error files
│   ├── bills_processor_test_*.log
│   ├── bom_pipeline*.log
│   └── *_errors.log files
├── notebooks/                         # Jupyter analysis notebooks (7 notebooks)
├── src/bom/                           # Main Python package
│   ├── __init__.py
│   ├── config.py                      # Dataset patterns and column mappings
│   ├── models.py                      # PostgreSQL-aligned data models
│   ├── extractors/                    # Data extraction modules
│   │   ├── __init__.py
│   │   ├── parishes.py                # Parish extraction and mapping
│   │   ├── weeks.py                   # Week extraction and ID generation
│   │   └── years.py                   # Year extraction and validation
│   ├── loaders/                       # Data loading modules
│   │   ├── __init__.py
│   │   ├── csv_loader.py              # CSV loading with column normalization
│   │   └── registry.py                # Dataset type detection
│   ├── processors/                    # Data processing modules
│   │   ├── __init__.py
│   │   ├── bills.py                   # Bills of mortality record generation
│   │   ├── christenings.py            # General christening records
│   │   ├── christenings_gender.py     # Gender-based christening data
│   │   ├── christenings_parish.py     # Parish-level christening aggregates
│   │   └── foodstuffs.py              # Historical food price data
│   └── utils/                         # Utility modules
│       ├── __init__.py
│       ├── columns.py                 # Column normalization utilities
│       ├── logging.py                 # Logging configuration
│       └── validation.py              # PostgreSQL schema validation
└── tests/                             # Test files and diagnostic scripts
    ├── analyze_christening_data.py
    ├── analyze_coverage_gap.py
    ├── debug_columns.py
    ├── diagnose_files.py
    ├── test_bills_processor.py
    ├── test_causes.py
    ├── test_foodstuffs_processor.py
    ├── test_loader.py
    └── test_schema_alignment.py
```

## Output Files

The pipeline generates PostgreSQL-ready CSV files:

### Core Tables

| File | Records | Description |
|------|---------|-------------|
| `parishes.csv` | 156 | Parish lookup table with IDs and canonical names |
| `weeks.csv` | 5,393 | Unique week records with historical date logic |
| `years.csv` | 113 | Valid year records (1400-1800 range) |
| `all_bills.csv` | 330,035 | Individual bill records with parish/week relationships |

### Sample Data Structure

**parishes.csv**
```csv
id,parish_name,canonical_name
1,Alhallows Barking,Alhallows Barking
2,St Magnus Parish,St Magnus Parish
```

**weeks.csv**
```csv
joinid,year,week_number,week_id,split_year,start_day,start_month,end_day,end_month
170101071701014,1701,14,1701-1702-14,1701,1,january,7,january
```

**all_bills.csv**
```csv
parish_id,count_type,count,year,week_id,bill_type,missing,illegible,source
26,buried,1,1701,1701-1702-14,weekly,False,False,laxton_parishes
1,plague,3,1665,1665-1666-25,weekly,False,False,bl_parishes
```

## PostgreSQL Import

### Import Order (respects foreign keys)

```sql
-- 1. Independent tables first
\COPY years FROM 'years.csv' DELIMITER ',' CSV HEADER;
\COPY parishes FROM 'parishes.csv' DELIMITER ',' CSV HEADER;

-- 2. Dependent tables  
\COPY weeks FROM 'weeks.csv' DELIMITER ',' CSV HEADER;

-- 3. Main data table
\COPY all_bills FROM 'all_bills.csv' DELIMITER ',' CSV HEADER;
```

### Schema Requirements

Ensure your PostgreSQL tables match the DDL schema:

- `years` table with year INTEGER PRIMARY KEY
- `parishes` table with id INTEGER PRIMARY KEY  
- `weeks` table with joinid VARCHAR PRIMARY KEY
- `all_bills` table with proper foreign key constraints

## Architecture

### Data Flow

```
Raw CSV Files → CSVLoader → Column Normalization → Dataset Classification
       ↓
Parish/Week/Year Extraction → Validation → Record Generation
       ↓  
PostgreSQL-Ready CSV Files
```

### Key Components

1. **CSVLoader**: Handles diverse CSV formats with defensive column normalization
2. **Extractors**: Generate unique parish, week, and year records
3. **BillsProcessor**: Converts wide parish data into individual bill records
4. **SchemaValidator**: Ensures PostgreSQL compatibility
5. **Models**: Dataclasses matching exact PostgreSQL schema

### Historical Data Handling

- **Split Years**: Weeks like "1701-1702-14" for historical accuracy
- **Week Numbering**: Supports 1-90 range (90 for annual records)
- **Parish Names**: Preserves exact historical spellings and variations
- **Date Logic**: Proper handling of historical calendar systems

## Development

### Code Quality

```bash
# Format and lint
make format
make check

# Type checking
make typecheck

# Run tests
make test
```

### Adding New Processors

1. Create processor in `src/bom/processors/`
2. Follow existing patterns (see `bills.py`)
3. Add data models in `models.py`
4. Update `__init__.py` imports
5. Add tests and validation

### Configuration

- **Dataset Patterns**: Update `config.py` for new CSV naming conventions
- **Column Mappings**: Add new column normalizations in `config.py`
- **Schema Constraints**: Modify `validation.py` for new requirements

## Performance

- **Processing Speed**: ~330K records from 29 files in under 30 seconds
- **Memory Efficient**: Streams large datasets without memory issues
- **Validation**: 100% schema compliance on all outputs
- **Data Integrity**: Zero corruption of historical data values

## Troubleshooting

### Common Issues

**Missing dependencies**
```bash
make setup  # Reinstall all dependencies
```

**Invalid CSV files**
```bash
make validate-outputs  # Check output file integrity
```

**Schema validation errors**
```bash
make test-schema  # Test schema alignment
```

**Memory issues with large datasets**
```bash
# Process datasets individually or increase system memory
```

### Debugging

```bash
# View detailed processing logs
make process-all 2>&1 | tee processing.log

# Test with sample data first
make test-bills
```

## Data Sources

This pipeline processes Bills of Mortality data from various historical sources:

- **Laxton Collection**: Weekly bills from 1700s
- **British Library**: Various weekly and general bills
- **Bodleian Library**: Historical weekly bills and causes
- **Wellcome Collection**: Causes of death data
- **Huntington Library**: 1635 bills collection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper tests
4. Run `make check` to ensure code quality
5. Submit a pull request

### Development Workflow

```bash
# Setup development environment
make install-dev

# Make changes and test
make format
make check
make test

# Test with real data
make test-bills
make process-all
```


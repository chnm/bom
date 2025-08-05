# BOM Processing Scripts

This directory contains scripts and tools for processing Bills of Mortality data.

## Structure

### bompy/
Python-based data processing pipeline for Bills of Mortality data. This is the current, actively maintained implementation.

**Key components:**
- `src/bom/` - Core Python package with processors, loaders, and extractors
- `data-raw/` - Raw CSV data files from various sources
- `data/` - Processed output data files
- `notebooks/` - Jupyter notebooks for analysis and exploration
- `tests/` - Test scripts and debugging tools
- `process_all_data.py` - Main processing script

### bomr/
R-based data processing scripts. **ARCHIVED/DEPRECATED** - This has been superseded by the Python implementation in `bompy/`.

### Other Files
- `python-analyses/` - Additional Python analysis scripts designed for checking the math/completeness of the datasets
- `spreadsheets/` - R scripts for data extraction. **ARCHIVED** -- originally designed to structure data from old spreadsheets.
- `create_geojson.sh` & `insert_geojson.sh` - Shell scripts for geographic data processing

## Usage

For current data processing, use the `bompy/` directory. See `bompy/README.md` for detailed usage instructions.

The `bomr/` directory is maintained for historical reference but is no longer actively developed.

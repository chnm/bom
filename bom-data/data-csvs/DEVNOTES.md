# Data Quality Checking Tools

This directory contains a couple of tools for analyzing the quality and completeness of the Bills of Mortality (BOM) CSV datasets.

## Files

- `check_illegible.py` - Python script to analyze `is_illegible` column values across all CSV files
- `DEVNOTES.md` - This documentation file

## Overview

The BOM datasets contain an `is_illegible` column that marks records where the original document text was too unclear to transcribe accurately. This column uses the following values:

- `1` - Record is marked as illegible
- `` (empty) - No illegibility marking (most common)
- Other values may exist but are rare

## Usage

### Checking Illegible Records

To analyze illegible records across all CSV files in the current directory:

```bash
python check_illegible.py
```

### Output

The script provides three sections of output:

1. **Files with Illegible Records**: Lists only files that contain at least one illegible record
2. **Summary Statistics**: Overall counts and percentages across all files  
3. **Detailed Breakdown**: Complete table showing illegible/empty/total counts for each file

### Sample Output

```
Analyzing 30 CSV files...

============================================================
FILES WITH ILLEGIBLE RECORDS:
============================================================
2023-03-28-BodleianV2-weeklybills-parishes.csv: 1 illegible out of 275 total records
2024-09-25-BodleianV1-weeklybills-parishes.csv: 18 illegible out of 312 total records
...

Total files with illegible records: 9

============================================================
SUMMARY STATISTICS:
============================================================
Total CSV files analyzed: 30
Total records: 12,345
Total illegible records: 43
Total empty is_illegible fields: 12,302
Percentage illegible: 0.348%
```
## Requirements

- Python 3.x
- Standard library modules only (csv, os, sys, collections)

## Notes

- The script automatically detects CSV files in the current directory
- Files without an `is_illegible` column are silently skipped
- Error handling is included for files that cannot be read
- Results are sorted alphabetically by filename for consistency

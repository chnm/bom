# Bills of Mortality Data Analysis Tools

This directory contains Python scripts for analyzing the quality, completeness, and content of the Bills of Mortality (BOM) CSV datasets.

## Files

- `analyze_bill_years.py` - Categorize bills by type and extract historical year ranges
- `analyze_burials.py` - Analyze burial data from weekly bills parishes
- `analyze_subtotals.py` - Analyze geographical subtotal burial data by region
- `check_illegible.py` - Check data quality by analyzing `is_illegible` column values
- `DEVNOTES.md` - This documentation file

## Overview

These tools help analyze various aspects of the Bills of Mortality datasets:
- Historical year coverage across different bill types
- Parish-level burial data aggregation and trends
- Regional subtotal analysis for geographical comparisons
- Data quality checks for illegible records

---

## 1. analyze_bill_years.py

### Purpose
Categorizes bills by type (weekly, general, other) and extracts the complete historical year ranges from CSV data. Analyzes actual year data from file contents rather than relying on filenames.

### Usage

```bash
python analyze_bill_years.py
```

### Output

The script provides both console output and a detailed text file (`bill_years_analysis.txt`) containing:
1. **Weekly Bills**: Year ranges, unique years, and list of files with data
2. **General Bills**: Year ranges for bills with Start/End year columns
3. **Other Bills**: Any bills not categorized as weekly or general
4. **Summary Statistics**: Combined coverage across all bill types

### Sample Output

```
BILLS OF MORTALITY - HISTORICAL YEAR RANGE ANALYSIS
============================================================

SUMMARY:
Weekly bills: 25 files (487 unique years)
  Year range: 1603 - 1849
General bills: 3 files (245 unique years)
  Year range: 1604 - 1849

Combined coverage: 1603 - 1849 (502 unique years total)

Detailed results written to: bill_years_analysis.txt
```

### Requirements
- Python 3.x
- Standard library modules: `csv`, `glob`, `collections`

---

## 2. analyze_burials.py

### Purpose
Extracts and analyzes all burial columns from parish-level weekly bills data. Sums burial counts by year and week, identifies peak mortality weeks, and exports aggregated results.

### Usage

```bash
python analyze_burials.py
```

**Note**: Script is currently configured to analyze `2025-10-27-Laxton-combineddata-weeklybills-parishes.csv`. Update the `csv_file` variable in `main()` to analyze different files.

### Output

The script provides:
1. **Summary Statistics**: Total records, year coverage, average/max/min burials per week
2. **Yearly Totals**: Total burials aggregated by year
3. **Top Burial Weeks**: Weeks with highest mortality counts
4. **Export File**: CSV file (`burial_analysis_results.csv`) with aggregated data

### Sample Output

```
=== BURIAL DATA SUMMARY ===
Total records: 12,543
Years covered: 1603 - 1849
Total weeks: 53
Average burials per week: 287.3
Maximum burials in a week: 8,297

=== TOP 10 WEEKS BY BURIAL COUNT ===
Year 1665, Week 37: 8297 burials
Year 1665, Week 38: 7165 burials
...
```

### Requirements
- Python 3.x
- pandas
- numpy

---

## 3. analyze_subtotals.py

### Purpose
Analyzes geographical subtotal burial data by region: within the walls, without the walls, Middlesex and Surrey, and Westminster. Provides regional breakdowns and comparative analysis.

### Usage

```bash
python analyze_subtotals.py
```

**Note**: Script is currently configured to analyze `2025-10-27-Laxton-combineddata-weeklybills-parishes.csv`. Update the `csv_file` variable in `main()` to analyze different files.

### Output

The script provides:
1. **Regional Summaries**: Average burials per region per week
2. **Regional Trends**: Total burials by region with percentages
3. **Yearly Totals**: Regional breakdown by year (top 10 years)
4. **Top Weeks**: Highest mortality weeks with regional breakdowns
5. **Export File**: CSV file (`subtotal_analysis_results.csv`) with aggregated data

### Sample Output

```
=== REGIONAL ANALYSIS ===
Total burials by region (entire dataset):
  Within the Walls - Buried: 487,234 (35.2%)
  Without the Walls - Buried: 562,891 (40.7%)
  Middlesex and Surrey - Buried: 198,432 (14.3%)
  Westminster - Buried: 135,678 (9.8%)
```

### Requirements
- Python 3.x
- pandas
- numpy

---

## 4. check_illegible.py

### Purpose
Analyzes data quality by checking `is_illegible` column values across all CSV files. The `is_illegible` column marks records where original document text was too unclear to transcribe accurately.

### Column Values
- `1` - Record is marked as illegible
- `` (empty) - No illegibility marking (most common)

### Usage

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

### Requirements
- Python 3.x
- Standard library modules: `csv`, `os`, `sys`, `collections`

### Notes
- Automatically detects CSV files in the current directory
- Files without an `is_illegible` column are silently skipped
- Error handling included for files that cannot be read
- Results sorted alphabetically by filename for consistency

---

## General Notes

- All scripts include error handling for missing files and invalid data
- Scripts are designed to run from the data directory containing CSV files
- For `analyze_burials.py` and `analyze_subtotals.py`, update the `csv_file` variable in the `main()` function to analyze different datasets
- Output files are saved in the same directory as the scripts

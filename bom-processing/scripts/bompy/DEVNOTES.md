# Developer Notes: Bills of Mortality Data Processing

This document provides technical details for developers working on the Bills of Mortality data processing pipeline.

# Architecture Overview

## Data Flow
```
Raw CSV Files → CSVLoader → Column Normalization → Dataset Classification
     ↓
Parish/Week/Year Extraction → Validation → Record Generation  
     ↓
PostgreSQL-Ready CSV Files → Go Updater → PostgreSQL Database
```

## Source vs Bill Type

**Source Field**: Identifies the dataset/collection
- `laxton_parishes` - Laxton collection parish data (can contain both weekly and general)
- `blv1_parishes` - British Library Volume 1 parish data (weekly only)
- `bodleian_parishes` - Bodleian collection parish data (weekly only)
- `millar_parishes` - Millar collection parish data (general only)

**Bill Type Field**: Identifies the report type
- `weekly` - Regular weekly mortality reports
- `general` - Annual/biannual summary reports

## Bill Type Detection Logic
The system determines bill type automatically:
1. **Filename check**: "general" in filename → `general`
2. **Unique identifier check**: "GeneralBill" in record → `general`  
3. **Week pattern check**: Week 90 → `general`
4. **Default**: `weekly`

# Adding New Data Files

## Simple Case (Most Common)
1. **Add CSV file** to `/data-raw/` directory
2. **Run pipeline**: `make process-all` or `poetry run python process_all_data.py`
3. **Done!** The system automatically detects and processes the file

## Advanced Case (New Patterns)
If your file has a unique naming pattern, add it to `src/bom/config.py`:

```python
DATASET_PATTERNS = {
    # Existing patterns...
    "your_new_source": r"your_pattern.*parishes",
}
```

## Examples
- `2025-08-15-NewArchive-weeklybills-parishes.csv` → Auto-detected
- `2025-08-15-Wellcome-generalbills-parishes.csv` → Auto-detected as `wellcome_parishes` + `general` bill type

# Data Processing Details

## JoinID System
- **Weekly bills**: Use date-based joinids (e.g., `1701031817010325` for March 18-25, 1701)
- **General bills**: Match existing week records with week 90 (e.g., `1700121717001224` for Dec 17-24, 1700)
- **Purpose**: Links bill records to week records for temporal analysis

## Week 90 Convention
- Week 90 = Annual records (general bills)
- Weeks 1-52 = Regular weekly records
- This allows general bills to coexist with weekly data in the same temporal framework

## Database Schema Alignment
Generated CSV files match PostgreSQL table schemas exactly:
- `all_bills.csv` → `bom.bill_of_mortality` table
- `causes_of_death.csv` → `bom.causes_of_death` table  
- `christenings_by_parish.csv` → `bom.christenings` table (via temp table transformation)
- `weeks.csv` → `bom.week` table
- `parishes.csv` → `bom.parishes` table

# Go Updater Integration

## Database Constraint
The PostgreSQL database uses this unique constraint:
```sql
UNIQUE (parish_id, count_type, year, week_id, source, bill_type)
```

Including `bill_type` prevents weekly and general bills from overwriting each other.

## Conflict Resolution  
- **Weekly vs General**: Treated as separate records (different `bill_type`)
- **Same type duplicates**: Higher count value wins
- **Null vs Non-null**: Non-null count value wins

# Common Issues & Solutions

## "General bills not in database"
- **Check**: JoinIDs match week records (`grep joinid data/weeks.csv`)
- **Check**: Database constraint includes `bill_type`
- **Check**: Go updater WHERE clause includes week existence check

## "Decimal values in integer columns"
- **Solution**: All processors use `int(float(value))` for count conversions
- **Check**: DataFrame type conversion in `process_all_data.py` using `.astype("Int64")`

## "Source shows full file paths"
- **Solution**: Use `info.dataset_type` instead of `info.file_path` in pipeline
- **Check**: Source column shows labels like `laxton_parishes`, not paths

## "Missing week records"
- **Cause**: JoinID creation mismatch between bills and weeks
- **Solution**: Ensure consistent joinid creation across extractors and processors

# Development Workflow

## Testing Changes
```bash
# Test specific processor
make test-bills

# Test full pipeline  
make process-all

# Validate outputs
make validate-outputs

# Check data quality
make show-stats
```

## Code Quality
```bash
# Format code
make format

# Run linting
make lint

# Type checking
make check
```

## Adding New Features
1. **Follow existing patterns** in processors/
2. **Add validation** in utils/validation.py  
3. **Update schema** if needed in DDLs.txt
4. **Test thoroughly** with sample data
5. **Update documentation** in CLAUDE.md

# Performance Notes

## Processing Speed
- ~30 CSV files process in ~30 seconds
- Most time spent on parish column detection and record generation
- Memory usage scales with number of parish columns

## Optimization Opportunities
- **Parallel processing** of independent datasets
- **Vectorized operations** for large DataFrames  
- **Incremental processing** for unchanged files
- **Database bulk loading** instead of row-by-row upserts

# Troubleshooting

## Debug Mode
Enable verbose logging:
```python
logger.remove()
logger.add(sys.stderr, level="DEBUG")
```

## Common Log Messages
- `"Found X parish columns"` - Normal parish detection
- `"Generated X bill records"` - Normal processing output
- `"Deduplicated X duplicate records"` - Normal deduplication  
- `"Could not find parish ID"` - Missing parish mapping (check authority file)
- `"Invalid year"` - Data quality issue (check source data)

## Data Validation
The pipeline includes comprehensive validation:
- **Schema validation**: All records match PostgreSQL constraints
- **Referential integrity**: Week/parish IDs exist in lookup tables
- **Data quality checks**: Year ranges, required fields, data types
- **Duplication detection**: Automatic deduplication with conflict resolution

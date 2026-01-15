# AGENTS.md

This file provides comprehensive guidance for AI agents (Claude, Cursor, Copilot, etc.) working with this Bills of Mortality data processing repository.

## Project Overview

**Bills of Mortality Processing Pipeline** - A robust Python system that transforms historical CSV datasets (from DataScribe exports) into PostgreSQL-ready formats. This processes complex 17th-18th century mortality data from multiple archival sources (British Library, Bodleian, Wellcome, Laxton, Huntington, etc.) while maintaining data integrity and ensuring database schema compatibility.

**Core Problem Solved**: Converting DataScribe exports of historical Bills of Mortality into clean, normalized database tables matching exact PostgreSQL DDL schemas.

**Tech Stack**: Python 3.12, uv (package manager), pandas, pydantic, loguru, PostgreSQL

**Lines of Code**: ~5,000 lines of Python across modular processors

---

## Essential Commands

### Setup & Installation

```bash
# First-time setup
make setup              # Install dependencies with uv

# Alternative manual setup
uv sync                 # Install dependencies
uv sync --with dev      # Include dev dependencies
```

**Note**: This project uses `uv` (not Poetry), despite references in CLAUDE.md. The Makefile shows all commands use `uv run`.

### Primary Processing Pipeline

```bash
# Main pipeline - process all CSVs
make process-all        # Process all data-raw/*.csv → data/*.csv
uv run process_all_data.py  # Direct execution

# Copy raw data from external source
make copy-data          # Copies from ../../../bom-data/data-csvs/
```

**Processing Flow**:
1. Loads all CSV files from `data-raw/`
2. Normalizes column names without corrupting data
3. Extracts parishes, weeks, years
4. Generates bill records, causes of death, foodstuffs, christenings
5. Validates against PostgreSQL schema
6. Outputs to `data/*.csv`

**Expected Output Files** (11 files):
- `parishes.csv` - 156 unique parishes
- `weeks.csv` - 5,393 week records  
- `years.csv` - 113 year records (1400-1800 range)
- `all_bills.csv` - 330K+ individual bill records
- `causes_of_death.csv` - Death cause records
- `christenings.csv` - Combined christening records
- `christenings_by_parish.csv` - Parish-level aggregates
- `christenings_by_gender.csv` - Gender-based data
- `foodstuffs.csv` - Historical food prices
- `subtotals.csv` - Geographic subtotals (within/without walls)
- `dictionary.csv` - Cause definitions

### Testing & Validation

```bash
# Test specific processors
make test-bills         # Test bills processor with sample data
make test-schema        # Test schema alignment
make test               # Run full pytest suite

# Validation
make validate-outputs   # Validate generated CSV files
make check              # Run all code quality checks (lint + typecheck)
```

### Development Commands

```bash
# Code quality
make format             # Format with black and isort
make lint               # Check formatting
make typecheck          # Run mypy type checking
make check              # Run all checks (lint + typecheck)

# Data management
make show-stats         # Show output file statistics
make clean-data         # Clean data/ directory
make clean-logs         # Clean log files
make show-logs          # Show recent log files
make tail-logs          # Tail most recent log

# Cleanup
make clean              # Clean all generated files
make reset              # Full reset (removes .venv)
```

### Database Integration

```bash
# PostgreSQL import commands
make psql-commands      # Display import commands

# Coverage analysis
make check-coverage     # Analyze data coverage gaps by parish/year
```

**Import Order** (respects foreign keys):
```sql
\COPY years FROM 'years.csv' DELIMITER ',' CSV HEADER;
\COPY parishes FROM 'parishes.csv' DELIMITER ',' CSV HEADER;
\COPY weeks FROM 'weeks.csv' DELIMITER ',' CSV HEADER;
\COPY all_bills FROM 'all_bills.csv' DELIMITER ',' CSV HEADER;
```

### Information Commands

```bash
make info               # Show project information
make psql-commands      # Show PostgreSQL import commands
make help               # Show all available commands
```

---

## Code Organization

### Directory Structure

```
bompy/
├── src/bom/                    # Main Python package
│   ├── config.py               # Dataset patterns, column mappings
│   ├── models.py               # Pydantic models matching PostgreSQL schemas
│   │
│   ├── loaders/                # CSV loading with normalization
│   │   ├── csv_loader.py       # Main CSV loader
│   │   └── registry.py         # Dataset type detection
│   │
│   ├── extractors/             # Entity extraction
│   │   ├── parishes.py         # Parish extraction & ID mapping
│   │   ├── weeks.py            # Week extraction & joinid generation
│   │   └── years.py            # Year extraction & validation
│   │
│   ├── processors/             # Data transformation
│   │   ├── bills.py            # Main bills processor (parish → bill records)
│   │   ├── general_bills.py    # General bills processor
│   │   ├── christenings.py     # General christening records
│   │   ├── christenings_parish.py  # Parish-level christening aggregates
│   │   ├── christenings_gender.py  # Gender-based christening data
│   │   └── foodstuffs.py       # Historical food price data
│   │
│   └── utils/                  # Utilities
│       ├── columns.py          # Column normalization (CRITICAL)
│       ├── validation.py       # PostgreSQL schema validation
│       └── logging.py          # Structured logging setup
│
├── process_all_data.py         # Main pipeline entry point
├── data-raw/                   # Input CSVs (29 files from archives)
├── data/                       # Output CSVs (PostgreSQL-ready)
├── tests/                      # Test files and diagnostic scripts
├── notebooks/                  # Jupyter analysis notebooks
├── logs/                       # Processing logs (timestamped)
├── data-qc/                    # Quality control outputs
├── data-compare/               # Reference data and crosswalks
│
├── Makefile                    # All commands
├── pyproject.toml              # Dependencies (uv format)
├── uv.lock                     # Lock file
├── CLAUDE.md                   # Claude-specific guidance
├── DEVNOTES.md                 # Developer technical notes
└── README.md                   # User-facing documentation
```

---

## Architecture & Data Flow

### Processing Pipeline

```
Raw CSV Files (data-raw/)
    ↓
CSVLoader (loaders/csv_loader.py)
    ↓ Normalize columns without corrupting data
Dataset Classification (loaders/registry.py)
    ↓ Detect dataset type from filename
Extractors (extractors/*.py)
    ├─→ Parishes → Parish IDs
    ├─→ Weeks → JoinIDs
    └─→ Years → Valid year records
    ↓
Processors (processors/*.py)
    ├─→ Bills: Parish columns → Individual records
    ├─→ Causes: Death causes
    ├─→ Christenings: Birth records
    ├─→ Foodstuffs: Price data
    └─→ Subtotals: Geographic aggregations
    ↓
Schema Validation (utils/validation.py)
    ↓ Ensure PostgreSQL compatibility
PostgreSQL-Ready CSV Files (data/)
    ↓
Go Updater (external) → PostgreSQL Database
```

### Key Components

**1. Column Normalization** (`src/bom/utils/columns.py`)
- **CRITICAL**: Normalizes column *names* only, never corrupts data values
- Maps variations: "Unique ID" → "unique_identifier", "Week Number" → "week_number"
- Filters irrelevant columns (Omeka, DataScribe metadata)
- Handles duplicate column names by adding suffixes

**2. Dataset Detection** (`src/bom/loaders/registry.py`)
- Uses regex patterns from `config.py` to identify dataset types
- Examples:
  - `laxton.*parishes` → `laxton_parishes`
  - `bodleian.*causes` → `bodleian_causes`
  - `blv1.*parishes` → `blv1_parishes`
- Automatically detects new files matching patterns

**3. Parish Extraction** (`src/bom/extractors/parishes.py`)
- Scans all DataFrames for parish-name columns
- Creates unique parish IDs
- Preserves exact historical spellings
- Handles aggregate groups: "Christened in the 97 parishes within the walls"

**4. Week Extraction** (`src/bom/extractors/weeks.py`)
- Creates `joinid` values for temporal linking
- Handles split-year dating: `"1701-1702-14"` for week 14 bridging years
- Week 90 convention: Annual/general bill records
- Validates date logic (start_day, end_day, months)

**5. Bills Processor** (`src/bom/processors/bills.py`)
- Converts wide parish data (columns) → tall bill records (rows)
- Identifies count types: buried, plague, christened
- Extracts parish names from column headers
- Maps to parish IDs and joinIDs
- Handles weekly vs general bill types
- Processes both parish data and causes of death
- Includes cause definitions dictionary
- Performs source-aware deduplication

**6. Schema Validation** (`src/bom/utils/validation.py`)
- Validates all records against PostgreSQL constraints
- Checks foreign key relationships
- Ensures data types match DDL schemas
- Validates year ranges (1400-1800)
- Reports validation errors with details

---

## Data Models & Validation

### Pydantic Models (`src/bom/models.py`)

All models match PostgreSQL schemas exactly:

```python
@dataclass
class ParishRecord:
    id: int
    parish_name: str
    canonical_name: str

@dataclass
class WeekRecord:
    joinid: str          # Primary key: "1701031817010325"
    year: int
    week_number: int
    week_id: str         # "1701-1702-14"
    split_year: Optional[int]
    start_day: Optional[int]
    start_month: Optional[str]
    end_day: Optional[int]
    end_month: Optional[str]

@dataclass
class BillOfMortalityRecord:
    parish_id: Optional[int]      # FK to parishes
    count_type: str              # "buried", "plague", "christened", or cause name
    count: Optional[int]
    year: int                    # FK to years
    joinid: str                  # FK to weeks
    bill_type: Optional[str]     # "weekly" or "general"
    missing: Optional[bool]
    illegible: Optional[bool]
    source: Optional[str]
    unique_identifier: Optional[str]
```

### JoinID System

**Purpose**: Links bill records to week records for temporal analysis

**Format**: `YYYYMMDDYYYYMMDD` (14 digits)
- Example: `1701031817010325` = March 18-25, 1701
- Format: `{year}{start_month_num:02d}{start_day:02d}{year}{end_month_num:02d}{end_day:02d}`

**Week 90 Convention**:
- Week 90 = Annual records (general bills)
- Weeks 1-52 = Regular weekly records
- Allows general bills to coexist with weekly data

**Weekly Bills**: Use date-based joinids
**General Bills**: Match existing week records with week 90

---

## Historical Data Handling

### Split-Year Logic

Historical bills often span calendar years:
- `"1701-1702-14"` = Week 14 bridging 1701 and 1702
- System preserves this in `week_id` field
- Uses primary year for `year` field (1701)

### Week Numbering

- **1-52**: Regular weekly bills
- **90**: Annual/general bill records
- Validates week numbers in this range

### Parish Name Preservation

**Critical**: Preserves exact historical spellings
- "Alhallows Barking" (not "All Hallows")
- "St Magnus Parish" (not standardized)
- Aggregate groups treated as distinct entities:
  - "Christened in the 97 parishes within the walls"
  - "Buried in the 97 parishes within the walls"
  - "Within the walls", "Without the walls", "Middlesex and Surrey"

### Bill Type Detection

Automatically determines bill type:
1. **Filename check**: "general" in filename → `general`
2. **Unique identifier check**: "GeneralBill" in record → `general`
3. **Week pattern check**: Week 90 → `general`
4. **Default**: `weekly`

### Source vs Bill Type

**Source Field**: Dataset/collection identifier
- `laxton_parishes` - Laxton collection (can contain both weekly and general)
- `blv1_parishes` - British Library Volume 1 (weekly only)
- `bodleian_parishes` - Bodleian collection (weekly only)
- `millar_parishes` - Millar collection (general only)

**Bill Type Field**: Report type
- `weekly` - Regular weekly mortality reports
- `general` - Annual/biannual summary reports

**Database Constraint**: `UNIQUE (parish_id, count_type, year, week_id, source, bill_type)`
- Including `bill_type` prevents weekly and general bills from overwriting each other

---

## Coding Conventions & Patterns

### File Naming

**Input CSVs** follow pattern: `YYYY-MM-DD-Source-billtype-datatype.csv`
- `2025-08-06-BLV1-weeklybills-causes.csv`
- `2025-04-20-Laxton-generalbills-parishes.csv`
- `2022-09-19-Laxton-1700-weeklybills-foodstuffs.csv`

**Output CSVs** are standardized table names:
- `parishes.csv`, `weeks.csv`, `years.csv`
- `all_bills.csv`, `causes_of_death.csv`
- `christenings.csv`, `christenings_by_parish.csv`, `christenings_by_gender.csv`
- `foodstuffs.csv`, `subtotals.csv`

### Code Style

**Formatting**: Black (line length 88) + isort
```bash
make format     # Auto-format
make lint       # Check formatting
```

**Type Checking**: mypy with strict settings
```python
# All functions require type hints
def process_data(df: pd.DataFrame, year: int) -> List[BillRecord]:
    ...
```

**Imports**: isort with black profile
```python
# Standard library
import sys
from pathlib import Path

# Third-party
import pandas as pd
from loguru import logger

# Local
from ..models import BillOfMortalityRecord
from ..utils.validation import SchemaValidator
```

### Logging Patterns

**Using loguru** (`from loguru import logger`)

```python
# Setup in main pipeline
from bom.utils.logging import setup_logging
log_file = setup_logging(log_level="INFO", log_name="bom_pipeline")

# Standard logging patterns
logger.info("Processing 25 datasets...")           # Progress
logger.success("✓ Generated 330K records")         # Success
logger.warning("Missing parish ID for: {name}")    # Warnings
logger.error("Failed to load {file}: {error}")     # Errors

# Use structured logging
logger.info(f"✓ {table_name}: {len(df):,} records → {output_file}")
```

**Log Files**: `logs/bom_pipeline_YYYY-MM-DD_HH-MM-SS_NNNNNN.log`

### Data Processing Patterns

**Always validate before saving**:
```python
validator = SchemaValidator()
valid_records = []
errors = []

for record in all_records:
    validation_errors = validator.validate_bill_of_mortality(record)
    if validation_errors:
        errors.extend(validation_errors)
    else:
        valid_records.append(record)
```

**Integer handling** (avoid `.0` in CSVs):
```python
# Use nullable integer type
if "year" in df.columns:
    df["year"] = df["year"].astype("Int64")
if "count" in df.columns:
    df["count"] = df["count"].astype("Int64")
```

**Count conversion** (handles mixed types):
```python
# Safely convert string/float to int
try:
    count = int(float(value)) if pd.notna(value) else None
except (ValueError, TypeError):
    count = None
```

### Deduplication Strategy

**Source-aware deduplication** (optional via `ENABLE_GLOBAL_DEDUPLICATION` flag):

```python
# Group by record key
key = (record.parish_id, record.count_type, record.year, record.joinid)

# Keep different sources (unique_identifier)
# Remove same-source duplicates (higher count wins)
if uid not in unique_id_to_record:
    unique_id_to_record[uid] = record
else:
    existing = unique_id_to_record[uid]
    if (record.count or 0) > (existing.count or 0):
        unique_id_to_record[uid] = record
```

**Purpose**: Preserve cross-source records while removing same-source duplicates

---

## Configuration Files

### `pyproject.toml`

**Package manager**: `uv` (not Poetry, despite some docs)
**Python version**: `~=3.10` (actually using 3.12 in practice)

**Dependencies**:
```toml
pandas~=2.0
pydantic~=2.0
typer>=0.9,<0.10
rich~=13.0
loguru>=0.7,<0.8
scipy<1.16
scikit-learn<1.5
jupyterlab>=4.4.5,<5
plotly>=6.2.0,<7
matplotlib>=3.10.5,<4
seaborn>=0.13.2,<0.14
```

**Dev dependencies**:
```toml
pytest~=7.0
black~=23.0
isort~=5.0
mypy~=1.0
```

**Tool configs**:
```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"

[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = true
```

### `src/bom/config.py`

**Dataset patterns** (regex for filename matching):
```python
DATASET_PATTERNS = {
    "laxton_parishes": r"laxton.*parishes",
    "blv1_parishes": r"blv1.*parishes",
    "bodleian_causes": r"bodleian.*causes",
    ...
}
```

**Column normalization** (name mapping only):
```python
COLUMN_NORMALIZATION = {
    "Unique ID": "unique_identifier",
    "Week Number": "week_number",
    "Start Day": "start_day",
    ...
}
```

**Skip patterns** (metadata columns to ignore):
```python
SKIP_COLUMN_PATTERNS = [
    r"omeka.*item",
    r"datascribe.*item",
    r"image.*filename",
]
```

### `.pre-commit-config.yaml`

Uses Ruff (not black/isort):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff-format  # formatter
      - id: ruff-check   # linter
```

**Note**: Makefile still references black/isort commands

---

## Common Tasks & Patterns

### Adding New Dataset Types

**1. If filename matches existing patterns**: Just add CSV to `data-raw/` and run `make process-all`

**2. If new naming pattern**: Update `src/bom/config.py`:
```python
DATASET_PATTERNS = {
    # Add new pattern
    "your_new_source": r"your_pattern.*parishes",
}
```

**3. If new column variations**: Update `COLUMN_NORMALIZATION` in config:
```python
COLUMN_NORMALIZATION = {
    "Your Column Name": "standard_column_name",
}
```

### Creating New Processors

**Pattern**: Follow `src/bom/processors/bills.py` structure

```python
class NewProcessor:
    def __init__(self):
        self.validator = SchemaValidator()
        
    def process_datasets(
        self, 
        datasets: Dict[str, pd.DataFrame]
    ) -> List[NewRecord]:
        records = []
        for name, df in datasets.items():
            # Process each dataset
            for _, row in df.iterrows():
                record = self._create_record(row)
                if record:
                    records.append(record)
        return records
    
    def get_records(self) -> List[NewRecord]:
        return self.records
```

**Then**:
1. Add model to `src/bom/models.py`
2. Add validation to `src/bom/utils/validation.py`
3. Wire into `process_all_data.py`
4. Add tests to `tests/test_new_processor.py`

### Debugging Data Issues

**1. Check column normalization**:
```bash
uv run tests/debug_columns.py
```

**2. Check parish extraction**:
```bash
uv run tests/debug_parish_extraction.py
```

**3. Examine specific dataset**:
```python
from bom.loaders import CSVLoader

loader = CSVLoader()
df, info = loader.load(Path("data-raw/your-file.csv"))

print(f"Columns: {df.columns.tolist()}")
print(f"Dataset type: {info.dataset_type}")
print(df.head())
```

**4. Test specific processor**:
```bash
make test-bills        # Test bills processor
make test-schema       # Test schema alignment
```

**5. Analyze logs**:
```bash
make show-logs         # List recent logs
make tail-logs         # Follow most recent log
```

### Schema Validation

**Validate before saving**:
```python
from bom.utils.validation import SchemaValidator

validator = SchemaValidator()

# Validate single record
errors = validator.validate_bill_of_mortality(record)
if errors:
    logger.error(f"Validation failed: {errors}")

# Validate batch
valid_records = []
for record in all_records:
    if not validator.validate_bill_of_mortality(record):
        valid_records.append(record)
```

**Common validation checks**:
- Year in range 1400-1800
- Week number in range 1-90
- Foreign key references exist (parish_id, joinid)
- Required fields present
- Data types correct

### Testing Changes

**Test workflow**:
```bash
# 1. Make changes
vim src/bom/processors/bills.py

# 2. Format
make format

# 3. Check quality
make check

# 4. Test specific component
make test-bills

# 5. Run full pipeline on sample
make process-all

# 6. Validate outputs
make validate-outputs

# 7. Check statistics
make show-stats
```

---

## Common Issues & Solutions

### Column Normalization vs Data Corruption

**Issue**: Accidentally corrupting parish names or data values during normalization

**Solution**: 
- Column normalization happens ONLY in `src/bom/utils/columns.py`
- Never modify data values, only column names
- Use `COLUMN_NORMALIZATION` dict for explicit mappings
- Test with `tests/debug_columns.py`

**Example**:
```python
# ✓ CORRECT: Normalize column name
df.rename(columns={"Parish Name": "parish_name"})

# ✗ WRONG: Don't normalize data values
df["parish_name"] = df["parish_name"].str.lower()  # Corrupts historical names!
```

### Schema Mismatches with PostgreSQL

**Issue**: Generated CSV fails to import into PostgreSQL

**Solution**: Check alignment at three levels:
1. Generated CSV headers
2. Temp table structure in Go updater (`go-updater/main.go` lines 178-197)
3. Final PostgreSQL table schema in `DDLs.txt`

**Example**:
```python
# christenings_by_parish.csv column: parish_name
# → Go updater temp table: parish_name
# → transforms to → bom.christenings table: christening
# → Go updater handles this mapping
```

### Week/Parish ID Mismatches

**Issue**: Bill records reference non-existent week/parish IDs

**Solution**:
- Ensure extractors run before processors
- Use same week/parish record lists throughout pipeline
- Check foreign key relationships in validation

```python
# In process_all_data.py
week_records = week_extractor.extract_weeks(...)  # Extract first
parish_records = parish_extractor.extract_parishes(...)  # Extract first

# Then pass to processors
bills_processor.process_parish_dataframes(
    dataframes, 
    parish_records,  # Pass extracted records
    week_records     # Pass extracted records
)
```

### Decimal Values in Integer Columns

**Issue**: Pandas converts integers to float when NaN present, causing `.0` in CSV

**Solution**: Use nullable integer type `"Int64"`
```python
df["year"] = df["year"].astype("Int64")
df["count"] = df["count"].astype("Int64")
df["week_number"] = df["week_number"].astype("Int64")
```

### Missing General Bills

**Issue**: General bills not appearing in database after import

**Solution**: 
- Check joinIDs match week records: `grep -F "joinid" data/weeks.csv`
- Verify database constraint includes `bill_type` field
- Check Go updater WHERE clause includes week existence check
- Ensure week 90 records exist for general bill years

### Source Field Shows Full Paths

**Issue**: Source column contains full file paths instead of dataset type labels

**Solution**: Use `info.dataset_type` instead of `info.file_path`
```python
# ✓ CORRECT
(df, name, info.dataset_type) for df, name, info in all_dataframes

# ✗ WRONG  
(df, name, info.file_path) for df, name, info in all_dataframes
```

---

## Database Integration

### PostgreSQL Schema

Defined in `DDLs.txt` (external to this repo):

**Core tables**:
- `bom.year` - Valid years 1400-1800
- `bom.week` - Week records with joinid primary key
- `bom.parishes` - Parish lookup with canonical names
- `bom.bill_of_mortality` - Individual bill records
- `bom.christenings` - Christening data
- `bom.causes_of_death` - Death cause records

**Foreign key relationships**:
- `bill_of_mortality.year` → `year.year`
- `bill_of_mortality.joinid` → `week.joinid`
- `bill_of_mortality.parish_id` → `parishes.id`

**Unique constraints**:
```sql
UNIQUE (parish_id, count_type, year, week_id, source, bill_type)
```

### Go Updater

**Location**: `go-updater/` directory (sibling to this repo)

**Purpose**: 
- Creates temporary tables matching CSV structure
- Transforms data during import (e.g., `parish_name` → `christening`)
- Handles upsert logic with conflict resolution
- Maintains referential integrity

**Key transformation**:
```go
// christenings_by_parish.csv structure
type TempChristening struct {
    ParishName   string  // Input from CSV
    WeekNumber   int     // Input from CSV
    Year         int
    Count        int
    // ... other fields
}

// Transforms to bom.christenings table
INSERT INTO bom.christenings (
    christening,    -- Mapped from parish_name
    week_number,    -- Mapped from week
    year,
    count,
    ...
)
```

**Conflict resolution**:
- Weekly vs General: Treated as separate records (different `bill_type`)
- Same type duplicates: Higher count value wins
- Null vs Non-null: Non-null count value wins

### Import Process

**1. Generate CSVs**: `make process-all`

**2. Import to PostgreSQL** (in order):
```sql
\COPY bom.year FROM 'years.csv' DELIMITER ',' CSV HEADER;
\COPY bom.parishes FROM 'parishes.csv' DELIMITER ',' CSV HEADER;
\COPY bom.week FROM 'weeks.csv' DELIMITER ',' CSV HEADER;
\COPY bom.bill_of_mortality FROM 'all_bills.csv' DELIMITER ',' CSV HEADER;
```

**3. Run Go updater** for specialized tables:
```bash
cd ../go-updater
go run main.go
```

---

## Testing & Validation

### Test Structure

**Unit tests**: `tests/test_*.py` (pytest format)
```bash
make test               # Run all pytest tests
uv run pytest tests/ -v  # Verbose output
```

**Integration tests**: `tests/test_bills_processor.py`, `tests/test_schema_alignment.py`
```bash
make test-bills         # Test bills processor
make test-schema        # Test schema alignment
```

**Diagnostic scripts**: `tests/debug_*.py`, `tests/analyze_*.py`
```bash
uv run tests/debug_columns.py           # Debug column normalization
uv run tests/debug_parish_extraction.py # Debug parish extraction
uv run tests/analyze_coverage_gap.py    # Analyze data coverage
```

### Validation Strategy

**Three-level validation**:

1. **Input validation** (CSVLoader):
   - Check file exists and is readable
   - Validate essential columns present
   - Normalize column names

2. **Processing validation** (Processors):
   - Check parish/week/year IDs exist
   - Validate data types
   - Handle missing/illegible data flags

3. **Output validation** (SchemaValidator):
   - Ensure PostgreSQL schema compliance
   - Check foreign key references
   - Validate constraints (year range, week range)

**Validation logging**:
```python
log_validation_results(
    component="Bills of Mortality",
    total_records=len(all_records),
    valid_records=len(valid_records),
    validation_errors=errors
)
```

### Data Quality Checks

**Coverage analysis**:
```bash
make check-coverage     # Analyze gaps by parish/year
```

**Statistics**:
```bash
make show-stats         # Show record counts per file
```

**Duplication analysis**:
- Source-aware deduplication in `process_all_data.py`
- Outputs to `data/duplicate_bills.csv`, `data/duplicate_bills_removable.csv`
- Analysis notebooks in `notebooks/09_duplication_analysis_*.ipynb`

---

## Jupyter Notebooks

**Location**: `notebooks/`

**Available notebooks** (12 total):
- `01_data_exploration.ipynb` - Dataset overview
- `02_temporal_analysis.ipynb` - Time series analysis
- `03_parish_analysis.ipynb` - Geographic patterns
- `04_data_quality.ipynb` - Quality assessment
- `05_causes_of_death_analysis.ipynb` - Cause analysis
- `06_foodstuffs_analysis.ipynb` - Price data
- `07_christenings_analysis.ipynb` - Birth records
- `08_mathematical_accuracy.ipynb` - Arithmetic validation
- `09_duplication_analysis_cod.ipynb` - Cause duplicates
- `09_duplication_analysis_parishes.ipynb` - Parish duplicates
- `11_external_data_comparison.ipynb` - Compare with external sources
- `12_visualization_analysis.ipynb` - Visualization gallery

**Commands** (if Makefile had them - not currently present):
```bash
# These would be useful additions to Makefile:
jupyter lab notebooks/              # Launch Jupyter
jupyter nbconvert --to html *.ipynb  # Convert to HTML
jupyter nbconvert --clear-output *.ipynb  # Clean outputs
```

**Current approach**:
```bash
uv run jupyter lab notebooks/
```

---

## Performance Notes

**Processing speed**: ~30 seconds for 29 CSV files → 330K records

**Memory usage**: Scales with number of parish columns (wide format)

**Bottlenecks**:
- Parish column detection in wide DataFrames
- Record generation (converting wide → tall format)
- Schema validation for large record sets

**Optimization opportunities**:
- Parallel processing of independent datasets
- Vectorized operations for large DataFrames
- Incremental processing for unchanged files
- Database bulk loading instead of row-by-row upserts

---

## Data Sources & Historical Context

### Archival Collections

**Laxton Collection**: Weekly bills from 1700s (largest source)
- Files: `*Laxton*` patterns
- Contains: parishes, causes, gender, foodstuffs, general bills

**British Library (BL)**: Multiple volumes
- BLV1: `*BLV1*` - 1673-1674 weekly bills
- BLV2: `*BLV2*` - Additional weekly bills
- BLV3: `*BLV3*` - Additional weekly bills
- BLV4: `*BLV4*` - Missing bills dataset + original dataset
- Special: `*BL1877*` - Post-fire data

**Bodleian Library**: Various versions
- V1, V2, V3: `*Bodleian*` - Weekly bills (parishes + causes)

**Other sources**:
- Wellcome Collection: `*Wellcome*` - 1669-1670 data
- Huntington Library (HEH): `*HEH*` - 1635 bills
- Millar Collection: `*millar*` - General bills (pre/post plague)
- Queen's College (QC): `*QC*` - Weekly bills
- DataScribe exports: `*datascribe*` - Direct DataScribe outputs

### Historical Context

**Time period**: 1400-1800 (validated range), primary data 1600s-1700s

**Key events tracked**:
- Great Plague (1665-1666): Massive mortality spike
- Great Fire (1666): Population displacement
- Seasonal patterns: Higher winter mortality
- General bills: Annual summaries (often week 90)

**Geographic divisions**:
- "Within the walls" - City of London proper
- "Without the walls" - Suburbs just outside walls
- "Middlesex and Surrey" - Outer parishes
- "Westminster" - Separate jurisdiction

---

## Git & Version Control

**Important files to commit**:
- `src/bom/**/*.py` - All source code
- `tests/**/*.py` - All tests
- `Makefile`, `pyproject.toml`, `uv.lock` - Configuration
- `*.md` - Documentation
- `.pre-commit-config.yaml` - Git hooks

**Files to ignore** (in `.gitignore`):
- `.venv/` - Virtual environment
- `__pycache__/`, `*.pyc` - Python cache
- `.pytest_cache/`, `.mypy_cache/` - Tool caches
- `logs/` - Log files
- `data/*.csv` - Generated outputs (large)
- `data-raw/*.csv` - Raw inputs (managed externally)
- `.DS_Store`, `.idea/` - Editor artifacts

**Note**: This is NOT a git repository currently (no .git/)

---

## External Dependencies

### Go Updater

**Location**: `go-updater/` (sibling directory, not in this repo)

**Purpose**: Database import with transformations

**Key file**: `main.go` lines 178-197 (temp table structures)

**Must align**: CSV columns → temp tables → final PostgreSQL schema

### BOM Data Repository

**Location**: `../../../bom-data/data-csvs/` (referenced in Makefile)

**Purpose**: Central repository of raw DataScribe CSV exports

**Command**: `make copy-data` copies from this location to `data-raw/`

### DDLs File

**Location**: `DDLs.txt` (referenced in docs, likely external)

**Purpose**: PostgreSQL schema definitions

**Contains**: All `CREATE TABLE` statements with constraints

---

## Memory File Instructions (CLAUDE.md)

The existing CLAUDE.md contains Claude-specific guidance. Key points:

**Priority over this file**: If CLAUDE.md and AGENTS.md conflict, follow CLAUDE.md for Claude-specific behavior

**Key differences**:
- CLAUDE.md: More Claude-specific workflow guidance
- AGENTS.md (this file): More comprehensive technical reference

**Commands**: CLAUDE.md shows Poetry commands, but actual commands use `uv` (see Makefile)

**When to update**:
- CLAUDE.md: Claude-specific workflows, known issues, decision points
- AGENTS.md: Technical reference, architecture, patterns, conventions

---

## Quick Reference

### Most Common Workflows

**1. Process new data**:
```bash
make copy-data          # Get raw CSVs
make process-all        # Process → outputs
make show-stats         # Verify results
```

**2. Debug data issues**:
```bash
uv run tests/debug_columns.py              # Column issues
uv run tests/debug_parish_extraction.py    # Parish issues
make tail-logs                             # Check logs
```

**3. Develop new feature**:
```bash
vim src/bom/processors/new_processor.py    # Implement
make format                                # Format code
make check                                 # Check quality
make test                                  # Run tests
make process-all                           # Test integration
```

**4. Code quality check**:
```bash
make format             # Auto-format
make check              # Lint + typecheck
make test               # Run tests
```

### Key Files to Check First

1. `Makefile` - All available commands
2. `pyproject.toml` - Dependencies and tool configs
3. `src/bom/config.py` - Dataset patterns and column mappings
4. `src/bom/models.py` - Data structures (PostgreSQL-aligned)
5. `process_all_data.py` - Main pipeline logic
6. `DEVNOTES.md` - Technical details and gotchas

### Critical Paths

- **Input**: `data-raw/*.csv` (29 files from archives)
- **Output**: `data/*.csv` (11 PostgreSQL-ready files)
- **Logs**: `logs/bom_pipeline_*.log` (timestamped)
- **Source**: `src/bom/` (~5,000 lines of modular Python)

---

## Additional Resources

**Documentation hierarchy**:
1. **AGENTS.md** (this file) - Comprehensive technical reference
2. **CLAUDE.md** - Claude-specific guidance and workflows
3. **README.md** - User-facing project documentation
4. **DEVNOTES.md** - Developer technical notes and gotchas
5. **Makefile** - All commands with inline help
6. **notebooks/README.md** - Jupyter notebook guide

**For more information**:
- Check `make help` for all available commands
- Review test files in `tests/` for usage examples
- Examine notebooks for data analysis patterns
- Read processor source code for implementation details

**Contact**: jason@jasonheppler.org (project maintainer)

"""Configuration and constants for BOM processing."""

from pathlib import Path
from typing import Dict, List

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data-raw"
DATA_OUTPUT_DIR = PROJECT_ROOT / "data"

# Dataset type patterns - used to identify dataset types from filenames
DATASET_PATTERNS = {
    "wellcome_causes": r"wellcome.*causes",
    "wellcome_parishes": r"wellcome.*parishes", 
    "laxton_causes": r"laxton.*causes",
    "laxton_parishes": r"laxton.*parishes",
    "bodleian_causes": r"bodleian.*causes",
    "bodleian_parishes": r"bodleian.*parishes",
    # British Library volumes - distinguish by volume number and dataset type
    "blv1_parishes": r"blv1.*parishes",
    "blv2_parishes": r"blv2.*parishes",
    "blv3_parishes": r"blv3.*parishes",
    "blv4_parishes_original": r"blv4.*originaldataset",
    "blv4_parishes_missing": r"blv4.*missingbillsdataset",
    "heh_parishes": r"heh.*parishes",
    "millar_parishes": r"millar.*parishes",
    "qc_parishes": r"qc.*parishes",
    "qc_causes": r"qc.*causes",
    "datascribe_parishes": r"datascribe.*dataset",
    "bl_parishes": r"bl1877.*minus3foldbill",  # Special BL file with parish data
    "bl_special": r"bl1877.*",
    "laxton_foodstuffs": r"laxton.*foodstuffs",
    "laxton_gender": r"laxton.*gender",
}

# Column mappings - normalize column names without affecting data
COLUMN_NORMALIZATION = {
    # Common variations
    "Unique ID": "unique_identifier",
    "Unique_ID": "unique_identifier", 
    "unique_id": "unique_identifier",
    "UniqueID": "unique_identifier",
    "Unique Identifier": "unique_identifier",
    
    # Date columns
    "Start Day": "start_day",
    "End Day": "end_day",
    "Start Month": "start_month", 
    "End Month": "end_month",
    "Start Year": "start_year",
    "End Year": "end_year",
    
    # Week columns
    "Week Number": "week_number",
    "Week": "week",
    
    # Other common columns
    "Year": "year",
    "Parish Name": "parish_name",
    "Count": "count",
}

# Data types for consistent processing
COLUMN_TYPES = {
    "year": "int64",
    "week": "str", 
    "week_number": "str",
    "start_day": "str",
    "end_day": "str", 
    "start_month": "str",
    "end_month": "str",
    "unique_identifier": "str",
    "parish_name": "str",
    "count": "str",  # Keep as string initially to handle mixed types
}

# Skip columns - these are typically metadata we don't need for processing
SKIP_COLUMN_PATTERNS = [
    r"omeka.*item",
    r"datascribe.*item", 
    r"datascribe.*record",
    r"datascribe.*position",
    r"image.*filename",
]

# Essential columns that must exist for processing
ESSENTIAL_COLUMNS = ["year"]

# Optional columns that we handle gracefully if missing
OPTIONAL_COLUMNS = [
    "week", "week_number", "start_day", "end_day", 
    "start_month", "end_month", "unique_identifier", 
    "parish_name", "count"
]
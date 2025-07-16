"""
Helper functions for processing Bills of Mortality data.

This module contains Python conversions of the R helper functions
for processing DataScribe exports and other historical data sources.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_data_check(data: pd.DataFrame, stage_name: str) -> bool:
    """
    Check data for duplicates and log statistics.

    Args:
        data: DataFrame to check
        stage_name: Name of the processing stage

    Returns:
        True if duplicates found, False otherwise
    """
    total_rows = len(data)
    distinct_rows = len(data.drop_duplicates())
    duplicates = total_rows - distinct_rows

    logger.info(f"\n=== Data Check: {stage_name} ===")
    logger.info(f"Total rows: {total_rows}")
    logger.info(f"Distinct rows: {distinct_rows}")
    logger.info(f"Duplicate rows: {duplicates}")

    if duplicates > 0:
        dupes = data[data.duplicated(keep=False)]
        logger.info(f"\nSample of duplicated rows:")
        logger.info(dupes.head(10))

    return duplicates > 0


def check_whitespace(df: pd.DataFrame) -> None:
    """Check for leading/trailing whitespace in key columns."""
    cols_to_check = [
        "parish_name",
        "count_type",
        "unique_identifier",
        "start_month",
        "end_month",
    ]

    for col in cols_to_check:
        if col in df.columns:
            # Check for leading/trailing whitespace
            whitespace_mask = df[col].astype(str).str.match(r"^\s|\s$")
            whitespace_issues = df[whitespace_mask]

            if len(whitespace_issues) > 0:
                logger.info(
                    f"Found {len(whitespace_issues)} rows with whitespace issues in {col}:"
                )
                logger.info(whitespace_issues[col].head(5))


def month_to_number(month_name: str) -> str:
    """Convert month name to zero-padded number string."""
    month_map = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12",
    }
    return month_map.get(month_name, "00")


def process_bodleian_data(data: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Process Bodleian data exports with proper handling of missing flag columns.

    Args:
        data: Raw DataScribe export
        source_name: Name of the data source

    Returns:
        Processed DataFrame with consistent structure
    """
    logger.info(f"Processing Bodleian {source_name} data...")

    # Standardize column names
    column_map = {
        "Unique ID": "UniqueID",
        "Unique_ID": "UniqueID",
        "unique_id": "UniqueID",
        "End month": "End Month",
        # Standardize DataScribe metadata column names
        "Omeka Item #": "omeka_item_no",
        "DataScribe Item #": "datascribe_item_no", 
        "DataScribe Record #": "datascribe_record_no",
        "DataScribe Record Position": "datascribe_record_position",
    }
    data = data.rename(columns=column_map)

    # Standardize column data types
    data = data.assign(
        **{
            col: data[col].astype(str).str.strip()
            for col in data.select_dtypes(include=["object"]).columns
        }
    )

    # Convert numeric columns
    numeric_cols = ["Year", "Week", "Start Day", "End Day"]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # String columns
    string_cols = ["Start Month", "End Month"]
    for col in string_cols:
        if col in data.columns:
            data[col] = data[col].astype(str)

    # Check for illegible and missing columns
    illegible_cols = [col for col in data.columns if col.startswith("is_illegible")]
    missing_cols = [col for col in data.columns if col.startswith("is_missing")]

    # Convert existing flag columns to boolean
    for col in illegible_cols + missing_cols:
        data[col] = data[col].fillna(False).astype(bool)

    # Process main data (parishes) - exclude flag columns and DataScribe metadata
    metadata_cols = [
        "Year",
        "Week",
        "UniqueID",
        "Start Day",
        "Start Month",
        "End Day",
        "End Month",
    ]
    
    flag_cols = illegible_cols + missing_cols

    # Get parish columns (everything except metadata and flags)
    parish_cols = [
        col
        for col in data.columns
        if col not in metadata_cols
        and col not in flag_cols
        and not col.startswith("omeka_")
        and not col.startswith("datascribe_")
        and not col.startswith("Omeka")
        and not col.startswith("DataScribe")
    ]

    # Create main data 
    main_data = data[metadata_cols + parish_cols].melt(
        id_vars=metadata_cols,
        value_vars=parish_cols,
        var_name="parish_name",
        value_name="count",
    )

    # Process illegible flags
    if illegible_cols:
        illegible_data = data[metadata_cols + illegible_cols].melt(
            id_vars=metadata_cols,
            value_vars=illegible_cols,
            var_name="parish_name",
            value_name="illegible",
        )
        illegible_data["parish_name"] = illegible_data["parish_name"].str.replace(
            "is_illegible_", ""
        )
        illegible_data["illegible"] = (
            illegible_data["illegible"].fillna(False).astype(bool)
        )
    else:
        # Create default illegible data
        illegible_data = main_data[metadata_cols + ["parish_name"]].copy()
        illegible_data["illegible"] = False

    # Process missing flags
    if missing_cols:
        missing_data = data[metadata_cols + missing_cols].melt(
            id_vars=metadata_cols,
            value_vars=missing_cols,
            var_name="parish_name",
            value_name="missing",
        )
        missing_data["parish_name"] = missing_data["parish_name"].str.replace(
            "is_missing_", ""
        )
        missing_data["missing"] = missing_data["missing"].fillna(False).astype(bool)
    else:
        # Create default missing data
        missing_data = main_data[metadata_cols + ["parish_name"]].copy()
        missing_data["missing"] = False

    # Join the data
    combined_data = main_data.merge(
        illegible_data, on=metadata_cols + ["parish_name"], how="left"
    ).merge(missing_data, on=metadata_cols + ["parish_name"], how="left")

    # Fill any remaining NaN values in flag columns
    combined_data["illegible"] = combined_data["illegible"].fillna(False)
    combined_data["missing"] = combined_data["missing"].fillna(False)

    # Add source
    combined_data["source"] = source_name

    logger.info(f"Processed Bodleian {source_name} data: {len(combined_data)} rows")

    return combined_data


def process_weekly_bills(
    data: pd.DataFrame, source_name: str, has_flags: bool = True
) -> pd.DataFrame:
    """
    Process weekly bills data from various sources.

    Args:
        data: Raw DataScribe export
        source_name: Name of the data source
        has_flags: Whether data has is_illegible/is_missing columns

    Returns:
        Processed DataFrame with consistent structure
    """
    logger.info(f"Processing {source_name} data...")

    # Identify metadata columns
    metadata_pattern = r"year|week|unique|start|end"
    metadata_cols = [
        col for col in data.columns if re.search(metadata_pattern, col.lower())
    ]

    # Identify parish columns
    flag_pattern = r"^is_(illegible|missing)"
    parish_cols = [
        col
        for col in data.columns
        if not re.search(metadata_pattern, col.lower())
        and not re.search(flag_pattern, col.lower())
    ]

    # Standardize types for key columns
    if "Year" in data.columns:
        data["Year"] = data["Year"].astype(str)
    if "Week" in data.columns:
        data["Week"] = data["Week"].astype(str)

    if has_flags:
        # Process data with flags
        result = process_flagged_data(data, source_name)
    else:
        # Process data without flags
        result = process_unflagged_data(data, source_name)

    # Standardize column names
    result = result.rename(
        columns={
            "unique id": "unique_identifier",
            "unique_id": "unique_identifier",
            "end month": "end_month",
        }
    )

    # Convert column names to lowercase and replace spaces with underscores
    result.columns = [col.lower().replace(" ", "_") for col in result.columns]

    # Preserve parish_name case
    if "parish_name" in result.columns:
        pass  # Keep as-is

    # Add source
    result["source"] = source_name

    return result


def process_flagged_data(data: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Process data that has illegible and missing flags."""
    # Convert column names to lowercase for consistency
    data.columns = [col.lower() for col in data.columns]

    if "year" in data.columns:
        data["year"] = data["year"].astype(str)

    # Identify columns
    metadata_cols = [
        "year",
        "week",
        "unique_id",
        "start_day",
        "start_month",
        "end_day",
        "end_month",
    ]
    metadata_cols = [col for col in metadata_cols if col in data.columns]

    illegible_cols = [col for col in data.columns if col.startswith("is_illegible")]
    missing_cols = [col for col in data.columns if col.startswith("is_missing")]

    # Process illegible flags
    if illegible_cols:
        illegible_data = data[metadata_cols + illegible_cols].melt(
            id_vars=metadata_cols,
            value_vars=illegible_cols,
            var_name="parish_name",
            value_name="illegible",
        )
        illegible_data["parish_name"] = illegible_data["parish_name"].str.replace(
            "is_illegible_", ""
        )
        illegible_data["illegible"] = (
            illegible_data["illegible"].fillna(False).astype(bool)
        )
    else:
        illegible_data = pd.DataFrame()

    # Process missing flags
    if missing_cols:
        missing_data = data[metadata_cols + missing_cols].melt(
            id_vars=metadata_cols,
            value_vars=missing_cols,
            var_name="parish_name",
            value_name="missing",
        )
        missing_data["parish_name"] = missing_data["parish_name"].str.replace(
            "is_missing_", ""
        )
        missing_data["missing"] = missing_data["missing"].fillna(False).astype(bool)
    else:
        missing_data = pd.DataFrame()

    # Process main data
    flag_cols = illegible_cols + missing_cols
    parish_cols = [
        col for col in data.columns if col not in metadata_cols and col not in flag_cols
    ]

    main_data = data[metadata_cols + parish_cols].melt(
        id_vars=metadata_cols,
        value_vars=parish_cols,
        var_name="parish_name",
        value_name="count",
    )

    main_data["count"] = pd.to_numeric(main_data["count"], errors="coerce")
    main_data["missing"] = False
    main_data["illegible"] = False

    # Combine data
    if not illegible_data.empty:
        main_data = main_data.merge(
            illegible_data[metadata_cols + ["parish_name", "illegible"]],
            on=metadata_cols + ["parish_name"],
            how="left",
            suffixes=("", "_ill"),
        )
        main_data["illegible"] = main_data["illegible_ill"].fillna(
            main_data["illegible"]
        )
        main_data = main_data.drop("illegible_ill", axis=1)

    if not missing_data.empty:
        main_data = main_data.merge(
            missing_data[metadata_cols + ["parish_name", "missing"]],
            on=metadata_cols + ["parish_name"],
            how="left",
            suffixes=("", "_miss"),
        )
        main_data["missing"] = main_data["missing_miss"].fillna(main_data["missing"])
        main_data = main_data.drop("missing_miss", axis=1)

    return main_data


def process_unflagged_data(data: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Process data without illegible/missing flags."""
    # Get first 7 columns as metadata, rest as parish data
    metadata_cols = data.columns[:7].tolist()
    parish_cols = data.columns[7:].tolist()

    result = data.melt(
        id_vars=metadata_cols,
        value_vars=parish_cols,
        var_name="parish_name",
        value_name="count",
    )

    result["missing"] = False
    result["illegible"] = False

    return result


def process_general_bills(data: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Process general bills data from various sources.
    
    Args:
        data: Raw DataScribe export
        source_name: Name of the data source
        
    Returns:
        Processed DataFrame with consistent structure
    """
    logger.info(f"Processing general bills from {source_name}...")
    
    # Check if this is pre-plague format (with burial/plague split)
    is_pre_plague = any(data.columns.str.contains(r" - (?:Buried|Plague)$"))
    
    if is_pre_plague:
        logger.info("Detected pre-plague format with burial/plague split")
        # Handle pre-plague format - select relevant columns
        metadata_cols = ["Start day", "Start month", "Start year",
                        "End day", "End month", "End year", "Unique Identifier"]
        
        # Get metadata columns that exist
        existing_metadata = [col for col in metadata_cols if col in data.columns]
        
        parish_cols = [col for col in data.columns if col.endswith(" - Buried") or col.endswith(" - Plague")]
        
        clean_data = data[existing_metadata + parish_cols]
        
        # Pivot the data
        general_bills = clean_data.melt(
            id_vars=existing_metadata,
            value_vars=parish_cols,
            var_name="parish_type",
            value_name="count"
        )
        
        # Split parish name and count type
        split_data = general_bills["parish_type"].str.extract(r"(.+) - (Buried|Plague)$")
        general_bills["parish_name"] = split_data[0].str.strip()
        general_bills["count_type"] = split_data[1]
        general_bills = general_bills.drop("parish_type", axis=1)
        
    else:
        logger.info("Detected post-plague format")
        # Handle post-plague format
        metadata_cols = ["Start day", "Start month", "Start year",
                        "End day", "End month", "End year", "Unique Identifier"]
        
        existing_metadata = [col for col in metadata_cols if col in data.columns]
        
        parish_cols = [col for col in data.columns if col not in existing_metadata and 
                      not col.startswith("is_") and not col.startswith("omeka_") and 
                      not col.startswith("datascribe_") and not col.startswith("Omeka") and
                      not col.startswith("DataScribe")]
        
        general_bills = data[existing_metadata + parish_cols].melt(
            id_vars=existing_metadata,
            value_vars=parish_cols,
            var_name="parish_name",
            value_name="count"
        )
        general_bills["count_type"] = "Total"
    
    # Common processing for both formats
    general_bills = general_bills.assign(
        week=90,
        bill_type="General",
        parish_name=lambda x: x["parish_name"].str.strip(),
        source=source_name
    )
    
    # Standardize column names
    general_bills.columns = [col.lower().replace(" ", "_") for col in general_bills.columns]
    
    # Extract year from unique identifier if needed
    if "unique_identifier" in general_bills.columns:
        general_bills["year"] = general_bills["unique_identifier"].str.extract(r"(\d{4})")
        general_bills["year"] = pd.to_numeric(general_bills["year"], errors="coerce")
    
    logger.info(f"Processed {len(general_bills)} rows")
    logger.info(f"Distinct parishes: {general_bills['parish_name'].nunique()}")
    
    return general_bills


def check_data_quality(df: pd.DataFrame) -> None:
    """Check data quality and report issues."""
    # Check for NA values
    na_counts = df.isnull().sum()
    na_counts = na_counts[na_counts > 0]

    if len(na_counts) > 0:
        logger.info("\nFound NA values:")
        logger.info(na_counts)

    # Check for suspicious parish names
    if "parish_name" in df.columns:
        suspicious_parishes = df[
            df["parish_name"].str.contains(r"^\s|\s$", na=False)
            | df["parish_name"].str.contains(r"Total|Sum|All", na=False)
            | (df["parish_name"].str.len() < 3)
        ]["parish_name"].drop_duplicates()

        if len(suspicious_parishes) > 0:
            logger.info("\nSuspicious parish names found:")
            logger.info(suspicious_parishes.tolist())

    # Check for extreme count values
    if "count" in df.columns:
        logger.info("\nCount summary:")
        logger.info(df["count"].describe())

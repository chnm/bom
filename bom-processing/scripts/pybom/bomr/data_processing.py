"""
Advanced data processing functions for Bills of Mortality data.

This module contains the more complex data processing functions
converted from the R helpers.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from .helpers import month_to_number

logger = logging.getLogger(__name__)


def extract_aggregate_entries(
    data: pd.DataFrame, dataset_name: str
) -> Dict[str, pd.DataFrame]:
    """
    Extract aggregate entries (christenings, burials, plague, parish status) from data.

    Args:
        data: Input DataFrame
        dataset_name: Name of the dataset for logging

    Returns:
        Dictionary with separate DataFrames for each aggregate type
    """
    logger.info(
        "Processing aggregate data (totals, parish status, and special counts)..."
    )

    # Identify entries by their patterns - removed capture groups to avoid warnings
    pattern = (
        r"^(?:Christened|Buried|Plague) in|"
        r"^Parishes (?:Infected|Clear)|"
        r"^Total|"
        r"Parishes Infected|"
        r"Parishes Clear of the Plague|"
        r"Total Christenings|"
        r"Total of all Burials|"
        r"Total of all Plague"
    )

    entries_to_process = data[data["parish_name"].str.contains(pattern, na=False)]

    # Create detection columns - removed capture groups to avoid warnings
    entries_with_types = entries_to_process.assign(
        christening_detect=entries_to_process["parish_name"].str.contains(
            r"^(?:Christened in|Total Christenings)", na=False
        ),
        burials_detect=entries_to_process["parish_name"].str.contains(
            r"^(?:Buried in|Total of all Burials)", na=False
        ),
        plague_detect=entries_to_process["parish_name"].str.contains(
            r"^(?:Plague in|Total of all Plague)", na=False
        ),
        parish_status_detect=entries_to_process["parish_name"].str.contains(
            r"^Parishes (?:Infected|Clear)", na=False
        ),
    )

    # Extract each type
    results = {}

    # Christenings
    christenings = entries_with_types[entries_with_types["christening_detect"]].copy()
    if len(christenings) > 0:
        christenings["joinid"] = (
            christenings["start_day"].astype(str)
            + christenings["start_month"].astype(str)
            + christenings["end_day"].astype(str)
            + christenings["end_month"].astype(str)
            + christenings["year"].astype(str)
        )
        christenings = christenings.drop(
            columns=[col for col in christenings.columns if col.endswith("_detect")]
        )
    results["christenings"] = christenings

    # Burials
    burials = entries_with_types[entries_with_types["burials_detect"]].copy()
    if len(burials) > 0:
        burials = burials.drop(
            columns=[col for col in burials.columns if col.endswith("_detect")]
        )
    results["burials"] = burials

    # Plague
    plague = entries_with_types[entries_with_types["plague_detect"]].copy()
    if len(plague) > 0:
        plague = plague.drop(
            columns=[col for col in plague.columns if col.endswith("_detect")]
        )
    results["plague"] = plague

    # Parish status
    parish_status = entries_with_types[
        entries_with_types["parish_status_detect"]
    ].copy()
    if len(parish_status) > 0:
        parish_status = parish_status.drop(
            columns=[col for col in parish_status.columns if col.endswith("_detect")]
        )
    results["parish_status"] = parish_status

    # Log summary
    logger.info(f"Found {len(results['christenings'])} christening entries")
    logger.info(f"Found {len(results['burials'])} burial entries")
    logger.info(f"Found {len(results['plague'])} plague entries")
    logger.info(f"Found {len(results['parish_status'])} parish status entries")

    return results


def process_unique_parishes(
    data: pd.DataFrame,
    authority_file_path: str = "data/London Parish Authority File.csv",
) -> pd.DataFrame:
    """
    Process unique parishes and match with authority file.

    Args:
        data: Input DataFrame with parish_name column
        authority_file_path: Path to parish authority file

    Returns:
        DataFrame with unique parishes and canonical names
    """
    logger.info("Processing unique parishes...")

    initial_count = data["parish_name"].nunique()

    # Get unique parishes
    parishes_unique = (
        data[["parish_name"]]
        .drop_duplicates()
        .assign(parish_name=lambda x: x["parish_name"].str.strip())
        .query('parish_name.notna() & (parish_name != "")')
        .sort_values("parish_name")
        .reset_index(drop=True)
    )

    # Load authority file
    logger.info("Loading parish authority file...")
    try:
        parish_canonical = pd.read_csv(authority_file_path)[
            ["Canonical DBN Name", "Omeka Parish Name"]
        ]
        parish_canonical = parish_canonical.rename(
            columns={
                "Canonical DBN Name": "canonical_name",
                "Omeka Parish Name": "parish_name",
            }
        )
    except FileNotFoundError:
        logger.warning(f"Authority file not found: {authority_file_path}")
        parish_canonical = pd.DataFrame(columns=["canonical_name", "parish_name"])

    # Join and process
    parishes_unique = (
        parishes_unique.merge(parish_canonical, on="parish_name", how="left")
        .assign(canonical_name=lambda x: x["canonical_name"].fillna(x["parish_name"]))
        .assign(parish_id=lambda x: range(1, len(x) + 1))
    )

    # Report on processing
    logger.info(f"Initial distinct parishes: {initial_count}")
    logger.info(f"Final distinct parishes: {len(parishes_unique)}")

    # Check for potential issues
    potential_issues = parishes_unique[
        parishes_unique["parish_name"].str.contains(r"\d", na=False)
        | parishes_unique["parish_name"].str.contains(r"^\s|\s$", na=False)
        | (parishes_unique["parish_name"].str.len() < 3)
    ]

    if len(potential_issues) > 0:
        logger.info(
            f"\nPotential issues found in {len(potential_issues)} parish names:"
        )
        logger.info(potential_issues[["parish_name"]])

    return parishes_unique


def process_unique_weeks(data_sources: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process unique weeks from all data sources.

    Args:
        data_sources: List of dicts with 'data' and 'name' keys

    Returns:
        DataFrame with unique weeks
    """
    logger.info("Processing unique weeks from all sources...")

    def process_source_weeks(data: pd.DataFrame, source_name: str) -> pd.DataFrame:
        logger.info(f"Processing weeks from {source_name}...")

        # Ensure required columns exist
        required_cols = [
            "year",
            "week",
            "start_day",
            "end_day",
            "start_month",
            "end_month",
            "unique_identifier",
        ]
        missing_cols = [col for col in required_cols if col not in data.columns]

        if missing_cols:
            logger.warning(f"Missing columns in {source_name}: {missing_cols}")
            return pd.DataFrame()

        # Standardize column names
        week_data = data.rename(columns={"week": "week_number"})

        # Process week data
        week_data = week_data.assign(
            start_day=lambda x: pd.to_numeric(x["start_day"], errors="coerce"),
            end_day=lambda x: pd.to_numeric(x["end_day"], errors="coerce"),
            year=lambda x: pd.to_numeric(x["year"], errors="coerce").astype("Int64"),
            week_number=lambda x: x["week_number"].astype(str),
            start_day_pad=lambda x: x["start_day"].apply(
                lambda d: f"{d:02.0f}" if pd.notna(d) else "00"
            ),
            end_day_pad=lambda x: x["end_day"].apply(
                lambda d: f"{d:02.0f}" if pd.notna(d) else "00"
            ),
        )

        # Convert numeric columns to integers to remove decimal places
        for col in ['start_day', 'end_day', 'week_number']:
            if col in week_data.columns:
                week_data[col] = pd.to_numeric(week_data[col], errors='coerce').fillna(0).astype(int)

        # Create week_id - handle NaN values first
        week_data = week_data.dropna(subset=['week_number'])
        week_data["week_tmp"] = week_data["week_number"].astype(str).str.zfill(2)
        
        def create_week_id(row):
            try:
                week_num = pd.to_numeric(row["week_number"], errors='coerce')
                if pd.isna(week_num):
                    return f"{row['year']}-{row['year']+1}-00"
                elif week_num > 15:
                    return f"{row['year']-1}-{row['year']}-{row['week_tmp']}"
                else:
                    return f"{row['year']}-{row['year']+1}-{row['week_tmp']}"
            except:
                return f"{row['year']}-{row['year']+1}-00"
        
        week_data["week_id"] = week_data.apply(create_week_id, axis=1)

        # Create other fields
        week_data["year_range"] = week_data["week_id"].str[:9]
        week_data["start_month_num"] = week_data["start_month"].apply(month_to_number)
        week_data["end_month_num"] = week_data["end_month"].apply(month_to_number)

        # Create joinid
        week_data["joinid"] = (
            week_data["year"].astype(str)
            + week_data["start_month_num"]
            + week_data["start_day_pad"]
            + week_data["year"].astype(str)
            + week_data["end_month_num"]
            + week_data["end_day_pad"]
        )

        # Create split_year
        def create_split_year(row):
            try:
                week_num = pd.to_numeric(row["week_number"], errors='coerce')
                if pd.isna(week_num):
                    return str(row["year"])
                elif week_num > 15:
                    return f"{row['year']-1}/{row['year']}"
                else:
                    return str(row["year"])
            except:
                return str(row["year"])
        
        week_data["split_year"] = week_data.apply(create_split_year, axis=1)

        # Clean up temporary columns
        week_data = week_data.drop(
            columns=[
                "week_tmp",
                "start_month_num",
                "end_month_num",
                "start_day_pad",
                "end_day_pad",
            ]
        ).dropna(subset=["year"])
        
        # Filter to only include columns needed for week table (remove DataScribe metadata)
        week_columns = [
            "joinid", "start_day", "start_month", "end_day", "end_month", 
            "year", "week_number", "split_year", "unique_identifier", 
            "week_id", "year_range"
        ]
        
        # Only include columns that exist in the data
        available_week_columns = [col for col in week_columns if col in week_data.columns]
        week_data = week_data[available_week_columns]

        # Filter non-standard years
        standard_years = week_data["year"].astype(str).str.len() == 4
        if not standard_years.all():
            non_standard = week_data[~standard_years]
            logger.info(f"Removing {len(non_standard)} records with non-standard years")
            week_data = week_data[standard_years]

        return week_data

    # Process each source
    all_weeks = []
    for source in data_sources:
        source_weeks = process_source_weeks(source["data"], source["name"])
        if not source_weeks.empty:
            all_weeks.append(source_weeks)

    if not all_weeks:
        return pd.DataFrame()

    # Combine all weeks
    combined_weeks = pd.concat(all_weeks, ignore_index=True)

    # Get unique weeks
    unique_weeks = combined_weeks.drop_duplicates(subset=["joinid"])

    # Report
    logger.info(f"\nProcessed {len(combined_weeks)} total weeks")
    logger.info(f"Found {len(unique_weeks)} unique weeks")
    if len(unique_weeks) > 0:
        logger.info(
            f"Year range: {unique_weeks['year'].min()} - {unique_weeks['year'].max()}"
        )

    return unique_weeks


def process_unique_years(week_data: pd.DataFrame) -> pd.DataFrame:
    """Process unique years from week data."""
    logger.info("Processing unique years from week data...")

    year_unique = (
        week_data[["year"]]
        .assign(
            year=lambda x: pd.to_numeric(x["year"], errors="coerce").astype("Int64")
        )
        .dropna(subset=["year"])
        .drop_duplicates()
        .sort_values("year")
        .reset_index(drop=True)
        .assign(year_id=lambda x: x["year"], id=lambda x: range(1, len(x) + 1))
    )

    logger.info(f"Found {len(year_unique)} unique years")
    if len(year_unique) > 0:
        logger.info(
            f"Year range: {year_unique['year'].min()} - {year_unique['year'].max()}"
        )

    return year_unique


def associate_week_ids(
    bills_data: pd.DataFrame, weeks_data: pd.DataFrame
) -> pd.DataFrame:
    """Associate bills data with week IDs for foreign key relationships."""
    logger.info("Associating bills with week IDs...")

    # Check join IDs
    bills_joinids = bills_data["joinid"].nunique()
    weeks_joinids = weeks_data["joinid"].nunique()

    logger.info(f"Unique join IDs in bills: {bills_joinids}")
    logger.info(f"Unique join IDs in weeks: {weeks_joinids}")

    # Check for duplicates in weeks_data
    duplicate_weeks = weeks_data[weeks_data.duplicated(subset=["joinid"], keep=False)]
    if len(duplicate_weeks) > 0:
        logger.info(f"Found {len(duplicate_weeks)} duplicate weeks")

    # Remove conflicting columns from bills_data before joining
    cols_to_remove = [
        "week",
        "start_day",
        "end_day",
        "start_month",
        "end_month",
        "year",
        "split_year",
    ]
    bills_clean = bills_data.drop(
        columns=[col for col in cols_to_remove if col in bills_data.columns]
    )

    # Join with weeks data
    weeks_for_join = weeks_data[["joinid", "year", "split_year"]].drop_duplicates(
        subset=["joinid"]
    )

    bills_with_weeks = bills_clean.merge(weeks_for_join, on="joinid", how="left")

    logger.info(f"Initial rows: {len(bills_data)}")
    logger.info(f"Final rows: {len(bills_with_weeks)}")

    # Check for missing joins
    missing_weeks = bills_with_weeks[bills_with_weeks["year"].isna()]
    if len(missing_weeks) > 0:
        logger.info(f"Found {len(missing_weeks)} bills with missing week data")

    return bills_with_weeks


def derive_causes(data_sources: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Combine causes of death data from multiple sources and standardize.
    
    Args:
        data_sources: List of dicts with 'data' and 'name' keys
        
    Returns:
        Combined and filtered DataFrame with standardized columns
    """
    logger.info("Deriving causes of death from multiple sources...")
    
    if not isinstance(data_sources, list):
        logger.error("data_sources must be a list")
        return pd.DataFrame()
    
    combined_datasets = []
    
    for source in data_sources:
        if not isinstance(source, dict) or 'data' not in source or 'name' not in source:
            logger.warning("Skipping invalid data source")
            continue
            
        data = source['data'].copy()
        source_name = source['name']
        
        if data.empty:
            logger.info(f"Skipping empty dataset: {source_name}")
            continue
            
        logger.info(f"Processing source: {source_name} ({len(data)} rows)")
        
        # Standardize column types
        if 'week_number' in data.columns:
            data['week_number'] = data['week_number'].astype(str)
        if 'start_day' in data.columns:
            data['start_day'] = data['start_day'].astype(str)
        if 'end_day' in data.columns:
            data['end_day'] = data['end_day'].astype(str)
        if 'count' in data.columns:
            data['count'] = pd.to_numeric(data['count'], errors='coerce')
            
        # Add source name if not present
        if 'source_name' not in data.columns:
            data['source_name'] = source_name
            
        combined_datasets.append(data)
    
    if not combined_datasets:
        logger.warning("No valid datasets to combine")
        return pd.DataFrame()
    
    # Combine all datasets
    combined_data = pd.concat(combined_datasets, ignore_index=True)
    logger.info(f"Combined {len(combined_datasets)} sources into {len(combined_data)} total rows")
    
    # Filter out unwanted entries
    exclusion_patterns = [
        r"^Christened \(",
        r"^Buried \(",
        r"Plague Deaths$",
        r"^Increase/Decrease",
        r"Parishes (?:Clear|Infected)",
        r"Ounces in",
        r"Found Dead",
        r"Description"
    ]
    
    # Create a combined pattern
    combined_pattern = "|".join(exclusion_patterns)
    
    # Filter out entries matching exclusion patterns
    if 'death' in combined_data.columns:
        before_filter = len(combined_data)
        combined_data = combined_data[~combined_data['death'].str.contains(combined_pattern, na=False, regex=True)]
        after_filter = len(combined_data)
        logger.info(f"Filtered out {before_filter - after_filter} unwanted entries")
    
    # Create joinid if missing
    if 'joinid' not in combined_data.columns:
        required_cols = ['year', 'start_month', 'start_day', 'end_month', 'end_day']
        if all(col in combined_data.columns for col in required_cols):
            logger.info("Creating joinid from date components")
            
            combined_data['start_month_num'] = combined_data['start_month'].apply(
                lambda x: month_to_number(str(x)) if pd.notna(x) else '00'
            )
            combined_data['end_month_num'] = combined_data['end_month'].apply(
                lambda x: month_to_number(str(x)) if pd.notna(x) else '00'
            )
            
            # Ensure numeric columns are properly converted
            combined_data['start_day'] = pd.to_numeric(combined_data['start_day'], errors='coerce')
            combined_data['end_day'] = pd.to_numeric(combined_data['end_day'], errors='coerce')
            combined_data['year'] = pd.to_numeric(combined_data['year'], errors='coerce')
            
            # Remove rows with invalid data
            combined_data = combined_data.dropna(subset=['start_day', 'end_day', 'year'])
            
            combined_data['start_day_pad'] = combined_data['start_day'].astype(int).astype(str).str.zfill(2)
            combined_data['end_day_pad'] = combined_data['end_day'].astype(int).astype(str).str.zfill(2)
            
            # Create joinid in format yyyymmddyyyymmdd
            combined_data['joinid'] = (
                combined_data['year'].astype(int).astype(str) + 
                combined_data['start_month_num'] + 
                combined_data['start_day_pad'] + 
                combined_data['year'].astype(int).astype(str) + 
                combined_data['end_month_num'] + 
                combined_data['end_day_pad']
            )
            
            # Clean up temporary columns
            combined_data = combined_data.drop(columns=['start_month_num', 'end_month_num', 'start_day_pad', 'end_day_pad'])
    
    # Select relevant columns
    output_cols = ['death', 'count', 'year', 'joinid', 'source_name']
    if 'descriptive_text' in combined_data.columns:
        output_cols.append('descriptive_text')
    
    # Keep only existing columns
    final_cols = [col for col in output_cols if col in combined_data.columns]
    result = combined_data[final_cols]
    
    logger.info(f"Final dataset contains {len(result)} rows with {len(final_cols)} columns")
    
    return result


def add_death_definitions(deaths_data: pd.DataFrame, dictionary_path: str = "dictionary.csv") -> pd.DataFrame:
    """
    Add death definitions from a dictionary file to causes of death data.
    
    Args:
        deaths_data: DataFrame containing death causes
        dictionary_path: Path to dictionary CSV file
        
    Returns:
        DataFrame with added definition columns
    """
    logger.info("Adding death definitions from dictionary...")
    
    if deaths_data.empty:
        logger.warning("Deaths data is empty")
        return deaths_data
    
    # Try to load dictionary file
    try:
        dictionary = pd.read_csv(dictionary_path)
        logger.info(f"Loaded dictionary with {len(dictionary)} entries from {dictionary_path}")
    except FileNotFoundError:
        logger.warning(f"Dictionary file not found: {dictionary_path}")
        # Create empty dictionary structure
        dictionary = pd.DataFrame(columns=['Cause', 'Definition', 'Source'])
    except Exception as e:
        logger.error(f"Error loading dictionary: {e}")
        dictionary = pd.DataFrame(columns=['Cause', 'Definition', 'Source'])
    
    if dictionary.empty:
        logger.warning("Dictionary is empty, returning original data")
        deaths_data['definition'] = pd.NA
        deaths_data['definition_source'] = pd.NA
        return deaths_data
    
    # Standardize dictionary column names
    dictionary = dictionary.rename(columns={
        'Cause': 'death',
        'Definition': 'definition', 
        'Source': 'definition_source'
    })
    
    # Create lowercase versions for case-insensitive matching
    dictionary['death_lower'] = dictionary['death'].astype(str).str.lower().str.strip()
    deaths_data['death_lower'] = deaths_data['death'].astype(str).str.lower().str.strip()
    
    # Perform left join on lowercase death names
    result = deaths_data.merge(
        dictionary[['death_lower', 'definition', 'definition_source']], 
        on='death_lower', 
        how='left'
    )
    
    # Clean up temporary column
    result = result.drop('death_lower', axis=1)
    
    # Report matching statistics
    total_deaths = len(result)
    matched_deaths = result['definition'].notna().sum()
    match_rate = (matched_deaths / total_deaths * 100) if total_deaths > 0 else 0
    
    logger.info(f"Matched {matched_deaths} out of {total_deaths} death causes ({match_rate:.1f}%)")
    
    # List unmatched deaths for review
    unmatched = result[result['definition'].isna()]['death'].drop_duplicates().sort_values()
    if len(unmatched) > 0:
        logger.info(f"Unmatched death causes ({len(unmatched)} unique):")
        for death in unmatched.head(10):  # Show first 10
            logger.info(f"  - {death}")
        if len(unmatched) > 10:
            logger.info(f"  ... and {len(unmatched) - 10} more")
    
    return result


def tidy_parish_data(combined_data: pd.DataFrame) -> pd.DataFrame:
    """
    Separate parish_name and count_type and clean whitespace.

    Args:
        combined_data: DataFrame with parish_name column containing "Parish-Type" format

    Returns:
        DataFrame with separated parish_name and count_type columns
    """
    logger.info("Tidying parish and count type data...")

    # Split parish_name on first dash
    split_data = combined_data["parish_name"].str.split("-", n=1, expand=True)

    result = combined_data.copy()
    result["parish_name"] = split_data[0].str.strip()
    result["count_type"] = split_data[1].str.strip().fillna("Count")

    # Strip whitespace from all string columns
    string_cols = result.select_dtypes(include=["object"]).columns
    for col in string_cols:
        result[col] = result[col].astype(str).str.strip()

    logger.info(f"Distinct parishes: {result['parish_name'].nunique()}")
    logger.info(f"Distinct count types: {result['count_type'].nunique()}")

    return result

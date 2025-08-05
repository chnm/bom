"""Column normalization utilities."""

import re
from typing import Dict, List
import pandas as pd
from loguru import logger

from ..config import COLUMN_NORMALIZATION, SKIP_COLUMN_PATTERNS


def normalize_column_name(column_name: str) -> str:
    """
    Normalize a single column name without affecting data content.
    
    Args:
        column_name: Original column name from CSV
        
    Returns:
        Normalized column name
    """
    # Remove quotes that might come from CSV headers
    clean_name = column_name.strip('"\'')
    
    # Check if we have an explicit mapping
    if clean_name in COLUMN_NORMALIZATION:
        return COLUMN_NORMALIZATION[clean_name]
    
    # Default normalization: lowercase and replace spaces with underscores
    normalized = clean_name.lower().replace(" ", "_")
    
    # Remove any remaining problematic characters
    normalized = re.sub(r'[^\w_]', '_', normalized)
    
    # Clean up multiple underscores
    normalized = re.sub(r'_+', '_', normalized).strip('_')
    
    return normalized


def normalize_dataframe_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, str]]:
    """
    Normalize all column names in a DataFrame while preserving data.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (normalized DataFrame, column mapping dict)
    """
    original_columns = df.columns.tolist()
    column_mapping = {}
    
    new_columns = []
    for col in original_columns:
        normalized = normalize_column_name(col)
        column_mapping[col] = normalized
        new_columns.append(normalized)
    
    # Check for duplicates after normalization
    if len(set(new_columns)) != len(new_columns):
        duplicates = [col for col in set(new_columns) if new_columns.count(col) > 1]
        logger.warning(f"Duplicate columns after normalization: {duplicates}")
        
        # Handle duplicates by adding suffixes
        seen = {}
        final_columns = []
        for col in new_columns:
            if col in seen:
                seen[col] += 1
                final_columns.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                final_columns.append(col)
        new_columns = final_columns
    
    # Create new DataFrame with normalized columns
    df_normalized = df.copy()
    df_normalized.columns = new_columns
    
    logger.info(f"Normalized {len(original_columns)} columns")
    return df_normalized, column_mapping


def should_skip_column(column_name: str) -> bool:
    """
    Check if a column should be skipped based on patterns.
    
    Args:
        column_name: Column name to check
        
    Returns:
        True if column should be skipped
    """
    normalized = normalize_column_name(column_name)
    
    for pattern in SKIP_COLUMN_PATTERNS:
        if re.match(pattern, normalized, re.IGNORECASE):
            return True
    
    return False


def filter_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns that should be skipped from processing.
    
    Args:
        df: Input DataFrame with normalized columns
        
    Returns:
        DataFrame with irrelevant columns removed
    """
    columns_to_keep = []
    columns_skipped = []
    
    for col in df.columns:
        if should_skip_column(col):
            columns_skipped.append(col)
        else:
            columns_to_keep.append(col)
    
    if columns_skipped:
        logger.info(f"Skipping columns: {columns_skipped}")
    
    return df[columns_to_keep]


def get_column_info(df: pd.DataFrame, original_mapping: Dict[str, str]) -> Dict[str, any]:
    """
    Get information about the columns in a DataFrame.
    
    Args:
        df: DataFrame to analyze
        original_mapping: Mapping from original to normalized column names
        
    Returns:
        Dictionary with column information
    """
    return {
        "total_columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "original_mapping": original_mapping,
        "data_types": df.dtypes.to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
    }
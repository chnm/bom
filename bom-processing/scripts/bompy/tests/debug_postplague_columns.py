#!/usr/bin/env python3
"""Debug script to analyze the column structure of the postplague file."""

import pandas as pd
import re
from pathlib import Path

def analyze_postplague_file():
    """Analyze the column structure and data patterns in the postplague file."""
    file_path = Path("data-raw/2022-04-06-millar-generalbills-postplague-parishes.csv")
    
    print(f"Analyzing file: {file_path}")
    
    # Load the file
    df = pd.read_csv(file_path)
    print(f"File shape: {df.shape}")
    
    # Get all columns
    columns = df.columns.tolist()
    print(f"Total columns: {len(columns)}")
    
    print("\n=== ALL COLUMNS ===")
    for i, col in enumerate(columns):
        print(f"{i+1:3d}: {col}")
    
    # Apply the same logic as the bills processor to identify parish columns
    print("\n=== PARISH COLUMN IDENTIFICATION (Current Logic) ===")
    
    # Count type patterns from bills processor
    count_type_patterns = {
        'buried': r'_buried$|buried_|^buried',
        'plague': r'_plague$|plague_|^plague', 
        'christened': r'_christened$|christened_|^christened|_baptized$|baptized_|^baptized',
        'other': r'_other$|other_|^other'
    }
    
    parish_columns = []
    excluded_columns = []
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Check metadata exclusions (from bills processor)
        if col_lower.startswith(('total', 'year', 'week', 'start_', 'end_', 'unique_')):
            excluded_columns.append((col, "metadata"))
            continue
            
        # Check aggregate exclusions
        if any(phrase in col_lower for phrase in [
            'christened in the', 'buried in the', 'plague in the',
            'christened in all', 'buried in all', 'plague in all'
        ]):
            excluded_columns.append((col, "aggregate"))
            continue
            
        # Check if it's a parish column (contains buried, plague, christened, or baptized)
        if any(pattern_name for pattern_name, pattern in count_type_patterns.items() 
               if re.search(pattern, col_lower)):
            parish_columns.append(col)
        else:
            # For General Bills data, parish columns might not have explicit count type suffixes
            # Let's check if this looks like a parish name
            if not col_lower.startswith(('omeka', 'datascribe', 'image_')):
                # This might be a parish column without explicit suffixes
                excluded_columns.append((col, "no_count_type_suffix"))
    
    print(f"\nFound {len(parish_columns)} parish columns using current logic:")
    for col in parish_columns:
        # Test count type identification
        col_lower = col.lower()
        count_type = "buried"  # default
        for ct, pattern in count_type_patterns.items():
            if re.search(pattern, col_lower):
                count_type = ct
                break
        print(f"  - {col} -> count_type: {count_type}")
    
    print(f"\nExcluded {len(excluded_columns)} columns:")
    for col, reason in excluded_columns:
        print(f"  - {col} -> {reason}")
    
    # Let's also check what the first few rows look like for parish columns
    print("\n=== SAMPLE DATA FOR PARISH COLUMNS ===")
    if parish_columns:
        sample_cols = parish_columns[:5]  # First 5 parish columns
        for col in sample_cols:
            print(f"\n{col}:")
            print(f"  Sample values: {df[col].iloc[:3].tolist()}")
            print(f"  Non-null count: {df[col].count()}/{len(df)}")
    
    # Check for potential parish columns that aren't being detected
    print("\n=== POTENTIAL PARISH COLUMNS NOT DETECTED ===")
    potential_parish_cols = []
    for col in df.columns:
        col_lower = col.lower()
        # Skip obvious metadata
        if col_lower.startswith(('omeka', 'datascribe', 'image_', 'unique_', 'start_', 'end_')):
            continue
        # Skip already identified parish columns
        if col in parish_columns:
            continue
        # Skip aggregate columns
        if any(phrase in col_lower for phrase in [
            'christened in the', 'buried in the', 'plague in the',
            'christened in all', 'buried in all', 'plague in all'
        ]):
            continue
        
        # Check if this looks like a parish name (starts with "St " or contains common parish words)
        if (col.startswith(('St ', 'Christ ', 'Trinity')) or 
            any(word in col for word in ['Parish', 'Church']) or
            col.startswith('Alhal')):  # Alhallows variations
            potential_parish_cols.append(col)
    
    print(f"Found {len(potential_parish_cols)} potential parish columns:")
    for col in potential_parish_cols[:10]:  # Show first 10
        print(f"  - {col}")
        print(f"    Sample values: {df[col].iloc[:3].tolist()}")
    
    if len(potential_parish_cols) > 10:
        print(f"  ... and {len(potential_parish_cols) - 10} more")

if __name__ == "__main__":
    analyze_postplague_file()
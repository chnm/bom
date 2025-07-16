#!/usr/bin/env python3
"""
Script to find rows with problematic years (outside 1630-1800) in Bills of Mortality data.

This script identifies data quality issues in the original CSV files where the Year column
contains values outside the expected historical range, helping to locate transcription errors
that need to be corrected at the source.

Usage:
    python find_problematic_years.py
"""

import pandas as pd
import glob
import os

def find_problematic_years(data_dir="../../../bom-data/data-csvs", year_min=1630, year_max=1800):
    """
    Find rows with years outside the valid historical range.
    
    Args:
        data_dir: Directory containing the CSV files
        year_min: Minimum valid year (default: 1630)
        year_max: Maximum valid year (default: 1800)
    """
    
    # Find all the problematic source files
    problem_sources = ['BLV2', 'BLV4']
    data_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    print(f'PROBLEMATIC ROWS WITH INVALID YEARS (outside {year_min}-{year_max}):\n')
    print('=' * 80)
    
    total_problems = 0
    
    for source in problem_sources:
        matching_files = [f for f in data_files if source in f]
        
        for file_path in matching_files:
            print(f'\nFILE: {file_path}')
            print('-' * 60)
            
            try:
                df = pd.read_csv(file_path)
                
                # Check if Year column exists
                if 'Year' not in df.columns:
                    print('No Year column found in this file.')
                    continue
                
                # Filter for years outside valid range
                bad_years = df[(df['Year'] < year_min) | (df['Year'] > year_max)]
                
                if len(bad_years) > 0:
                    print(f'Found {len(bad_years)} problematic rows:')
                    total_problems += len(bad_years)
                    
                    # Show the key columns that identify the problematic entries
                    key_columns = [
                        'Omeka Item #', 'DataScribe Item #', 'DataScribe Record #', 
                        'Year', 'Week', 'Unique ID', 'Start Day', 'Start Month', 
                        'End Day', 'End month'
                    ]
                    available_columns = [col for col in key_columns if col in df.columns]
                    
                    problem_rows = bad_years[available_columns].drop_duplicates()
                    
                    for idx, row in problem_rows.iterrows():
                        print(f'  Row {idx + 1}: Year={row["Year"]}, Unique_ID={row["Unique ID"]}, Week={row["Week"]}, Omeka_Item={row["Omeka Item #"]}, DataScribe_Item={row["DataScribe Item #"]}, DataScribe_Record={row["DataScribe Record #"]}')
                else:
                    print('No problematic years found.')
                    
            except Exception as e:
                print(f'Error reading file: {e}')
    
    print(f'\n{"=" * 80}')
    print(f'TOTAL PROBLEMATIC ROWS FOUND: {total_problems}')
    print(f'{"=" * 80}')

if __name__ == "__main__":
    find_problematic_years()
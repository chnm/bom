#!/usr/bin/env python3

import pandas as pd
import os
import re
from pathlib import Path

def analyze_christening_data():
    """Analyze all CSV files in data-raw directory for christening data."""
    
    data_raw_dir = Path("data-raw")
    results = []
    
    # Get all CSV files
    csv_files = list(data_raw_dir.glob("*.csv"))
    
    print(f"Analyzing {len(csv_files)} CSV files for christening data...\n")
    
    for csv_file in csv_files:
        try:
            # Read just the header first
            df = pd.read_csv(csv_file, nrows=0)
            columns = df.columns.tolist()
            
            # Find christening-related columns (case insensitive)
            christening_cols = [col for col in columns if re.search(r'christen', col, re.IGNORECASE)]
            
            if christening_cols:
                # Now read the full file to get row count and sample data
                df_full = pd.read_csv(csv_file)
                row_count = len(df_full)
                
                result = {
                    'filename': csv_file.name,
                    'christening_columns': christening_cols,
                    'row_count': row_count,
                    'sample_data': {}
                }
                
                # Get sample data for each christening column
                for col in christening_cols:
                    # Get first few non-null values
                    non_null_values = df_full[col].dropna()
                    if len(non_null_values) > 0:
                        sample_values = non_null_values.head(5).tolist()
                        result['sample_data'][col] = sample_values
                    else:
                        result['sample_data'][col] = ["No non-null values"]
                
                results.append(result)
                
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    # Print results
    for result in results:
        print(f"=== {result['filename']} ===")
        print(f"Row count: {result['row_count']:,}")
        print(f"Christening columns found: {len(result['christening_columns'])}")
        
        for col in result['christening_columns']:
            print(f"\nColumn: {col}")
            sample_data = result['sample_data'][col]
            print(f"Sample values: {sample_data}")
        
        print("\n" + "="*80 + "\n")
    
    # Summary
    total_files_with_christenings = len(results)
    total_christening_columns = sum(len(r['christening_columns']) for r in results)
    
    print(f"SUMMARY:")
    print(f"Files with christening data: {total_files_with_christenings}")
    print(f"Total christening columns across all files: {total_christening_columns}")
    
    return results

if __name__ == "__main__":
    analyze_christening_data()
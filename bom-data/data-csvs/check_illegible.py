#!/usr/bin/env python3
"""
Check is_illegible column values across all CSV files in the directory.

This script analyzes all CSV files in the current directory and reports:
- Which files contain records marked as illegible (is_illegible = 1)
- Count of illegible vs empty vs total records per file
- Summary statistics across all files

Usage:
    python check_illegible.py
"""

import csv
import os
import sys
from collections import defaultdict


def check_illegible_data():
    """
    Analyze is_illegible column values across all CSV files.
    
    Returns:
        dict: File counts with illegible, empty, and total record counts
    """
    file_counts = defaultdict(lambda: {'empty': 0, 'illegible': 0, 'total': 0, 'illegible_columns': 0})
    
    # Find all CSV files in current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in current directory.")
        return file_counts
    
    print(f"Analyzing {len(csv_files)} CSV files...\n")
    
    # Process each CSV file
    for filename in csv_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Find ALL is_illegible columns
                illegible_columns = [col for col in reader.fieldnames if col == 'is_illegible']
                
                if not illegible_columns:
                    continue
                
                file_counts[filename]['illegible_columns'] = len(illegible_columns)
                
                # Count records
                for row in reader:
                    file_counts[filename]['total'] += 1
                    
                    # Check if ANY is_illegible column has a '1' value
                    has_illegible = False
                    all_empty = True
                    
                    for col in illegible_columns:
                        value = row.get(col, '')
                        if value == '1':
                            has_illegible = True
                        if value != '':
                            all_empty = False
                    
                    if has_illegible:
                        file_counts[filename]['illegible'] += 1
                    elif all_empty:
                        file_counts[filename]['empty'] += 1
                            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
    
    return file_counts


def print_results(file_counts):
    """Print formatted results of the analysis."""
    
    # Files with illegible records
    print("=" * 60)
    print("FILES WITH ILLEGIBLE RECORDS:")
    print("=" * 60)
    
    illegible_files = []
    for filename, counts in sorted(file_counts.items()):
        if counts['illegible'] > 0:
            illegible_files.append((filename, counts))
            print(f"{filename}: {counts['illegible']} illegible out of {counts['total']} total records ({counts['illegible_columns']} illegible columns)")
    
    if not illegible_files:
        print("No files contain records marked as illegible.")
    
    print(f"\nTotal files with illegible records: {len(illegible_files)}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS:")
    print("=" * 60)
    
    total_files = len([f for f in file_counts if file_counts[f]['total'] > 0])
    total_records = sum(counts['total'] for counts in file_counts.values())
    total_illegible = sum(counts['illegible'] for counts in file_counts.values())
    total_empty = sum(counts['empty'] for counts in file_counts.values())
    
    print(f"Total CSV files analyzed: {total_files}")
    print(f"Total records: {total_records:,}")
    print(f"Total illegible records: {total_illegible}")
    print(f"Total empty is_illegible fields: {total_empty:,}")
    print(f"Percentage illegible: {(total_illegible/total_records*100):.3f}%")
    
    # Detailed breakdown
    print("\n" + "=" * 60)
    print("DETAILED BREAKDOWN BY FILE:")
    print("=" * 60)
    print(f"{'Filename':<50} {'Illegible':<10} {'Empty':<10} {'Total':<10} {'Cols':<5}")
    print("-" * 85)
    
    for filename, counts in sorted(file_counts.items()):
        if counts['total'] > 0:
            print(f"{filename:<50} {counts['illegible']:<10} {counts['empty']:<10} {counts['total']:<10} {counts['illegible_columns']:<5}")


def main():
    """Main function."""
    print("Checking is_illegible column values in CSV files...")
    
    file_counts = check_illegible_data()
    
    if not file_counts:
        sys.exit(1)
    
    print_results(file_counts)


if __name__ == "__main__":
    main()
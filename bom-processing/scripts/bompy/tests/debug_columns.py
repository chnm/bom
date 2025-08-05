#!/usr/bin/env python3
"""Debug script to check column detection in parish data."""

import pandas as pd
import sys
sys.path.append('src')

from bom.processors.bills import BillsProcessor

# Load sample parish data
sample_file = "data-raw/2025-07-30-BLV2-weeklybills-parishes.csv"
df = pd.read_csv(sample_file)

print(f"Total columns in {sample_file}: {len(df.columns)}")
print(f"First 10 columns: {list(df.columns[:10])}")

# Test our column filtering logic
processor = BillsProcessor()

parish_columns = [
    col for col in df.columns 
    if not col.lower().startswith(('total', 'year', 'week', 'start_', 'end_', 'unique_'))
    and any(pattern in col.lower() for pattern in ['buried', 'plague', 'christened', 'baptized'])
]

print(f"\nFiltered parish columns found: {len(parish_columns)}")
print(f"First 10 parish columns: {parish_columns[:10]}")

# Check what column patterns exist
buried_cols = [col for col in df.columns if 'buried' in col.lower()]
plague_cols = [col for col in df.columns if 'plague' in col.lower()]

print(f"\nBuried columns: {len(buried_cols)}")
print(f"Plague columns: {len(plague_cols)}")
print(f"Sample buried columns: {buried_cols[:5]}")
print(f"Sample plague columns: {plague_cols[:5]}")
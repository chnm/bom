#!/usr/bin/env python3
"""Test script to check if causes data is being processed."""

import pandas as pd
import sys
sys.path.append('src')

from bom.loaders.registry import DatasetRegistry

# Initialize registry and discover files
registry = DatasetRegistry()
registry.discover_datasets()

print("Discovered datasets:")
for dataset_type, files in registry.datasets.items():
    print(f"  {dataset_type}: {len(files)} files")
    
# Check causes files specifically
causes_files = [dataset_type for dataset_type in registry.datasets.keys() if 'causes' in dataset_type]
print(f"\nCauses datasets found: {causes_files}")

# Load one causes file and examine structure
if causes_files:
    causes_type = causes_files[0]
    sample_file = registry.datasets[causes_type][0]
    print(f"\nExamining {sample_file.path}...")
    
    df = pd.read_csv(sample_file.path)
    print(f"Columns: {len(df.columns)}")
    print(f"Rows: {len(df)}")
    
    # Find cause columns (not metadata)
    cause_cols = [col for col in df.columns 
                  if not col.lower().startswith(('omeka', 'datascribe', 'year', 'week', 'start_', 'end_', 'unique', 'is_missing', 'is_illegible'))]
    print(f"Cause columns: {len(cause_cols)}")
    print(f"Sample causes: {cause_cols[:10]}")
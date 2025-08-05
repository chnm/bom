#!/usr/bin/env python3
"""Diagnose which files are being processed vs ignored."""

import re
from pathlib import Path

# Import actual patterns from config
import sys
sys.path.insert(0, 'src')
from bom.config import DATASET_PATTERNS

def detect_dataset_type(filename: str) -> str:
    """Detect dataset type from filename patterns."""
    filename_lower = filename.lower()
    
    for dataset_type, pattern in DATASET_PATTERNS.items():
        if re.search(pattern, filename_lower, re.IGNORECASE):
            return dataset_type
    
    # Fallback detection
    if "cause" in filename_lower:
        return "causes_unknown"
    elif "parish" in filename_lower:
        return "parishes_unknown"
    else:
        return "unknown"

# Get all CSV files
data_dir = Path("data-raw")
csv_files = list(data_dir.glob("*.csv"))

print(f"=== DIAGNOSTIC: Processing {len(csv_files)} CSV files ===\n")

matched_files = {}
unmatched_files = []

for file_path in sorted(csv_files):
    filename = file_path.name
    detected_type = detect_dataset_type(filename)
    
    if detected_type in DATASET_PATTERNS:
        if detected_type not in matched_files:
            matched_files[detected_type] = []
        matched_files[detected_type].append(filename)
    else:
        unmatched_files.append((filename, detected_type))

print("✅ MATCHED FILES (will be processed):")
total_matched = 0
for dataset_type, files in matched_files.items():
    print(f"\n{dataset_type} ({len(files)} files):")
    for file in files:
        print(f"  - {file}")
    total_matched += len(files)

print(f"\n❌ UNMATCHED FILES (will be ignored): {len(unmatched_files)}")
for filename, detected_type in unmatched_files:
    print(f"  - {filename} -> {detected_type}")

print(f"\n📊 SUMMARY:")
print(f"  Matched files: {total_matched}")
print(f"  Unmatched files: {len(unmatched_files)}")
print(f"  Total files: {len(csv_files)}")
print(f"  Processing rate: {total_matched/len(csv_files)*100:.1f}%")
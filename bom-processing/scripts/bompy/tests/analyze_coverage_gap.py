#!/usr/bin/env python3
"""Analyze the coverage gap between R and Python outputs."""

import pandas as pd
from pathlib import Path

def analyze_coverage_gap():
    print("🔍 Analyzing coverage gap between R and Python outputs")
    print("=" * 60)
    
    # Load both datasets
    r_data = pd.read_csv('data-bomr/all_bills.csv')
    py_data = pd.read_csv('data/all_bills.csv')
    
    print(f"📊 Dataset sizes:")
    print(f"  R output: {len(r_data):,} records")
    print(f"  Python output: {len(py_data):,} records")
    print(f"  Missing: {len(r_data) - len(py_data):,} records ({(len(r_data) - len(py_data))/len(r_data)*100:.1f}%)")
    
    print(f"\n🏛️ Sources comparison:")
    r_sources = r_data['source'].value_counts()
    py_sources = py_data['source'].value_counts()
    
    print(f"\nR sources ({len(r_sources)} unique):")
    for source, count in r_sources.head(10).items():
        py_count = py_sources.get(source, 0)
        coverage = py_count / count * 100 if count > 0 else 0
        print(f"  {source[:40]:40} - R: {count:>6,} | Py: {py_count:>6,} | Coverage: {coverage:>5.1f}%")
    
    print(f"\nPython sources ({len(py_sources)} unique):")
    for source, count in py_sources.head(10).items():
        print(f"  {source[:40]:40} - {count:,}")
    
    # Check if there are sources in R that we're completely missing
    r_source_set = set(r_sources.index)
    py_source_set = set(py_sources.index)
    missing_sources = r_source_set - py_source_set
    
    if missing_sources:
        print(f"\n❌ Sources in R but missing in Python ({len(missing_sources)}):")
        for source in sorted(missing_sources):
            count = r_sources[source]
            print(f"  {source[:50]:50} - {count:,} records")
            
        # Calculate how many records these missing sources account for
        missing_records = sum(r_sources[source] for source in missing_sources)
        print(f"\n📊 Records from completely missing sources: {missing_records:,}")
        print(f"   This accounts for {missing_records/(len(r_data) - len(py_data))*100:.1f}% of the gap")
    
    # Check count type distribution
    print(f"\n📋 Count types comparison:")
    r_count_types = r_data['count_type'].value_counts()
    py_count_types = py_data['count_type'].value_counts()
    
    print(f"R count types:")
    for count_type, count in r_count_types.items():
        py_count = py_count_types.get(count_type, 0)
        coverage = py_count / count * 100 if count > 0 else 0
        print(f"  {count_type[:20]:20} - R: {count:>7,} | Py: {py_count:>7,} | Coverage: {coverage:>5.1f}%")
    
    # Check year distribution
    print(f"\n📅 Year coverage:")
    r_years = r_data['year'].value_counts().sort_index()
    py_years = py_data['year'].value_counts().sort_index()
    
    # Find years with big discrepancies
    year_gaps = []
    for year in r_years.index:
        r_count = r_years[year]
        py_count = py_years.get(year, 0)
        gap = r_count - py_count
        if gap > 1000:  # Significant gaps
            year_gaps.append((year, r_count, py_count, gap))
    
    if year_gaps:
        print(f"Years with >1,000 missing records:")
        for year, r_count, py_count, gap in sorted(year_gaps, key=lambda x: x[3], reverse=True)[:10]:
            coverage = py_count / r_count * 100 if r_count > 0 else 0
            print(f"  {year}: R={r_count:>5,} | Py={py_count:>5,} | Gap={gap:>5,} | Coverage={coverage:>5.1f}%")
    
    # Check for empty counts in both datasets
    print(f"\n📊 Empty/Zero counts analysis:")
    r_empty = r_data['count'].isna().sum()
    r_zero = (r_data['count'] == 0).sum()
    py_empty = py_data['count'].isna().sum()
    py_zero = (py_data['count'] == 0).sum()
    
    print(f"  R - Empty counts: {r_empty:,}, Zero counts: {r_zero:,}")
    print(f"  Py - Empty counts: {py_empty:,}, Zero counts: {py_zero:,}")
    
    # Try to identify record structure differences
    print(f"\n🔍 Record structure analysis:")
    print(f"  R columns: {list(r_data.columns)}")
    print(f"  Py columns: {list(py_data.columns)}")
    
    # Check for potential data expansion in R
    print(f"\n🔢 Data expansion analysis:")
    
    # Group by key identifying fields to see if R creates more records per logical unit
    if 'unique_identifier' in r_data.columns and 'unique_identifier' in py_data.columns:
        r_unique_bills = r_data['unique_identifier'].nunique()
        py_unique_bills = py_data['unique_identifier'].nunique()
        
        r_records_per_bill = len(r_data) / r_unique_bills if r_unique_bills > 0 else 0
        py_records_per_bill = len(py_data) / py_unique_bills if py_unique_bills > 0 else 0
        
        print(f"  R - Unique bills: {r_unique_bills:,}, Records per bill: {r_records_per_bill:.1f}")
        print(f"  Py - Unique bills: {py_unique_bills:,}, Records per bill: {py_records_per_bill:.1f}")
        
        if r_records_per_bill > py_records_per_bill:
            print(f"  ⚠️ R creates {r_records_per_bill/py_records_per_bill:.1f}x more records per bill!")
            print(f"     This suggests different record expansion logic")

if __name__ == "__main__":
    analyze_coverage_gap()
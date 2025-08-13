#!/usr/bin/env python3
"""Debug parish extraction from general bills."""

from src.bom.loaders.csv_loader import CSVLoader
from src.bom.extractors.parishes import ParishExtractor
from pathlib import Path


def debug_parish_extraction():
    """Debug why parish extraction fails for general bills."""
    # Load the postplague file
    file_path = Path('data-raw/2022-04-06-millar-generalbills-postplague-parishes.csv')
    loader = CSVLoader()
    df, info = loader.load(file_path)
    
    print("=== DEBUG PARISH EXTRACTION ===")
    print(f"Dataset type: {info.dataset_type}")
    print(f"Is general bill: {'general' in info.dataset_type.lower()}")
    print(f"Total columns: {len(df.columns)}")
    
    # Check parish-related columns
    parish_cols = [col for col in df.columns if 'parish' in col.lower()]
    print(f"\nColumns with 'parish': {len(parish_cols)}")
    for col in parish_cols:
        print(f"  - {col}")
    
    # Check columns ending with suffixes (weekly bill pattern)
    potential_parish_cols = [
        col for col in df.columns 
        if col.endswith(('_buried', '_plague', '_christened')) and not col.startswith('total')
    ]
    print(f"\nColumns with suffixes (_buried, _plague, _christened): {len(potential_parish_cols)}")
    for col in potential_parish_cols:
        print(f"  - {col}")
    
    # Check individual parish columns (general bill pattern)
    individual_parish_cols = []
    for col in df.columns:
        col_lower = col.lower()
        # Skip metadata columns
        if col_lower.startswith(('total', 'year', 'week', 'start_', 'end_', 'unique_')):
            continue
        if col_lower.startswith(('omeka', 'datascribe', 'image_', 'is_missing', 'is_illegible')):
            continue
        
        # Skip aggregate columns 
        if any(phrase in col_lower for phrase in [
            'christened in the', 'buried in the', 'plague in the'
        ]):
            continue
        
        # Individual parish columns in general bills
        if (col.startswith(('st_', 'christ_', 'trinity', 'alhal', 's_')) or 
            any(word in col for word in ['parish', 'church', 'precinct']) or
            col.endswith('_parish')):
            individual_parish_cols.append(col)
    
    print(f"\nIndividual parish columns (general bill pattern): {len(individual_parish_cols)}")
    for col in individual_parish_cols[:10]:  # Show first 10
        print(f"  - {col}")
    if len(individual_parish_cols) > 10:
        print(f"  ... and {len(individual_parish_cols) - 10} more")
    
    # Test extraction
    extractor = ParishExtractor()
    dataframes = [(df, info.dataset_type)]
    parish_records = extractor.extract_parishes_from_dataframes(dataframes)
    
    print(f"\nExtracted parish records: {len(parish_records)}")
    
    print("\n=== CONCLUSION ===")
    print("The parish extractor is designed for weekly bills with suffixes like '_buried'.")
    print("General bills have individual parish columns without suffixes.")
    print("This is why parish extraction fails and generates 0 bill records.")


if __name__ == "__main__":
    debug_parish_extraction()
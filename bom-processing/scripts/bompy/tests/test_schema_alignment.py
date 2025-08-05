#!/usr/bin/env python3
"""Test schema alignment with actual data."""

import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bom.loaders import CSVLoader
from bom.extractors import WeekExtractor
from bom.models import WeekRecord
from bom.utils.validation import SchemaValidator

def main():
    """Test our schema-aligned processing."""
    
    # Configure logging
    logger.add(sys.stderr, level="INFO")
    
    # Load a sample dataset
    data_raw_dir = Path(__file__).parent / "data-raw"
    csv_files = list(data_raw_dir.glob("*parishes*.csv"))[:2]  # Just test 2 files
    
    if not csv_files:
        logger.error("No parish CSV files found")
        return
    
    # Load the data
    loader = CSVLoader()
    dataframes = []
    
    for csv_file in csv_files:
        try:
            df, info = loader.load(csv_file)
            dataframes.append((df, info.dataset_type))
            logger.info(f"Loaded {info.dataset_type}: {df.shape}")
        except Exception as e:
            logger.error(f"Failed to load {csv_file.name}: {e}")
    
    # Test week extraction
    logger.info("\n=== Testing Week Extraction ===")
    week_extractor = WeekExtractor()
    
    try:
        weeks = week_extractor.extract_weeks_from_dataframes(dataframes)
        logger.info(f"Extracted {len(weeks)} unique weeks")
        
        # Show a sample
        if weeks:
            sample_week = weeks[0]
            logger.info(f"Sample week: {sample_week.joinid}")
            logger.info(f"  Year: {sample_week.year}")
            logger.info(f"  Week ID: {sample_week.week_id}")
            logger.info(f"  Split Year: {sample_week.split_year}")
        
        # Validate the weeks
        valid_weeks = week_extractor.validate_weeks(weeks)
        logger.info(f"✓ {len(valid_weeks)} weeks passed validation")
        
        # Test DataFrame conversion
        if valid_weeks:
            import pandas as pd
            week_df = pd.DataFrame([w.to_dict() for w in valid_weeks[:5]])
            logger.info("Sample week DataFrame:")
            print(week_df.to_string(max_cols=6))
        
    except Exception as e:
        logger.error(f"Week extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n✅ Schema alignment test completed!")

if __name__ == "__main__":
    main()
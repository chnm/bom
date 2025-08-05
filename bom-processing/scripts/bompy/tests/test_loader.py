#!/usr/bin/env python3
"""Test script for the CSV loader."""

import sys
from pathlib import Path
from loguru import logger

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bom.loaders import CSVLoader

def main():
    """Test the CSV loader with actual data files."""
    
    # Configure logging
    logger.add(sys.stderr, level="INFO")
    
    # Point to our data-raw directory
    data_raw_dir = Path(__file__).parent / "data-raw"
    
    if not data_raw_dir.exists():
        logger.error(f"Data directory not found: {data_raw_dir}")
        return
    
    # Find CSV files
    csv_files = list(data_raw_dir.glob("*.csv"))
    
    if not csv_files:
        logger.error(f"No CSV files found in {data_raw_dir}")
        return
    
    logger.info(f"Found {len(csv_files)} CSV files")
    
    # Test the loader
    loader = CSVLoader()
    
    # Load first few files as a test
    for csv_file in csv_files[:3]:  # Just test first 3 files
        try:
            logger.info(f"\n--- Testing {csv_file.name} ---")
            df, info = loader.load(csv_file)
            
            logger.info(f"Dataset type: {info.dataset_type}")
            logger.info(f"Shape: {df.shape}")
            logger.info(f"Columns: {', '.join(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
            
            if info.processing_notes:
                logger.info(f"Notes: {', '.join(info.processing_notes)}")
            
            # Show a sample of the data to verify it's not corrupted
            if not df.empty:
                logger.info("Sample data:")
                print(df.head(2).to_string(max_cols=6))
            
        except Exception as e:
            logger.error(f"Failed to process {csv_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info("\nLoader test completed!")

if __name__ == "__main__":
    main()
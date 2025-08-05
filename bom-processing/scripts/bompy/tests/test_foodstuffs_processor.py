#!/usr/bin/env python3
"""Test the foodstuffs processor with sample data."""

import sys
import time
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bom.loaders import CSVLoader
from bom.processors import FoodstuffsProcessor
from bom.utils.logging import setup_logging


def main():
    """Test foodstuffs processor with sample data."""
    
    start_time = time.time()
    
    # Setup logging
    log_file = setup_logging(
        log_level="INFO", log_name="foodstuffs_processor_test", console_output=True
    )
    
    logger.info("🍞 Starting foodstuffs processor test")
    
    # Setup paths
    data_raw_dir = Path(__file__).parent.parent / "data-raw"
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    # Find foodstuffs CSV files
    foodstuff_files = list(data_raw_dir.glob("*foodstuff*.csv"))
    logger.info(f"Found {len(foodstuff_files)} foodstuffs files to test")
    
    if not foodstuff_files:
        logger.error("No foodstuffs files found in data-raw directory")
        return
        
    # Load CSV files
    loader = CSVLoader()
    datasets = {}
    
    for csv_file in foodstuff_files:
        logger.info(f"Loading CSV: {csv_file.name}")
        df, dataset_info = loader.load(csv_file)
        dataset_name = dataset_info.dataset_type
        datasets[dataset_name] = df
        logger.info(f"Loaded {dataset_name}: {df.shape}")
    
    # Initialize and run foodstuffs processor
    processor = FoodstuffsProcessor()
    processor.process_datasets(datasets)
    
    # Get results
    records = processor.get_records()
    logger.info(f"Generated {len(records)} foodstuffs records")
    
    # Display sample records
    if records:
        logger.info("Sample foodstuffs records:")
        for i, record in enumerate(records[:5]):
            logger.info(f"  {i+1}. {record.year} Week {record.week}: {record.commodity_type} "
                       f"({record.quality_grade}) = {record.raw_value}")
    
    # Save to CSV
    output_path = output_dir / "foodstuffs.csv"
    processor.save_csv(output_path)
    
    # Generate summary statistics
    df = processor.to_dataframe()
    if not df.empty:
        logger.info("\n📊 Foodstuffs Data Summary:")
        logger.info(f"  • Total records: {len(df)}")
        logger.info(f"  • Years covered: {df['year'].min()}-{df['year'].max()}")
        logger.info(f"  • Commodity categories: {df['commodity_category'].unique().tolist()}")
        logger.info(f"  • Commodity types: {df['commodity_type'].nunique()} unique types")
        logger.info(f"  • Quality grades: {df['quality_grade'].value_counts().to_dict()}")
        logger.info(f"  • Measurement standards: {df['measurement_standard'].value_counts().to_dict()}")
        
        # Show value distributions
        non_null_weights = df[df['weight_pounds'].notna() | df['weight_ounces'].notna() | 
                             df['weight_drams'].notna()]
        non_null_prices = df[df['price_shillings'].notna() | df['price_pence'].notna()]
        
        logger.info(f"  • Records with weight data: {len(non_null_weights)}")
        logger.info(f"  • Records with price data: {len(non_null_prices)}")
    
    end_time = time.time()
    logger.success(f"✅ Foodstuffs processor test completed successfully in {end_time - start_time:.2f}s")


if __name__ == "__main__":
    main()
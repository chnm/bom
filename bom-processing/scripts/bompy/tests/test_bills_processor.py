#!/usr/bin/env python3
"""Test the bills processor with actual data."""

import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bom.loaders import CSVLoader
from bom.extractors import WeekExtractor, ParishExtractor
from bom.processors import BillsProcessor
from bom.utils.validation import SchemaValidator
from bom.utils.logging import LoggingContext

def main():
    """Test the bills processor with real data."""
    
    # Setup component-specific logging
    with LoggingContext("bills_processor_test", log_level="INFO"):
        
        # Load sample parish datasets
        data_raw_dir = Path(__file__).parent.parent / "data-raw"
        csv_files = list(data_raw_dir.glob("*parishes*.csv"))[:2]  # Test with 2 files
        
        if not csv_files:
            logger.error("No parish CSV files found")
            return
        
        logger.info(f"Testing bills processor with {len(csv_files)} files")
        
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
        
        if not dataframes:
            logger.error("No dataframes loaded")
            return
        
        # Extract parishes
        logger.info("\n=== Extracting Parishes ===")
        parish_extractor = ParishExtractor()
        parish_records = parish_extractor.extract_parishes_from_dataframes(dataframes)
        logger.info(f"Extracted {len(parish_records)} unique parishes")
        
        # Show sample parishes
        if parish_records:
            logger.info("Sample parishes:")
            for parish in parish_records[:5]:
                logger.info(f"  {parish.id}: {parish.parish_name}")
        
        # Extract weeks  
        logger.info("\n=== Extracting Weeks ===")
        week_extractor = WeekExtractor()
        week_records = week_extractor.extract_weeks_from_dataframes(dataframes)
        valid_weeks = week_extractor.validate_weeks(week_records)
        logger.info(f"Extracted {len(valid_weeks)} valid weeks")
        
        # Process bills
        logger.info("\n=== Processing Bills ===")
        bills_processor = BillsProcessor()
        
        try:
            bill_records, cause_records, new_week_records, new_year_records = bills_processor.process_parish_dataframes(
                dataframes, parish_records, valid_weeks
            )
            
            logger.info(f"Generated {len(bill_records)} bill records")
            
            # Show sample records
            if bill_records:
                logger.info("Sample bill records:")
                for i, record in enumerate(bill_records[:5]):
                    logger.info(f"  {i+1}. Parish {record.parish_id}, {record.count_type}: {record.count}, Year: {record.year}, Week: {record.joinid}")
            
            # Validate all records
            validator = SchemaValidator()
            valid_count = 0
            invalid_count = 0
            
            for record in bill_records:
                errors = validator.validate_bill_of_mortality(record)
                if errors:
                    invalid_count += 1
                    if invalid_count <= 5:  # Show first 5 errors
                        logger.warning(f"Invalid record: {errors}")
                else:
                    valid_count += 1
            
            logger.info(f"✓ {valid_count} valid bill records")
            if invalid_count > 0:
                logger.warning(f"✗ {invalid_count} invalid bill records")
            
            # Test CSV conversion
            if bill_records:
                import pandas as pd
                
                sample_records = bill_records[:10]
                bill_df = pd.DataFrame([r.to_dict() for r in sample_records])
                
                logger.info("\nSample bill DataFrame:")
                print(bill_df.to_string(max_cols=6))
                
                # Test CSV output
                output_dir = Path(__file__).parent.parent / "data"
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / "sample_bills.csv"
                bill_df.to_csv(output_file, index=False)
                logger.info(f"Sample data written to: {output_file}")
        
        except Exception as e:
            logger.error(f"Bills processing failed: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("\n✅ Bills processor test completed!")

if __name__ == "__main__":
    main()
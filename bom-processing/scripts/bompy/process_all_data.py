#!/usr/bin/env python3
"""Complete processing pipeline for Bills of Mortality data."""

import sys
import time
from pathlib import Path
from loguru import logger
import pandas as pd
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bom.loaders import CSVLoader
from bom.extractors import WeekExtractor, ParishExtractor, YearExtractor
from bom.processors import (BillsProcessor, FoodstuffsProcessor, ChristeningsProcessor, 
                             ChristeningsGenderProcessor, ChristeningsParishProcessor)
from bom.utils.validation import SchemaValidator
from bom.utils.logging import (
    setup_logging,
    log_processing_summary,
    log_validation_results,
    log_data_quality_metrics,
)


def main():
    """Process all Bills of Mortality data and generate PostgreSQL-ready outputs."""
    
    # Configuration flags
    ENABLE_GLOBAL_DEDUPLICATION = False  # Set to True to remove duplicate records across sources

    start_time = time.time()

    # Setup logging with timestamp-based log files
    log_file = setup_logging(
        log_level="INFO", log_name="bom_pipeline", console_output=True
    )

    logger.info("🚀 Starting complete Bills of Mortality processing pipeline")
    logger.info(f"📝 Log file: {log_file}")

    # Setup paths
    data_raw_dir = Path(__file__).parent / "data-raw"
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)

    # Find all CSV files
    csv_files = list(data_raw_dir.glob("*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files to process")

    if not csv_files:
        logger.error("No CSV files found in data-raw directory")
        return

    # Load all datasets
    logger.info("\n=== Loading All Datasets ===")
    loader = CSVLoader()
    all_dataframes = []
    total_input_rows = 0
    load_errors = 0

    for csv_file in csv_files:
        try:
            df, info = loader.load(csv_file)
            all_dataframes.append((df, info.dataset_type))
            total_input_rows += len(df)

            logger.info(
                f"✓ Loaded {info.dataset_type}: {df.shape} from {csv_file.name}"
            )

            # Log data quality metrics for first few files
            if len(all_dataframes) <= 3:
                null_counts = df.isnull().sum().to_dict()
                unique_counts = {col: df[col].nunique() for col in df.columns[:5]}
                data_types = df.dtypes.to_dict()

                log_data_quality_metrics(
                    dataset_name=info.dataset_type,
                    shape=df.shape,
                    null_counts=null_counts,
                    unique_counts=unique_counts,
                    data_types=data_types,
                )

        except Exception as e:
            load_errors += 1
            logger.error(f"✗ Failed to load {csv_file.name}: {e}")

    if not all_dataframes:
        logger.error("No datasets loaded successfully")
        return

    logger.info(f"Successfully loaded {len(all_dataframes)} datasets")
    logger.info(f"Total input rows: {total_input_rows:,}")
    if load_errors > 0:
        logger.warning(f"Load errors: {load_errors} files failed")

    # Extract all entities
    logger.info("\n=== Extracting All Entities ===")

    # Extract parishes
    parish_extractor = ParishExtractor()
    parish_records = parish_extractor.extract_parishes_from_dataframes(all_dataframes)
    logger.info(f"✓ Extracted {len(parish_records)} unique parishes")

    # Extract weeks
    week_extractor = WeekExtractor()
    week_records = week_extractor.extract_weeks_from_dataframes(all_dataframes)
    valid_weeks = week_extractor.validate_weeks(week_records)
    logger.info(f"✓ Extracted {len(valid_weeks)} valid weeks")

    # Extract years
    year_extractor = YearExtractor()
    year_records = year_extractor.extract_years_from_dataframes(all_dataframes)
    logger.info(f"✓ Extracted {len(year_records)} unique years")

    # Process bills
    logger.info("\n=== Processing Bills of Mortality ===")
    dictionary_path = output_dir / "dictionary.csv"
    bills_processor = BillsProcessor(
        dictionary_path=str(dictionary_path) if dictionary_path.exists() else None
    )

    # Filter to parish and causes datasets for bills processing
    bill_dataframes = [
        (df, name)
        for df, name in all_dataframes
        if "parish" in name.lower() or "causes" in name.lower()
    ]
    logger.info(
        f"Processing {len(bill_dataframes)} datasets (parish + causes) for bills"
    )

    bill_records, cause_records = bills_processor.process_parish_dataframes(
        bill_dataframes, parish_records, valid_weeks
    )
    logger.info(f"✓ Generated {len(bill_records)} bill of mortality records")
    logger.info(f"✓ Generated {len(cause_records)} causes of death records")

    # Process foodstuffs data
    logger.info("\n=== Processing Foodstuffs Data ===")
    foodstuffs_processor = FoodstuffsProcessor()
    
    # Filter to foodstuffs datasets
    foodstuffs_datasets = {
        name: df for df, name in all_dataframes
        if "foodstuff" in name.lower()
    }
    
    if foodstuffs_datasets:
        logger.info(f"Processing {len(foodstuffs_datasets)} foodstuffs datasets")
        foodstuffs_processor.process_datasets(foodstuffs_datasets)
        foodstuff_records = foodstuffs_processor.get_records()
        logger.info(f"✓ Generated {len(foodstuff_records)} foodstuffs records")
    else:
        logger.info("No foodstuffs datasets found")
        foodstuff_records = []

    # Process christenings data - split into gender and parish processing
    logger.info("\n=== Processing Christenings Data ===")
    
    # Process gender christenings
    gender_processor = ChristeningsGenderProcessor()
    gender_datasets = {
        name: df for df, name in all_dataframes
        if "gender" in name.lower()
    }
    
    if gender_datasets:
        logger.info(f"Processing {len(gender_datasets)} gender datasets for christenings")
        gender_processor.process_datasets(gender_datasets)
        gender_christening_records = gender_processor.get_records()
        logger.info(f"✓ Generated {len(gender_christening_records)} gender christening records")
    else:
        logger.info("No gender datasets found for christenings")
        gender_christening_records = []
    
    # Process parish christenings
    parish_processor = ChristeningsParishProcessor()
    parish_datasets = {
        name: df for df, name in all_dataframes
        if "parish" in name.lower()
    }
    
    if parish_datasets:
        logger.info(f"Processing {len(parish_datasets)} parish datasets for christenings")
        parish_processor.process_datasets(parish_datasets, parish_records, valid_weeks)
        parish_christening_records = parish_processor.get_records()
        logger.info(f"✓ Generated {len(parish_christening_records)} parish christening records")
    else:
        logger.info("No parish datasets found for christenings")
        parish_christening_records = []
    
    # Keep old processor for backward compatibility (combine all records)
    christenings_processor = ChristeningsProcessor()
    all_christenings_datasets = {
        name: df for df, name in all_dataframes
        if "gender" in name.lower() or "christening" in name.lower() or "parish" in name.lower()
    }
    
    if all_christenings_datasets:
        christenings_processor.process_datasets(all_christenings_datasets)
        christening_records = christenings_processor.get_records()
        logger.info(f"✓ Generated {len(christening_records)} total christening records (combined)")
    else:
        christening_records = []

    # Validate all records
    logger.info("\n=== Validating All Records ===")
    validator = SchemaValidator()

    # Validate bills
    valid_bills = []
    validation_errors = []
    for record in bill_records:
        errors = validator.validate_bill_of_mortality(record)
        if errors:
            validation_errors.extend(errors)
        else:
            valid_bills.append(record)

    log_validation_results(
        component="Bills of Mortality",
        total_records=len(bill_records),
        valid_records=len(valid_bills),
        validation_errors=validation_errors,
    )

    # Global deduplication for bills (optional)
    if ENABLE_GLOBAL_DEDUPLICATION:
        logger.info("Performing global deduplication on bills...")
        pre_dedup_count = len(valid_bills)
        seen_keys = {}
        
        for record in valid_bills:
            key = (record.parish_id, record.count_type, record.year, record.joinid)
            if key not in seen_keys:
                seen_keys[key] = record
            else:
                # Keep the record with higher count, or the newer one if counts are equal
                existing = seen_keys[key]
                if (record.count or 0) > (existing.count or 0):
                    seen_keys[key] = record
        
        valid_bills = list(seen_keys.values())
        post_dedup_count = len(valid_bills)
        
        if pre_dedup_count != post_dedup_count:
            logger.info(f"Global deduplication removed {pre_dedup_count - post_dedup_count} duplicate bill records")
        else:
            logger.info("No duplicate bill records found across sources")
    else:
        logger.info("Global deduplication disabled - preserving all source records")

    # Validate causes records
    valid_causes = []
    cause_validation_errors = []
    for record in cause_records:
        errors = validator.validate_causes_of_death(record)
        if errors:
            cause_validation_errors.extend(errors)
        else:
            valid_causes.append(record)

    log_validation_results(
        component="Causes of Death",
        total_records=len(cause_records),
        valid_records=len(valid_causes),
        validation_errors=cause_validation_errors,
    )

    # Global deduplication for causes (optional)
    if ENABLE_GLOBAL_DEDUPLICATION:
        logger.info("Performing global deduplication on causes...")
        pre_dedup_count = len(valid_causes)
        seen_keys = {}
        
        for record in valid_causes:
            key = (record.death, record.year, record.joinid)
            if key not in seen_keys:
                seen_keys[key] = record
            else:
                # Keep the record with non-null count, or higher count if both have counts
                existing = seen_keys[key]
                should_replace = False
                
                if existing.count is None and record.count is not None:
                    should_replace = True
                elif existing.count is not None and record.count is not None:
                    should_replace = record.count > existing.count
                # If both are None or existing has count and new doesn't, keep existing
                
                if should_replace:
                    seen_keys[key] = record
        
        valid_causes = list(seen_keys.values())
        post_dedup_count = len(valid_causes)
        
        if pre_dedup_count != post_dedup_count:
            logger.info(f"Global deduplication removed {pre_dedup_count - post_dedup_count} duplicate cause records")
        else:
            logger.info("No duplicate cause records found across sources")
    else:
        logger.info("Global deduplication disabled - preserving all source records")

    # Generate CSV outputs
    logger.info("\n=== Generating CSV Outputs ===")

    # Create DataFrames
    dataframes = {
        "parishes": pd.DataFrame([p.to_dict() for p in parish_records]),
        "weeks": pd.DataFrame([w.to_dict() for w in valid_weeks]),
        "years": pd.DataFrame([y.to_dict() for y in year_records]),
        "all_bills": pd.DataFrame([b.to_dict() for b in valid_bills]),
        "causes_of_death": pd.DataFrame([c.to_dict() for c in valid_causes]),
        "foodstuffs": pd.DataFrame([f.to_dict() for f in foodstuff_records]),
        "christenings_by_gender": pd.DataFrame([c.to_dict() for c in gender_christening_records]),
        "christenings_by_parish": pd.DataFrame([c.to_dict() for c in parish_christening_records]),
        "christenings": pd.DataFrame([c.to_dict() for c in christening_records]),  # Keep for backward compatibility
    }

    # Write CSV files
    output_files = {}
    for table_name, df in dataframes.items():
        if len(df) > 0:
            output_file = output_dir / f"{table_name}.csv"
            df.to_csv(output_file, index=False)
            output_files[table_name] = output_file
            logger.info(f"✓ {table_name}: {len(df):,} records → {output_file}")
        else:
            logger.warning(f"✗ {table_name}: No records to write")

    # Generate comprehensive summary report
    end_time = time.time()
    processing_time = end_time - start_time

    output_record_counts = {
        "parishes": len(parish_records),
        "weeks": len(valid_weeks),
        "years": len(year_records),
        "bill_of_mortality": len(valid_bills),
        "causes_of_death": len(valid_causes),
        "foodstuffs": len(foodstuff_records),
        "christenings_by_gender": len(gender_christening_records),
        "christenings_by_parish": len(parish_christening_records),
        "christenings": len(christening_records),
    }

    error_count = load_errors + len(validation_errors) + len(cause_validation_errors)

    log_processing_summary(
        input_files=len(csv_files),
        input_rows=total_input_rows,
        output_records=output_record_counts,
        processing_time=processing_time,
        errors=error_count,
    )

    logger.info("📁 Output Files:")
    for table_name, file_path in output_files.items():
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"   • {file_path} ({file_size:.1f} MB)")

    logger.success("🎉 Processing pipeline completed successfully!")
    logger.info(f"📝 Detailed logs saved to: {log_file}")


if __name__ == "__main__":
    main()

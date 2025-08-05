"""Year extraction for the year table."""

import pandas as pd
from typing import List, Set
from loguru import logger

from ..models import YearRecord
from ..utils.validation import SchemaValidator


class YearExtractor:
    """Extracts unique years for the year table."""
    
    def extract_years_from_dataframes(self, dataframes: List[tuple[pd.DataFrame, str]]) -> List[YearRecord]:
        """Extract unique years from multiple DataFrames."""
        all_years: Set[int] = set()
        
        for df, source_name in dataframes:
            if "year" in df.columns:
                years = df["year"].dropna().astype(int).unique()
                all_years.update(years)
                logger.info(f"Found {len(years)} years in {source_name}")
        
        # Convert to YearRecord objects
        year_records = [YearRecord(year=year) for year in sorted(all_years)]
        
        # Validate
        validator = SchemaValidator()
        valid_records = []
        for record in year_records:
            errors = validator.validate_year_record(record)
            if not errors:
                valid_records.append(record)
            else:
                logger.warning(f"Invalid year {record.year}: {errors}")
        
        logger.info(f"Extracted {len(valid_records)} valid unique years")
        return valid_records
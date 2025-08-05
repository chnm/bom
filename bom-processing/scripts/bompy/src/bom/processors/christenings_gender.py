"""Gender-specific christenings data processor for Bills of Mortality."""

import re
import pandas as pd
from typing import Dict, List, Optional, Any
from loguru import logger
from dataclasses import dataclass

from ..utils.columns import normalize_column_name


@dataclass
class ChristeningGenderRecord:
    """Represents a christenings_by_gender record."""
    year: int
    week_number: Optional[int]
    unique_identifier: str
    start_day: Optional[int]
    start_month: Optional[str]
    end_day: Optional[int]
    end_month: Optional[str]
    christening: str  # "Christened (Male)", "Christened (Female)", "Christened (In All)"
    count: Optional[int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "year": self.year,
            "week_number": self.week_number,
            "unique_identifier": self.unique_identifier,
            "start_day": self.start_day,
            "start_month": self.start_month,
            "end_day": self.end_day,
            "end_month": self.end_month,
            "christening": self.christening,
            "count": self.count,
        }


class ChristeningsGenderProcessor:
    """Processes gender-specific christenings data from Bills of Mortality datasets."""
    
    def __init__(self):
        """Initialize the gender christenings processor."""
        self.records: List[ChristeningGenderRecord] = []
        
    def process_datasets(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Process multiple datasets to extract gender christenings data.
        
        Args:
            datasets: Dictionary mapping dataset names to DataFrames
        """
        logger.info("👶 Processing gender christenings data from datasets")
        
        for dataset_name, df in datasets.items():
            # Only process gender datasets for this processor
            if "gender" in dataset_name.lower():
                logger.info(f"Processing gender christenings from {dataset_name}")
                self._process_single_dataset(df, dataset_name)
            
        logger.info(f"Generated {len(self.records)} gender christenings records total")
    
    def _process_single_dataset(self, df: pd.DataFrame, dataset_name: str) -> None:
        """Process a single dataset for gender christenings data.
        
        Args:
            df: DataFrame to process
            dataset_name: Name of the dataset for source tracking
        """
        # Find gender-specific christening columns
        gender_columns = self._find_gender_christening_columns(df)
        
        if not gender_columns:
            logger.info(f"No gender christening columns found in {dataset_name}")
            return
            
        logger.info(f"Found {len(gender_columns)} gender christening columns in {dataset_name}")
        
        # Process each row in the dataset
        for _, row in df.iterrows():
            # Extract basic temporal data
            year = self._extract_year(row)
            week_number = self._extract_week_number(row)
            unique_identifier = self._extract_unique_identifier(row)
            
            if not year or not unique_identifier:
                continue
            
            # Extract date information
            start_day = self._extract_date_field(row, 'start_day')
            start_month = self._extract_date_field(row, 'start_month')
            end_day = self._extract_date_field(row, 'end_day')
            end_month = self._extract_date_field(row, 'end_month')
            
            # Process each gender christening column
            for column_name in gender_columns:
                christening_type = self._parse_gender_column(column_name)
                raw_value = row.get(column_name)
                
                # Skip if no value or invalid
                if pd.isna(raw_value) or raw_value == '':
                    continue
                    
                # Parse count from raw value
                count = self._parse_count(raw_value)
                
                # Create gender christening record
                record = ChristeningGenderRecord(
                    year=year,
                    week_number=week_number,
                    unique_identifier=unique_identifier,
                    start_day=start_day,
                    start_month=start_month,
                    end_day=end_day,
                    end_month=end_month,
                    christening=christening_type,
                    count=count
                )
                
                self.records.append(record)
    
    def _find_gender_christening_columns(self, df: pd.DataFrame) -> List[str]:
        """Find gender-specific christening columns.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of column names containing gender christening data
        """
        gender_columns = []
        
        # Patterns for gender-specific christening columns
        patterns = [
            r'christened.*male',
            r'christened.*female', 
            r'christened.*total',
            r'christened.*all',
        ]
        
        for column in df.columns:
            normalized_col = normalize_column_name(column).lower()
            original_col = column.lower()
            
            # Check if column matches any gender christening pattern
            for pattern in patterns:
                if re.search(pattern, normalized_col, re.IGNORECASE) or re.search(pattern, original_col, re.IGNORECASE):
                    gender_columns.append(column)
                    break
                    
        return list(set(gender_columns))  # Remove duplicates
    
    def _parse_gender_column(self, column_name: str) -> str:
        """Parse a gender column name to extract christening type.
        
        Args:
            column_name: Name of the column to parse
            
        Returns:
            Standardized christening type string
        """
        normalized = normalize_column_name(column_name).lower()
        
        # Map to standard format matching R output
        if 'male' in normalized and 'female' not in normalized:
            return 'Christened (Male)'
        elif 'female' in normalized:
            return 'Christened (Female)'
        elif 'total' in normalized or 'all' in normalized:
            return 'Christened (In All)'
        else:
            return 'Christened (In All)'  # Default fallback
    
    def _extract_year(self, row: pd.Series) -> Optional[int]:
        """Extract year from row data."""
        year_fields = ['year', 'Year']
        
        for field in year_fields:
            if field in row.index and not pd.isna(row[field]):
                try:
                    return int(row[field])
                except (ValueError, TypeError):
                    continue
                    
        return None
    
    def _extract_week_number(self, row: pd.Series) -> Optional[int]:
        """Extract week number from row data."""
        week_fields = ['week', 'Week', 'week_number', 'Week Number']
        
        for field in week_fields:
            if field in row.index and not pd.isna(row[field]):
                try:
                    return int(row[field])
                except (ValueError, TypeError):
                    continue
                    
        return None
    
    def _extract_unique_identifier(self, row: pd.Series) -> Optional[str]:
        """Extract unique identifier from row data."""
        id_fields = ['unique_identifier', 'Unique Identifier', 'identifier', 'id']
        
        for field in id_fields:
            if field in row.index and not pd.isna(row[field]):
                return str(row[field])
                
        return None
    
    def _extract_date_field(self, row: pd.Series, field_type: str) -> Optional[Any]:
        """Extract date field from row data."""
        field_mappings = {
            'start_day': ['start_day', 'Start Day'],
            'start_month': ['start_month', 'Start Month'],
            'end_day': ['end_day', 'End Day'],
            'end_month': ['end_month', 'End Month']
        }
        
        fields = field_mappings.get(field_type, [])
        
        for field in fields:
            if field in row.index and not pd.isna(row[field]):
                if field_type in ['start_day', 'end_day']:
                    try:
                        return int(row[field])
                    except (ValueError, TypeError):
                        continue
                else:
                    return str(row[field])
                    
        return None
    
    def _parse_count(self, raw_value: Any) -> Optional[int]:
        """Parse count value from raw data."""
        if pd.isna(raw_value):
            return None
            
        # Convert to string for processing
        value_str = str(raw_value).strip()
        
        # Handle common non-numeric indicators
        if value_str.lower() in ['', 'none', 'n/a', 'na', '-']:
            return None
            
        # Try to extract numeric value
        try:
            # Remove common punctuation and whitespace
            clean_value = re.sub(r'[^\d]', '', value_str)
            if clean_value:
                return int(clean_value)
        except (ValueError, TypeError):
            pass
            
        return None
    
    def get_records(self) -> List[ChristeningGenderRecord]:
        """Get all processed gender christening records."""
        return self.records
    
    def save_csv(self, output_path: str) -> None:
        """Save processed gender christening records to CSV file.
        
        Args:
            output_path: Path to output CSV file
        """
        if not self.records:
            logger.warning("No gender christenings records to save")
            return
            
        # Convert records to DataFrame
        df = pd.DataFrame([record.to_dict() for record in self.records])
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(self.records)} gender christenings records to {output_path}")
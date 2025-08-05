"""Parish-level christenings data processor for Bills of Mortality."""

import re
import pandas as pd
from typing import Dict, List, Optional, Any
from loguru import logger
from dataclasses import dataclass

from ..models import ParishRecord, WeekRecord
from ..utils.columns import normalize_column_name


@dataclass
class ChristeningParishRecord:
    """Represents a christenings record matching temp table schema."""
    year: int
    week: Optional[int]
    unique_identifier: str
    start_day: Optional[int]
    start_month: Optional[str]
    end_day: Optional[int]
    end_month: Optional[str]
    parish_name: str
    count: Optional[int]
    missing: Optional[bool]
    illegible: Optional[bool]
    source: str
    bill_type: Optional[str]
    joinid: Optional[str]
    start_year: Optional[int]
    end_year: Optional[int]
    count_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "year": self.year,
            "week": self.week,
            "unique_identifier": self.unique_identifier,
            "start_day": self.start_day,
            "start_month": self.start_month,
            "end_day": self.end_day,
            "end_month": self.end_month,
            "parish_name": self.parish_name,
            "count": self.count,
            "missing": self.missing,
            "illegible": self.illegible,
            "source": self.source,
            "bill_type": self.bill_type,
            "joinid": self.joinid,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "count_type": self.count_type,
        }


class ChristeningsParishProcessor:
    """Processes parish-level christenings data from Bills of Mortality datasets."""
    
    def __init__(self):
        """Initialize the parish christenings processor."""
        self.records: List[ChristeningParishRecord] = []
        
    def process_datasets(self, datasets: Dict[str, pd.DataFrame], 
                        parish_records: List[ParishRecord], 
                        week_records: List[WeekRecord]) -> None:
        """Process multiple datasets to extract parish christenings data.
        
        Args:
            datasets: Dictionary mapping dataset names to DataFrames
            parish_records: List of parish records for mapping
            week_records: List of week records for mapping
        """
        logger.info("⛪ Processing parish christenings data from datasets")
        
        # Create mappings for lookups
        parish_mapping = self._create_parish_mapping(parish_records)
        week_mapping = {week.joinid: week for week in week_records}
        
        for dataset_name, df in datasets.items():
            # Only process parish datasets for this processor
            if "parish" in dataset_name.lower():
                logger.info(f"Processing parish christenings from {dataset_name}")
                self._process_single_dataset(df, dataset_name, parish_mapping, week_mapping)
            
        logger.info(f"Generated {len(self.records)} parish christenings records total")
    
    def _process_single_dataset(self, df: pd.DataFrame, dataset_name: str,
                               parish_mapping: Dict[str, str], 
                               week_mapping: Dict[str, WeekRecord]) -> None:
        """Process a single dataset for parish christenings data.
        
        Args:
            df: DataFrame to process
            dataset_name: Name of the dataset for source tracking
            parish_mapping: Mapping from column names to parish names
            week_mapping: Mapping from joinid to week records
        """
        # Find parish christening columns
        parish_christening_columns = self._find_parish_christening_columns(df)
        
        if not parish_christening_columns:
            logger.info(f"No parish christening columns found in {dataset_name}")
            return
            
        logger.info(f"Found {len(parish_christening_columns)} parish christening columns in {dataset_name}")
        
        # Process each row in the dataset
        for _, row in df.iterrows():
            # Extract basic temporal data
            year = self._extract_year(row)
            week_number = self._extract_week_number(row)
            unique_identifier = self._extract_unique_identifier(row)
            
            # Validate year range (1400-1800)
            if year and (year < 1400 or year >= 1800):
                logger.warning(f"Invalid year {year} in record {unique_identifier} from {dataset_name}. Skipping record.")
                continue
                
            # Validate week number range (1-90)
            if week_number and (week_number < 1 or week_number > 90):
                logger.warning(f"Invalid week {week_number} in record {unique_identifier} from {dataset_name}. Skipping record.")
                continue
            
            if not year or not unique_identifier:
                continue
            
            # Extract date information
            start_day = self._extract_date_field(row, 'start_day')
            start_month = self._extract_date_field(row, 'start_month')
            end_day = self._extract_date_field(row, 'end_day')
            end_month = self._extract_date_field(row, 'end_month')
            
            # Create joinid for week lookup
            joinid = self._create_joinid(year, week_number, unique_identifier, 
                                       start_day, start_month, end_day, end_month)
            week_record = week_mapping.get(joinid)
            
            # Determine bill type
            bill_type = self._determine_bill_type(week_number)
            
            # Process each parish christening column
            for column_name in parish_christening_columns:
                parish_name = self._extract_parish_name_from_column(column_name)
                raw_value = row.get(column_name)
                
                # Skip if no value
                if pd.isna(raw_value) or raw_value == '':
                    continue
                    
                # Parse count from raw value
                count = self._parse_count(raw_value)
                missing = self._is_missing_value(raw_value)
                illegible = self._is_illegible_value(raw_value)
                
                # Create parish christening record
                record = ChristeningParishRecord(
                    year=year,
                    week=week_number,
                    unique_identifier=unique_identifier,
                    start_day=start_day,
                    start_month=start_month,
                    end_day=end_day,
                    end_month=end_month,
                    parish_name=parish_name,
                    count=count,
                    missing=missing,
                    illegible=illegible,
                    source=dataset_name,
                    bill_type=bill_type,
                    joinid=joinid,
                    start_year=year,
                    end_year=year,
                    count_type="christened",
                )
                
                self.records.append(record)
    
    def _find_parish_christening_columns(self, df: pd.DataFrame) -> List[str]:
        """Find parish-level christening columns.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of column names containing parish christening data
        """
        christening_columns = []
        
        # Patterns for parish christening columns
        patterns = [
            # Aggregate parish patterns (most common in parish files)
            r'christened.*parish',
            r'christened.*wall',
            r'christened.*middlesex',
            r'christened.*surrey', 
            r'christened.*westminster',
            # Patterns that start with christened (for parish aggregate columns)
            r'^christened.*in.*the',
            r'^christened.*parishes',
        ]
        
        for column in df.columns:
            normalized_col = normalize_column_name(column).lower()
            original_col = column.lower()
            
            # Check if column matches any parish christening pattern
            for pattern in patterns:
                if re.search(pattern, normalized_col, re.IGNORECASE) or re.search(pattern, original_col, re.IGNORECASE):
                    christening_columns.append(column)
                    break
                    
        return list(set(christening_columns))  # Remove duplicates
    
    def _extract_parish_name_from_column(self, column_name: str) -> str:
        """Extract parish name from column name.
        
        Args:
            column_name: Name of the column
            
        Returns:
            Parish name extracted from column
        """
        # Handle aggregate parish groups
        normalized = normalize_column_name(column_name).lower()
        
        if 'christened_in_the_97_parishes_within_the_walls' in normalized:
            return 'Christened in the 97 parishes within the walls'
        elif 'christened_in_the_parishes_without_the_walls' in normalized:
            return 'Christened in the parishes without the walls'
        elif 'christened_in_the_out_parishes_in_middlesex_and_surrey' in normalized:
            return 'Christened in the out-Parishes in Middlesex and Surrey'
        elif 'christened_in_the_parishes_and_liberties_of_westminster' in normalized:
            return 'Christened in the Parishes and Liberties of Westminster'
        elif 'christened_in_the_parishes_in_the_city_and_liberties_of_westminster' in normalized:
            return 'Christened in the Parishes in the City and Liberties of Westminster'
        else:
            # Clean up column name for parish name
            parish_name = column_name.replace('_', ' ').title()
            parish_name = re.sub(r'\s+', ' ', parish_name).strip()
            return parish_name
    
    def _create_parish_mapping(self, parish_records: List[ParishRecord]) -> Dict[str, str]:
        """Create mapping from column names to parish names."""
        mapping = {}
        for parish in parish_records:
            mapping[parish.parish_name.lower()] = parish.parish_name
            mapping[parish.canonical_name.lower()] = parish.parish_name
        return mapping
    
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
    
    def _create_joinid(self, year: int, week_number: Optional[int], 
                      unique_identifier: str, start_day: Optional[int] = None,
                      start_month: Optional[str] = None, end_day: Optional[int] = None,
                      end_month: Optional[str] = None) -> str:
        """Create joinid for week lookup using WeekExtractor logic."""
        from ..extractors.weeks import WeekExtractor
        extractor = WeekExtractor()
        
        # Use WeekExtractor's create_joinid method for consistency
        if start_day and start_month and end_day and end_month:
            return extractor.create_joinid(year, start_month, start_day, end_month, end_day)
        else:
            # Fallback to default date range if specific dates not available
            return extractor.create_joinid(year, "january", 1, "january", 7)
    
    def _determine_bill_type(self, week_number: Optional[int]) -> Optional[str]:
        """Determine bill type based on week number."""
        if week_number == 90:
            return "general"
        elif week_number and 1 <= week_number <= 53:
            return "weekly"
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
    
    def _is_missing_value(self, raw_value: Any) -> Optional[bool]:
        """Determine if a value represents missing data."""
        if pd.isna(raw_value):
            return True
            
        value_str = str(raw_value).strip().lower()
        missing_indicators = ['missing', 'miss', 'm', 'n/a', 'na', '']
        
        return value_str in missing_indicators
    
    def _is_illegible_value(self, raw_value: Any) -> Optional[bool]:
        """Determine if a value represents illegible data."""
        if pd.isna(raw_value):
            return False
            
        value_str = str(raw_value).strip().lower()
        illegible_indicators = ['illegible', 'illeg', 'unclear', '?', 'torn']
        
        return any(indicator in value_str for indicator in illegible_indicators)
    
    def get_records(self) -> List[ChristeningParishRecord]:
        """Get all processed parish christening records."""
        return self.records
    
    def save_csv(self, output_path: str) -> None:
        """Save processed parish christening records to CSV file.
        
        Args:
            output_path: Path to output CSV file
        """
        if not self.records:
            logger.warning("No parish christenings records to save")
            return
            
        # Convert records to DataFrame
        df = pd.DataFrame([record.to_dict() for record in self.records])
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(self.records)} parish christenings records to {output_path}")
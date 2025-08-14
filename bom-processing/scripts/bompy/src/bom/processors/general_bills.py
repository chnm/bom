"""Specialized processor for General Bills data format."""

import pandas as pd
from typing import List, Dict, Set, Optional, Tuple
from loguru import logger
import re

from ..models import BillOfMortalityRecord, ParishRecord, WeekRecord, YearRecord
from ..utils.validation import SchemaValidator


class GeneralBillsProcessor:
    """Specialized processor for General Bills data format.
    
    General Bills have a different structure than Weekly Bills:
    - Individual parish columns are raw parish names without suffixes
    - Each individual parish column represents burial counts by default
    - Aggregate columns like "Christened in the 97 parishes within the walls"
    - No individual is_missing/is_illegible columns per parish
    """
    
    def __init__(self):
        self.validator = SchemaValidator()
        
        # Patterns to identify aggregate vs individual parish columns
        self.aggregate_patterns = [
            r'christened in the.*parishes',
            r'buried in the.*parishes', 
            r'plague in the.*parishes',
            r'parishes clear of',
            r'parishes infected',
        ]
        
        # Common London parish name patterns for individual parishes
        self.parish_name_patterns = [
            r'^st\s+\w+',           # "St Mary", "St John", etc.
            r'^saint\s+\w+',        # "Saint Mary"
            r'^alhallows?\s+\w+',   # "Alhallows Barking", "Allhallows Great"
            r'^christ\s+church',    # "Christ Church"
            r'^trinity',            # "Trinity Parish"
            r'^s\s+\w+',           # "S Sepulchres Parish"
            r'parish$',             # Ends with "Parish"
            r'church$',             # Ends with "Church"
            r'precinct$',           # Ends with "Precinct"
        ]
    
    def is_general_bill_dataset(self, source_name: str) -> bool:
        """Determine if this dataset contains General Bills."""
        return 'general' in source_name.lower()
    
    def is_aggregate_column(self, column_name: str) -> bool:
        """Check if column is an aggregate (not individual parish)."""
        col_lower = column_name.lower()
        return any(re.search(pattern, col_lower) for pattern in self.aggregate_patterns)
    
    def is_individual_parish_column(self, column_name: str) -> bool:
        """Check if column represents an individual parish."""
        col_lower = column_name.lower()
        
        # Skip metadata columns
        if any(skip in col_lower for skip in ['omeka', 'datascribe', 'image_', 'unique_', 'start_', 'end_']):
            return False
        
        # Skip aggregate columns
        if self.is_aggregate_column(column_name):
            return False
            
        # Check parish name patterns
        return any(re.search(pattern, col_lower) for pattern in self.parish_name_patterns)
    
    def extract_parish_name(self, column_name: str) -> str:
        """Extract clean parish name from column name."""
        # Remove count type suffixes if present (sometimes general bills have them)
        parish_name = re.sub(r'_(buried|plague|christened|baptized|other)$', '', column_name)
        parish_name = re.sub(r'\s+(buried|plague|christened|baptized|other)$', '', parish_name, flags=re.IGNORECASE)
        
        # Convert underscores to spaces and standardize case
        parish_name = parish_name.replace('_', ' ')
        
        # Standardize case: Title case for most words, but preserve 'St' abbreviations
        words = parish_name.split()
        standardized_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower in ['st', 's']:
                standardized_words.append(word_lower.title())  # 'St', 'S'
            elif word_lower.startswith('st'):
                # Handle cases like 'stbotolphs' -> 'St Botolphs' 
                if len(word) > 2 and word[2:].isalpha():
                    standardized_words.append('St ' + word[2:].title())
                else:
                    standardized_words.append(word.title())
            else:
                standardized_words.append(word.title())
        
        parish_name = ' '.join(standardized_words)
        
        # Clean up spacing
        parish_name = re.sub(r'\s+', ' ', parish_name).strip()
        
        return parish_name
    
    def determine_count_type(self, column_name: str) -> str:
        """Determine count type for General Bills columns."""
        col_lower = column_name.lower()
        
        # Check aggregate columns for explicit types
        if 'christened' in col_lower:
            return 'christened'
        elif 'plague' in col_lower:
            return 'plague' 
        elif 'buried' in col_lower:
            return 'buried'
        else:
            # Individual parish columns in General Bills default to burial counts
            return 'buried'
    
    def find_parish_columns(self, df: pd.DataFrame, source_name: str) -> Tuple[List[str], List[str]]:
        """Find parish columns in General Bills format.
        
        Returns:
            Tuple of (individual_parish_columns, aggregate_columns)
        """
        individual_columns = []
        aggregate_columns = []
        
        for col in df.columns:
            if self.is_individual_parish_column(col):
                individual_columns.append(col)
            elif self.is_aggregate_column(col):
                aggregate_columns.append(col)
        
        logger.info(f"Found {len(individual_columns)} individual parish columns in {source_name}")
        logger.info(f"Found {len(aggregate_columns)} aggregate columns in {source_name}")
        
        return individual_columns, aggregate_columns
    
    def create_parish_id_mapping(self, parish_records: List[ParishRecord]) -> Dict[str, int]:
        """Create mapping from parish name to parish ID."""
        mapping = {}
        
        for parish in parish_records:
            # Map both original and canonical names to the same ID
            mapping[parish.parish_name.lower().strip()] = parish.id
            mapping[parish.canonical_name.lower().strip()] = parish.id
        
        return mapping
    
    def create_week_id_mapping(self, week_records: List[WeekRecord]) -> Dict[str, str]:
        """Create mapping from joinid to week_id."""
        return {week.joinid: week.week_id for week in week_records}
    
    def find_parish_id(self, parish_name: str, parish_mapping: Dict[str, int]) -> Optional[int]:
        """Find parish ID using fuzzy matching."""
        parish_clean = parish_name.lower().strip()
        
        # Direct match
        if parish_clean in parish_mapping:
            return parish_mapping[parish_clean]
        
        # Try variations
        variations = [
            parish_clean,
            parish_clean.replace('st ', 'saint '),
            parish_clean.replace('saint ', 'st '),
            parish_clean.replace(' church', ''),
            parish_clean.replace(' parish', ''),
            # Handle "Alhallows" vs "All Hallows" variations
            parish_clean.replace('alhallows ', 'all hallows '),
            parish_clean.replace('all hallows ', 'alhallows '),
        ]
        
        for variation in variations:
            if variation in parish_mapping:
                return parish_mapping[variation]
        
        # Partial match
        for mapped_name, parish_id in parish_mapping.items():
            if parish_clean in mapped_name or mapped_name in parish_clean:
                return parish_id
        
        return None
    
    def extract_year_from_row(self, row: pd.Series) -> Optional[int]:
        """Extract year from General Bills row."""
        # General Bills use start_year and end_year columns
        for col in ['start_year', 'end_year', 'year']:
            if col in row.index and pd.notna(row.get(col)):
                try:
                    return int(row[col])
                except (ValueError, TypeError):
                    continue
        return None
    
    def find_week_id_for_row(self, row: pd.Series, week_mapping: Dict[str, str], new_week_records: List[WeekRecord], new_year_records: List[YearRecord], seen_years: Set[int]) -> Optional[str]:
        """Find week_id for General Bills row."""
        try:
            year = self.extract_year_from_row(row)
            if not year:
                return None
            
            # Extract actual end date from row data
            start_day = int(row.get('start_day')) if pd.notna(row.get('start_day')) else None
            start_month = str(row.get('start_month')) if pd.notna(row.get('start_month')) else None
            end_day = int(row.get('end_day')) if pd.notna(row.get('end_day')) else None
            end_month = str(row.get('end_month')) if pd.notna(row.get('end_month')) else None
            
            # Handle year-spanning periods
            start_year = int(row.get('start_year', year)) if pd.notna(row.get('start_year')) else year
            end_year = int(row.get('end_year', year)) if pd.notna(row.get('end_year')) else year
            
            # Use defaults if data is missing
            if not start_day or not start_month:
                start_day = 17
                start_month = 'december'
            if not end_day or not end_month:
                end_day = 16  
                end_month = 'december'
            
            # Import WeekExtractor to create consistent joinid
            from ..extractors.weeks import WeekExtractor
            extractor = WeekExtractor()
            joinid = extractor.create_joinid(start_year, start_month, start_day, end_year, end_month, end_day)
            
            # If joinid exists in mapping, use it; otherwise create new WeekRecord
            if joinid not in week_mapping:
                week_id = extractor.create_week_id(end_year, 90)  # General bills use week 90
                year_range = f"{start_year}-{end_year}" if start_year != end_year else str(end_year)
                
                # Create new WeekRecord for this general bill period
                new_week = WeekRecord(
                    joinid=joinid,
                    start_day=start_day,
                    start_month=start_month,
                    end_day=end_day, 
                    end_month=end_month,
                    year=end_year,
                    week_number=90,  # General bills use week 90
                    split_year=year_range,
                    unique_identifier=row.get('unique_identifier', ''),
                    week_id=week_id,
                    year_range=year_range
                )
                
                new_week_records.append(new_week)
                week_mapping[joinid] = week_id
                
                # Track new years for YearRecord creation
                if end_year not in seen_years:
                    new_year_record = YearRecord(year=end_year)
                    new_year_records.append(new_year_record)
                    seen_years.add(end_year)
                
                if start_year != end_year and start_year not in seen_years:
                    new_year_record = YearRecord(year=start_year)
                    new_year_records.append(new_year_record)
                    seen_years.add(start_year)
                
            return joinid
        except Exception:
            return None
    
    def process_general_bills_dataframe(
        self,
        df: pd.DataFrame,
        source_name: str,
        parish_records: List[ParishRecord],
        week_records: List[WeekRecord]
    ) -> Tuple[List[BillOfMortalityRecord], List[WeekRecord], List[YearRecord]]:
        """Process a General Bills DataFrame into BillOfMortalityRecord objects."""
        
        parish_mapping = self.create_parish_id_mapping(parish_records)
        week_mapping = self.create_week_id_mapping(week_records)
        new_week_records = []
        new_year_records = []
        seen_years = set()
        
        # Find parish columns
        individual_columns, aggregate_columns = self.find_parish_columns(df, source_name)
        all_parish_columns = individual_columns + aggregate_columns
        
        if not all_parish_columns:
            logger.warning(f"No parish columns found in General Bills dataset: {source_name}")
            return []
        
        # Create parish×count_type combinations
        parish_count_combinations = []
        for col in all_parish_columns:
            parish_name = self.extract_parish_name(col)
            parish_id = self.find_parish_id(parish_name, parish_mapping)
            count_type = self.determine_count_type(col)
            
            if parish_id:
                parish_count_combinations.append((parish_id, count_type, col))
            else:
                logger.warning(f"Could not find parish ID for '{parish_name}' from column '{col}'")
        
        logger.info(f"Found {len(parish_count_combinations)} parish×count_type combinations")
        
        records = []
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                year = self.extract_year_from_row(row)
                if not year:
                    continue
                
                week_id = self.find_week_id_for_row(row, week_mapping, new_week_records, new_year_records, seen_years)
                unique_identifier = row.get('unique_identifier', '')
                bill_type = 'general'  # Always general for this processor
                
                # Create records for all parish×count_type combinations
                for parish_id, count_type, col in parish_count_combinations:
                    count_value = row[col]
                    
                    # Handle missing/empty counts
                    if pd.isna(count_value) or count_value == '':
                        count = 0
                        is_missing = True
                    else:
                        try:
                            count = int(count_value)
                            is_missing = False
                        except (ValueError, TypeError):
                            count = 0
                            is_missing = True
                    
                    # Create bill record
                    record = BillOfMortalityRecord(
                        parish_id=parish_id,
                        count_type=count_type,
                        count=count,
                        year=year,
                        joinid=week_id,
                        bill_type=bill_type,
                        missing=is_missing,
                        illegible=False,  # General Bills don't have illegible flags per parish
                        source=source_name,
                        unique_identifier=unique_identifier
                    )
                    
                    records.append(record)
            
            except Exception as e:
                logger.warning(f"Failed to process row {idx} in {source_name}: {e}")
                continue
        
        # Deduplicate records
        seen_keys = {}
        for record in records:
            key = (record.parish_id, record.count_type, record.year, record.joinid)
            if key not in seen_keys:
                seen_keys[key] = record
            else:
                # Keep record with higher count
                existing = seen_keys[key]
                if (record.count or 0) > (existing.count or 0):
                    seen_keys[key] = record
        
        deduplicated = list(seen_keys.values())
        
        if len(records) != len(deduplicated):
            logger.info(f"Deduplicated {len(records) - len(deduplicated)} duplicate records")
        
        logger.info(f"Generated {len(deduplicated)} General Bills records from {source_name}")
        logger.info(f"Created {len(new_week_records)} new week records for General Bills")
        logger.info(f"Created {len(new_year_records)} new year records for General Bills")
        return deduplicated, new_week_records, new_year_records
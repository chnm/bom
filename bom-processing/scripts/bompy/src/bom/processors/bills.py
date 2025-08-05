"""Bills processor for converting parish data to BillOfMortalityRecord objects."""

import pandas as pd
from typing import List, Dict, Set, Optional, Tuple
from loguru import logger
import re

from ..models import BillOfMortalityRecord, CausesOfDeathRecord, ParishRecord, WeekRecord
from ..utils.validation import SchemaValidator


class BillsProcessor:
    """Processes parish datasets into individual BillOfMortalityRecord objects."""
    
    def __init__(self, dictionary_path: Optional[str] = None):
        self.validator = SchemaValidator()
        
        # Count type patterns to identify what type of data each column represents
        self.count_type_patterns = {
            'buried': r'_buried$|buried_|^buried',
            'plague': r'_plague$|plague_|^plague', 
            'christened': r'_christened$|christened_|^christened|_baptized$|baptized_|^baptized',
            'other': r'_other$|other_|^other'
        }
        
        # Load dictionary for cause definitions
        self.cause_definitions = self._load_dictionary(dictionary_path)
    
    def _load_dictionary(self, dictionary_path: Optional[str]) -> Dict[str, Dict[str, str]]:
        """Load cause definitions from dictionary CSV file."""
        if not dictionary_path:
            logger.info("No dictionary path provided, cause definitions will be empty")
            return {}
        
        try:
            import os
            if not os.path.exists(dictionary_path):
                logger.warning(f"Dictionary file not found at {dictionary_path}")
                return {}
            
            dict_df = pd.read_csv(dictionary_path)
            logger.info(f"Loaded {len(dict_df)} cause definitions from {dictionary_path}")
            
            # Create mapping from cause name (normalized) to definition info
            definitions = {}
            for _, row in dict_df.iterrows():
                cause = str(row.get('Cause', '')).lower().strip()
                if cause:
                    definitions[cause] = {
                        'definition': str(row.get('Definition', '')),
                        'source': str(row.get('Source', '')),
                        'notes': str(row.get('Notes', ''))
                    }
            
            return definitions
        except Exception as e:
            logger.error(f"Failed to load dictionary from {dictionary_path}: {e}")
            return {}
    
    def _normalize_cause_name(self, cause_name: str) -> str:
        """Normalize cause name for dictionary lookup."""
        # Convert to lowercase, replace underscores with spaces, strip whitespace
        normalized = cause_name.lower().replace('_', ' ').strip()
        
        # Handle common variations
        replacements = {
            'flox and small pox': 'smallpox',
            'st anthony s fire': "st. anthony's fire",
            'kings evil': "king's evil",
            'griping in the guts': 'griping in the guts',
            'rising of the lights': 'rising of the lights',
            'running of the reins': 'running of the reins',
            'stopping of the stomach': 'stopping of the stomach',
            'falling sickness': 'falling sickness',
            'noli me tangere': 'noli me tangere',
            'scald head': 'scald head',
            'spotted fever': 'spotted fever',
            'still born': 'stillborn',
            'swine pox': 'swine-pox',
            'french pox': 'syphilis'
        }
        
        for old, new in replacements.items():
            if old in normalized:
                normalized = normalized.replace(old, new)
                break
        
        return normalized
    
    def identify_count_type(self, column_name: str) -> str:
        """Identify the count type from column name."""
        col_lower = column_name.lower()
        
        for count_type, pattern in self.count_type_patterns.items():
            if re.search(pattern, col_lower):
                return count_type
        
        # Default fallback - if column contains numbers, assume it's buried
        return 'buried'
    
    def extract_parish_name_from_column(self, column_name: str) -> str:
        """Extract parish name from column name by removing count type suffixes."""
        # Remove common suffixes
        parish_name = re.sub(r'_(buried|plague|christened|baptized|other)$', '', column_name)
        
        # Convert underscores to spaces and title case
        parish_name = parish_name.replace('_', ' ').title()
        
        # Clean up any artifacts
        parish_name = re.sub(r'\s+', ' ', parish_name).strip()
        
        return parish_name
    
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
    
    def process_parish_dataframes(
        self, 
        dataframes: List[tuple[pd.DataFrame, str]], 
        parish_records: List[ParishRecord],
        week_records: List[WeekRecord]
    ) -> Tuple[List[BillOfMortalityRecord], List[CausesOfDeathRecord]]:
        """
        Process DataFrames into BillOfMortalityRecord and CausesOfDeathRecord objects.
        Handles both parish data and causes data with different processing logic.
        
        Args:
            dataframes: List of (DataFrame, source_name) tuples
            parish_records: List of ParishRecord objects for ID mapping
            week_records: List of WeekRecord objects for week_id mapping
            
        Returns:
            Tuple of (BillOfMortalityRecord list, CausesOfDeathRecord list)
        """
        parish_mapping = self.create_parish_id_mapping(parish_records)
        week_mapping = self.create_week_id_mapping(week_records)
        
        bill_records = []
        cause_records = []
        
        for df, source_name in dataframes:
            logger.info(f"Processing bills from {source_name}")
            
            # Determine if this is parish data or causes data
            is_causes_data = 'causes' in source_name.lower()
            
            if is_causes_data:
                # Process causes data
                records = self._process_causes_dataframe(df, source_name, week_mapping)
                cause_records.extend(records)
                logger.info(f"Generated {len(records)} cause records from {source_name}")
            else:
                # Process parish data
                records = self._process_parish_dataframe(df, source_name, parish_mapping, week_mapping)
                bill_records.extend(records)
                logger.info(f"Generated {len(records)} bill records from {source_name}")
        
        logger.info(f"Total bill of mortality records: {len(bill_records)}")
        logger.info(f"Total causes of death records: {len(cause_records)}")
        return bill_records, cause_records
    
    def _process_parish_dataframe(
        self, 
        df: pd.DataFrame, 
        source_name: str, 
        parish_mapping: Dict[str, int], 
        week_mapping: Dict[str, str]
    ) -> List[BillOfMortalityRecord]:
        """Process parish data structure."""
        # Find parish columns (exclude total columns and metadata)
        parish_columns = [
            col for col in df.columns 
            if not col.lower().startswith(('total', 'year', 'week', 'start_', 'end_', 'unique_'))
            and any(pattern in col.lower() for pattern in ['buried', 'plague', 'christened', 'baptized'])
        ]
        
        logger.info(f"Found {len(parish_columns)} parish columns in {source_name}")
        
        if not parish_columns:
            logger.warning(f"No parish columns found in {source_name}")
            return []
        
        # Extract unique parishes and count types from columns
        parish_count_combinations = []
        for col in parish_columns:
            parish_name = self.extract_parish_name_from_column(col)
            parish_id = self._find_parish_id(parish_name, parish_mapping)
            count_type = self.identify_count_type(col)
            
            if parish_id:
                parish_count_combinations.append((parish_id, count_type, col))
            else:
                logger.warning(f"Could not find parish ID for '{parish_name}' from column '{col}'")
        
        logger.info(f"Found {len(parish_count_combinations)} parish×count_type combinations")
        
        records = []
        # Process each row in the dataframe
        for idx, row in df.iterrows():
            try:
                year = int(row['year']) if pd.notna(row.get('year')) else None
                if not year:
                    continue
                
                # Create joinid for this row to find week_id
                week_id = self._find_week_id_for_row(row, week_mapping)
                
                # Determine bill type based on unique identifier and week data
                unique_identifier = row.get('unique_identifier', '')
                bill_type = self._determine_bill_type(unique_identifier, week_id)
                
                # Create a record for EVERY parish×count_type combination for this bill
                # This matches R's approach of creating comprehensive records
                for parish_id, count_type, col in parish_count_combinations:
                    count_value = row[col]
                    
                    # Handle missing/empty counts (preserve them as 0 with flags)
                    if pd.isna(count_value) or count_value == '' or count_value == 0:
                        count = 0
                        is_missing = pd.isna(count_value) or count_value == ''
                    else:
                        try:
                            count = int(count_value)
                            is_missing = False
                        except (ValueError, TypeError):
                            # Invalid count - preserve as 0 with missing flag
                            count = 0
                            is_missing = True
                    
                    # Create record with all required fields (even if count is 0/empty)
                    record = BillOfMortalityRecord(
                        parish_id=parish_id,
                        count_type=count_type,
                        count=count,
                        year=year,
                        joinid=week_id,
                        bill_type=bill_type,
                        missing=is_missing,
                        illegible=False,
                        source=source_name,
                        unique_identifier=unique_identifier
                    )
                    
                    # Always add the record (don't validate out empty records)
                    records.append(record)
            
            except Exception as e:
                logger.warning(f"Failed to process row {idx} in {source_name}: {e}")
                continue
        
        # Deduplicate records based on unique key (parish_id, count_type, year, joinid)
        # Keep the record with the highest count when duplicates exist
        seen_keys = {}
        
        for record in records:
            key = (record.parish_id, record.count_type, record.year, record.joinid)
            if key not in seen_keys:
                seen_keys[key] = record
            else:
                # Keep the record with higher count, or the newer one if counts are equal
                existing = seen_keys[key]
                if (record.count or 0) > (existing.count or 0):
                    seen_keys[key] = record
        
        deduplicated = list(seen_keys.values())
        
        if len(records) != len(deduplicated):
            logger.info(f"Deduplicated {len(records) - len(deduplicated)} duplicate bill records")
        
        return deduplicated
    
    def _process_causes_dataframe(
        self, 
        df: pd.DataFrame, 
        source_name: str, 
        week_mapping: Dict[str, str]
    ) -> List[CausesOfDeathRecord]:
        """
        Process causes data structure.
        Creates CausesOfDeathRecord objects for each cause.
        """
        # Find cause columns (exclude metadata columns and descriptive text)
        exclude_cols = {
            'omeka_item', 'datascribe_item', 'datascribe_record', 'datascribe_record_position', 
            'image_filename_s', 'year', 'week_number', 'unique_identifier', 'start_day', 
            'start_month', 'end_day', 'end_month', 'joinid', 'week_id', 'year_range', 'split_year',
            'christened_male', 'christened_female', 'christened_in_all', 'buried_male', 
            'buried_female', 'buried_all', 'plague_deaths', 'increase_decrease_in_burials',
            'increase_decrease_in_plague_deaths', 'parishes_clear_of_the_plague', 
            'parishes_infected_with_plague', 'ounces_in_penny_wheaten_loaf', 
            'ounces_in_three_half_penny_white_loaf'
        }
        
        # Filter out metadata and descriptive text columns
        cause_columns = []
        for col in df.columns:
            col_lower = col.lower()
            # Skip if it's in exclude list
            if col_lower in exclude_cols:
                continue
            # Skip metadata fields like "is_illegible_134", "is_missing_xyz"
            if col_lower.startswith(('is_illegible', 'is_missing')):
                continue
            # Skip descriptive text fields like "drowned_descriptive_text"
            if col_lower.endswith('_descriptive_text'):
                continue
            # This is a valid cause column
            cause_columns.append(col)
        
        logger.info(f"Found {len(cause_columns)} cause columns in {source_name}")
        
        if not cause_columns:
            logger.warning(f"No cause columns found in {source_name}")
            return []
        
        records = []
        # Process each row in the dataframe
        for idx, row in df.iterrows():
            try:
                year = int(row['year']) if pd.notna(row.get('year')) else None
                if not year:
                    continue
                
                # Create joinid for this row to find week_id
                week_id = self._find_week_id_for_row(row, week_mapping)
                
                # Create a record for EVERY cause for this bill
                for cause_col in cause_columns:
                    count_value = row[cause_col]
                    
                    # Handle missing/empty counts 
                    count = None
                    if pd.isna(count_value) or count_value == '':
                        count = None
                    elif count_value == 0:
                        count = 0
                    else:
                        try:
                            count = int(count_value)
                        except (ValueError, TypeError):
                            # For causes, text values might be descriptive
                            count = None
                    
                    # Look up definition for this cause
                    normalized_cause = self._normalize_cause_name(cause_col)
                    definition_info = self.cause_definitions.get(normalized_cause, {})
                    
                    # Convert cause name from column format to readable text
                    # Replace underscores with spaces and keep original capitalization
                    readable_cause_name = cause_col.replace('_', ' ')
                    
                    # Create causes of death record
                    record = CausesOfDeathRecord(
                        death=readable_cause_name,
                        count=count,
                        year=year,
                        joinid=week_id,
                        descriptive_text=None,
                        source_name=source_name,
                        definition=definition_info.get('definition'),
                        definition_source=definition_info.get('source')
                    )
                    
                    # Always add the record (preserve empty records for completeness)
                    records.append(record)
            
            except Exception as e:
                logger.warning(f"Failed to process row {idx} in {source_name}: {e}")
                continue
        
        # Deduplicate records based on unique key (death, year, joinid)
        # Keep the record with non-null count when duplicates exist, or the last one processed
        seen_keys = {}
        
        for record in records:
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
        
        deduplicated = list(seen_keys.values())
        
        if len(records) != len(deduplicated):
            logger.info(f"Deduplicated {len(records) - len(deduplicated)} duplicate cause records")
        
        return deduplicated
    
    def _find_week_id_for_row(self, row: pd.Series, week_mapping: Dict[str, str]) -> Optional[str]:
        """Find joinid for a row by creating it from row data."""
        try:
            # Try to create joinid from row data
            year = int(row.get('year', 0))
            start_day = int(row.get('start_day', 1)) if pd.notna(row.get('start_day')) else 1
            end_day = int(row.get('end_day', 7)) if pd.notna(row.get('end_day')) else 7
            start_month = str(row.get('start_month', 'january')) if pd.notna(row.get('start_month')) else 'january'
            end_month = str(row.get('end_month', 'january')) if pd.notna(row.get('end_month')) else 'january'
            
            # Import WeekExtractor to use its joinid creation logic
            from ..extractors.weeks import WeekExtractor
            extractor = WeekExtractor()
            joinid = extractor.create_joinid(year, start_month, start_day, end_month, end_day)
            
            # Return the joinid directly if it exists in the week mapping
            if joinid in week_mapping:
                return joinid
            else:
                return None
        except Exception:
            return None
    
    def _determine_bill_type(self, unique_identifier: str, week_id: Optional[str]) -> str:
        """
        Determine if this is a general or weekly bill.
        
        Args:
            unique_identifier: The unique identifier from the row
            week_id: The computed week_id
            
        Returns:
            "general" or "weekly"
        """
        if not unique_identifier:
            return "weekly"  # Default
        
        # Check identifier patterns
        identifier_lower = unique_identifier.lower()
        if any(pattern in identifier_lower for pattern in ['generalbill', 'general-bill', 'general_bill']):
            return "general"
        
        # Check if week_id indicates week 90 (general bill week)
        if week_id and '-90' in week_id:
            return "general"
        
        return "weekly"  # Default for all other cases
    
    def _find_parish_id(self, parish_name: str, parish_mapping: Dict[str, int]) -> Optional[int]:
        """Find parish ID using fuzzy matching."""
        parish_clean = parish_name.lower().strip()
        
        # Direct match
        if parish_clean in parish_mapping:
            return parish_mapping[parish_clean]
        
        # Try without common prefixes/suffixes
        variations = [
            parish_clean,
            parish_clean.replace('st ', 'saint '),
            parish_clean.replace('saint ', 'st '),
            parish_clean.replace(' church', ''),
            parish_clean.replace(' parish', ''),
        ]
        
        for variation in variations:
            if variation in parish_mapping:
                return parish_mapping[variation]
        
        # Partial match - find any parish name that contains this as substring
        for mapped_name, parish_id in parish_mapping.items():
            if parish_clean in mapped_name or mapped_name in parish_clean:
                return parish_id
        
        return None
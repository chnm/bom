"""Parish extraction for the parishes table."""

import pandas as pd
from typing import List, Set, Dict
from loguru import logger
import re

from ..models import ParishRecord


class ParishExtractor:
    """Extracts unique parishes for the parishes table."""
    
    def __init__(self):
        # Parish name cleaning patterns
        self.cleaning_patterns = [
            (r'\s+', ' '),  # Multiple spaces to single space
            (r'^\s+|\s+$', ''),  # Strip leading/trailing spaces
            (r'_+', ' '),  # Multiple underscores to single space (in case of normalization artifacts)
        ]
        
        # Load parish authority file
        self.authority_mapping = self._load_parish_authority()
    
    def _load_parish_authority(self) -> Dict[str, str]:
        """Load parish authority file to map parish names to canonical names."""
        authority_mapping = {}
        
        try:
            authority_file = "data/London Parish Authority File.csv"
            df = pd.read_csv(authority_file)
            
            for _, row in df.iterrows():
                canonical_name = row['Canonical DBN Name']
                omeka_name = row['Omeka Parish Name']
                variant_names = row['Variant Names'] if pd.notna(row['Variant Names']) else ""
                
                # Map Omeka name to canonical name
                if pd.notna(omeka_name) and pd.notna(canonical_name):
                    omeka_clean = str(omeka_name).strip()
                    canonical_clean = str(canonical_name).strip()
                    if omeka_clean and canonical_clean:
                        authority_mapping[omeka_clean] = canonical_clean
                
                # Map variant names to canonical name
                if variant_names and pd.notna(canonical_name):
                    canonical_clean = str(canonical_name).strip()
                    for variant in str(variant_names).split(','):
                        variant = variant.strip()
                        if variant and canonical_clean:
                            authority_mapping[variant] = canonical_clean
            
            logger.info(f"Loaded {len(authority_mapping)} parish name mappings from authority file")
            
        except Exception as e:
            logger.warning(f"Could not load parish authority file: {e}")
            logger.warning("Will use basic canonicalization")
        
        return authority_mapping
    
    def clean_parish_name(self, name: str) -> str:
        """Clean parish name while preserving original content."""
        if not name or pd.isna(name):
            return ""
        
        cleaned = str(name)
        for pattern, replacement in self.cleaning_patterns:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        return cleaned.strip()
    
    def _standardize_parish_name(self, parish_name: str) -> str:
        """Standardize parish name case and formatting."""
        # Convert underscores to spaces 
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
    
    def is_valid_parish_name(self, name: str) -> bool:
        """Check if a name is a valid parish name (not descriptive text)."""
        if not name or pd.isna(name):
            return False
        
        name_lower = name.lower()
        
        # Filter out descriptive entries
        invalid_patterns = [
            'demolished parishes',
            'parishes clear of',
            'parishes infected with',
            'parishes within the walls',
            'parishes without the walls',
            'out-parishes',
            'christened in the',
            'buried in the',
            'plague in the',
            'in the parishes',
            'total',
            'sum',
        ]
        
        for pattern in invalid_patterns:
            if pattern in name_lower:
                return False
        
        # Also filter names that are too generic/descriptive
        if name_lower.startswith(('in the', 'parishes ', 'total ', 'sum ')):
            return False
            
        return True
    
    def create_canonical_name(self, parish_name: str) -> str:
        """Create canonical name from parish name using authority file mapping."""
        if not parish_name:
            return ""
        
        cleaned_name = self.clean_parish_name(parish_name)
        
        # First try exact match in authority mapping
        if cleaned_name in self.authority_mapping:
            return self.authority_mapping[cleaned_name]
        
        # Try case-insensitive match
        for authority_name, canonical_name in self.authority_mapping.items():
            if authority_name.lower() == cleaned_name.lower():
                return canonical_name
        
        # If no match found, use the cleaned name as canonical
        logger.warning(f"No authority mapping found for parish: '{cleaned_name}'")
        return cleaned_name
    
    def extract_parishes_from_dataframes(self, dataframes: List[tuple[pd.DataFrame, str]]) -> List[ParishRecord]:
        """Extract unique parishes from multiple DataFrames."""
        parish_names: Set[str] = set()
        
        for df, source_name in dataframes:
            # Look for parish-related columns
            parish_cols = [col for col in df.columns if 'parish' in col.lower()]
            
            # Also look for columns that might be parish names (end with buried, plague, etc.)
            potential_parish_cols = [
                col for col in df.columns 
                if col.endswith(('_buried', '_plague', '_christened')) and not col.startswith('total')
            ]
            
            # For General Bills: Look for individual parish columns without suffixes
            is_general_bill = 'general' in source_name.lower()
            general_bill_parish_cols = []
            
            if is_general_bill:
                for col in df.columns:
                    col_lower = col.lower()
                    # Skip metadata and aggregate columns
                    if col_lower.startswith(('omeka', 'datascribe', 'image_', 'is_missing', 'is_illegible')):
                        continue
                    if col_lower.startswith(('total', 'year', 'week', 'start_', 'end_', 'unique_')):
                        continue
                    if any(phrase in col_lower for phrase in [
                        'christened in the', 'buried in the', 'plague in the'
                    ]):
                        continue  # Skip aggregate columns
                        
                    # Include individual parish columns for general bills  
                    # Handle both original format ('St Alban Woodstreet') and normalized format ('st_alban_woodstreet')
                    if (col.startswith(('St ', 'Christ ', 'Trinity', 'Alhal', 'S ')) or 
                        col_lower.startswith(('st_', 'christ_', 'trinity', 'alhal', 's_')) or
                        any(word in col for word in ['Parish', 'Church', 'Precinct']) or
                        any(word in col_lower for word in ['parish', 'church', 'precinct']) or
                        col.endswith(' Parish') or col_lower.endswith('_parish')):
                        general_bill_parish_cols.append(col)
                
                logger.info(f"Found {len(general_bill_parish_cols)} general bill parish columns in {source_name}")
            
            all_parish_cols = parish_cols + potential_parish_cols + general_bill_parish_cols
            
            if parish_cols:
                logger.info(f"Found parish columns in {source_name}: {parish_cols}")
                
                # Extract from parish_name column if it exists
                if 'parish_name' in df.columns:
                    names = df['parish_name'].dropna().unique()
                    for name in names:
                        cleaned = self.clean_parish_name(name)
                        if self.is_valid_parish_name(cleaned):
                            parish_names.add(cleaned)
            
            if potential_parish_cols:
                logger.info(f"Found {len(potential_parish_cols)} potential parish columns in {source_name}")
                
                # Extract parish names from column names themselves
                for col in potential_parish_cols:
                    # Remove suffixes like _buried, _plague to get parish name
                    parish_name = re.sub(r'_(buried|plague|christened|baptized|other)$', '', col)
                    parish_name = re.sub(r'\s+(buried|plague|christened|baptized|other)$', '', parish_name, flags=re.IGNORECASE)
                    parish_name = self._standardize_parish_name(parish_name)
                    cleaned = self.clean_parish_name(parish_name)
                    if cleaned and self.is_valid_parish_name(cleaned):
                        parish_names.add(cleaned)
            
            # For General Bills: Extract parish names directly from column names
            if general_bill_parish_cols:
                for col in general_bill_parish_cols:
                    # Remove suffixes and standardize case like weekly bills
                    parish_name = re.sub(r'_(buried|plague|christened|baptized|other)$', '', col)
                    parish_name = re.sub(r'\s+(buried|plague|christened|baptized|other)$', '', parish_name, flags=re.IGNORECASE)
                    parish_name = self._standardize_parish_name(parish_name)
                    cleaned = self.clean_parish_name(parish_name)
                    if cleaned and self.is_valid_parish_name(cleaned):
                        parish_names.add(cleaned)
        
        # Remove empty names
        parish_names = {name for name in parish_names if name}
        
        # Convert to ParishRecord objects
        parish_records = []
        for i, parish_name in enumerate(sorted(parish_names), 1):
            canonical_name = self.create_canonical_name(parish_name)
            
            record = ParishRecord(
                id=i,
                parish_name=parish_name,
                canonical_name=canonical_name
            )
            parish_records.append(record)
        
        logger.info(f"Extracted {len(parish_records)} unique parishes")
        return parish_records
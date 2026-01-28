"""Specialized processor for General Bills data format."""

import re
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
from loguru import logger

from ..models import (
    BillOfMortalityRecord,
    ParishRecord,
    SubtotalRecord,
    WeekRecord,
    YearRecord,
)
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
        # Support both space and underscore versions (columns get normalized)
        self.aggregate_patterns = [
            r"christened[_ ]in[_ ]the.*parishes",
            r"buried[_ ]in[_ ]the.*parishes",
            r"plague[_ ]in[_ ]the.*parishes",
            r"parishes[_ ]clear[_ ]of",
            r"parishes[_ ]infected",
        ]

        # Common London parish name patterns for individual parishes
        # Use [_\s]+ to match both underscores (normalized) and spaces (original)
        self.parish_name_patterns = [
            r"^st[_\s]+\w+",  # "St Mary", "St John", "st_mary", "st_john", etc.
            r"^saint[_\s]+\w+",  # "Saint Mary", "saint_mary"
            r"^alhallows?[_\s]+\w+",  # "Alhallows Barking", "alhallows_barking", "Allhallows Great"
            r"^christ[_\s]+church",  # "Christ Church", "christ_church"
            r"^trinity",  # "Trinity Parish", "trinity_parish"
            r"^s[_\s]+\w+",  # "S Sepulchres Parish", "s_sepulchres"
            r"^pesthouse",  # Pesthouses (e.g., "Pesthouse without the walls")
            r"^saviours?",  # Saviour's Southwark
            r"parish$",  # Ends with "Parish" or "parish"
            r"church$",  # Ends with "Church" or "church"
            r"precinct$",  # Ends with "Precinct" or "precinct"
        ]

    def is_general_bill_dataset(self, source_name: str) -> bool:
        """Determine if this dataset contains General Bills."""
        return "general" in source_name.lower()

    def is_aggregate_column(self, column_name: str) -> bool:
        """Check if column is an aggregate (not individual parish)."""
        col_lower = column_name.lower()
        return any(re.search(pattern, col_lower) for pattern in self.aggregate_patterns)

    def is_individual_parish_column(self, column_name: str) -> bool:
        """Check if column represents an individual parish."""
        col_lower = column_name.lower()

        # Skip metadata columns
        if any(
            skip in col_lower
            for skip in ["omeka", "datascribe", "image_", "unique_", "start_", "end_"]
        ):
            return False

        # Skip unnamed columns from dirty data
        if col_lower.startswith("unnamed"):
            return False

        # Skip aggregate columns
        if self.is_aggregate_column(column_name):
            return False

        # Extract base parish name by removing count type suffixes
        # This allows patterns like "parish$" to match "hackney_parish_buried"
        base_name = self._remove_count_suffix(col_lower)

        # Check parish name patterns against the base name
        return any(
            re.search(pattern, base_name) for pattern in self.parish_name_patterns
        )

    def _remove_count_suffix(self, column_name: str) -> str:
        """Remove count type suffix from column name for pattern matching.

        This is a lightweight version used only for pattern detection,
        not for final parish name extraction.
        """
        # Remove common count type suffixes
        name = re.sub(
            r"[_\s-]+(buried|plague|christened|baptized|other)$",
            "",
            column_name,
            flags=re.IGNORECASE,
        )
        return name.strip()

    def extract_parish_name(self, column_name: str) -> str:
        """Extract clean parish name from column name."""
        # Remove count type suffixes if present (sometimes general bills have them)
        # IMPORTANT: Check for hyphen format FIRST before space format
        # because space format will partially match and leave trailing hyphens

        # Handle "Parish - Buried" format (with hyphen separator) - CHECK FIRST
        parish_name = re.sub(
            r"\s*-\s*(buried|plague|christened|baptized|other)$",
            "",
            column_name,
            flags=re.IGNORECASE,
        )
        # Handle "Parish_Buried" format (with underscore)
        parish_name = re.sub(
            r"_(buried|plague|christened|baptized|other)$", "", parish_name
        )
        # Handle "Parish Buried" format (with space only, no hyphen)
        parish_name = re.sub(
            r"\s+(buried|plague|christened|baptized|other)$",
            "",
            parish_name,
            flags=re.IGNORECASE,
        )

        # Convert underscores to spaces and standardize case
        parish_name = parish_name.replace("_", " ")

        # Standardize case: Title case for most words, but preserve 'St' abbreviations
        words = parish_name.split()
        standardized_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower in ["st", "s"]:
                standardized_words.append(word_lower.title())  # 'St', 'S'
            else:
                # Just apply title case - don't try to split words starting with 'st'
                # This avoids incorrectly converting "Stayning" -> "St Ayning"
                # and "Stephen/Steven" -> "St Ephen/St Even"
                standardized_words.append(word.title())

        parish_name = " ".join(standardized_words)

        # Clean up spacing
        parish_name = re.sub(r"\s+", " ", parish_name).strip()

        return parish_name

    def determine_count_type(self, column_name: str) -> str:
        """Determine count type for General Bills columns."""
        col_lower = column_name.lower()

        # Check aggregate columns for explicit types
        if "christened" in col_lower:
            return "christened"
        elif "plague" in col_lower:
            return "plague"
        elif "buried" in col_lower:
            return "buried"
        else:
            # Individual parish columns in General Bills default to burial counts
            return "buried"

    def extract_subtotal_category(self, column_name: str) -> str:
        """
        Extract the subtotal category name from an aggregate column.

        Returns a standardized subtotal category name like:
        - "Within the walls"
        - "Without the walls"
        - "Middlesex and Surrey"
        - "Westminster"
        """
        col_lower = column_name.lower()

        # Check for within walls patterns (handle both space and underscore)
        if "within_the_walls" in col_lower or "within the walls" in col_lower:
            return "Within the walls"
        # Check for without walls patterns
        elif "without_the_walls" in col_lower or "without the walls" in col_lower:
            return "Without the walls"
        # Check for Middlesex and Surrey patterns
        elif "middlesex_and_surrey" in col_lower or "middlesex and surrey" in col_lower:
            return "Middlesex and Surrey"
        # Check for Westminster/City and Liberties patterns
        elif (
            "westminster" in col_lower
            or "city_and_liberties" in col_lower
            or "city and liberties" in col_lower
        ):
            return "Westminster"
        # Check for "parishes clear of" or "parishes infected" patterns
        elif "parishes_clear" in col_lower or "parishes clear" in col_lower:
            return "Parishes clear of plague"
        elif "parishes_infected" in col_lower or "parishes infected" in col_lower:
            return "Parishes infected"

        # Fallback - return cleaned column name
        return column_name.replace("_", " ").title()

    def find_parish_columns(
        self, df: pd.DataFrame, source_name: str
    ) -> Tuple[List[str], List[str]]:
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

        logger.info(
            f"Found {len(individual_columns)} individual parish columns in {source_name}"
        )
        logger.info(
            f"Found {len(aggregate_columns)} aggregate columns in {source_name}"
        )

        return individual_columns, aggregate_columns

    def create_parish_id_mapping(
        self, parish_records: List[ParishRecord]
    ) -> Dict[str, int]:
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

    def find_parish_id(
        self, parish_name: str, parish_mapping: Dict[str, int]
    ) -> Optional[int]:
        """Find parish ID using fuzzy matching."""
        parish_clean = parish_name.lower().strip()

        # Direct match
        if parish_clean in parish_mapping:
            return parish_mapping[parish_clean]

        # Try variations
        variations = [
            parish_clean,
            parish_clean.replace("st ", "saint "),
            parish_clean.replace("saint ", "st "),
            parish_clean.replace(" church", ""),
            parish_clean.replace(" parish", ""),
            # Handle "Alhallows" vs "All Hallows" variations
            parish_clean.replace("alhallows ", "all hallows "),
            parish_clean.replace("all hallows ", "alhallows "),
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
        """Extract year from General Bills row.

        General bills span December to December (e.g., 1694-1695 = Dec 1694 to Dec 1695).
        We attribute them to the end_year since that's when the bill was published.
        """
        # Check end_year first for split-year bills
        for col in ["end_year", "start_year", "year"]:
            if col in row.index and pd.notna(row.get(col)):
                try:
                    return int(row[col])
                except (ValueError, TypeError):
                    continue
        return None

    def find_week_id_for_row(
        self,
        row: pd.Series,
        week_mapping: Dict[str, str],
        new_week_records: List[WeekRecord],
        new_year_records: List[YearRecord],
        seen_years: Set[int],
    ) -> Optional[str]:
        """Find week_id for General Bills row."""
        try:
            year = self.extract_year_from_row(row)
            if not year:
                return None

            # Extract actual end date from row data
            start_day = (
                int(row.get("start_day")) if pd.notna(row.get("start_day")) else None
            )
            start_month = (
                str(row.get("start_month"))
                if pd.notna(row.get("start_month"))
                else None
            )
            end_day = int(row.get("end_day")) if pd.notna(row.get("end_day")) else None
            end_month = (
                str(row.get("end_month")) if pd.notna(row.get("end_month")) else None
            )

            # Handle year-spanning periods
            start_year = (
                int(row.get("start_year", year))
                if pd.notna(row.get("start_year"))
                else year
            )
            end_year = (
                int(row.get("end_year", year))
                if pd.notna(row.get("end_year"))
                else year
            )

            # Use defaults if data is missing
            if not start_day or not start_month:
                start_day = 17
                start_month = "december"
            if not end_day or not end_month:
                end_day = 16
                end_month = "december"

            # Import WeekExtractor to create consistent joinid
            from ..extractors.weeks import WeekExtractor

            extractor = WeekExtractor()
            joinid = extractor.create_joinid(
                start_year, start_month, start_day, end_year, end_month, end_day
            )

            # If joinid exists in mapping, use it; otherwise create new WeekRecord
            if joinid not in week_mapping:
                week_id = extractor.create_week_id(
                    end_year, 90
                )  # General bills use week 90
                year_range = (
                    f"{start_year}-{end_year}"
                    if start_year != end_year
                    else str(end_year)
                )

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
                    unique_identifier=row.get("unique_identifier", ""),
                    week_id=week_id,
                    year_range=year_range,
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
        week_records: List[WeekRecord],
    ) -> Tuple[
        List[BillOfMortalityRecord],
        List[WeekRecord],
        List[YearRecord],
        List[SubtotalRecord],
    ]:
        """Process a General Bills DataFrame into BillOfMortalityRecord and SubtotalRecord objects."""

        parish_mapping = self.create_parish_id_mapping(parish_records)
        week_mapping = self.create_week_id_mapping(week_records)
        new_week_records = []
        new_year_records = []
        seen_years = set()

        # Find parish columns - separate individual from aggregate
        individual_columns, aggregate_columns = self.find_parish_columns(
            df, source_name
        )

        if not individual_columns and not aggregate_columns:
            logger.warning(
                f"No parish columns found in General Bills dataset: {source_name}"
            )
            return [], [], [], []

        # Create parish×count_type combinations for individual parish columns only
        parish_count_combinations = []
        for col in individual_columns:
            parish_name = self.extract_parish_name(col)
            parish_id = self.find_parish_id(parish_name, parish_mapping)
            count_type = self.determine_count_type(col)

            if parish_id:
                parish_count_combinations.append((parish_id, count_type, col))
            else:
                logger.warning(
                    f"Could not find parish ID for '{parish_name}' from column '{col}'"
                )

        # Create subtotal combinations for aggregate columns
        subtotal_combinations = []
        for col in aggregate_columns:
            subtotal_category = self.extract_subtotal_category(col)
            count_type = self.determine_count_type(col)
            subtotal_combinations.append((subtotal_category, count_type, col))

        logger.info(
            f"Found {len(parish_count_combinations)} parish×count_type combinations"
        )
        logger.info(
            f"Found {len(subtotal_combinations)} subtotal×count_type combinations"
        )

        records = []
        subtotal_records = []

        # Process each row
        for idx, row in df.iterrows():
            try:
                year = self.extract_year_from_row(row)
                if not year:
                    continue

                week_id = self.find_week_id_for_row(
                    row, week_mapping, new_week_records, new_year_records, seen_years
                )
                unique_identifier = row.get("unique_identifier", "")
                bill_type = "general"  # Always general for this processor

                # Create records for individual parish columns
                for parish_id, count_type, col in parish_count_combinations:
                    count_value = row[col]

                    # Handle missing/empty counts
                    if pd.isna(count_value) or count_value == "":
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
                        unique_identifier=unique_identifier,
                    )

                    records.append(record)

                # Create subtotal records for aggregate columns
                for subtotal_category, count_type, col in subtotal_combinations:
                    count_value = row[col]

                    # Handle missing/empty counts
                    if pd.isna(count_value) or count_value == "":
                        count = 0
                        is_missing = True
                    else:
                        try:
                            count = int(count_value)
                            is_missing = False
                        except (ValueError, TypeError):
                            count = 0
                            is_missing = True

                    # Create subtotal record
                    subtotal_record = SubtotalRecord(
                        subtotal_category=subtotal_category,
                        count_type=count_type,
                        count=count,
                        year=year,
                        joinid=week_id,
                        bill_type=bill_type,
                        missing=is_missing,
                        illegible=False,
                        source=source_name,
                        unique_identifier=unique_identifier,
                    )

                    subtotal_records.append(subtotal_record)

            except Exception as e:
                logger.warning(f"Failed to process row {idx} in {source_name}: {e}")
                continue

        # Deduplicate bill records
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
            logger.info(
                f"Deduplicated {len(records) - len(deduplicated)} duplicate bill records"
            )

        # Deduplicate subtotal records
        subtotal_seen_keys = {}
        for subtotal_rec in subtotal_records:
            key = (
                subtotal_rec.subtotal_category,
                subtotal_rec.count_type,
                subtotal_rec.year,
                subtotal_rec.joinid,
            )
            if key not in subtotal_seen_keys:
                subtotal_seen_keys[key] = subtotal_rec
            else:
                # Keep record with higher count
                existing = subtotal_seen_keys[key]
                if (subtotal_rec.count or 0) > (existing.count or 0):
                    subtotal_seen_keys[key] = subtotal_rec

        deduplicated_subtotals = list(subtotal_seen_keys.values())

        if len(subtotal_records) != len(deduplicated_subtotals):
            logger.info(
                f"Deduplicated {len(subtotal_records) - len(deduplicated_subtotals)} duplicate subtotal records"
            )

        logger.info(
            f"Generated {len(deduplicated)} General Bills records from {source_name}"
        )
        logger.info(
            f"Generated {len(deduplicated_subtotals)} General Bills subtotal records from {source_name}"
        )
        logger.info(
            f"Created {len(new_week_records)} new week records for General Bills"
        )
        logger.info(
            f"Created {len(new_year_records)} new year records for General Bills"
        )
        return deduplicated, new_week_records, new_year_records, deduplicated_subtotals

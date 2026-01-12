"""Bills processor for converting parish data to BillOfMortalityRecord objects."""

import re
from typing import Dict, List, Optional, Tuple

import pandas as pd
from loguru import logger

from ..models import (
    BillOfMortalityRecord,
    CausesOfDeathRecord,
    ParishRecord,
    SubtotalRecord,
    WeekRecord,
    YearRecord,
)
from ..utils.validation import SchemaValidator
from .general_bills import GeneralBillsProcessor


class BillsProcessor:
    """Processes parish datasets into individual BillOfMortalityRecord objects."""

    def __init__(
        self,
        dictionary_path: Optional[str] = None,
        edited_causes_path: Optional[str] = None,
    ):
        self.validator = SchemaValidator()

        # Initialize specialized General Bills processor
        self.general_bills_processor = GeneralBillsProcessor()

        # Count type patterns to identify what type of data each column represents
        self.count_type_patterns = {
            "buried": r"_buried$|buried_|^buried",
            "plague": r"_plague$|plague_|^plague",
            "christened": r"_christened$|christened_|^christened|_baptized$|baptized_|^baptized",
            "other": r"_other$|other_|^other",
        }

        # Load dictionary for cause definitions
        self.cause_definitions = self._load_dictionary(dictionary_path)

        # Load edited causes controlled vocabulary
        self.edited_causes_lookup = self._load_edited_causes(edited_causes_path)

    def _load_dictionary(
        self, dictionary_path: Optional[str]
    ) -> Dict[str, Dict[str, str]]:
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
            logger.info(
                f"Loaded {len(dict_df)} cause definitions from {dictionary_path}"
            )

            # Create mapping from cause name (normalized) to definition info
            definitions = {}
            for _, row in dict_df.iterrows():
                cause = str(row.get("Cause", "")).lower().strip()
                if cause:
                    definitions[cause] = {
                        "definition": str(row.get("Definition", "")),
                        "source": str(row.get("Source", "")),
                        "notes": str(row.get("Notes", "")),
                    }

            return definitions
        except Exception as e:
            logger.error(f"Failed to load dictionary from {dictionary_path}: {e}")
            return {}

    def _load_edited_causes(
        self, edited_causes_path: Optional[str]
    ) -> Dict[Tuple[int, str], str]:
        """Load edited causes controlled vocabulary from CSV file.

        Returns:
            Dictionary mapping (year, normalized_original_cause) -> edited_cause
        """
        if not edited_causes_path:
            logger.info(
                "No edited causes path provided, controlled vocabulary will be empty"
            )
            return {}

        try:
            import os

            if not os.path.exists(edited_causes_path):
                logger.warning(f"Edited causes file not found at {edited_causes_path}")
                return {}

            edited_df = pd.read_csv(edited_causes_path)
            logger.info(
                f"Loaded {len(edited_df)} edited causes mappings from {edited_causes_path}"
            )

            # Create mapping from (year, normalized original cause) to edited cause
            lookup = {}
            for _, row in edited_df.iterrows():
                try:
                    year = int(row.get("Year", 0))
                    original_cause = str(row.get("original_cause", "")).lower().strip()
                    edited_cause = str(row.get("edited_cause", "")).strip()

                    if year and original_cause and edited_cause:
                        lookup[(year, original_cause)] = edited_cause
                except (ValueError, TypeError):
                    continue

            logger.info(f"Created lookup with {len(lookup)} cause mappings")
            return lookup
        except Exception as e:
            logger.error(f"Failed to load edited causes from {edited_causes_path}: {e}")
            return {}

    def _lookup_edited_cause(self, death: str, year: Optional[int]) -> Optional[str]:
        """Look up the edited cause for a given death cause and year.

        Args:
            death: The original cause of death (from data)
            year: The year of the record

        Returns:
            The edited cause if found, None otherwise
        """
        if not year or not self.edited_causes_lookup:
            return None

        # Normalize the death cause for lookup (lowercase and strip)
        normalized_death = death.lower().strip()

        # Try direct lookup
        key = (year, normalized_death)
        if key in self.edited_causes_lookup:
            return self.edited_causes_lookup[key]

        return None

    def _normalize_cause_name(self, cause_name: str) -> str:
        """Normalize cause name for dictionary lookup."""
        # Convert to lowercase, replace underscores with spaces, strip whitespace
        normalized = cause_name.lower().replace("_", " ").strip()

        # Handle common variations
        replacements = {
            "flox and small pox": "smallpox",
            "st anthony s fire": "st. anthony's fire",
            "kings evil": "king's evil",
            "griping in the guts": "griping in the guts",
            "rising of the lights": "rising of the lights",
            "running of the reins": "running of the reins",
            "stopping of the stomach": "stopping of the stomach",
            "falling sickness": "falling sickness",
            "noli me tangere": "noli me tangere",
            "scald head": "scald head",
            "spotted fever": "spotted fever",
            "still born": "stillborn",
            "swine pox": "swine-pox",
        }

        for old, new in replacements.items():
            if old in normalized:
                normalized = normalized.replace(old, new)
                break

        return normalized

    def is_subtotal_column(self, column_name: str) -> bool:
        """
        Identify if a column represents a subtotal rather than individual parish data.

        Subtotals are identified by specific phrases:
        - "within the walls"
        - "without the walls"
        - "Middlesex and Surrey"
        - "Westminster" with "Parishes and Liberties"

        But exclude individual Westminster parish columns like "Westminster - Buried"
        and pesthouses which are individual parishes, not subtotals.
        """
        col_lower = column_name.lower()

        # Debug logging to see what columns we're evaluating
        # logger.debug(f"Checking column for subtotal: '{column_name}' -> '{col_lower}'")

        # FIRST: Exclude pesthouses - they are individual parishes, not subtotals
        # Even if they contain subtotal patterns like "pesthouse without the walls"
        if "pesthouse" in col_lower:
            return False

        # Check for subtotal patterns (be more flexible with the patterns)
        subtotal_patterns = [
            "within_the_walls",  # "buried_in_the_97_parishes_within_the_walls"
            "within the walls",  # "buried in the 97 parishes within the walls"
            "without_the_walls",  # "buried_in_the_parishes_without_the_walls"
            "without the walls",  # "buried in the parishes without the walls"
            "middlesex_and_surrey",  # "buried_in_the_out_parishes_in_middlesex_and_surrey"
            "middlesex and surrey",  # "buried in the out-Parishes in Middlesex and Surrey"
        ]

        # Check basic subtotal patterns
        for pattern in subtotal_patterns:
            if pattern in col_lower:
                return True

        # Special handling for Westminster subtotals vs individual Westminster parishes
        if "westminster" in col_lower:
            # It's a subtotal if it mentions "parishes and liberties"
            if (
                "parishes_and_liberties" in col_lower
                or "parishes and liberties" in col_lower
            ):
                return True
            # It's NOT a subtotal if it follows individual parish pattern like "Westminster - Buried" or "Westminster - Plague"
            elif " - " in column_name or (
                "_buried" in col_lower and "parishes" not in col_lower
            ):
                return False

        return False

    def extract_subtotal_category(self, column_name: str) -> str:
        """
        Extract the subtotal category name from a subtotal column.

        Returns a standardized subtotal category name like:
        - "Within the walls"
        - "Without the walls"
        - "Middlesex and Surrey"
        - "Westminster"
        """
        col_lower = column_name.lower()

        # Check for within walls patterns
        if "within_the_walls" in col_lower or "within the walls" in col_lower:
            return "Within the walls"
        # Check for without walls patterns
        elif "without_the_walls" in col_lower or "without the walls" in col_lower:
            return "Without the walls"
        # Check for Middlesex and Surrey patterns
        elif "middlesex_and_surrey" in col_lower or "middlesex and surrey" in col_lower:
            return "Middlesex and Surrey"
        # Check for Westminster patterns
        elif "westminster" in col_lower and (
            "parishes_and_liberties" in col_lower
            or "parishes and liberties" in col_lower
        ):
            return "Westminster"

        # Fallback - return the original column name if pattern not recognized
        return column_name

    def identify_count_type(
        self, column_name: str, is_general_bill: bool = False
    ) -> str:
        """Identify the count type from column name."""
        col_lower = column_name.lower()

        # For general bills, check aggregate columns first
        if is_general_bill:
            if "christened in" in col_lower:
                return "christened"
            elif "plague in" in col_lower:
                return "plague"
            elif "buried in" in col_lower:
                return "buried"
            else:
                # Default: individual parish columns in general bills are burial counts
                return "buried"

        # Original logic for weekly bills
        for count_type, pattern in self.count_type_patterns.items():
            if re.search(pattern, col_lower):
                return count_type

        # Default fallback - if column contains numbers, assume it's buried
        return "buried"

    def extract_parish_name_from_column(
        self, column_name: str, is_general_bill: bool = False
    ) -> str:
        """Extract parish name from column name by removing count type suffixes."""
        # Remove count type suffixes
        parish_name = re.sub(
            r"_(buried|plague|christened|baptized|other)$", "", column_name
        )
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
            elif word_lower.startswith("st"):
                # Handle cases like 'stbotolphs' -> 'St Botolphs'
                if len(word) > 2 and word[2:].isalpha():
                    standardized_words.append("St " + word[2:].title())
                else:
                    standardized_words.append(word.title())
            else:
                standardized_words.append(word.title())

        parish_name = " ".join(standardized_words)

        # Clean up spacing
        parish_name = re.sub(r"\s+", " ", parish_name).strip()

        return parish_name

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

    def process_parish_dataframes(
        self,
        dataframes: List[tuple[pd.DataFrame, str]],
        parish_records: List[ParishRecord],
        week_records: List[WeekRecord],
    ) -> Tuple[
        List[BillOfMortalityRecord],
        List[CausesOfDeathRecord],
        List[WeekRecord],
        List[YearRecord],
        List[SubtotalRecord],
    ]:
        """
        Process DataFrames into BillOfMortalityRecord, CausesOfDeathRecord, and SubtotalRecord objects.
        Handles both parish data and causes data with different processing logic.

        Args:
            dataframes: List of (DataFrame, source_name) tuples
            parish_records: List of ParishRecord objects for ID mapping
            week_records: List of WeekRecord objects for week_id mapping

        Returns:
            Tuple of (BillOfMortalityRecord list, CausesOfDeathRecord list, WeekRecord list, YearRecord list, SubtotalRecord list)
        """
        parish_mapping = self.create_parish_id_mapping(parish_records)
        week_mapping = self.create_week_id_mapping(week_records)

        bill_records = []
        cause_records = []
        subtotal_records = []
        all_new_week_records = []
        all_new_year_records = []

        for df, source_name in dataframes:
            logger.info(f"Processing bills from {source_name}")

            # Determine if this is parish data or causes data
            is_causes_data = "causes" in source_name.lower()

            if is_causes_data:
                # Process causes data
                records = self._process_causes_dataframe(df, source_name, week_mapping)
                cause_records.extend(records)
                logger.info(
                    f"Generated {len(records)} cause records from {source_name}"
                )
            else:
                # Check if this is a General Bills dataset
                if self.general_bills_processor.is_general_bill_dataset(source_name):
                    # Use specialized General Bills processor
                    (
                        records,
                        new_week_records,
                        new_year_records,
                        general_subtotals,
                    ) = self.general_bills_processor.process_general_bills_dataframe(
                        df, source_name, parish_records, week_records
                    )
                    bill_records.extend(records)
                    all_new_week_records.extend(new_week_records)
                    all_new_year_records.extend(new_year_records)
                    subtotal_records.extend(general_subtotals)
                    logger.info(
                        f"Generated {len(records)} General Bills records from {source_name}"
                    )
                    logger.info(
                        f"Generated {len(general_subtotals)} General Bills subtotal records from {source_name}"
                    )
                    logger.info(
                        f"Created {len(new_week_records)} new week records from {source_name}"
                    )
                    logger.info(
                        f"Created {len(new_year_records)} new year records from {source_name}"
                    )
                else:
                    # Process as Weekly Bills data
                    records, subtotal_recs = self._process_parish_dataframe(
                        df, source_name, parish_mapping, week_mapping
                    )
                    bill_records.extend(records)
                    subtotal_records.extend(subtotal_recs)
                    logger.info(
                        f"Generated {len(records)} Weekly Bills records from {source_name}"
                    )
                    logger.info(
                        f"Generated {len(subtotal_recs)} subtotal records from {source_name}"
                    )

        logger.info(f"Total bill of mortality records: {len(bill_records)}")
        logger.info(f"Total causes of death records: {len(cause_records)}")
        logger.info(f"Total subtotal records: {len(subtotal_records)}")
        logger.info(f"Total new week records: {len(all_new_week_records)}")
        logger.info(f"Total new year records: {len(all_new_year_records)}")
        return (
            bill_records,
            cause_records,
            all_new_week_records,
            all_new_year_records,
            subtotal_records,
        )

    def _process_parish_dataframe(
        self,
        df: pd.DataFrame,
        source_name: str,
        parish_mapping: Dict[str, int],
        week_mapping: Dict[str, str],
    ) -> Tuple[List[BillOfMortalityRecord], List[SubtotalRecord]]:
        """Process parish data structure."""
        # Detect if this is a general bill dataset
        is_general_bill = "general" in source_name.lower()

        # Find parish columns and subtotal columns (exclude total columns, metadata, and aggregate christening columns)
        parish_columns = []
        subtotal_columns = []
        for col in df.columns:
            col_lower = col.lower()
            # Skip metadata columns
            if col_lower.startswith(
                ("total", "year", "week", "start_", "end_", "unique_")
            ):
                continue
            # Skip explicit metadata fields
            if col_lower.startswith(
                ("omeka", "datascribe", "image_", "is_missing", "is_illegible")
            ):
                continue

            # Check if this is a subtotal column first
            if self.is_subtotal_column(col):
                subtotal_columns.append(col)
                continue

            if is_general_bill:
                # For general bills, include aggregate columns and individual parish columns
                if any(
                    phrase in col_lower
                    for phrase in [
                        "christened_in_the",
                        "buried_in_the",
                        "plague_in_the",
                        "christened in the",
                        "buried in the",
                        "plague in the",  # Handle spaces too
                    ]
                ):
                    parish_columns.append(
                        col
                    )  # Include aggregate columns for general bills
                elif (
                    col_lower.startswith(("st ", "st_", "saint ", "saint_"))
                    or col.startswith(("St ", "St_", "Saint ", "Saint_"))
                    or col_lower.startswith(("christ ", "christ_"))
                    or col.startswith(("Christ ", "Christ_"))
                    or col_lower.startswith(("trinity", "alhal", "alhallows"))
                    or col.startswith(("Trinity", "Alhal", "Alhallows"))
                    or col_lower.startswith("s ")
                    or col.startswith("S ")
                    or any(  # "S Sepulchres Parish"
                        word in col_lower for word in ["parish", "church", "precinct"]
                    )
                    or any(word in col for word in ["Parish", "Church", "Precinct"])
                    or col_lower.endswith("_parish")
                    or col.endswith(" Parish")
                ):
                    # Additional checks for individual parish names in general bills
                    if not any(
                        skip in col_lower
                        for skip in [
                            "omeka",
                            "datascribe",
                            "image_",
                            "unique_",
                            "start_",
                            "end_",
                        ]
                    ):
                        parish_columns.append(col)  # Include individual parish columns
            else:
                # Original logic for weekly bills - exclude aggregate columns
                if any(
                    phrase in col_lower
                    for phrase in [
                        "christened in the",
                        "buried in the",
                        "plague in the",
                        "christened in all",
                        "buried in all",
                        "plague in all",
                    ]
                ):
                    continue
                # Include individual parish columns with suffixes
                if any(
                    pattern in col_lower
                    for pattern in ["buried", "plague", "christened", "baptized"]
                ):
                    parish_columns.append(col)

        logger.info(f"Found {len(parish_columns)} parish columns in {source_name}")
        logger.info(f"Found {len(subtotal_columns)} subtotal columns in {source_name}")

        if not parish_columns and not subtotal_columns:
            logger.warning(f"No parish or subtotal columns found in {source_name}")
            return [], []

        # Extract unique parishes and count types from columns
        parish_count_combinations = []
        for col in parish_columns:
            parish_name = self.extract_parish_name_from_column(col, is_general_bill)
            parish_id = self._find_parish_id(parish_name, parish_mapping)
            count_type = self.identify_count_type(col, is_general_bill)

            if parish_id:
                parish_count_combinations.append((parish_id, count_type, col))
            else:
                logger.warning(
                    f"Could not find parish ID for '{parish_name}' from column '{col}'"
                )

        # Extract subtotal categories and count types from subtotal columns
        subtotal_combinations = []
        for col in subtotal_columns:
            subtotal_category = self.extract_subtotal_category(col)
            count_type = self.identify_count_type(col, is_general_bill)
            subtotal_combinations.append((subtotal_category, count_type, col))

        logger.info(
            f"Found {len(parish_count_combinations)} parish×count_type combinations"
        )
        logger.info(
            f"Found {len(subtotal_combinations)} subtotal×count_type combinations"
        )

        records = []
        subtotal_records = []
        # Process each row in the dataframe
        for idx, row in df.iterrows():
            try:
                year = self._extract_year_from_row(row)
                if not year:
                    continue

                # Create joinid for this row to find week_id
                week_id = self._find_week_id_for_row(row, week_mapping)

                # Determine bill type based on unique identifier and week data
                unique_identifier = row.get("unique_identifier", "")
                bill_type = self._determine_bill_type(
                    unique_identifier, week_id, source_name
                )

                # Create a record for EVERY parish×count_type combination for this bill
                # This matches R's approach of creating comprehensive records
                for parish_id, count_type, col in parish_count_combinations:
                    count_value = row[col]

                    # Look for corresponding is_missing and is_illegible flag columns
                    is_missing_col = self._find_flag_column(
                        col, df.columns, "is_missing"
                    )
                    is_illegible_col = self._find_flag_column(
                        col, df.columns, "is_illegible"
                    )

                    # Get flag values from the flag columns if they exist
                    explicit_missing = False
                    explicit_illegible = False

                    if is_missing_col and is_missing_col in row.index:
                        missing_val = row[is_missing_col]
                        explicit_missing = self._is_flag_true(missing_val)

                    if is_illegible_col and is_illegible_col in row.index:
                        illegible_val = row[is_illegible_col]
                        explicit_illegible = self._is_flag_true(illegible_val)

                    # Handle missing/empty counts (preserve them as 0 with flags)
                    if pd.isna(count_value) or count_value == "" or count_value == 0:
                        count = 0
                        # Use explicit missing flag if available, otherwise infer from empty value
                        is_missing = explicit_missing or (
                            pd.isna(count_value) or count_value == ""
                        )
                    else:
                        try:
                            count = int(count_value)
                            is_missing = explicit_missing  # Use explicit flag
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
                        illegible=explicit_illegible,  # Use explicit illegible flag
                        source=source_name,
                        unique_identifier=unique_identifier,
                    )

                    # Always add the record (don't validate out empty records)
                    records.append(record)

                # Process subtotal records for this row
                for subtotal_category, count_type, col in subtotal_combinations:
                    count_value = row[col]

                    # Look for corresponding is_missing and is_illegible flag columns
                    is_missing_col = self._find_flag_column(
                        col, df.columns, "is_missing"
                    )
                    is_illegible_col = self._find_flag_column(
                        col, df.columns, "is_illegible"
                    )

                    # Get flag values from the flag columns if they exist
                    explicit_missing = False
                    explicit_illegible = False

                    if is_missing_col and is_missing_col in row.index:
                        missing_val = row[is_missing_col]
                        explicit_missing = self._is_flag_true(missing_val)

                    if is_illegible_col and is_illegible_col in row.index:
                        illegible_val = row[is_illegible_col]
                        explicit_illegible = self._is_flag_true(illegible_val)

                    # Handle missing/empty counts (preserve them as 0 with flags)
                    if pd.isna(count_value) or count_value == "" or count_value == 0:
                        count = 0
                        # Use explicit missing flag if available, otherwise infer from empty value
                        is_missing = explicit_missing or (
                            pd.isna(count_value) or count_value == ""
                        )
                    else:
                        try:
                            count = int(count_value)
                            is_missing = explicit_missing  # Use explicit flag
                        except (ValueError, TypeError):
                            # Invalid count - preserve as 0 with missing flag
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
                        illegible=explicit_illegible,
                        source=source_name,
                        unique_identifier=unique_identifier,
                    )

                    # Always add the subtotal record
                    subtotal_records.append(subtotal_record)

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
            logger.info(
                f"Deduplicated {len(records) - len(deduplicated)} duplicate bill records"
            )

        # Deduplicate subtotal records based on unique key (subtotal_category, count_type, year, joinid)
        subtotal_seen_keys = {}

        for record in subtotal_records:
            key = (
                record.subtotal_category,
                record.count_type,
                record.year,
                record.joinid,
            )
            if key not in subtotal_seen_keys:
                subtotal_seen_keys[key] = record
            else:
                # Keep the record with higher count, or the newer one if counts are equal
                existing = subtotal_seen_keys[key]
                if (record.count or 0) > (existing.count or 0):
                    subtotal_seen_keys[key] = record

        deduplicated_subtotals = list(subtotal_seen_keys.values())

        if len(subtotal_records) != len(deduplicated_subtotals):
            logger.info(
                f"Deduplicated {len(subtotal_records) - len(deduplicated_subtotals)} duplicate subtotal records"
            )

        return deduplicated, deduplicated_subtotals

    def _is_general_bills_causes_format(self, df: pd.DataFrame) -> bool:
        """
        Detect if this DataFrame uses the general bills causes format.

        General bills causes have repeating Cause/Number column headers,
        with actual cause names in data cells rather than column headers.
        """
        # Look for the telltale sign: multiple columns named 'Cause' and 'Number'
        # After column normalization, these become 'cause', 'cause_1', 'cause_2', etc.
        # (pandas auto-renames duplicates to 'cause.1', then normalization converts dots to underscores)
        columns_lower = [col.lower() for col in df.columns]

        # Check for 'number' with numeric suffixes (dots or underscores) indicating pandas renaming + normalization
        import re

        number_pattern_count = sum(
            1
            for col in columns_lower
            if col == "number"
            or re.match(r"number[._]\d+", col)
            or col.startswith("number_")
        )

        cause_pattern_count = sum(
            1
            for col in columns_lower
            if col == "cause"
            or re.match(r"cause[._]\d+", col)
            or col.startswith("cause_")
        )

        # If we have multiple 'Cause' and 'Number' columns, it's general bills causes format
        return number_pattern_count >= 2 and cause_pattern_count >= 2

    def _transform_general_bills_causes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform general bills causes from long format to wide format.

        Input format (repeating columns):
            Year | Cause | is_missing | is_illegible | Number | is_missing | is_illegible | Cause | ...
            1657 | Aged  |            |              | 869    |            |              | Fever | ...

        Output format (causes as columns):
            Year | Aged | Fever | Consumption | ...
            1657 | 869  | 44    | 57          | ...
        """
        logger.info("Transforming general bills causes from long to wide format")

        # Find metadata columns to preserve
        metadata_cols = []
        for col in df.columns:
            col_lower = col.lower()
            if any(
                meta in col_lower
                for meta in [
                    "omeka",
                    "datascribe",
                    "year",
                    "unique_identifier",
                    "start_day",
                    "start_month",
                    "end_day",
                    "end_month",
                    "start_year",
                    "end_year",
                    "image_filename",
                ]
            ):
                metadata_cols.append(col)

        # Process each row to extract cause/number pairs
        transformed_rows = []

        for idx, row in df.iterrows():
            # Start with metadata
            new_row = {col: row[col] for col in metadata_cols}

            # Extract cause/number pairs from the repeating pattern
            # Columns alternate: Cause, is_missing, is_illegible, Number, is_missing, is_illegible, ...
            col_list = list(df.columns)
            i = 0

            while i < len(col_list):
                col_name = col_list[i]
                col_lower = col_name.lower()

                # Look for a 'Cause' column (handles 'cause', 'cause_1', 'cause.1', etc.)
                import re

                is_cause_col = (
                    col_lower == "cause"
                    or re.match(r"cause[._]\d+", col_lower)
                    or col_lower.startswith("cause_")
                )

                if is_cause_col:
                    cause_value = row[col_name]

                    # Skip if cause is empty/null
                    if pd.isna(cause_value) or str(cause_value).strip() == "":
                        # Skip ahead to find next Cause column
                        i += 1
                        continue

                    # Find the corresponding Number column (should be ~3 columns ahead)
                    # Pattern: Cause, is_missing, is_illegible, Number
                    number_value = None
                    for offset in range(1, 6):  # Look ahead up to 5 columns
                        if i + offset < len(col_list):
                            next_col = col_list[i + offset]
                            next_col_lower = next_col.lower()
                            is_number_col = (
                                next_col_lower == "number"
                                or re.match(r"number[._]\d+", next_col_lower)
                                or next_col_lower.startswith("number_")
                            )
                            if is_number_col:
                                number_value = row[next_col]
                                break

                    # Add this cause/number pair to the row
                    cause_name = str(cause_value).strip()
                    if cause_name and cause_name.lower() not in ["nan", "none"]:
                        # Convert number to int if possible, otherwise None
                        count = None
                        if pd.notna(number_value) and str(number_value).strip() != "":
                            try:
                                count = int(float(number_value))
                            except (ValueError, TypeError):
                                count = None

                        new_row[cause_name] = count

                i += 1

            transformed_rows.append(new_row)

        # Create new DataFrame
        transformed_df = pd.DataFrame(transformed_rows)

        logger.info(f"Transformed {len(df)} rows with repeating Cause/Number columns")
        logger.info(
            f"Extracted {len(transformed_df.columns) - len(metadata_cols)} unique causes"
        )

        return transformed_df

    def _process_causes_dataframe(
        self, df: pd.DataFrame, source_name: str, week_mapping: Dict[str, str]
    ) -> List[CausesOfDeathRecord]:
        """
        Process causes data structure.
        Creates CausesOfDeathRecord objects for each cause.

        Handles two formats:
        1. Weekly bills: causes as column headers
        2. General bills: repeating Cause/Number columns with cause names in data cells
        """
        # Check if this is general bills causes format and transform if needed
        if self._is_general_bills_causes_format(df):
            logger.info(f"Detected general bills causes format in {source_name}")
            df = self._transform_general_bills_causes(df)

        # Now proceed with standard causes processing
        # Find cause columns (exclude metadata columns and descriptive text)
        exclude_cols = {
            "omeka_item",
            "datascribe_item",
            "datascribe_record",
            "datascribe_record_position",
            "image_filename_s",
            "year",
            "week_number",
            "unique_identifier",
            "start_day",
            "start_month",
            "end_day",
            "end_month",
            "start_year",
            "end_year",
            "joinid",
            "week_id",
            "year_range",
            "split_year",
            "christened_male",
            "christened_female",
            "christened_in_all",
            "christened (male)",  # General bills format
            "christened (female)",  # General bills format
            "christened (in all)",  # General bills format
            "buried_male",
            "buried_female",
            "buried_all",
            "buried (male)",  # General bills format
            "buried (female)",  # General bills format
            "buried (all)",  # General bills format
            "plague_deaths",
            "increase_decrease_in_burials",
            "increase_decrease_in_plague_deaths",
            "increase/decrease in burials",  # General bills format
            "increase/decrease in plague",  # General bills format
            "parishes_clear_of_the_plague",
            "parishes_infected_with_plague",
            "parishes clear of the plague",  # General bills format
            "parishes infected",  # General bills format
            "ounces_in_penny_wheaten_loaf",
            "ounces_in_three_half_penny_white_loaf",
        }

        # Filter out metadata and descriptive text columns
        cause_columns = []
        for col in df.columns:
            col_lower = col.lower()
            # Skip if it's in exclude list
            if col_lower in exclude_cols:
                continue
            # Skip metadata fields like "is_illegible_134", "is_missing_xyz"
            if col_lower.startswith(("is_illegible", "is_missing")):
                continue
            # Skip descriptive text fields like "drowned_descriptive_text"
            if col_lower.endswith("_descriptive_text"):
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
                year = self._extract_year_from_row(row)
                if not year:
                    continue

                # Create joinid for this row to find week_id
                week_id = self._find_week_id_for_row(row, week_mapping)

                # Determine bill type based on unique identifier and week data
                unique_identifier = row.get("unique_identifier", "")
                bill_type = self._determine_bill_type(
                    unique_identifier, week_id, source_name
                )

                # Create a record for EVERY cause for this bill
                for cause_col in cause_columns:
                    count_value = row[cause_col]

                    # Handle missing/empty counts
                    count = None
                    if pd.isna(count_value) or count_value == "":
                        count = None
                    elif count_value == 0:
                        count = 0
                    else:
                        try:
                            # Convert decimal values to integers (e.g., 1.0 -> 1)
                            count = int(float(count_value))
                        except (ValueError, TypeError):
                            # For causes, text values might be descriptive
                            count = None

                    # Look up definition for this cause
                    normalized_cause = self._normalize_cause_name(cause_col)
                    definition_info = self.cause_definitions.get(normalized_cause, {})

                    # Convert cause name from column format to readable text
                    # Replace underscores with spaces and keep original capitalization
                    readable_cause_name = cause_col.replace("_", " ")

                    # Look up edited cause from controlled vocabulary
                    edited_cause = self._lookup_edited_cause(readable_cause_name, year)

                    # Create causes of death record
                    record = CausesOfDeathRecord(
                        death=readable_cause_name,
                        count=count,
                        year=year,
                        joinid=week_id,
                        descriptive_text=None,
                        source_name=source_name,
                        definition=definition_info.get("definition"),
                        definition_source=definition_info.get("source"),
                        bill_type=bill_type,
                        edited_cause=edited_cause,
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
            logger.info(
                f"Deduplicated {len(records) - len(deduplicated)} duplicate cause records"
            )

        return deduplicated

    def _find_week_id_for_row(
        self, row: pd.Series, week_mapping: Dict[str, str]
    ) -> Optional[str]:
        """Find joinid for a row by creating it from row data."""
        try:
            # Extract year using the same logic as the main processing
            year = self._extract_year_from_row(row)
            if not year:
                return None

            # Check if this is a general bill (has start_year/end_year but no week data)
            is_general_bill = (
                "start_year" in row.index or "end_year" in row.index
            ) and "week" not in row.index

            if is_general_bill:
                # For general bills, use the start date from the row
                # General bills span a full year but we need to match existing week records
                start_day = (
                    int(row.get("start_day", 17))
                    if pd.notna(row.get("start_day"))
                    else 17
                )
                start_month = (
                    str(row.get("start_month", "december"))
                    if pd.notna(row.get("start_month"))
                    else "december"
                )

                # For general bills, try to find an existing week record that starts with the same date
                # Use the start date for both start and end to match existing weekly records
                from ..extractors.weeks import WeekExtractor

                extractor = WeekExtractor()
                joinid = extractor.create_joinid(
                    year, start_month, start_day, year, start_month, start_day + 7
                )

                # If that doesn't work, try to find any existing week record for this year/month
                if joinid not in week_mapping:
                    # Try common general bill week patterns that might exist
                    potential_joinids = [
                        extractor.create_joinid(
                            year,
                            start_month,
                            start_day,
                            year,
                            start_month,
                            min(start_day + 7, 31),
                        ),
                        extractor.create_joinid(
                            year, start_month, start_day, year, start_month, 24
                        )
                        if start_day == 17
                        else None,
                        extractor.create_joinid(
                            year, start_month, 17, year, start_month, 24
                        ),  # Common Dec 17-24 pattern
                    ]

                    for potential_id in potential_joinids:
                        if potential_id and potential_id in week_mapping:
                            return potential_id

                    # If still no match, add it to the mapping for consistency
                    week_mapping[joinid] = joinid

                return joinid

            # For weekly bills, try to create joinid from date data
            start_day = (
                int(row.get("start_day", 1)) if pd.notna(row.get("start_day")) else 1
            )
            end_day = int(row.get("end_day", 7)) if pd.notna(row.get("end_day")) else 7
            start_month = (
                str(row.get("start_month", "january"))
                if pd.notna(row.get("start_month"))
                else "january"
            )
            end_month = (
                str(row.get("end_month", "january"))
                if pd.notna(row.get("end_month"))
                else "january"
            )

            # Import WeekExtractor to use its joinid creation logic
            from ..extractors.weeks import WeekExtractor

            extractor = WeekExtractor()
            joinid = extractor.create_joinid(
                year, start_month, start_day, year, end_month, end_day
            )

            # Return the joinid directly if it exists in the week mapping
            if joinid in week_mapping:
                return joinid

            # If exact match fails, try fuzzy matching with existing week records
            return self._fuzzy_match_week_record(
                year, start_month, start_day, end_month, end_day, week_mapping
            )
        except Exception:
            return None

    def _fuzzy_match_week_record(
        self,
        year: int,
        start_month: str,
        start_day: int,
        end_month: str,
        end_day: int,
        week_mapping: Dict[str, str],
    ) -> Optional[str]:
        """
        Find the best matching week record when exact joinid match fails.

        This handles cases where bill row dates don't exactly match existing week records
        due to slight variations in date parsing or recording.
        """
        from ..extractors.weeks import WeekExtractor

        extractor = WeekExtractor()

        # Get all week records for this year
        year_week_records = []
        for joinid in week_mapping.keys():
            if joinid.startswith(f"{year}-"):
                year_week_records.append(joinid)

        if not year_week_records:
            logger.warning(f"No week records found for year {year}")
            return None

        # Strategy 1: Try variations with different end days (±1, ±2, ±3 days)
        for day_offset in range(-3, 4):
            adjusted_end_day = end_day + day_offset
            if adjusted_end_day > 0:  # Don't go negative
                try:
                    test_joinid = extractor.create_joinid(
                        year, start_month, start_day, year, end_month, adjusted_end_day
                    )
                    if test_joinid in week_mapping:
                        logger.info(
                            f"Found week match with {day_offset} day offset: {test_joinid}"
                        )
                        return test_joinid
                except Exception as e:
                    logger.warning(f"Failed to find week match: {e}")
                    continue

        # Strategy 2: Try variations with different start days (±1, ±2 days)
        for day_offset in range(-2, 3):
            adjusted_start_day = start_day + day_offset
            if adjusted_start_day > 0:
                try:
                    test_joinid = extractor.create_joinid(
                        year, start_month, adjusted_start_day, year, end_month, end_day
                    )
                    if test_joinid in week_mapping:
                        logger.info(
                            f"Found week match with {day_offset} start day offset: {test_joinid}"
                        )
                        return test_joinid
                except Exception as e:
                    logger.warning(f"Failed to find week match: {e}")
                    continue

        # Strategy 3: Match by month and approximate date range
        # Find any week record in the same month with overlapping dates
        start_month_lower = start_month.lower()
        for existing_joinid in year_week_records:
            # Parse existing joinid to extract date info
            if start_month_lower in existing_joinid.lower():
                # If months match, this is likely the right week
                logger.info(f"Found month-based week match: {existing_joinid}")
                return existing_joinid

        # Strategy 4: Use the first week record for this year as last resort
        # This prevents total data loss when date matching fails
        if year_week_records:
            fallback_joinid = sorted(year_week_records)[
                0
            ]  # Use earliest week as fallback
            logger.warning(f"Using fallback week record for {year}: {fallback_joinid}")
            return fallback_joinid

        return None

    def _extract_year_from_row(self, row: pd.Series) -> Optional[int]:
        """Extract year from row data, handling both weekly and general bill formats."""
        # Try weekly bills format first (year column)
        if "year" in row.index and pd.notna(row.get("year")):
            try:
                return int(row["year"])
            except (ValueError, TypeError):
                pass

        # Try general bills format (start_year or end_year columns)
        year_columns = ["start_year", "end_year"]
        for col in year_columns:
            if col in row.index and pd.notna(row.get(col)):
                try:
                    return int(row[col])
                except (ValueError, TypeError):
                    continue

        return None

    def _determine_bill_type(
        self, unique_identifier: str, week_id: Optional[str], source_name: str
    ) -> str:
        """
        Determine if this is a general or weekly bill.

        Args:
            unique_identifier: The unique identifier from the row
            week_id: The computed week_id
            source_name: The name of the source dataset/file

        Returns:
            "general" or "weekly"
        """
        # Check source filename for "general" pattern (highest priority)
        if source_name and "general" in source_name.lower():
            return "general"

        if not unique_identifier:
            return "weekly"  # Default

        # Check identifier patterns
        identifier_lower = unique_identifier.lower()
        if any(
            pattern in identifier_lower
            for pattern in ["generalbill", "general-bill", "general_bill"]
        ):
            return "general"

        # Check if week_id indicates week 90 (general bill week)
        if week_id and "-90" in week_id:
            return "general"

        return "weekly"  # Default for all other cases

    def _find_flag_column(
        self, data_column: str, all_columns, flag_type: str
    ) -> Optional[str]:
        """
        Find the corresponding is_missing or is_illegible flag column for a data column.

        After column normalization, the pattern becomes:
        [Data Column] -> look for nearest is_missing_X or is_illegible_X column

        Args:
            data_column: Name of the data column (normalized)
            all_columns: List of all column names in the DataFrame (normalized)
            flag_type: Either 'is_missing' or 'is_illegible'

        Returns:
            Name of the corresponding flag column, or None if not found
        """
        try:
            columns_list = list(all_columns)
            data_col_index = columns_list.index(data_column)

            # Search forward and backward for the closest flag column
            # DataScribe pattern: data_col, is_missing_X, is_illegible_X
            search_range = min(10, len(columns_list))  # Look within reasonable distance

            # Search forward first (most common case)
            for offset in range(1, search_range):
                if data_col_index + offset < len(columns_list):
                    potential_col = columns_list[data_col_index + offset]
                    # Match exact flag_type or numbered versions (is_illegible_1, is_illegible_2, etc.)
                    if potential_col == flag_type or potential_col.startswith(
                        f"{flag_type}_"
                    ):
                        return potential_col
                    # Stop searching if we hit another data column (parish name)
                    if self._looks_like_data_column(potential_col):
                        break

            # Search backward as backup
            for offset in range(1, min(5, data_col_index + 1)):
                if data_col_index - offset >= 0:
                    potential_col = columns_list[data_col_index - offset]
                    if potential_col == flag_type or potential_col.startswith(
                        f"{flag_type}_"
                    ):
                        return potential_col

            return None
        except (ValueError, IndexError):
            return None

    def _looks_like_data_column(self, column_name: str) -> bool:
        """Check if a column name looks like a data column (not a flag column)."""
        col_lower = column_name.lower()
        return not any(
            flag in col_lower
            for flag in [
                "is_missing",
                "is_illegible",
                "omeka",
                "datascribe",
                "unique_identifier",
                "start_",
                "end_",
                "year",
                "week",
            ]
        )

    def _is_flag_true(self, value) -> bool:
        """Check if a flag value should be considered True."""
        if pd.isna(value):
            return False
        # Handle various representations of True
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value == 1 or value == 1.0
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "y")
        return False

    def _find_parish_id(
        self, parish_name: str, parish_mapping: Dict[str, int]
    ) -> Optional[int]:
        """Find parish ID using fuzzy matching."""
        parish_clean = parish_name.lower().strip()

        # Direct match
        if parish_clean in parish_mapping:
            return parish_mapping[parish_clean]

        # Try without common prefixes/suffixes
        variations = [
            parish_clean,
            parish_clean.replace("st ", "saint "),
            parish_clean.replace("saint ", "st "),
            parish_clean.replace(" church", ""),
            parish_clean.replace(" parish", ""),
        ]

        for variation in variations:
            if variation in parish_mapping:
                return parish_mapping[variation]

        # Partial match - find any parish name that contains this as substring
        for mapped_name, parish_id in parish_mapping.items():
            if parish_clean in mapped_name or mapped_name in parish_clean:
                return parish_id

        return None

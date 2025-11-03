"""Christenings data processor for Bills of Mortality."""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from loguru import logger

from ..models import ChristeningRecord
from ..utils.columns import normalize_column_name


class ChristeningsProcessor:
    """Processes christenings data from Bills of Mortality datasets."""

    def __init__(self):
        """Initialize the christenings processor."""
        self.records: List[ChristeningRecord] = []

    def process_datasets(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Process multiple datasets to extract christenings data.

        Args:
            datasets: Dictionary mapping dataset names to DataFrames
        """
        logger.info("👶 Processing christenings data from datasets")

        for dataset_name, df in datasets.items():
            logger.info(f"Processing christenings from {dataset_name}")
            self._process_single_dataset(df, dataset_name)

        logger.info(f"Generated {len(self.records)} christenings records total")

    def _process_single_dataset(self, df: pd.DataFrame, dataset_name: str) -> None:
        """Process a single dataset for christenings data.

        Args:
            df: DataFrame to process
            dataset_name: Name of the dataset for source tracking
        """
        # Find christening-related columns
        christening_columns = self._find_christening_columns(df)

        if not christening_columns:
            logger.info(f"No christening columns found in {dataset_name}")
            return

        logger.info(
            f"Found {len(christening_columns)} christening columns in {dataset_name}"
        )

        # Process each row in the dataset
        for _, row in df.iterrows():
            # Extract basic temporal data
            year = self._extract_year(row)
            week_number = self._extract_week_number(row)
            unique_identifier = self._extract_unique_identifier(row)

            # For General Bills, set week_number to 90 if not present (indicates annual data)
            if week_number is None and "general" in dataset_name.lower():
                week_number = 90

            # Extract date information
            start_day = self._extract_date_field(row, "start_day")
            start_month = self._extract_date_field(row, "start_month")
            end_day = self._extract_date_field(row, "end_day")
            end_month = self._extract_date_field(row, "end_month")

            # Create week join ID
            joinid = self._create_week_joinid(year, week_number, unique_identifier)

            # Process each christening column
            for column_name in christening_columns:
                christening_info = self._parse_christening_column(column_name)
                raw_value = row.get(column_name)

                # Skip if no value or invalid
                if pd.isna(raw_value) or raw_value == "":
                    continue

                # Parse count from raw value
                count = self._parse_count(raw_value)

                # Create christening record
                record = ChristeningRecord(
                    christening=christening_info["type"],
                    count=count,
                    week_number=week_number,
                    start_month=start_month,
                    end_month=end_month,
                    year=year,
                    start_day=start_day,
                    end_day=end_day,
                    missing=self._is_missing_value(raw_value),
                    illegible=self._is_illegible_value(raw_value),
                    source=dataset_name,
                    bill_type=self._determine_bill_type(dataset_name, week_number),
                    joinid=joinid,
                    unique_identifier=unique_identifier,
                )

                self.records.append(record)

    def _find_christening_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns related to christenings data.

        Args:
            df: DataFrame to analyze

        Returns:
            List of column names containing christening data
        """
        christening_columns = []

        # Common patterns for christening columns
        patterns = [
            r"christen",
            r"baptis",
            r"birth",
            # Gender-specific patterns
            r"christened.*male",
            r"christened.*female",
            r"christened.*total",
            r"christened.*all",
            # Aggregate parish patterns (most common in parish files)
            r"christened.*parish",
            r"christened.*wall",
            r"christened.*middlesex",
            r"christened.*surrey",
            r"christened.*westminster",
            # Patterns that start with christened (for parish aggregate columns)
            r"^christened.*in.*the",
            r"^christened.*parishes",
        ]

        for column in df.columns:
            normalized_col = normalize_column_name(column).lower()
            original_col = column.lower()

            # Check if column matches any christening pattern
            for pattern in patterns:
                if re.search(pattern, normalized_col, re.IGNORECASE) or re.search(
                    pattern, original_col, re.IGNORECASE
                ):
                    christening_columns.append(column)
                    break

        return list(set(christening_columns))  # Remove duplicates

    def _parse_christening_column(self, column_name: str) -> Dict[str, Optional[str]]:
        """Parse a christening column name to extract christening information.

        Args:
            column_name: Name of the column to parse

        Returns:
            Dictionary with christening type information
        """
        normalized = normalize_column_name(column_name).lower()

        info = {"type": "christened_general", "gender": None, "area": None}

        # Determine gender
        if "male" in normalized and "female" not in normalized:
            info["gender"] = "male"
            info["type"] = "christened_male"
        elif "female" in normalized:
            info["gender"] = "female"
            info["type"] = "christened_female"
        elif "total" in normalized or "all" in normalized:
            info["type"] = "christened_total"

        # Determine area/geographic scope
        if "within" in normalized and "wall" in normalized:
            info["area"] = "within_walls"
            info["type"] = f"christened_parishes_within_walls"
        elif "without" in normalized and "wall" in normalized:
            info["area"] = "without_walls"
            info["type"] = f"christened_parishes_without_walls"
        elif "middlesex" in normalized or "surrey" in normalized:
            info["area"] = "out_parishes"
            info["type"] = f"christened_out_parishes"
        elif "westminster" in normalized:
            info["area"] = "westminster"
            info["type"] = f"christened_westminster"
        elif "parish" in normalized:
            # Generic parish christenings
            if info["gender"]:
                info["type"] = f"christened_parishes_{info['gender']}"
            else:
                info["type"] = "christened_parishes_total"

        return info

    def _extract_year(self, row: pd.Series) -> Optional[int]:
        """Extract year from row data."""
        year_fields = ["year", "Year", "start_year", "Start Year"]

        for field in year_fields:
            if field in row.index and not pd.isna(row[field]):
                try:
                    return int(row[field])
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_week_number(self, row: pd.Series) -> Optional[int]:
        """Extract week number from row data."""
        week_fields = ["week", "Week", "week_number", "Week Number"]

        for field in week_fields:
            if field in row.index and not pd.isna(row[field]):
                try:
                    # Convert decimal values to integers (e.g., 14.0 -> 14)
                    return int(float(row[field]))
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_unique_identifier(self, row: pd.Series) -> Optional[str]:
        """Extract unique identifier from row data."""
        id_fields = ["unique_identifier", "Unique Identifier", "identifier", "id"]

        for field in id_fields:
            if field in row.index and not pd.isna(row[field]):
                return str(row[field])

        return None

    def _extract_date_field(self, row: pd.Series, field_type: str) -> Optional[Any]:
        """Extract date field from row data.

        Args:
            row: Pandas Series containing row data
            field_type: Type of field ('start_day', 'start_month', 'end_day', 'end_month')
        """
        field_mappings = {
            "start_day": ["start_day", "Start Day"],
            "start_month": ["start_month", "Start Month"],
            "end_day": ["end_day", "End Day"],
            "end_month": ["end_month", "End Month"],
        }

        fields = field_mappings.get(field_type, [])

        for field in fields:
            if field in row.index and not pd.isna(row[field]):
                if field_type in ["start_day", "end_day"]:
                    try:
                        # Convert decimal values to integers (e.g., 18.0 -> 18)
                        return int(float(row[field]))
                    except (ValueError, TypeError):
                        continue
                else:
                    return str(row[field])

        return None

    def _create_week_joinid(
        self,
        year: Optional[int],
        week_number: Optional[int],
        unique_identifier: Optional[str],
    ) -> Optional[str]:
        """Create a week join ID for linking to weeks table."""
        if year and week_number is not None:
            return f"{year}-{week_number:02d}"
        elif unique_identifier:
            return unique_identifier
        return None

    def _parse_count(self, raw_value: Any) -> Optional[int]:
        """Parse count value from raw data.

        Args:
            raw_value: Raw value from dataset

        Returns:
            Parsed integer count or None if not parseable
        """
        if pd.isna(raw_value):
            return None

        # Convert to string for processing
        value_str = str(raw_value).strip()

        # Handle common non-numeric indicators
        if value_str.lower() in ["", "none", "n/a", "na", "-"]:
            return None

        # Try to extract numeric value
        try:
            # First try direct conversion for decimal values
            return int(float(value_str))
        except (ValueError, TypeError):
            try:
                # Fallback: Remove common punctuation and whitespace
                clean_value = re.sub(r"[^\d]", "", value_str)
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
        missing_indicators = ["missing", "miss", "m", "n/a", "na", ""]

        return value_str in missing_indicators

    def _is_illegible_value(self, raw_value: Any) -> Optional[bool]:
        """Determine if a value represents illegible data."""
        if pd.isna(raw_value):
            return False

        value_str = str(raw_value).strip().lower()
        illegible_indicators = ["illegible", "illeg", "unclear", "?", "torn"]

        return any(indicator in value_str for indicator in illegible_indicators)

    def _determine_bill_type(
        self, source_name: str, week_number: Optional[int]
    ) -> Optional[str]:
        """Determine bill type based on source dataset name and week number.

        Args:
            source_name: Name of source dataset file
            week_number: Week number from the data

        Returns:
            "general" or "weekly" or None
        """
        # Check source filename for "general" pattern (highest priority)
        if source_name and "general" in source_name.lower():
            return "general"

        # Fallback to week number logic for files without clear naming
        if week_number == 90:
            return "general"
        elif week_number and 1 <= week_number <= 53:
            return "weekly"

        # Default for files without clear indicators
        return "weekly"

    def get_records(self) -> List[ChristeningRecord]:
        """Get all processed christening records."""
        return self.records

    def save_csv(self, output_path: str) -> None:
        """Save processed christening records to CSV file.

        Args:
            output_path: Path to output CSV file
        """
        if not self.records:
            logger.warning("No christenings records to save")
            return

        # Convert records to DataFrame
        df = pd.DataFrame([record.to_dict() for record in self.records])

        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(self.records)} christenings records to {output_path}")

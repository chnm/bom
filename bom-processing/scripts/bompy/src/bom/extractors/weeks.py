"""Week extraction and unique week ID generation."""

from typing import Dict, List, Optional, Set

import pandas as pd
from loguru import logger

from ..models import WeekRecord
from ..utils.validation import SchemaValidator


class WeekExtractor:
    """Extracts and creates unique week records for the week table."""

    def __init__(self):
        self.month_mapping = {
            "january": "01",
            "jan": "01",
            "january)": "01",
            "february": "02",
            "feb": "02",
            "february)": "02",
            "march": "03",
            "mar": "03",
            "march)": "03",
            "april": "04",
            "apr": "04",
            "april)": "04",
            "may": "05",
            "may)": "05",
            "june": "06",
            "jun": "06",
            "june)": "06",
            "july": "07",
            "jul": "07",
            "july)": "07",
            "august": "08",
            "aug": "08",
            "august)": "08",
            "september": "09",
            "sep": "09",
            "sept": "09",
            "september)": "09",
            "october": "10",
            "oct": "10",
            "october)": "10",
            "november": "11",
            "nov": "11",
            "november)": "11",
            "december": "12",
            "dec": "12",
            "december)": "12",
        }

    def month_to_number(self, month: Optional[str]) -> str:
        """Convert month name to number string."""
        if not month:
            return "01"  # Default fallback

        month_clean = str(month).lower().strip()
        return self.month_mapping.get(month_clean, "01")

    def create_joinid(
        self,
        start_year: int,
        start_month: Optional[str],
        start_day: Optional[int],
        end_year: int,
        end_month: Optional[str],
        end_day: Optional[int],
    ) -> str:
        """Create joinid in format yyyymmddyyyymmdd."""
        start_month_num = self.month_to_number(start_month)
        end_month_num = self.month_to_number(end_month)

        start_day_pad = f"{start_day:02d}" if start_day else "01"
        end_day_pad = f"{end_day:02d}" if end_day else "07"  # Default week length

        return f"{start_year}{start_month_num}{start_day_pad}{end_year}{end_month_num}{end_day_pad}"

    def create_week_id(self, year: int, week_number: Optional[int]) -> str:
        """Create week_id for historical date ranges."""
        if not week_number:
            return f"{year}-unknown"

        week_pad = f"{week_number:02d}"

        # General bills (week 90) span full year
        if week_number == 90:
            return f"{year}-{year}-{week_pad}"
        # Historical year handling - weeks > 15 span previous year
        elif week_number > 15:
            return f"{year-1}-{year}-{week_pad}"
        else:
            return f"{year}-{year+1}-{week_pad}"

    def create_split_year(self, year: int, week_number: Optional[int]) -> str:
        """Create split year string."""
        if not week_number:
            return str(year)

        # General bills span full year
        if week_number == 90:
            return str(year)
        elif week_number > 15:
            return f"{year-1}/{year}"
        else:
            return str(year)

    def extract_weeks_from_dataframes(
        self, dataframes: List[tuple[pd.DataFrame, str]]
    ) -> List[WeekRecord]:
        """
        Extract unique weeks from multiple DataFrames.

        Args:
            dataframes: List of (DataFrame, source_name) tuples

        Returns:
            List of unique WeekRecord objects
        """
        all_weeks = []
        seen_joinids: Set[str] = set()

        for df, source_name in dataframes:
            logger.info(f"Extracting weeks from {source_name}")

            # Find relevant columns
            week_cols = self._find_week_columns(df)
            if not week_cols:
                logger.warning(f"No week columns found in {source_name}")
                continue

            # Extract week data
            week_data = df[week_cols].copy()
            week_data = week_data.dropna(subset=["year"]).drop_duplicates()

            logger.info(f"Found {len(week_data)} potential week records")

            for _, row in week_data.iterrows():
                try:
                    week_record = self._create_week_record(row, source_name)

                    # Only add if we haven't seen this joinid before
                    if week_record.joinid not in seen_joinids:
                        all_weeks.append(week_record)
                        seen_joinids.add(week_record.joinid)

                except Exception as e:
                    logger.warning(f"Failed to create week record: {e}")
                    continue

        logger.info(f"Extracted {len(all_weeks)} unique weeks total")
        return all_weeks

    def _find_week_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns needed for week extraction."""
        required = ["year"]
        optional = [
            "week_number",
            "week",
            "start_day",
            "end_day",
            "start_month",
            "end_month",
            "unique_identifier",
        ]

        available = []

        # Must have year
        if "year" not in df.columns:
            return []
        available.append("year")

        # Add any optional columns that exist
        for col in optional:
            if col in df.columns:
                available.append(col)

        return available

    def _create_week_record(self, row: pd.Series, source_name: str) -> WeekRecord:
        """Create a WeekRecord from a DataFrame row."""
        # Get values with fallbacks
        year = int(row["year"]) if pd.notna(row["year"]) else None
        week_number = (
            int(row.get("week_number", row.get("week", 1)))
            if pd.notna(row.get("week_number", row.get("week")))
            else 1
        )

        start_day = int(row["start_day"]) if pd.notna(row.get("start_day")) else None
        end_day = int(row["end_day"]) if pd.notna(row.get("end_day")) else None
        start_month = (
            str(row["start_month"]) if pd.notna(row.get("start_month")) else None
        )
        end_month = str(row["end_month"]) if pd.notna(row.get("end_month")) else None
        unique_identifier = (
            str(row["unique_identifier"])
            if pd.notna(row.get("unique_identifier"))
            else None
        )

        # Handle year-spanning periods (for general bills)
        start_year = (
            int(row.get("start_year", year))
            if pd.notna(row.get("start_year"))
            else year
        )
        end_year = (
            int(row.get("end_year", year)) if pd.notna(row.get("end_year")) else year
        )

        # Detect general bills and set week_number = 90
        if self._is_general_bill(
            unique_identifier, start_month, end_month, start_day, end_day
        ):
            week_number = 90
            logger.debug(
                f"Detected general bill: {unique_identifier}, setting week_number = 90"
            )

        # Create computed fields
        joinid = self.create_joinid(
            start_year, start_month, start_day, end_year, end_month, end_day
        )
        week_id = self.create_week_id(year, week_number)
        split_year = self.create_split_year(year, week_number)
        year_range = (
            week_id.split("-")[0] + "-" + week_id.split("-")[1]
            if "-" in week_id
            else str(year)
        )

        return WeekRecord(
            joinid=joinid,
            start_day=start_day,
            start_month=start_month,
            end_day=end_day,
            end_month=end_month,
            year=year,
            week_number=week_number,
            split_year=split_year,
            unique_identifier=unique_identifier,
            week_id=week_id,
            year_range=year_range,
        )

    def _is_general_bill(
        self,
        unique_identifier: Optional[str],
        start_month: Optional[str],
        end_month: Optional[str],
        start_day: Optional[int],
        end_day: Optional[int],
    ) -> bool:
        """
        Detect if this is a general bill based on identifier and date span.

        General bills typically:
        1. Have 'GeneralBill' in unique_identifier
        2. Span close to a full year (e.g., December to December)
        3. Have large date spans indicating annual summaries
        """
        if not unique_identifier:
            return False

        # Check identifier patterns
        identifier_lower = unique_identifier.lower()
        if any(
            pattern in identifier_lower
            for pattern in ["generalbill", "general-bill", "general_bill"]
        ):
            return True

        # Check date span patterns that suggest annual coverage
        if start_month and end_month:
            start_month_lower = start_month.lower()
            end_month_lower = end_month.lower()

            # December to December pattern (common for general bills)
            if "december" in start_month_lower and "december" in end_month_lower:
                return True

            # Large month spans that suggest annual coverage
            start_month_num = int(self.month_to_number(start_month))
            end_month_num = int(self.month_to_number(end_month))

            # Handle year-spanning ranges
            if start_month_num == 12 and end_month_num == 12:  # Dec to Dec
                return True
            elif start_month_num > end_month_num:  # Year-spanning range
                month_span = (12 - start_month_num) + end_month_num
                if month_span >= 10:  # Spans 10+ months
                    return True

        return False

    def validate_weeks(self, weeks: List[WeekRecord]) -> List[WeekRecord]:
        """Validate week records against schema constraints."""
        valid_weeks = []
        validator = SchemaValidator()

        for week in weeks:
            errors = validator.validate_week(week)
            if errors:
                logger.warning(f"Invalid week record {week.joinid}: {errors}")
            else:
                valid_weeks.append(week)

        logger.info(f"Validated {len(valid_weeks)}/{len(weeks)} week records")
        return valid_weeks

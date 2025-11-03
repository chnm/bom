"""Data validation utilities for PostgreSQL schema compliance."""

from typing import Any, List, Optional

import pandas as pd
from loguru import logger

from ..models import (
    BillOfMortalityRecord,
    CausesOfDeathRecord,
    ChristeningRecord,
    ParishRecord,
    WeekRecord,
    YearRecord,
)


class SchemaValidator:
    """Validates data against PostgreSQL schema constraints."""

    @staticmethod
    def validate_year(year: Optional[int]) -> bool:
        """Validate year is within historical range (1400-1800)."""
        if year is None:
            return True  # Nullable in some tables
        return 1400 < year < 1800

    @staticmethod
    def validate_week_number(week_number: Optional[int]) -> bool:
        """Validate week number is 1-90 (90 for annual records)."""
        if week_number is None:
            return True  # Nullable
        return 1 <= week_number <= 90

    @staticmethod
    def validate_day(day: Optional[int]) -> bool:
        """Validate day is 1-31."""
        if day is None:
            return True  # Nullable
        return 1 <= day <= 31

    @staticmethod
    def validate_bill_of_mortality(record: BillOfMortalityRecord) -> List[str]:
        """Validate bill_of_mortality record."""
        errors = []

        # Required fields
        if not record.count_type:
            errors.append("count_type is required")
        if not record.year:
            errors.append("year is required")
        if not record.joinid:
            errors.append("joinid is required")
        if not record.parish_id:
            errors.append("parish_id is required")

        # Range validations
        if not SchemaValidator.validate_year(record.year):
            errors.append(f"year {record.year} not in valid range (1400-1800)")

        return errors

    @staticmethod
    def validate_causes_of_death(record: CausesOfDeathRecord) -> List[str]:
        """Validate causes_of_death record."""
        errors = []

        # Required fields
        if not record.death:
            errors.append("death is required")
        if not record.joinid:
            errors.append("joinid is required")

        # Range validations
        if not SchemaValidator.validate_year(record.year):
            errors.append(f"year {record.year} not in valid range (1400-1800)")

        return errors

    @staticmethod
    def validate_christening(record: ChristeningRecord) -> List[str]:
        """Validate christenings record."""
        errors = []

        # Required fields
        if not record.christening:
            errors.append("christening is required")

        # Range validations
        if not SchemaValidator.validate_year(record.year):
            errors.append(f"year {record.year} not in valid range (1400-1800)")
        if not SchemaValidator.validate_week_number(record.week_number):
            errors.append(f"week_number {record.week_number} not in valid range (1-90)")
        if not SchemaValidator.validate_day(record.start_day):
            errors.append(f"start_day {record.start_day} not in valid range (1-31)")
        if not SchemaValidator.validate_day(record.end_day):
            errors.append(f"end_day {record.end_day} not in valid range (1-31)")

        return errors

    @staticmethod
    def validate_parish(record: ParishRecord) -> List[str]:
        """Validate parishes record."""
        errors = []

        # Required fields
        if not record.parish_name:
            errors.append("parish_name is required")
        if not record.canonical_name:
            errors.append("canonical_name is required")
        if record.id is None:
            errors.append("id is required")

        return errors

    @staticmethod
    def validate_week(record: WeekRecord) -> List[str]:
        """Validate week record."""
        errors = []

        # Required fields
        if not record.joinid:
            errors.append("joinid is required")

        # Range validations
        if not SchemaValidator.validate_year(record.year):
            errors.append(f"year {record.year} not in valid range (1400-1800)")
        if not SchemaValidator.validate_week_number(record.week_number):
            errors.append(f"week_number {record.week_number} not in valid range (1-90)")
        if not SchemaValidator.validate_day(record.start_day):
            errors.append(f"start_day {record.start_day} not in valid range (1-31)")
        if not SchemaValidator.validate_day(record.end_day):
            errors.append(f"end_day {record.end_day} not in valid range (1-31)")

        return errors

    @staticmethod
    def validate_year_record(record: YearRecord) -> List[str]:
        """Validate year record."""
        errors = []

        # Required fields and range
        if not SchemaValidator.validate_year(record.year):
            errors.append(f"year {record.year} not in valid range (1400-1800)")

        return errors

    @staticmethod
    def validate_dataframe_for_postgres(df: pd.DataFrame, table_name: str) -> List[str]:
        """Validate a DataFrame before PostgreSQL insertion."""
        errors = []

        # Check for duplicate keys based on unique constraints
        if table_name == "bill_of_mortality":
            # Unique constraint: (parish_id, count_type, year, joinid)
            key_cols = ["parish_id", "count_type", "year", "joinid"]
            if all(col in df.columns for col in key_cols):
                duplicates = df.duplicated(subset=key_cols)
                if duplicates.any():
                    errors.append(
                        f"Found {duplicates.sum()} duplicate records for unique constraint"
                    )

        elif table_name == "causes_of_death":
            # Unique constraint: (death, year, joinid)
            key_cols = ["death", "year", "joinid"]
            if all(col in df.columns for col in key_cols):
                duplicates = df.duplicated(subset=key_cols)
                if duplicates.any():
                    errors.append(
                        f"Found {duplicates.sum()} duplicate records for unique constraint"
                    )

        elif table_name == "christenings":
            # Unique constraint: (christening, week_number, start_day, start_month, end_day, end_month, year)
            key_cols = [
                "christening",
                "week_number",
                "start_day",
                "start_month",
                "end_day",
                "end_month",
                "year",
            ]
            if all(col in df.columns for col in key_cols):
                duplicates = df.duplicated(subset=key_cols)
                if duplicates.any():
                    errors.append(
                        f"Found {duplicates.sum()} duplicate records for unique constraint"
                    )

        elif table_name == "parishes":
            # Unique constraint: parish_name
            if "parish_name" in df.columns:
                duplicates = df.duplicated(subset=["parish_name"])
                if duplicates.any():
                    errors.append(f"Found {duplicates.sum()} duplicate parish names")

        # Check for NULL values in required fields
        required_fields = {
            "bill_of_mortality": ["parish_id", "count_type", "year", "joinid"],
            "causes_of_death": ["death", "joinid"],
            "christenings": ["christening"],
            "parishes": ["parish_name", "canonical_name"],
            "week": ["joinid"],
            "year": ["year"],
        }

        if table_name in required_fields:
            for field in required_fields[table_name]:
                if field in df.columns:
                    null_count = df[field].isnull().sum()
                    if null_count > 0:
                        errors.append(
                            f"Found {null_count} NULL values in required field '{field}'"
                        )

        return errors

    @staticmethod
    def log_validation_summary(
        df: pd.DataFrame, table_name: str, errors: List[str]
    ) -> None:
        """Log validation summary."""
        if errors:
            logger.warning(f"Validation errors for {table_name} ({len(df)} rows):")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info(f"✓ {table_name} validation passed ({len(df)} rows)")


def validate_processing_result(result) -> bool:
    """Validate all records in a processing result."""
    validator = SchemaValidator()
    all_valid = True

    # Convert to DataFrames for validation
    dataframes = result.to_dataframes()

    for table_name, df in dataframes.items():
        if not df.empty:
            errors = validator.validate_dataframe_for_postgres(df, table_name)
            validator.log_validation_summary(df, table_name, errors)
            if errors:
                all_valid = False

    return all_valid

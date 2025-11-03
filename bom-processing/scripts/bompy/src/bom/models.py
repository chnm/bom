"""Data models for Bills of Mortality processing - matching PostgreSQL schema exactly."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class FoodstuffsRecord:
    """Represents a foodstuffs record with bread prices and commodity data."""

    year: int
    week: Optional[int]
    unique_identifier: str
    start_day: Optional[int]
    start_month: Optional[str]
    end_day: Optional[int]
    end_month: Optional[str]
    commodity_category: str  # 'bread', 'seasoning', etc.
    commodity_type: str  # 'penny_loaf', 'salt', etc.
    quality_grade: Optional[str]  # 'white', 'wheaten', 'household'
    measurement_standard: Optional[str]  # 'troy_weight', 'common_weight'
    weight_pounds: Optional[int]
    weight_ounces: Optional[int]
    weight_drams: Optional[int]
    price_shillings: Optional[int]
    price_pence: Optional[int]
    raw_value: str  # Original value from dataset
    source: str  # Source dataset
    column_name: str  # Original column name

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
            "commodity_category": self.commodity_category,
            "commodity_type": self.commodity_type,
            "quality_grade": self.quality_grade,
            "measurement_standard": self.measurement_standard,
            "weight_pounds": self.weight_pounds,
            "weight_ounces": self.weight_ounces,
            "weight_drams": self.weight_drams,
            "price_shillings": self.price_shillings,
            "price_pence": self.price_pence,
            "raw_value": self.raw_value,
            "source": self.source,
            "column_name": self.column_name,
        }


@dataclass
class BillOfMortalityRecord:
    """Represents a bill_of_mortality table record."""

    parish_id: Optional[int]  # Foreign key to parishes table (None for causes data)
    count_type: str  # "buried", "plague", "christened", or cause name
    count: Optional[int]
    year: int  # Foreign key to year table
    joinid: str  # Foreign key to week table (joinid)
    bill_type: Optional[str]  # "weekly" or "general"
    missing: Optional[bool]
    illegible: Optional[bool]
    source: Optional[str]
    unique_identifier: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "parish_id": self.parish_id,
            "count_type": self.count_type,
            "count": self.count,
            "year": self.year,
            "joinid": self.joinid,
            "bill_type": self.bill_type,
            "missing": self.missing,
            "illegible": self.illegible,
            "source": self.source,
            "unique_identifier": self.unique_identifier,
        }


@dataclass
class SubtotalRecord:
    """Represents a subtotal record for geographic aggregations like 'within the walls'."""

    subtotal_category: str  # "Within the walls", "Without the walls", "Middlesex and Surrey", "Westminster"
    count_type: str  # "buried", "plague", "christened"
    count: Optional[int]
    year: int  # Foreign key to year table
    joinid: str  # Foreign key to week table (joinid)
    bill_type: Optional[str]  # "weekly" or "general"
    missing: Optional[bool]
    illegible: Optional[bool]
    source: Optional[str]
    unique_identifier: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "subtotal_category": self.subtotal_category,
            "count_type": self.count_type,
            "count": self.count,
            "year": self.year,
            "joinid": self.joinid,
            "bill_type": self.bill_type,
            "missing": self.missing,
            "illegible": self.illegible,
            "source": self.source,
            "unique_identifier": self.unique_identifier,
        }


@dataclass
class CausesOfDeathRecord:
    """Represents a causes_of_death table record."""

    death: str  # The cause of death
    count: Optional[int]
    year: Optional[int]  # Foreign key to year table
    joinid: str  # Foreign key to week table (joinid)
    descriptive_text: Optional[str]
    source_name: Optional[str]
    definition: Optional[str]  # From dictionary
    definition_source: Optional[str]
    bill_type: Optional[str]  # 'weekly' or 'general'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "death": self.death,
            "count": self.count,
            "year": self.year,
            "joinid": self.joinid,
            "descriptive_text": self.descriptive_text,
            "source_name": self.source_name,
            "definition": self.definition,
            "definition_source": self.definition_source,
            "bill_type": self.bill_type,
        }


@dataclass
class ChristeningRecord:
    """Represents a christenings table record."""

    christening: str  # Type of christening record
    count: Optional[int]
    week_number: Optional[int]
    start_month: Optional[str]
    end_month: Optional[str]
    year: Optional[int]  # Foreign key to year table
    start_day: Optional[int]
    end_day: Optional[int]
    missing: Optional[bool]
    illegible: Optional[bool]
    source: Optional[str]
    bill_type: Optional[str]
    joinid: Optional[str]  # Foreign key to week table
    unique_identifier: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "christening": self.christening,
            "count": self.count,
            "week_number": self.week_number,
            "start_month": self.start_month,
            "end_month": self.end_month,
            "year": self.year,
            "start_day": self.start_day,
            "end_day": self.end_day,
            "missing": self.missing,
            "illegible": self.illegible,
            "source": self.source,
            "bill_type": self.bill_type,
            "joinid": self.joinid,
            "unique_identifier": self.unique_identifier,
        }


@dataclass
class ParishRecord:
    """Represents a parishes table record."""

    id: int  # Primary key
    parish_name: str  # Must be unique
    canonical_name: str  # Required canonical name
    bills_subunit: Optional[
        str
    ] = None  # Bills subunit classification (e.g., "97 parishes within the walls")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "id": self.id,
            "parish_name": self.parish_name,
            "canonical_name": self.canonical_name,
            "bills_subunit": self.bills_subunit,
        }


@dataclass
class WeekRecord:
    """Represents a week table record."""

    joinid: str  # Primary key
    start_day: Optional[int]  # 1-31 constraint
    start_month: Optional[str]
    end_day: Optional[int]  # 1-31 constraint
    end_month: Optional[str]
    year: Optional[int]  # Foreign key to year table
    week_number: Optional[int]  # 1-90 constraint (90 for annual records)
    split_year: Optional[str]
    unique_identifier: Optional[str]
    week_id: Optional[str]
    year_range: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {
            "joinid": self.joinid,
            "start_day": self.start_day,
            "start_month": self.start_month,
            "end_day": self.end_day,
            "end_month": self.end_month,
            "year": self.year,
            "week_number": self.week_number,
            "split_year": self.split_year,
            "unique_identifier": self.unique_identifier,
            "week_id": self.week_id,
            "year_range": self.year_range,
        }


@dataclass
class YearRecord:
    """Represents a year table record."""

    year: int  # Primary key, 1400 < year < 1800 constraint

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        return {"year": self.year}


@dataclass
class ProcessingResult:
    """Container for processed data results."""

    bills: List[BillOfMortalityRecord]
    causes: List[CausesOfDeathRecord]
    christenings: List[ChristeningRecord]
    parishes: List[ParishRecord]
    weeks: List[WeekRecord]
    years: List[YearRecord]
    subtotals: List[SubtotalRecord]
    source_file: str
    processing_notes: List[str]

    def to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert to pandas DataFrames matching PostgreSQL schema."""
        return {
            "bill_of_mortality": pd.DataFrame([bill.to_dict() for bill in self.bills]),
            "causes_of_death": pd.DataFrame([cause.to_dict() for cause in self.causes]),
            "christenings": pd.DataFrame(
                [christening.to_dict() for christening in self.christenings]
            ),
            "parishes": pd.DataFrame([parish.to_dict() for parish in self.parishes]),
            "week": pd.DataFrame([week.to_dict() for week in self.weeks]),
            "year": pd.DataFrame([year.to_dict() for year in self.years]),
            "subtotals": pd.DataFrame(
                [subtotal.to_dict() for subtotal in self.subtotals]
            ),
        }


@dataclass
class DatasetInfo:
    """Information about a loaded dataset."""

    file_path: str
    dataset_type: str
    original_columns: List[str]
    normalized_columns: List[str]
    row_count: int
    processing_notes: List[str]


# Helper classes for intermediate processing
@dataclass
class RawBillRecord:
    """Intermediate record before parish_id lookup."""

    parish_name: str  # Will be converted to parish_id
    count_type: str
    count: Optional[int]
    year: int
    week_id: str
    bill_type: Optional[str]
    missing: Optional[bool]
    illegible: Optional[bool]
    source: Optional[str]
    unique_identifier: Optional[str]

#!/usr/bin/env python3
"""
Foodstuffs processor for Bills of Mortality data.

Extracts bread prices, commodity data, and food-related economic information
from the historical Bills of Mortality datasets.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from ..models import FoodstuffsRecord
from ..utils.columns import normalize_column_name


class FoodstuffsProcessor:
    """Process foodstuffs and commodity data from Bills of Mortality datasets."""

    def __init__(self):
        """Initialize the foodstuffs processor."""
        self.records: List[FoodstuffsRecord] = []

        # Foodstuff patterns for column identification
        self.foodstuff_patterns = {
            "bread": r".*loaf.*|.*bread.*",
            "commodity": r"salt|wheat|grain|flour",
            "price": r".*price.*|.*cost.*",
            "weight": r".*weight.*|.*troy.*|.*common.*",
        }

        # Bread type patterns
        self.bread_types = {
            "penny_loaf": r"penny\s+loaf",
            "two_penny_loaf": r"two\s+penny\s+loaf",
            "six_penny_loaf": r"six\s+penny\s+loaf",
            "twelve_penny_loaf": r"twelve\s+penny\s+loaf",
            "eighteen_penny_loaf": r"eighteen\s+penny\s+loaf",
            "quartern_loaf": r"quartern\s+loaf",
            "half_peck_loaf": r"half\s+peck\s+loaf",
            "peck_loaf": r"peck\s+loaf",
        }

        # Quality grades
        self.quality_grades = ["white", "wheaten", "household"]

        # Weight standards
        self.weight_standards = ["troy_weight", "common_weight"]

    def process_datasets(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """
        Process multiple datasets and extract foodstuffs records.

        Args:
            datasets: Dictionary mapping dataset names to DataFrames
        """
        logger.info("🍞 Processing foodstuffs data from datasets")

        for dataset_name, df in datasets.items():
            logger.info(f"Processing foodstuffs from {dataset_name}")
            self._process_single_dataset(df, dataset_name)

        logger.info(f"Generated {len(self.records)} foodstuffs records total")

    def _process_single_dataset(self, df: pd.DataFrame, source: str) -> None:
        """
        Process a single dataset for foodstuffs data.

        Args:
            df: DataFrame to process
            source: Source dataset name
        """
        # Find foodstuff-related columns
        foodstuff_columns = self._identify_foodstuff_columns(df.columns.tolist())

        if not foodstuff_columns:
            logger.info(f"No foodstuff columns found in {source}")
            return

        logger.info(f"Found {len(foodstuff_columns)} foodstuff columns in {source}")

        # Process each row
        for _, row in df.iterrows():
            self._process_row(row, foodstuff_columns, source)

    def _identify_foodstuff_columns(self, columns: List[str]) -> List[str]:
        """
        Identify columns that contain foodstuffs data.

        Args:
            columns: List of column names

        Returns:
            List of foodstuff-related column names
        """
        foodstuff_cols = []

        for col in columns:
            normalized_col = normalize_column_name(col).lower()

            # Skip unnamed columns from dirty data
            if normalized_col.startswith("unnamed"):
                continue

            # Check for bread patterns
            for bread_pattern in self.bread_types.values():
                if re.search(bread_pattern, normalized_col, re.IGNORECASE):
                    foodstuff_cols.append(col)
                    break

            # Check for commodity patterns
            if col not in foodstuff_cols:
                for pattern in self.foodstuff_patterns.values():
                    if re.search(pattern, normalized_col, re.IGNORECASE):
                        foodstuff_cols.append(col)
                        break

        return foodstuff_cols

    def _process_row(
        self, row: pd.Series, foodstuff_columns: List[str], source: str
    ) -> None:
        """
        Process a single row to extract foodstuffs records.

        Args:
            row: DataFrame row
            foodstuff_columns: List of foodstuff column names
            source: Source dataset name
        """
        # Extract basic temporal and reference data
        year = self._safe_get_value(row, ["year", "Year"])
        week = self._safe_get_value(row, ["week", "Week"])
        unique_id = self._safe_get_value(
            row, ["unique_identifier", "Unique Identifier"]
        )

        # Extract date information
        start_day = self._safe_get_value(row, ["start_day", "Start day"])
        start_month = self._safe_get_value(row, ["start_month", "Start month"])
        end_day = self._safe_get_value(row, ["end_day", "End day"])
        end_month = self._safe_get_value(row, ["end_month", "End month"])

        if not all([year, week, unique_id]):
            return

        # Process each foodstuff column
        for col in foodstuff_columns:
            value = row.get(col)
            if pd.isna(value) or value == "" or value is None:
                continue

            # Parse column to extract commodity details
            commodity_info = self._parse_foodstuff_column(col)

            # Parse value to extract weight/price information
            parsed_value = self._parse_foodstuff_value(str(value))

            # Create foodstuffs record
            record = FoodstuffsRecord(
                year=int(year),
                week=int(week) if week else None,
                unique_identifier=str(unique_id),
                start_day=int(start_day)
                if start_day and str(start_day).isdigit()
                else None,
                start_month=str(start_month) if start_month else None,
                end_day=int(end_day) if end_day and str(end_day).isdigit() else None,
                end_month=str(end_month) if end_month else None,
                commodity_category=commodity_info["category"],
                commodity_type=commodity_info["type"],
                quality_grade=commodity_info["quality"],
                measurement_standard=commodity_info["standard"],
                weight_pounds=parsed_value["pounds"],
                weight_ounces=parsed_value["ounces"],
                weight_drams=parsed_value["drams"],
                price_shillings=parsed_value["shillings"],
                price_pence=parsed_value["pence"],
                raw_value=str(value),
                source=source,
                column_name=col,
            )

            self.records.append(record)

    def _parse_foodstuff_column(self, column_name: str) -> Dict[str, Optional[str]]:
        """
        Parse a foodstuff column name to extract commodity information.

        Args:
            column_name: Name of the column

        Returns:
            Dictionary with commodity details
        """
        normalized = normalize_column_name(column_name).lower()

        info = {
            "category": "unknown",
            "type": "unknown",
            "quality": None,
            "standard": None,
        }

        # Determine category and type
        if "salt" in normalized:
            info["category"] = "seasoning"
            info["type"] = "salt"
        elif "loaf" in normalized or "bread" in normalized:
            info["category"] = "bread"

            # Determine bread type
            for bread_key, pattern in self.bread_types.items():
                if re.search(pattern, normalized, re.IGNORECASE):
                    info["type"] = bread_key
                    break
            else:
                info["type"] = "bread_general"

        # Determine quality grade
        for quality in self.quality_grades:
            if quality in normalized:
                info["quality"] = quality
                break

        # Determine weight standard
        if "troy" in normalized:
            info["standard"] = "troy_weight"
        elif "common" in normalized:
            info["standard"] = "common_weight"

        return info

    def _parse_foodstuff_value(self, value: str) -> Dict[str, Optional[int]]:
        """
        Parse a foodstuff value to extract weight and price information.

        Args:
            value: Raw value string

        Returns:
            Dictionary with parsed numerical values
        """
        parsed = {
            "pounds": None,
            "ounces": None,
            "drams": None,
            "shillings": None,
            "pence": None,
        }

        if not value or value.strip() == "":
            return parsed

        # Parse weight format: "00;08;00" (pounds;ounces;drams)
        weight_pattern = r"(\d+);(\d+);(\d+)"
        weight_match = re.search(weight_pattern, value)
        if weight_match:
            parsed["pounds"] = int(weight_match.group(1))
            parsed["ounces"] = int(weight_match.group(2))
            parsed["drams"] = int(weight_match.group(3))

        # Parse price format: "56 l. to the Bushel 5 s" or similar
        shilling_pattern = r"(\d+)\s*s"
        shilling_match = re.search(shilling_pattern, value, re.IGNORECASE)
        if shilling_match:
            parsed["shillings"] = int(shilling_match.group(1))

        pence_pattern = r"(\d+)\s*d"
        pence_match = re.search(pence_pattern, value, re.IGNORECASE)
        if pence_match:
            parsed["pence"] = int(pence_match.group(1))

        return parsed

    def _safe_get_value(
        self, row: pd.Series, possible_keys: List[str]
    ) -> Optional[str]:
        """
        Safely get a value from a row using multiple possible keys.

        Args:
            row: DataFrame row
            possible_keys: List of possible column names

        Returns:
            Value if found, None otherwise
        """
        for key in possible_keys:
            if key in row and not pd.isna(row[key]):
                return row[key]
        return None

    def get_records(self) -> List[FoodstuffsRecord]:
        """
        Get all processed foodstuffs records.

        Returns:
            List of FoodstuffsRecord objects
        """
        return self.records

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert foodstuffs records to a pandas DataFrame.

        Returns:
            DataFrame with foodstuffs data
        """
        if not self.records:
            return pd.DataFrame()

        return pd.DataFrame([record.to_dict() for record in self.records])

    def save_csv(self, output_path: Path) -> None:
        """
        Save foodstuffs records to CSV file.

        Args:
            output_path: Path to save CSV file
        """
        df = self.to_dataframe()
        if df.empty:
            logger.warning("No foodstuffs records to save")
            return

        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} foodstuffs records to {output_path}")

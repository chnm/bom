"""CSV loading with proper column normalization."""

from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from loguru import logger

from ..models import DatasetInfo
from ..utils.columns import (
    filter_relevant_columns,
    get_column_info,
    normalize_dataframe_columns,
)


class CSVLoader:
    """Loads CSV files with consistent column normalization."""

    def __init__(self):
        self.processing_notes: list[str] = []

    def load(self, file_path: Path, **kwargs: Any) -> tuple[pd.DataFrame, DatasetInfo]:
        """
        Load a CSV file with proper column normalization.

        Args:
            file_path: Path to CSV file
            **kwargs: Additional arguments for pandas.read_csv()

        Returns:
            Tuple of (DataFrame, DatasetInfo)
        """
        self.processing_notes = []

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        logger.info(f"Loading CSV: {file_path.name}")

        # Load raw CSV
        try:
            df_raw = pd.read_csv(file_path, **kwargs)
            logger.info(f"Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise

        original_columns = df_raw.columns.tolist()

        # Normalize column names (but preserve data!)
        df_normalized, column_mapping = normalize_dataframe_columns(df_raw)

        # Filter out irrelevant columns
        df_filtered = filter_relevant_columns(df_normalized)

        # Track what we did
        columns_removed = len(df_normalized.columns) - len(df_filtered.columns)
        if columns_removed > 0:
            self.processing_notes.append(
                f"Removed {columns_removed} irrelevant columns"
            )

        # Get column information
        column_info = get_column_info(df_filtered, column_mapping)

        # Create dataset info
        dataset_info = DatasetInfo(
            file_path=str(file_path),
            dataset_type=self._detect_dataset_type(file_path.name),
            original_columns=original_columns,
            normalized_columns=df_filtered.columns.tolist(),
            row_count=len(df_filtered),
            processing_notes=self.processing_notes.copy(),
        )

        logger.info(f"Processed dataset: {dataset_info.dataset_type}")
        logger.info(f"Final shape: {df_filtered.shape}")

        return df_filtered, dataset_info

    def _detect_dataset_type(self, filename: str) -> str:
        """
        Detect dataset type from filename patterns.

        Args:
            filename: Name of the file

        Returns:
            Dataset type string
        """
        import re

        from ..config import DATASET_PATTERNS

        filename_lower = filename.lower()

        for dataset_type, pattern in DATASET_PATTERNS.items():
            if re.search(pattern, filename_lower, re.IGNORECASE):
                return dataset_type

        # Fallback detection
        if "cause" in filename_lower:
            return "causes_unknown"
        elif "parish" in filename_lower:
            return "parishes_unknown"
        else:
            return "unknown"

    def load_multiple(
        self, file_paths: list[Path], **kwargs: Any
    ) -> Dict[str, tuple[pd.DataFrame, DatasetInfo]]:
        """
        Load multiple CSV files.

        Args:
            file_paths: List of paths to CSV files
            **kwargs: Additional arguments for pandas.read_csv()

        Returns:
            Dictionary mapping filename to (DataFrame, DatasetInfo)
        """
        results = {}

        for file_path in file_paths:
            try:
                df, info = self.load(file_path, **kwargs)
                results[file_path.name] = (df, info)
            except Exception as e:
                logger.error(f"Failed to load {file_path.name}: {e}")
                continue

        logger.info(f"Successfully loaded {len(results)}/{len(file_paths)} files")
        return results

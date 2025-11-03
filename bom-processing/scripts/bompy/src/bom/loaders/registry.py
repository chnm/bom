"""Dataset registry for identifying and routing different dataset types."""

import re
from pathlib import Path
from typing import Dict, Type

from ..config import DATASET_PATTERNS


class DatasetRegistry:
    """Registry for mapping dataset types to processors."""

    def __init__(self):
        self.processors: Dict[str, Type] = {}

    def register(self, dataset_type: str, processor_class: Type):
        """Register a processor for a dataset type."""
        self.processors[dataset_type] = processor_class

    def get_dataset_type(self, filename: str) -> str:
        """
        Detect dataset type from filename patterns.

        Args:
            filename: Name of the file

        Returns:
            Dataset type string
        """
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

    def get_processor(self, filename: str):
        """Get appropriate processor for a file (placeholder for now)."""
        dataset_type = self.get_dataset_type(filename)
        # For now, just return the dataset type
        # Later we'll return actual processor instances
        return dataset_type

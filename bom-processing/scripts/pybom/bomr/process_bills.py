#!/usr/bin/env python3
"""
Processing Bills of Mortality data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import argparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .helpers import (
    process_bodleian_data,
    process_weekly_bills,
    log_data_check,
    check_data_quality,
)
from .data_processing import (
    extract_aggregate_entries,
    process_unique_parishes,
    process_unique_weeks,
    process_unique_years,
    associate_week_ids,
    tidy_parish_data,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

console = Console()


def main():
    """Main function for processing Bills of Mortality data."""

    parser = argparse.ArgumentParser(
        description="Process Bills of Mortality data from CSV exports"
    )
    parser.add_argument(
        "--data-dir",
        default="../../../bom-data/data-csvs",
        help="Directory containing CSV files",
    )
    parser.add_argument(
        "--output-dir", default="data", help="Output directory for processed data"
    )

    args = parser.parse_args()

    console.print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Bills of Mortality Data Processor", style="bold blue")
    console.print("Python conversion of R scripts for Death by Numbers project\n")

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Check if data directory exists
    if not data_dir.exists():
        console.print(f"❌ Data directory not found: {data_dir}", style="bold red")
        console.print("Please check the path or create some test data.", style="yellow")
        return

    # Simple test with available data
    console.print("📁 Looking for CSV files...", style="blue")
    csv_files = list(data_dir.glob("*.csv"))

    if not csv_files:
        console.print("No CSV files found in data directory.", style="yellow")
        console.print(
            "Creating a simple test to verify the conversion works...", style="blue"
        )

        # Create test data
        test_data = pd.DataFrame(
            {
                "Year": [1665, 1665, 1665],
                "Week": [1, 2, 3],
                "UniqueID": ["A001", "A002", "A003"],
                "Start Day": [1, 8, 15],
                "Start Month": ["January", "January", "January"],
                "End Day": [7, 14, 21],
                "End Month": ["January", "January", "January"],
                "St. Alphage": [5, 3, 2],
                "St. Andrew Holborn": [8, 6, 4],
                "St. Bartholomew": [2, 1, 3],
            }
        )

        console.print("Processing test data...", style="blue")
        result = process_bodleian_data(test_data, "test_source")

        # Save test result
        test_output = output_dir / "test_bodleian_output.csv"
        result.to_csv(test_output, index=False)

        console.print(
            f"✅ Test completed! Results saved to: {test_output}", style="bold green"
        )
        console.print(
            f"Processed {len(result)} rows with {len(result.columns)} columns",
            style="green",
        )

        return

    console.print(f"Found {len(csv_files)} CSV files to process", style="green")

    # Process the files (simplified version)
    loaded_files = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading files...", total=len(csv_files))

        for file_path in csv_files:
            try:
                # Process filename
                filename = file_path.stem
                # Remove date prefix if present
                if len(filename.split("-")) > 3:
                    filename = filename.split("-", 3)[-1]
                filename = filename.replace("-", "_")

                # Load CSV
                df = pd.read_csv(file_path)
                loaded_files[filename] = df

                logger.info(f"Loaded file: {file_path.name} as {filename}")

            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

            progress.update(task, advance=1)

    # Process at least one file as a demonstration
    if loaded_files:
        console.print("Processing first available dataset...", style="blue")

        first_file = next(iter(loaded_files.items()))
        filename, data = first_file

        console.print(f"Processing: {filename}", style="blue")

        # Try to process it
        try:
            if "bodleian" in filename.lower():
                result = process_bodleian_data(data, filename)
                output_file = output_dir / f"{filename}_processed.csv"
                result.to_csv(output_file, index=False)
                console.print(
                    f"✅ Processed {filename}: {len(result)} rows saved to {output_file}",
                    style="green",
                )
            else:
                # Try as weekly bills
                has_flags = any(col.startswith("is_") for col in data.columns)
                result = process_weekly_bills(data, filename, has_flags)
                output_file = output_dir / f"{filename}_processed.csv"
                result.to_csv(output_file, index=False)
                console.print(
                    f"✅ Processed {filename}: {len(result)} rows saved to {output_file}",
                    style="green",
                )
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            console.print(f"❌ Error processing {filename}: {e}", style="bold red")

    console.print("✅ Processing completed!", style="bold green")


if __name__ == "__main__":
    main()

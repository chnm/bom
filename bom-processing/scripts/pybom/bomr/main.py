"""
Main script for processing Bills of Mortality data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Any
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .helpers import (
    process_bodleian_data,
    process_weekly_bills,
    process_general_bills,
    month_to_number,
    log_data_check,
    check_data_quality,
)
from .data_processing import (
    extract_aggregate_entries,
    derive_causes,
    add_death_definitions,
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
app = typer.Typer()


class BOMProcessor:
    """Main processor for Bills of Mortality data."""

    def __init__(
        self, data_dir: str = "../../../bom-data/data-csvs", output_dir: str = "data"
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.loaded_files = {}
        self.processed_causes = {}
        self.deaths_data_sources = []

    def load_csv_files(self) -> None:
        """Load all CSV files from the data directory."""
        console.print("Loading CSV files...", style="blue")

        csv_files = list(self.data_dir.glob("*.csv"))

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
                    # Remove date prefix (yyyy-mm-dd)
                    filename = (
                        filename.split("-", 3)[-1]
                        if len(filename.split("-")) > 3
                        else filename
                    )
                    # Replace dashes with underscores
                    filename = filename.replace("-", "_")

                    # Load CSV
                    df = pd.read_csv(file_path)
                    self.loaded_files[filename] = {
                        "data": df,
                        "original_filename": file_path.name,
                        "variable_name": filename,
                        "file_path": str(file_path),
                    }

                    logger.info(f"Loaded file: {file_path.name} as variable {filename}")

                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")

                progress.update(task, advance=1)

        logger.info(f"Loaded {len(self.loaded_files)} files total")

    def process_causes_data(self) -> None:
        """Process causes of death datasets."""
        console.print("Processing causes of death data...", style="blue")

        # Find causes datasets
        causes_datasets = [
            name for name in self.loaded_files.keys() if "causes" in name
        ]
        logger.info(
            f"Found {len(causes_datasets)} causes datasets: {', '.join(causes_datasets)}"
        )

        combined_processed_cause = None

        for dataset_name in causes_datasets:
            if dataset_name not in self.loaded_files:
                logger.warning(f"Variable {dataset_name} not found, skipping")
                continue

            dataset = self.loaded_files[dataset_name]["data"]

            # Handle Bodleian datasets
            if "bodleian" in dataset_name.lower():
                source_name = dataset_name.replace("_weeklybills_causes", "").lower()
                logger.info(
                    f"Processing Bodleian dataset: {dataset_name} as {source_name}"
                )

                try:
                    processed_cause = self.process_bodleian_causes(dataset, source_name)
                except Exception as e:
                    logger.error(
                        f"Error processing Bodleian dataset {source_name}: {e}"
                    )
                    continue

            # Handle other datasets (Wellcome, Laxton, etc.)
            else:
                if "wellcome" in dataset_name.lower():
                    source_name = "wellcome"
                    skip_cols = 5
                    pivot_range = (8, 109)
                    n_descriptive_cols = 4
                elif "laxton_1700" in dataset_name.lower():
                    source_name = "laxton_1700"
                    skip_cols = 4
                    pivot_range = (8, 125)
                    n_descriptive_cols = 7
                elif "laxton" in dataset_name.lower():
                    source_name = "laxton_pre1700"
                    skip_cols = 4
                    pivot_range = (8, 125)
                    n_descriptive_cols = 7
                else:
                    logger.warning(f"Unknown dataset pattern: {dataset_name}, skipping")
                    continue

                # Process standard causes data
                processed_cause = self.process_standard_causes(
                    dataset, source_name, skip_cols, pivot_range
                )

            # Store and combine results
            if processed_cause is not None and not processed_cause.empty:
                if "source" not in processed_cause.columns:
                    processed_cause["source"] = source_name

                self.processed_causes[dataset_name] = processed_cause

                if combined_processed_cause is None:
                    combined_processed_cause = processed_cause
                else:
                    combined_processed_cause = pd.concat(
                        [combined_processed_cause, processed_cause], ignore_index=True
                    )

                logger.info(
                    f"Successfully processed {dataset_name} ({len(processed_cause)} rows)"
                )

        # Organize by source name
        for dataset_name, data in self.processed_causes.items():
            if "wellcome" in dataset_name:
                source_name = "wellcome"
            elif "laxton_1700" in dataset_name:
                source_name = "laxton"
            elif "laxton" in dataset_name:
                source_name = "laxton"
            elif "bodleian" in dataset_name:
                source_name = "bodleian"
            else:
                source_name = "unknown"

            self.deaths_data_sources.append({"data": data, "name": source_name})

    def process_deaths_pipeline(self) -> pd.DataFrame:
        """Process the deaths pipeline to create consolidated deaths data."""
        console.print("Processing deaths pipeline...", style="blue")
        
        if not self.deaths_data_sources:
            logger.warning("No deaths data sources available")
            return pd.DataFrame()
        
        # Derive causes from all sources
        deaths_long = derive_causes(self.deaths_data_sources)
        
        # Add death definitions
        deaths_with_definitions = add_death_definitions(deaths_long, "dictionary.csv")
        
        return deaths_with_definitions
    
    def process_aggregate_entries(self, weekly_bills: pd.DataFrame, general_bills: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Process aggregate entries from weekly and general bills."""
        console.print("Processing aggregate entries...", style="blue")
        
        aggregate_results = {}
        
        # Extract from weekly bills
        if not weekly_bills.empty:
            weekly_aggregates = extract_aggregate_entries(weekly_bills, "weekly_bills")
            for key, data in weekly_aggregates.items():
                if not data.empty:
                    data['bill_type'] = 'Weekly'
                    aggregate_results[key] = [data]
                else:
                    aggregate_results[key] = []
        
        # Extract from general bills
        if not general_bills.empty:
            general_aggregates = extract_aggregate_entries(general_bills, "general_bills")
            for key, data in general_aggregates.items():
                if not data.empty:
                    data['bill_type'] = 'General'
                    if key in aggregate_results:
                        aggregate_results[key].append(data)
                    else:
                        aggregate_results[key] = [data]
        
        # Combine and clean up each type
        final_results = {}
        for key, data_list in aggregate_results.items():
            if data_list:
                combined = pd.concat(data_list, ignore_index=True)
                
                # Filter out invalid years
                if 'year' in combined.columns:
                    combined['year'] = pd.to_numeric(combined['year'], errors='coerce')
                    combined = combined[
                        combined['year'].notna() & 
                        (combined['year'] >= 1500) & 
                        (combined['year'] <= 1800)
                    ]
                
                # Remove DataScribe metadata columns from aggregate files
                datascribe_cols = [col for col in combined.columns if 
                                 col.startswith('omeka_') or col.startswith('datascribe_') or 
                                 col.startswith('Omeka') or col.startswith('DataScribe')]
                if datascribe_cols:
                    combined = combined.drop(columns=datascribe_cols)
                
                final_results[key] = combined
            else:
                final_results[key] = pd.DataFrame()
        
        return final_results

    def process_bodleian_causes(
        self, data: pd.DataFrame, source_name: str
    ) -> pd.DataFrame:
        """Process Bodleian causes data with specialized handling."""
        logger.info(f"Processing {source_name} with specialized Bodleian handler...")

        # Identify death columns (exclude metadata, flags, and descriptive text)
        exclude_patterns = [
            "is_missing",
            "is_illegible",
            "Omeka",
            "DataScribe",
            "\\(Descriptive Text\\)",
            "Year",
            "Week",
            "Unique",
            "Start",
            "End",
        ]

        death_cols = []
        for col in data.columns:
            if not any(pattern in col for pattern in exclude_patterns):
                death_cols.append(col)

        descriptive_cols = [col for col in data.columns if "(Descriptive Text)" in col]

        logger.info(
            f"Found {len(death_cols)} death columns and {len(descriptive_cols)} descriptive text columns"
        )

        # Required metadata columns
        metadata_cols = [
            "Year",
            "Week Number",
            "Unique Identifier",
            "Start Day",
            "Start Month",
            "End Day",
            "End Month",
        ]

        # Find actual column names (case-insensitive)
        actual_metadata_cols = {}
        for required_col in metadata_cols:
            found = False
            for col in data.columns:
                if col.lower() == required_col.lower():
                    actual_metadata_cols[required_col] = col
                    found = True
                    break
            if not found:
                # Try fuzzy matching
                for col in data.columns:
                    if required_col.lower().replace(" ", "") in col.lower().replace(
                        " ", ""
                    ):
                        actual_metadata_cols[required_col] = col
                        found = True
                        break
            if not found:
                raise ValueError(f"Required metadata column not found: {required_col}")

        # Process each death column
        result_list = []

        for death_col in death_cols:
            try:
                # Skip special columns
                if any(
                    skip in death_col
                    for skip in [
                        "Christened",
                        "Buried",
                        "Plague Deaths",
                        "Increase/Decrease",
                        "Parishes",
                        "Total",
                    ]
                ):
                    continue

                # Get metadata + death column
                cols_to_select = list(actual_metadata_cols.values()) + [death_col]
                single_death = data[cols_to_select].copy()

                # Rename columns to standard names
                single_death = single_death.rename(columns=actual_metadata_cols)
                single_death = single_death.rename(columns={death_col: "count"})

                # Add descriptive text if available
                desc_col = f"{death_col} (Descriptive Text)"
                if desc_col in data.columns:
                    single_death["descriptive_text"] = data[desc_col].astype(str)
                else:
                    single_death["descriptive_text"] = pd.NA

                # Add death name and source
                single_death["death"] = death_col
                single_death["source"] = source_name
                single_death["count"] = pd.to_numeric(
                    single_death["count"], errors="coerce"
                )

                result_list.append(single_death)

            except Exception as e:
                logger.error(f"Error processing death cause {death_col}: {e}")

        if not result_list:
            raise ValueError("Failed to process any death causes")

        # Combine results
        combined_result = pd.concat(result_list, ignore_index=True)

        # Standardize column names
        combined_result.columns = [
            col.lower().replace(" ", "_") for col in combined_result.columns
        ]

        # Create joinid
        combined_result["start_month_num"] = combined_result["start_month"].apply(
            lambda x: self.month_to_number(x) if pd.notna(x) else "00"
        )
        combined_result["end_month_num"] = combined_result["end_month"].apply(
            lambda x: self.month_to_number(x) if pd.notna(x) else "00"
        )

        combined_result["joinid"] = (
            combined_result["year"].astype(str)
            + combined_result["start_month_num"]
            + combined_result["start_day"].astype(str).str.zfill(2)
            + combined_result["year"].astype(str)
            + combined_result["end_month_num"]
            + combined_result["end_day"].astype(str).str.zfill(2)
        )

        # Clean up
        combined_result = combined_result.drop(
            columns=["start_month_num", "end_month_num"]
        )

        logger.info(f"Finished processing {source_name} - {len(combined_result)} rows")

        return combined_result

    def process_standard_causes(
        self, data: pd.DataFrame, source_name: str, skip_cols: int, pivot_range: tuple
    ) -> pd.DataFrame:
        """Process standard (non-Bodleian) causes data."""
        logger.info(f"Processing {source_name} causes of death...")

        # Get columns to pivot
        pivot_cols = data.columns[pivot_range[0] : pivot_range[1]]

        # Get metadata columns
        metadata_cols = data.columns[skip_cols : skip_cols + 7]

        # Convert pivot columns to string and pivot
        for col in pivot_cols:
            data[col] = data[col].astype(str)

        result = data.melt(
            id_vars=metadata_cols,
            value_vars=pivot_cols,
            var_name="death",
            value_name="count",
        )

        # Clean and standardize
        result = result.assign(
            death=lambda x: x["death"].str.strip(),
            count=lambda x: pd.to_numeric(x["count"], errors="coerce"),
        )

        # Standardize column names
        result.columns = [col.lower().replace(" ", "_") for col in result.columns]

        return result

    def month_to_number(self, month_name: str) -> str:
        """Convert month name to padded number."""
        months = {
            "January": "01",
            "February": "02",
            "March": "03",
            "April": "04",
            "May": "05",
            "June": "06",
            "July": "07",
            "August": "08",
            "September": "09",
            "October": "10",
            "November": "11",
            "December": "12",
        }
        return months.get(str(month_name), "00")

    def process_weekly_bills_data(self) -> pd.DataFrame:
        """Process all weekly bills data."""
        console.print("Processing weekly bills data...", style="blue")

        weekly_dataframes = []

        # Process different sources
        sources_config = [
            ("1669_1670_Wellcome_weeklybills_parishes", "Wellcome", False),
            ("Laxton_old_weeklybills_parishes", "Laxton", True),
            ("Laxton_new_weekly_parishes", "Laxton", True),
            ("Laxton_weeklybills_parishes", "Laxton", True),
            ("HEH1635_weeklybills_parishes", "HEH", True),
        ]

        for dataset_name, source_name, has_flags in sources_config:
            if dataset_name in self.loaded_files:
                data = self.loaded_files[dataset_name]["data"]
                processed = process_weekly_bills(data, source_name, has_flags)
                weekly_dataframes.append(processed)

        # Process Bodleian versions
        bodleian_datasets = [
            "BodleianV1_weeklybills_parishes",
            "BodleianV2_weeklybills_parishes",
            "BodleianV3_weeklybills_parishes",
            "BLV1_weeklybills_parishes",
            "BLV2_weeklybills_parishes",
            "BLV3_weeklybills_parishes",
            "BLV4_weeklybills_parishes_missingbillsdataset",
            "BLV4_weeklybills_parishes_originaldataset",
            "BL1877_e_7_V1PostFire_minus3foldbill",
            "BLV1_1673_1674_weeklybills_parishes",
        ]

        bodleian_results = []
        for dataset_name in bodleian_datasets:
            if dataset_name in self.loaded_files:
                data = self.loaded_files[dataset_name]["data"]
                # Convert numeric columns to string
                for col in data.select_dtypes(include=[np.number]).columns:
                    data[col] = data[col].astype(str)

                processed = process_bodleian_data(data, dataset_name)
                bodleian_results.append(processed)

        if bodleian_results:
            bodleian_combined = pd.concat(bodleian_results, ignore_index=True)
            # Standardize column names
            bodleian_combined.columns = [
                col.lower().replace(" ", "_") for col in bodleian_combined.columns
            ]
            bodleian_combined = bodleian_combined.rename(
                columns={"uniqueid": "unique_identifier"}
            )
            weekly_dataframes.append(bodleian_combined)

        # Combine all weekly data
        if weekly_dataframes:
            weekly_bills = pd.concat(weekly_dataframes, ignore_index=True)

            # Standardize types
            numeric_cols = ["week", "year", "start_day", "end_day"]
            for col in numeric_cols:
                if col in weekly_bills.columns:
                    weekly_bills[col] = pd.to_numeric(
                        weekly_bills[col], errors="coerce"
                    )

            weekly_bills["count"] = pd.to_numeric(
                weekly_bills["count"], errors="coerce"
            )
            weekly_bills["bill_type"] = "Weekly"

            # Tidy parish data
            weekly_bills = tidy_parish_data(weekly_bills)
            
            # Standardize parish names 
            weekly_bills["parish_name"] = weekly_bills["parish_name"].str.replace("Allhallows", "Alhallows")

            return weekly_bills

        return pd.DataFrame()

    def process_general_bills_data(self) -> pd.DataFrame:
        """Process general bills data."""
        console.print("Processing general bills data...", style="blue")
        
        general_dataframes = []
        
        # Process general bills sources
        general_sources = [
            ("millar_generalbills_postplague_parishes", "millar post-plague"),
            ("millar_generalbills_preplague_parishes", "millar pre-plague")
        ]
        
        for dataset_name, source_name in general_sources:
            if dataset_name in self.loaded_files:
                data = self.loaded_files[dataset_name]["data"]
                processed = process_general_bills(data, source_name)
                general_dataframes.append(processed)
        
        # Combine all general data
        if general_dataframes:
            general_bills = pd.concat(general_dataframes, ignore_index=True)
            
            # Standardize types
            numeric_cols = ["week", "year", "start_day", "end_day"]
            for col in numeric_cols:
                if col in general_bills.columns:
                    general_bills[col] = pd.to_numeric(general_bills[col], errors="coerce")
            
            general_bills["count"] = pd.to_numeric(general_bills["count"], errors="coerce")
            
            # Standardize parish names 
            general_bills["parish_name"] = general_bills["parish_name"].str.replace("Allhallows", "Alhallows")
            
            return general_bills
        
        return pd.DataFrame()

    def create_all_bills(self, weekly_bills: pd.DataFrame, general_bills: pd.DataFrame) -> pd.DataFrame:
        """Create combined all_bills DataFrame with proper joinid."""
        console.print("Creating combined all_bills data...", style="blue")
        
        all_dataframes = []
        
        # Standardize weekly bills - add missing year columns
        if not weekly_bills.empty:
            weekly_standardized = weekly_bills.copy()
            # Add start_year and end_year columns from the year column
            if 'year' in weekly_standardized.columns:
                weekly_standardized['start_year'] = weekly_standardized['year']
                weekly_standardized['end_year'] = weekly_standardized['year']
            all_dataframes.append(weekly_standardized)
        
        if not general_bills.empty:
            all_dataframes.append(general_bills)
        
        if not all_dataframes:
            return pd.DataFrame()
        
        # Combine all bills
        all_bills = pd.concat(all_dataframes, ignore_index=True)
        
        # Create joinid for all bills (similar to R script)
        required_cols = ['start_month', 'end_month', 'start_day', 'end_day', 'year']
        if all(col in all_bills.columns for col in required_cols):
            # Clean data before processing
            all_bills = all_bills.dropna(subset=['start_month', 'end_month', 'start_day', 'end_day', 'year'])
            
            all_bills['start_month_num'] = all_bills['start_month'].apply(
                lambda x: month_to_number(str(x)) if pd.notna(x) else '00'
            )
            all_bills['end_month_num'] = all_bills['end_month'].apply(
                lambda x: month_to_number(str(x)) if pd.notna(x) else '00'
            )
            
            # Ensure numeric columns are properly converted
            all_bills['start_day'] = pd.to_numeric(all_bills['start_day'], errors='coerce')
            all_bills['end_day'] = pd.to_numeric(all_bills['end_day'], errors='coerce')
            all_bills['year'] = pd.to_numeric(all_bills['year'], errors='coerce')
            
            # Remove rows with invalid data
            all_bills = all_bills.dropna(subset=['start_day', 'end_day', 'year'])
            
            all_bills['start_day_pad'] = all_bills['start_day'].astype(int).astype(str).str.zfill(2)
            all_bills['end_day_pad'] = all_bills['end_day'].astype(int).astype(str).str.zfill(2)
            
            # Create joinid in format yyyymmddyyyymmdd
            all_bills['joinid'] = (
                all_bills['year'].astype(int).astype(str) + 
                all_bills['start_month_num'] + 
                all_bills['start_day_pad'] + 
                all_bills['year'].astype(int).astype(str) + 
                all_bills['end_month_num'] + 
                all_bills['end_day_pad']
            )
            
            # Clean up temporary columns
            all_bills = all_bills.drop(columns=['start_month_num', 'end_month_num', 'start_day_pad', 'end_day_pad'])
        
        return all_bills

    def save_results(self, weekly_bills: pd.DataFrame, general_bills: pd.DataFrame) -> None:
        """Save all processed data to CSV files."""
        console.print("Saving results...", style="blue")

        # Process deaths pipeline
        deaths_long = self.process_deaths_pipeline()
        if not deaths_long.empty:
            deaths_long.to_csv(self.output_dir / "causes_of_death.csv", index=False)

        # Process aggregate entries
        aggregate_data = self.process_aggregate_entries(weekly_bills, general_bills)
        
        # Save aggregate data files
        for key, data in aggregate_data.items():
            if not data.empty:
                filename = f"{key}_by_parish.csv"
                data.to_csv(self.output_dir / filename, index=False)
                logger.info(f"Saved {filename} with {len(data)} rows")

        # Save weekly bills (remove DataScribe metadata)
        if not weekly_bills.empty:
            weekly_bills_clean = weekly_bills.copy()
            datascribe_cols = [col for col in weekly_bills_clean.columns if 
                             col.startswith('omeka_') or col.startswith('datascribe_') or 
                             col.startswith('Omeka') or col.startswith('DataScribe')]
            if datascribe_cols:
                weekly_bills_clean = weekly_bills_clean.drop(columns=datascribe_cols)
            weekly_bills_clean.to_csv(self.output_dir / "bills_weekly.csv", index=False)

        # Save general bills
        if not general_bills.empty:
            general_bills.to_csv(self.output_dir / "bills_general.csv", index=False)

        # Save causes data
        if self.processed_causes:
            for name, data in self.processed_causes.items():
                filename = f"{name}_causes.csv"
                data.to_csv(self.output_dir / filename, index=False)

        # Process unique deaths from all sources
        if self.processed_causes:
            deaths_unique_list = []
            for name, data in self.processed_causes.items():
                if 'death' in data.columns:
                    unique_deaths = data[['death']].drop_duplicates().assign(source=name)
                    deaths_unique_list.append(unique_deaths)
            
            if deaths_unique_list:
                # Combine all unique deaths
                all_unique_deaths = pd.concat(deaths_unique_list, ignore_index=True)
                deaths_unique = all_unique_deaths.groupby('death').first().reset_index()
                deaths_unique = deaths_unique.sort_values('death').reset_index(drop=True)
                deaths_unique['death_id'] = range(1, len(deaths_unique) + 1)
                deaths_unique.to_csv(self.output_dir / "deaths_unique.csv", index=False)

        # Create and save all_bills
        all_bills = self.create_all_bills(weekly_bills, general_bills)
        if not all_bills.empty:
            # Process unique entities from all_bills
            parishes_unique = process_unique_parishes(all_bills)
            parishes_unique.to_csv(self.output_dir / "parishes_unique.csv", index=False)

            # Add parish IDs to all_bills
            all_bills_with_ids = all_bills.merge(
                parishes_unique[['parish_name', 'parish_id']], 
                on='parish_name', 
                how='left'
            )

            # Unique weeks
            week_sources = [{"data": all_bills, "name": "all_bills"}]
            week_unique = process_unique_weeks(week_sources)
            if not week_unique.empty:
                week_unique.to_csv(self.output_dir / "week_unique.csv", index=False)

                # Unique years
                year_unique = process_unique_years(week_unique)
                year_unique.to_csv(self.output_dir / "year_unique.csv", index=False)

                # Associate week IDs with all_bills
                all_bills_final = associate_week_ids(all_bills_with_ids, week_unique)
                
                # Select only the columns that match the original R script structure
                final_columns = [
                    "unique_identifier", "parish_name", "count_type", "count", 
                    "missing", "illegible", "source", "bill_type", 
                    "start_year", "end_year", "joinid", "parish_id", "year", "split_year"
                ]
                
                # Filter to only include columns that exist in the data
                existing_columns = [col for col in final_columns if col in all_bills_final.columns]
                all_bills_clean = all_bills_final[existing_columns]
                
                # Convert year columns to integers to remove decimal places
                for col in ['start_year', 'end_year', 'year']:
                    if col in all_bills_clean.columns:
                        all_bills_clean[col] = all_bills_clean[col].fillna(0).astype(int)
                
                # Convert boolean columns to lowercase for PostgreSQL compatibility
                for col in ['missing', 'illegible']:
                    if col in all_bills_clean.columns:
                        all_bills_clean[col] = all_bills_clean[col].astype(str).str.lower()
                
                # Save final all_bills
                all_bills_clean.to_csv(self.output_dir / "all_bills.csv", index=False)

        logger.info("All results saved successfully")


@app.command()
def main(data_dir: str = "../../../bom-data/data-csvs", output_dir: str = "data"):
    """Process Bills of Mortality data from CSV exports."""

    console.print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Bills of Mortality Data Processor", style="bold blue")
    console.print("Python conversion of R scripts for Death by Numbers project\n")

    processor = BOMProcessor(data_dir, output_dir)

    try:
        # Load data
        processor.load_csv_files()

        # Process causes
        processor.process_causes_data()

        # Process weekly bills
        weekly_bills = processor.process_weekly_bills_data()

        # Process general bills
        general_bills = processor.process_general_bills_data()

        # Save results
        processor.save_results(weekly_bills, general_bills)

        console.print("✅ Processing completed successfully!", style="bold green")

    except Exception as e:
        console.print(f"❌ Error during processing: {e}", style="bold red")
        logger.error(f"Processing failed: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

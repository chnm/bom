# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates CSV files of long tables for the
# parishes and types of death as well as extracting burials, christenings, and
# plague numbers from the transcriptions.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2025-07-30

library(tidyverse)
source("helpers.R")

# ----------------------------------------------------------------------
# Data sources
# Each of these are separate DataScribe exports that we are preparing for
# the PostgreSQL database.
# ----------------------------------------------------------------------
## The following reads each CSV file in our directory and creates a ew variable 
## for each one based on its filename. Then, use tidyverse::read_csv to read the
## CSV file and assign it to a variable.

# Get all the CSV files in the data directory
# Create a data structure to track loaded files
loaded_files <- list()
files <- list.files("../../../bom-data/data-csvs", pattern = "*.csv", full.names = TRUE)

# Loop through the files and assign them to a variable based on the csv filename
for (file in files) {
  tryCatch({
    # Get the filename without the path
    filename <- basename(file)
    # Remove the .csv extension
    filename <- str_remove(filename, ".csv")
    # Remove the prepended date string yyyy-mm-dd from the filename
    filename <- str_remove(filename, "^[0-9]{4}-[0-9]{2}-[0-9]{2}-")
    # Replace any dashes with underscores
    filename <- gsub("-", "_", filename)
    # Read the CSV file, normalize column names, and assign it to a variable
    assign(filename, normalize_column_names(read_csv(file)))
    # Store information about the loaded file
    loaded_files[[filename]] <- list(
      original_filename = basename(file),
      variable_name = filename,
      file_path = file
    )
    message(sprintf("Loaded file: %s as variable %s", basename(file), filename))
  }, error = function(e) {
    warning(sprintf("Failed to load %s: %s", file, e$message))
  })
}

# Print summary of loaded files
message(sprintf("Loaded %d files total", length(loaded_files)))

# ----------------------------------------------------------------------
# Lookup tables and causes of death data
# We need to do several lookups and cross-references throughout our data
# preparation. To make this script a bit more readable, we're going to 
# prepare these lookup tables here.
#
# The following identifies the causes of death data as well as generating
# lookup tables that we need for connecting various parts of data together.
# ----------------------------------------------------------------------

# Causes of Death
causes_datasets <- names(loaded_files)[grep("causes", names(loaded_files))]
message(sprintf("Found %d causes of death datasets: %s", 
                length(causes_datasets),
                paste(causes_datasets, collapse=", ")))

# Process each causes dataset
processed_causes <- list()
combined_processed_cause <- NULL

for (dataset_name in causes_datasets) {
  # Skip if variable doesn't exist
  if (!exists(dataset_name)) {
    cat(sprintf("Variable %s not found, skipping\n", dataset_name))
    next
  }
  
  # Get the data
  dataset_processing <- get(dataset_name)
  
  # Handle Bodleian datasets
  if (grepl("bodleian", dataset_name, ignore.case = TRUE)) {
    source_name <- str_replace(dataset_name, "_weeklybills_causes", "")
    source_name <- tolower(source_name)
    
    cat(sprintf("Processing Bodleian dataset: %s as %s\n", dataset_name, source_name))
    processed_cause <- tryCatch({
      process_bodleian_causes(dataset_processing, source_name)
    }, error = function(e) {
      cat(sprintf("Error processing Bodleian dataset %s: %s\n", source_name, e$message))
      return(NULL)
    })
  } 
  # Handle non-Bodleian datasets
  else {
    if (grepl("wellcome", dataset_name, ignore.case = TRUE)) {
      source_name <- "wellcome"
      skip_cols <- 5
      pivot_range <- c(8, 109)
      n_descriptive_cols <- 4
    } else if (grepl("laxton_1700", dataset_name, ignore.case = TRUE)) {
      source_name <- "laxton_1700"
      skip_cols <- 4
      pivot_range <- c(12, 125) 
      n_descriptive_cols <- 7
    } else if (grepl("laxton", dataset_name, ignore.case = TRUE)) {
      source_name <- "laxton_pre1700"
      skip_cols <- 4  # Skip same as other datasets to preserve unique_identifier
      pivot_range <- c(8, 70)  # After removing is_missing/is_illegible columns, causes start much earlier
      n_descriptive_cols <- 7
    } else {
      cat(sprintf("Unknown dataset pattern: %s, skipping\n", dataset_name))
      next
    }
    
    # Create lookup table and process
    lookup_table <- create_lookup_table(dataset_processing, source_name, n_descriptive_cols)
    processed_cause <- process_causes_of_death(dataset_processing, source_name, lookup_table, skip_cols, pivot_range)
  }
  
  # Combine processed causes
  if (!is.null(processed_cause)) {
    # Add source column if it doesn't exist
    if (!"source" %in% names(processed_cause)) {
      processed_cause$source <- source_name
    }
    
    # Store the individual dataset
    processed_causes[[dataset_name]] <- processed_cause
    
    # Combine for the overall dataset
    if (is.null(combined_processed_cause)) {
      combined_processed_cause <- processed_cause
    } else {
      # Standardize types before combining to avoid type mismatch errors
      combined_processed_cause <- combined_processed_cause |>
        mutate(across(contains("increase/decrease"), ~as.character(.)))
      processed_cause <- processed_cause |>
        mutate(across(contains("increase/decrease"), ~as.character(.)))
      
      # Ensure column order is consistent
      combined_processed_cause <- bind_rows(combined_processed_cause, processed_cause)
    }
    
    cat(sprintf("Successfully processed %s (%d rows)\n", 
                dataset_name, nrow(processed_cause)))
  }
}

# After processing,organize by source name for later use
deaths_data_sources <- list()
for (dataset_name in names(processed_causes)) {
  source_name <- if (grepl("wellcome", dataset_name)) "wellcome"
  else if (grepl("laxton_1700", dataset_name)) "laxton"
  else if (grepl("laxton", dataset_name)) "laxton"
  else if (grepl("bodleian", dataset_name)) "bodleian"
  else "unknown"
  
  deaths_data_sources[[length(deaths_data_sources) + 1]] <- list(
    data = processed_causes[[dataset_name]],
    name = source_name
  )
}
deaths_long <- derive_causes(deaths_data_sources)
deaths_long <- add_death_definitions(deaths_long, "dictionary.csv")

# Process unique deaths from all sources
deaths_unique_list <- lapply(names(processed_causes), function(name) {
  process_unique_deaths(processed_causes[[name]], name)
})

# Initialize with the first dataset
deaths_unique <- deaths_unique_list[[1]]

# Join with remaining datasets
if (length(deaths_unique_list) > 1) {
  for (i in 2:length(deaths_unique_list)) {
    deaths_unique <- deaths_unique |>
      left_join(deaths_unique_list[[i]])
  }
}

# Add death IDs
deaths_unique <- deaths_unique |>
  arrange(death) |>
  mutate(death_id = row_number())

# ----------------------------------------------------------------------
# Weekly Bills - Dynamic Processing
# ----------------------------------------------------------------------
# Find and process parish datasets dynamically
parish_datasets <- names(loaded_files)[grep("parishes", names(loaded_files))]
message(sprintf("Found %d parish datasets: %s", 
                length(parish_datasets),
                paste(parish_datasets, collapse=", ")))

# Process each parish dataset
processed_weekly <- list()
for (dataset_name in parish_datasets) {
  # Skip if variable doesn't exist
  if (!exists(dataset_name)) {
    cat(sprintf("Variable %s not found, skipping\n", dataset_name))
    next
  }
  
  # Get the data
  dataset_processing <- get(dataset_name)
  
  # Determine source name and flags based on filename pattern
  if (grepl("wellcome", dataset_name, ignore.case = TRUE)) {
    source_name <- "Wellcome"
    has_flags <- FALSE
  } else if (grepl("laxton", dataset_name, ignore.case = TRUE)) {
    source_name <- "Laxton"
    has_flags <- TRUE
  } else if (grepl("heh", dataset_name, ignore.case = TRUE)) {
    source_name <- "HEH"
    has_flags <- TRUE
  } else if (grepl("millar", dataset_name, ignore.case = TRUE)) {
    # Skip millar datasets - they're processed separately as general bills
    next
  } else {
    source_name <- str_extract(dataset_name, "^[^_]+")
    has_flags <- TRUE  # Default assumption
  }
  
  cat(sprintf("Processing parish dataset: %s as %s\n", dataset_name, source_name))
  processed_parish <- tryCatch({
    process_weekly_bills(dataset_processing, source_name, has_flags)
  }, error = function(e) {
    cat(sprintf("Error processing parish dataset %s: %s\n", dataset_name, e$message))
    return(NULL)
  })
  
  if (!is.null(processed_parish)) {
    processed_weekly[[dataset_name]] <- processed_parish
    cat(sprintf("Successfully processed %s (%d rows)\n", 
                dataset_name, nrow(processed_parish)))
  }
}

# Process Bodleian datasets dynamically
bodleian_datasets <- names(loaded_files)[grep("bodleian|blv|bl1877", names(loaded_files), ignore.case = TRUE)]
bodleian_versions <- list()

for (dataset_name in bodleian_datasets) {
  if (exists(dataset_name)) {
    # Extract version from dataset name
    version_name <- str_replace(dataset_name, "_weeklybills_parishes.*", "") |>
      str_replace_all("_", " ") |>
      str_to_title()
    
    bodleian_versions[[length(bodleian_versions) + 1]] <- list(
      data = get(dataset_name),
      version = version_name
    )
  }
}

# Process all versions and store in a single dataframe
bodleian_all_versions <- map(bodleian_versions, function(v) {
  cat("Processing dataset:", v$version, "with", ncol(v$data), "columns\n")
  
  # First convert all potential count columns to character
  data_with_char_counts <- v$data %>%
    mutate(across(where(is.numeric), ~as.character(.)))
  
  # Then process
  tryCatch({
    result <- process_bodleian_data(data_with_char_counts, v$version) %>%
      mutate(version = v$version)
    cat("Successfully processed", v$version, "\n")
    return(result)
  }, error = function(e) {
    cat("Error processing", v$version, ":", e$message, "\n")
    cat("Dataset columns:", paste(names(v$data)[1:min(10, ncol(v$data))], collapse = ", "), "\n")
    stop(e)
  })
}) %>% list_rbind()

# Fix column names
#bodleian_weekly <- bodleian_all_versions |>
#  rename_with(tolower) |>
#  rename_with(~str_replace_all(., " ", "_")) |>
#  rename(unique_identifier = uniqueid)
#rm(bodleian_all_versions)

# Combine dynamically processed weekly data
weekly_bills_list <- list()

# Add processed parish datasets
for (dataset_name in names(processed_weekly)) {
  if (!is.null(processed_weekly[[dataset_name]])) {
    # Debug: show available columns
    dataset <- processed_weekly[[dataset_name]]
    cat(sprintf("Dataset %s columns: %s\n", dataset_name, 
                paste(names(dataset)[1:min(10, ncol(dataset))], collapse = ", ")))
    
    # Check which columns exist before mutating (only warn about essential columns)
    essential_cols <- c("week", "year", "count")
    optional_cols <- c("start_day", "end_day")
    
    missing_essential <- setdiff(essential_cols, names(dataset))
    if (length(missing_essential) > 0) {
      cat(sprintf("ERROR: Dataset %s missing essential columns: %s\n", 
                  dataset_name, paste(missing_essential, collapse = ", ")))
    }
    
    # Only convert columns that exist
    converted_dataset <- dataset
    if ("week" %in% names(dataset)) converted_dataset <- converted_dataset |> mutate(week = as.numeric(week))
    if ("year" %in% names(dataset)) converted_dataset <- converted_dataset |> mutate(year = as.numeric(year))
    if ("start_day" %in% names(dataset)) converted_dataset <- converted_dataset |> mutate(start_day = as.numeric(start_day))
    if ("end_day" %in% names(dataset)) converted_dataset <- converted_dataset |> mutate(end_day = as.numeric(end_day))
    if ("count" %in% names(dataset)) converted_dataset <- converted_dataset |> mutate(count = as.character(count))
    
    weekly_bills_list[[dataset_name]] <- converted_dataset
  }
}

# Add Bodleian data if it exists
if (exists("bodleian_all_versions")) {
  cat(sprintf("Bodleian data columns: %s\n", 
              paste(names(bodleian_all_versions)[1:min(10, ncol(bodleian_all_versions))], collapse = ", ")))
  
  # Only convert columns that exist in Bodleian data
  bodleian_converted <- bodleian_all_versions
  if ("week" %in% names(bodleian_all_versions)) bodleian_converted <- bodleian_converted |> mutate(week = as.numeric(week))
  if ("year" %in% names(bodleian_all_versions)) bodleian_converted <- bodleian_converted |> mutate(year = as.numeric(year))
  if ("start_day" %in% names(bodleian_all_versions)) bodleian_converted <- bodleian_converted |> mutate(start_day = as.numeric(start_day))
  if ("end_day" %in% names(bodleian_all_versions)) bodleian_converted <- bodleian_converted |> mutate(end_day = as.numeric(end_day))
  if ("count" %in% names(bodleian_all_versions)) bodleian_converted <- bodleian_converted |> mutate(count = as.character(count))
  
  weekly_bills_list[["bodleian_weekly"]] <- bodleian_converted
}

# Combine all weekly data
weekly_bills <- bind_rows(weekly_bills_list) |> 
  mutate(
    bill_type = "Weekly",
    count = as.numeric(count)  # Convert back to numeric after binding
  )

# ----------------------------------------------------------------------
# General Bills
# ----------------------------------------------------------------------
# TODO Forthcoming: Laxton general bills
general_sources <- list(
  list(data = millar_generalbills_postplague_parishes, name = "millar post-plague"),
  list(data = millar_generalbills_preplague_parishes, name = "millar pre-plague")
)
combine_general_bills <- function(sources) {
  all_bills <- map_df(sources, function(source) {
    process_general_bills(source$data, source$name)
  })
  
  message(sprintf("\nCombined %d sources into %d total rows", 
                  length(sources), 
                  nrow(all_bills)))
  
  return(all_bills)
}
general_bills <- combine_general_bills(general_sources)
rm(combine_general_bills)

# Derive unique parishes from weekly bills -------------------------------------
## Find all unique values for parish name and join to authority file. These will be
## referenced as foreign keys in PostgreSQL.
# We extract "Christened in," "Buried in," and "Plague in" and other aggregate 
# records into their own dataframe and remove them from the overall weekly bills 
# data.
aggregate_entries_weekly <- extract_aggregate_entries(weekly_bills, "weekly_bills")
aggregate_entries_general <- extract_aggregate_entries(general_bills, "general_bills")

# Combine the special entries
all_christenings <- bind_rows(
  aggregate_entries_weekly$christenings |> mutate(bill_type = "Weekly", year = as.numeric(year)),
  aggregate_entries_general$christenings |> mutate(bill_type = "General", year = as.numeric(year))
)

# Check for years outside the valid historical range
out_of_range_years <- all_christenings |>
  filter(!is.na(year) & (year < 1500 | year > 1800)) |>
  select(year, unique_identifier) |>
  distinct()

if(nrow(out_of_range_years) > 0) {
  message(sprintf("Found %d records with years outside the 1500-1800 range:", 
                  nrow(out_of_range_years)))
  print(out_of_range_years)
}

all_christenings <- all_christenings |>
  filter(
    !is.na(year),
    nchar(as.character(year)) == 4,
    year >= 1500,
    year <= 1800
  ) |>
  mutate(
    year = year,
    start_month_num = month_to_number(start_month),
    end_month_num = month_to_number(end_month),
    start_day_pad = sprintf("%02d", start_day),
    end_day_pad = sprintf("%02d", end_day),
    # Create numeric joinid in format yyyymmddyyyymmdd
    joinid = paste0(
      year, start_month_num, start_day_pad,
      year, end_month_num, end_day_pad
    )
  ) |>
  select(-start_month_num, -end_month_num, -start_day_pad, -end_day_pad, -version)

all_plague <- bind_rows(
  aggregate_entries_weekly$plague |> mutate(bill_type = "Weekly", year = as.numeric(year)),
  aggregate_entries_general$plague |> mutate(bill_type = "General", year = as.numeric(year))
)

all_burials <- bind_rows(
  aggregate_entries_weekly$burials |> mutate(bill_type = "Weekly", year = as.numeric(year)),
  aggregate_entries_general$burials |> mutate(bill_type = "General", year = as.numeric(year))
)

all_parish_status <- bind_rows(
  aggregate_entries_weekly$parish_status |> mutate(bill_type = "Weekly", year = as.numeric(year)),
  aggregate_entries_general$parish_status |> mutate(bill_type = "General", year = as.numeric(year))
)

# Then, write this data
write_csv(all_christenings, "data/christenings_by_parish.csv", na = "")
write_csv(all_burials, "data/burials_by_parish.csv", na = "")
write_csv(all_plague, "data/plague_by_parish.csv", na = "")
write_csv(all_parish_status, "data/aggregate_totals_by_parish", na = "")

# Finally, tidy the weekly bills data.
weekly_bills <- weekly_bills |> tidy_parish_data()
weekly_bills <- weekly_bills |>
  mutate_at("parish_name", str_replace, "Allhallows", "Alhallows")
general_bills <- general_bills |>
  mutate_at("parish_name", str_replace, "Allhallows", "Alhallows")

all_bills <- bind_rows(
  weekly_bills |> 
    mutate(year = as.integer(year)),
  general_bills |> 
    mutate(year = as.integer(year))
)
# Create a unique joinid for all_bills to use with combining into the weeks data
all_bills <- all_bills |>
  mutate(start_month_num = month_to_number(start_month),
         end_month_num = month_to_number(end_month),
         start_day_pad = sprintf("%02d", start_day),
         end_day_pad = sprintf("%02d", end_day),
         # Create numeric joinid in format yyyymmddyyyymmdd
         joinid = paste0(
           year, start_month_num, start_day_pad,
           year, end_month_num, end_day_pad
  )) |>
  select(-start_month_num, -end_month_num, -start_day_pad, -end_day_pad)

parishes_unique <- process_unique_parishes(all_bills)
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")

# ----------------------------------------------------------------------
# Unique values with IDs
# ----------------------------------------------------------------------
weekly_data_sources <- list(
  list(data = weekly_bills, name = "weekly"),
  list(data = general_bills, name = "general"),
  list(data = processed_cause, name = "causes")
)
week_unique <- process_unique_weeks(weekly_data_sources)
rm(weekly_data_sources)

# Unique year values
year_unique <- process_unique_years(week_unique)

# Set parish ID values to all bills
# ------------------------------------------------------------------------------
# The following sets up the unique ID values in all_bills to their corresponding
# values for parishes, weeks, and years. This way we can use foreign keys when
# we ingest the data into PostgreSQL.

# Parish IDs
## Match unique parish IDs with the long parish tables, and drop the parish
## name from the long table. We'll use SQL foreign keys to keep the relationship
## by parish_id in all_bills and parishes_unique.
all_bills <- all_bills |>
  dplyr::left_join(parishes_unique |> select(parish_name, parish_id), 
            by = "parish_name")

# Week IDs
## Match unique week IDs to the long parish tables, and drop the existing
## start and end months and days from long_parish so they're only referenced
## through the unique week ID.
all_bills <- associate_week_ids(all_bills, week_unique)
all_bills <- all_bills |> select(-version)

# --------------------------------------------------
# Write data
# --------------------------------------------------
# Write data to csv: causes of death
write_csv(deaths_unique, "data/deaths_unique.csv", na = "")
write_csv(deaths_long, na = "", "data/causes_of_death.csv")

# Write data to csv: parishes and bills
write_csv(weekly_bills, "data/bills_weekly.csv", na = "")
write_csv(general_bills, "data/bills_general.csv", na = "")
write_csv(all_bills, "data/all_bills.csv", na = "")
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")
write_csv(week_unique, "data/week_unique.csv", na = "")
write_csv(year_unique, "data/year_unique.csv", na = "")

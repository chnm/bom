# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates CSV files of long tables for the
# parishes and types of death as well as extracting burials, christenings, and
# plague numbers from the transcriptions.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2025-02-27

library(tidyverse)
# ----------------------------------------------------------------------
# Functions
# 
# Logging function
log_data_check <- function(data, stage_name) {
  total_rows <- nrow(data)
  distinct_rows <- nrow(distinct(data))
  duplicates <- total_rows - distinct_rows
  
  # Get sample of duplicates if they exist
  if(duplicates > 0) {
    dupes <- data[duplicated(data) | duplicated(data, fromLast = TRUE), ]
    sample_dupes <- head(dupes, 10)  # Show first 10 duplicates
  } else {
    sample_dupes <- NULL
  }
  
  message(sprintf("\n=== Data Check: %s ===", stage_name))
  message(sprintf("Total rows: %d", total_rows))
  message(sprintf("Distinct rows: %d", distinct_rows))
  message(sprintf("Duplicate rows: %d", duplicates))
  
  if(!is.null(sample_dupes)) {
    message("\nSample of duplicated rows:")
    print(sample_dupes)
  }
  
  # Return TRUE if duplicates found
  return(duplicates > 0)
}

# Check data for whitespace
check_whitespace <- function(df) {
  cols_to_check <- c("parish_name", "count_type", "unique_identifier", 
                     "start_month", "end_month")
  
  for(col in cols_to_check) {
    if(col %in% names(df)) {
      # Check for leading/trailing whitespace
      whitespace_issues <- df |>
        filter(str_detect(!!sym(col), "^\\s|\\s$")) |>
        select(all_of(col))
      
      if(nrow(whitespace_issues) > 0) {
        message(sprintf("Found %d rows with whitespace issues in %s:", 
                        nrow(whitespace_issues), col))
        print(head(whitespace_issues, 5))
      }
    }
  }
}

# Process Bodleian exports
# Update the process_bodleian_data function to ensure consistent data types for all flags
process_bodleian_data <- function(data, source_name) {
  # Standardize column names (your existing code)
  data <- data |>
    rename_with(
      ~ case_when(
        . == "Unique ID" ~ "UniqueID",
        . == "Unique_ID" ~ "UniqueID",
        . == "unique_id" ~ "UniqueID",
        . == "End month" ~ "End Month",
        TRUE ~ .
      )
    )
  
  # Standardize column data types
  data <- data |>
    mutate(
      across(where(is.character), str_trim),
      Year = as.integer(Year),
      Week = as.integer(Week),
      `Start Day` = as.integer(`Start Day`),
      `End Day` = as.integer(`End Day`),
      `Start Month` = as.character(`Start Month`),
      `End Month` = as.character(`End Month`)
    )
  
  # Convert all illegible and missing flags to logical (TRUE/FALSE) before processing
  data <- data |>
    mutate(across(starts_with("is_illegible") | starts_with("is_missing"), 
                  ~ifelse(is.na(.), FALSE, as.logical(.))))
  
  # Process main data (parishes)
  main_data <- data |>
    select(-starts_with("is_")) |>
    select(!1:4) |>
    pivot_longer(
      cols = -(1:7),  # Exclude the first 7 columns (metadata)
      names_to = "parish_name",
      values_to = "count"
    )
  
  # Process illegible flags
  illegible_data <- data |>
    select(!1:4) |>
    select(Year, Week, UniqueID, 
           `Start Day`, `Start Month`, 
           `End Day`, `End Month`,
           starts_with("is_illegible")) |>
    pivot_longer(
      cols = starts_with("is_illegible"),
      names_to = "parish_name",
      values_to = "illegible"
    ) |>
    mutate(
      parish_name = str_remove(parish_name, "is_illegible_"),
      illegible = ifelse(is.na(illegible), FALSE, as.logical(illegible))  # Force logical type
    )
  
  # Process missing flags
  missing_data <- data |>
    select(!1:4) |>
    select(Year, Week, UniqueID, 
           `Start Day`, `Start Month`, 
           `End Day`, `End Month`,
           starts_with("is_missing")) |>
    pivot_longer(
      cols = starts_with("is_missing"),
      names_to = "parish_name",
      values_to = "missing"
    ) |>
    mutate(
      parish_name = str_remove(parish_name, "is_missing_"),
      missing = ifelse(is.na(missing), FALSE, as.logical(missing))  # Force logical type
    )
  
  # Join the data
  combined_data <- main_data |>
    left_join(illegible_data, 
              by = c("Year", "Week", "UniqueID", "Start Day", 
                     "Start Month", "End Day", "End Month", "parish_name")) |>
    left_join(missing_data,
              by = c("Year", "Week", "UniqueID", "Start Day", 
                     "Start Month", "End Day", "End Month", "parish_name")) |>
    mutate(source = source_name)
  
  message(sprintf("Processed Bodleian %s data: %d rows", 
                  source_name, nrow(combined_data)))
  
  return(combined_data)
}

# Process Wellcome and Laxton exports
process_weekly_bills <- function(data, source_name, has_flags = TRUE) {
  message(sprintf("Processing %s data...", source_name))
  
  if(has_flags) {
    # Process data with missing/illegible flags (Laxton)
    result <- process_flagged_data(data, source_name)
  } else {
    # Process data without flags (Wellcome)
    result <- process_unflagged_data(data, source_name)
  }
  
  # Standardize column names
  result <- result |>
    rename_with(tolower) |>
    rename_with(~str_replace_all(., " ", "_")) |>
    rename_with(
      ~ case_when(
        . == "Unique ID" ~ "unique_identifier",
        . == "Unique_ID" ~ "unique_identifier",
        . == "unique_id" ~ "unique_identifier",
        . == "End month" ~ "End Month",
        TRUE ~ .
      )
    )
  
  # Add source identifier
  result <- result |>
    mutate(source = source_name)
  
  return(result)
}

process_general_bills <- function(data, source_name) {
  message(sprintf("Processing general bills from %s...", source_name))
  
  # Check if this is a pre-plague format (with flags and burial/plague split)
  is_pre_plague <- any(str_detect(names(data), " - (Buried|Plague)$"))
  
  if(is_pre_plague) {
    message("Detected pre-plague format with burial/plague split")
    # Handle pre-plague format
    clean_data <- data |>
      select(!1:4) |>
      # Remove all is_missing and is_illegible columns
      select(-matches("is_(missing|illegible)")) |>
      select(
        `Start day`, `Start month`, `Start year`,
        `End day`, `End month`, `End year`,
        `Unique Identifier`,
        matches(" - (Buried|Plague)$")
      )
  } else {
    message("Detected post-plague format")
    # Handle post-plague format
    clean_data <- data |>
      select(!1:4)
  }
  
  # Get metadata columns
  metadata_cols <- c("Start day", "Start month", "Start year",
                     "End day", "End month", "End year",
                     "Unique Identifier")
  
  # For pre-plague data, we need to pivot twice
  if(is_pre_plague) {
    general_bills <- clean_data |>
      pivot_longer(
        cols = matches(" - (Buried|Plague)$"),
        names_to = c("parish_name", "count_type"),
        names_pattern = "(.+) - (Buried|Plague)$",
        values_to = "count"
      )
  } else {
    # Post-plague format just needs a simple pivot
    parish_cols <- setdiff(names(clean_data), metadata_cols)
    general_bills <- clean_data |>
      pivot_longer(
        cols = all_of(parish_cols),
        names_to = "parish_name",
        values_to = "count"
      ) |>
      mutate(count_type = "Total")
  }
  
  # Common processing for both formats
  general_bills <- general_bills |>
    mutate(
      week = 90,
      bill_type = "General",
      parish_name = str_trim(parish_name),
      source = source_name
    ) |>
    rename_with(tolower) |>
    rename_with(~gsub(" ", "_", .))
  
  # Extract year if needed
  if("unique_identifier" %in% names(general_bills)) {
    general_bills <- general_bills |>
      mutate(year = str_sub(unique_identifier, 8, 11))
  }
  
  # Report on processing
  message(sprintf("\nProcessed %d rows", nrow(general_bills)))
  message(sprintf("Distinct parishes: %d", n_distinct(general_bills$parish_name)))
  
  return(general_bills)
}

# Helper function for data quality checks
check_data_quality <- function(df) {
  # Check for NA values
  na_counts <- sapply(df, function(x) sum(is.na(x)))
  if(any(na_counts > 0)) {
    message("\nFound NA values:")
    print(na_counts[na_counts > 0])
  }
  
  # Check for suspicious parish names
  suspicious_parishes <- df |>
    select(parish_name) |>
    distinct() |>
    filter(
      str_detect(parish_name, "^\\s|\\s$") |  # Leading/trailing whitespace
        str_detect(parish_name, "Total|Sum|All") |  # Potential aggregate entries
        nchar(parish_name) < 3  # Very short names
    )
  
  if(nrow(suspicious_parishes) > 0) {
    message("\nSuspicious parish names found:")
    print(suspicious_parishes)
  }
  
  # Check for extreme count values
  count_summary <- summary(df$count)
  message("\nCount summary:")
  print(count_summary)
}

# Helper function for data with is_missing/is_illegible
process_flagged_data <- function(data, source_name) {
  # Extract illegible flags
  illegible_data <- data |>
    select(!1:4) |>
    select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) |>
    select(Year, Week, `Unique ID`, `Start Day`, `Start Month`, 
           `End Day`, `End month`, contains("is_illegible")) |>
    pivot_longer(
      cols = starts_with("is_illegible"),
      names_to = "parish_name",
      values_to = "illegible"
    ) |>
    mutate(illegible = ifelse(is.na(illegible), FALSE, TRUE))
  
  # Extract missing flags
  missing_data <- data |>
    select(!1:4) |>
    select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) |>
    select(Year, Week, `Unique ID`, `Start Day`, `Start Month`, 
           `End Day`, `End month`, contains("is_missing")) |>
    pivot_longer(
      cols = starts_with("is_missing"),
      names_to = "parish_name",
      values_to = "missing"
    ) |>
    mutate(missing = ifelse(is.na(missing), FALSE, TRUE))
  
  # Process main data
  main_data <- data |>
    select(-starts_with("is_")) |>
    select(!1:4) |>
    pivot_longer(
      cols = -c(1:7),
      names_to = "parish_name",
      values_to = "count"
    )
  
  # Combine using left_join instead of bind_rows
  combined_data <- main_data |>
    left_join(missing_data, 
              by = c("Year", "Week", "Unique ID", "Start Day", 
                     "Start Month", "End Day", "End month", "parish_name")) |>
    left_join(illegible_data,
              by = c("Year", "Week", "Unique ID", "Start Day", 
                     "Start Month", "End Day", "End month", "parish_name"))
  
  return(combined_data)
}

# Helper function for data without is_missing/is_illegible
process_unflagged_data <- function(data, source_name) {
  result <- data |>
    select(!1:4) |>
    pivot_longer(
      cols = -c(1:7),
      names_to = "parish_name",
      values_to = "count"
    ) |>
    mutate(
      missing = FALSE,
      illegible = FALSE
    )
  
  return(result)
}

# Extract data on buried/plague/totals/status/counts.
extract_aggregate_entries <- function(data, dataset_name) {
  message("Processing aggregate data (totals, parish status, and special counts)...")
  
  # Identify entries by their prefixes and exact matches
  entries_to_process <- data |>
    filter(
      str_detect(parish_name, "^(Christened|Buried|Plague) in") |
        str_detect(parish_name, "^Parishes (Infected|Clear)") |
        str_detect(parish_name, "^Total") |
        parish_name %in% c(
          "Parishes Infected",
          "Parishes Clear of the Plague",
          "Total Christenings",
          "Total of all Burials",
          "Total of all Plague"
        )
    )
  
  # Create detection function for reuse
  detect_entry_types <- function(df) {
    df |>
      mutate(
        christening_detect = str_detect(parish_name, "^(Christened in|Total Christenings)"),
        burials_detect = str_detect(parish_name, "^(Buried in|Total of all Burials)"),
        plague_detect = str_detect(parish_name, "^(Plague in|Total of all Plague)"),
        parish_status_detect = str_detect(parish_name, "^Parishes (Infected|Clear)")
      )
  }
  
  # Add detection columns
  entries_with_types <- entries_to_process |>
    detect_entry_types()
  
  # Extract each type
  results <- list(
    christenings = entries_with_types |>
      filter(christening_detect) |>
      select(-ends_with("_detect")) |>
      mutate(joinid = paste0(start_day, start_month, end_day, end_month, year)),
    
    burials = entries_with_types |>
      filter(burials_detect) |>
      select(-ends_with("_detect")),
    
    plague = entries_with_types |>
      filter(plague_detect) |>
      select(-ends_with("_detect")),
    
    parish_status = entries_with_types |>
      filter(parish_status_detect) |>
      select(-ends_with("_detect"))
  )
  
  # Log summary statistics
  message(sprintf("Found %d christening entries", nrow(results$christenings)))
  message(sprintf("Found %d burial entries", nrow(results$burials)))
  message(sprintf("Found %d plague entries", nrow(results$plague)))
  message(sprintf("Found %d parish status entries", nrow(results$parish_status)))
  
  # Create filtered dataset without these special entries
  filtered_data <- data |>
    anti_join(entries_with_types |> 
                filter(christening_detect | burials_detect | 
                         plague_detect | parish_status_detect),
              by = names(data))
  
  message(sprintf("Removed %d special entries from main dataset", 
                  nrow(data) - nrow(filtered_data)))
  
  # Add final check
  final_check <- filtered_data |>
    filter(
      str_detect(parish_name, "^(Christened|Buried|Plague) in|^Total|^Parishes (Infected|Clear)")
    )
  
  if(nrow(final_check) > 0) {
    warning("\nSome entries may have been missed:")
    print(final_check |> 
            select(parish_name) |> 
            distinct())
  }
  
  # Update weekly_bills in parent environment
  assign(dataset_name, filtered_data, envir = parent.frame())
  
  return(results)
}

process_unique_parishes <- function(data, authority_file_path = "data/London Parish Authority File.csv") {
  message("Processing unique parishes...")
  
  # Get initial count before processing
  initial_count <- n_distinct(data$parish_name)
  
  # Process parish names
  parishes_unique <- data |>
    ungroup() |>
    select(parish_name) |>
    mutate(parish_name = str_trim(parish_name)) |>
    filter(!is.na(parish_name), parish_name != "") |>
    distinct() |>
    arrange(parish_name)
  
  # Load and process authority file
  message("Loading parish authority file...")
  parish_canonical <- read_csv(authority_file_path) |>
    select(`Canonical DBN Name`, `Omeka Parish Name`) |>
    mutate(
      canonical_name = `Canonical DBN Name`, 
      parish_name = `Omeka Parish Name`
    ) |>
    select(canonical_name, parish_name)
  
  # Join and process
  parishes_unique <- parishes_unique |>
    left_join(parish_canonical, by = "parish_name") |>
    mutate(
      canonical = coalesce(canonical_name, parish_name)
    ) |>
    select(-canonical_name) |>
    mutate(canonical_name = canonical) |>
    select(-canonical) |>
    mutate(parish_id = row_number())
  
  # Report on the processing
  message(sprintf("Initial distinct parishes: %d", initial_count))
  message(sprintf("Final distinct parishes: %d", nrow(parishes_unique)))
  
  # Check for potential issues
  potential_issues <- parishes_unique |>
    filter(
      str_detect(parish_name, "\\d") |  # Contains numbers
        str_detect(parish_name, "^\\s|\\s$") |  # Has leading/trailing whitespace
        nchar(parish_name) < 3  # Very short names might be suspicious
    )
  
  if(nrow(potential_issues) > 0) {
    message("\nPotential issues found in parish names:")
    print(potential_issues)
  }
  
  # Check for parishes without canonical names
  missing_canonical <- parishes_unique |>
    filter(parish_name != canonical_name)
  
  if(nrow(missing_canonical) > 0) {
    message("\nParishes without matching canonical names:")
    print(missing_canonical)
  }
  
  return(parishes_unique)
}

# Helper function for creating unique IDs for weeks
month_to_number <- function(month_name) {
  month_numbers <- setNames(
    sprintf("%02d", 1:12),
    c("January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December")
  )
  return(month_numbers[month_name])
}

process_unique_weeks <- function(data_sources) {
  message("Processing unique weeks from all sources...")
  
  process_source_weeks <- function(data, source_name) {
    message(sprintf("Processing weeks from %s...", source_name))
    
    # Standardize column names first
    week_data <- data |>
      rename_with(~ifelse(. == "week", "week_number", .)) |>
      select(
        year,
        week_number,
        start_day,
        end_day,
        start_month,
        end_month,
        unique_identifier
      ) |>
      mutate(
        # Standardize types
        year = as.integer(year),
        week_number = as.numeric(week_number),
        
        # Create padded week number
        week_tmp = str_pad(week_number, 2, pad = "0"),
        
        # Create week_id
        week_id = ifelse(
          week_number > 15,
          paste0(year - 1, "-", year, "-", week_tmp),
          paste0(year, "-", year + 1, "-", week_tmp)
        ),
        
        # Create year range and join ID
        year_range = str_sub(week_id, 1, 9),
        start_month_num = month_to_number(start_month),
        end_month_num = month_to_number(end_month),
        start_day_pad = sprintf("%02d", start_day),
        end_day_pad = sprintf("%02d", end_day),
        # Create numeric joinid in format yyyymmddyyyymmdd
        joinid = paste0(
          year, start_month_num, start_day_pad,
          year, end_month_num, end_day_pad
        ),
        
        # Calculate split year
        split_year = ifelse(
          week_number > 15,
          paste0(year - 1, "/", year),
          paste0(year)
        )
      ) |>
      select(-week_tmp, -start_month_num, -end_month_num, -start_day_pad, -end_day_pad)
    
    # Special handling for Laxton data
    if(str_detect(source_name, "laxton")) {
      week_data <- week_data |>
        mutate(
          week_id = ifelse(
            is.na(week_id),
            str_replace(unique_identifier, "Laxton-", ""),
            week_id
          ),
          week_id = str_replace(week_id, "-verso", "")
        )
    }
    
    return(week_data)
  }
  
  # Process each source
  all_weeks <- map_df(data_sources, function(source) {
    process_source_weeks(source$data, source$name)
  })
  
  # Get unique weeks
  unique_weeks <- all_weeks |>
    distinct(joinid, .keep_all = TRUE)
  
  # Report on processing
  message(sprintf("\nProcessed %d total weeks", nrow(all_weeks)))
  message(sprintf("Found %d unique weeks", nrow(unique_weeks)))
  message(sprintf("Year range: %d - %d", 
                  min(unique_weeks$year), 
                  max(unique_weeks$year)))
  
  return(unique_weeks)
}

process_unique_years <- function(week_data) {
  message("Processing unique years from week data...")
  
  year_unique <- week_data |>
    ungroup() |>
    select(year) |>
    mutate(
      year = as.integer(year),
      year_id = year  # Keep original year as ID for easy reference
    ) |>
    filter(!is.na(year)) |>
    distinct() |>
    arrange(year) |>
    mutate(id = row_number())
  
  # Report on processing
  message(sprintf("Found %d unique years", nrow(year_unique)))
  message(sprintf("Year range: %d - %d", 
                  min(year_unique$year), 
                  max(year_unique$year)))
  
  # Check for any gaps in years
  year_gaps <- year_unique |>
    mutate(gap = year - lag(year)) |>
    filter(gap > 1) |>
    select(year, previous_year = year_id, gap)
  
  if(nrow(year_gaps) > 0) {
    message("\nFound gaps in year sequence:")
    print(year_gaps)
  }
  
  return(year_unique)
}

# Associate all_bills data with unique IDs so we can use foreign keys in Postgres
# to look up the week.
associate_week_ids <- function(bills_data, weeks_data) {
  message("Associating bills with week IDs...")
  
  # First, let's examine the join keys
  message("\nChecking join IDs:")
  message("Unique join IDs in bills: ", 
          n_distinct(bills_data$joinid))
  message("Unique join IDs in weeks: ", 
          n_distinct(weeks_data$joinid))
  
  # Check for duplicates in weeks_data
  duplicate_weeks <- weeks_data %>%
    group_by(joinid) %>%
    filter(n() > 1)
  
  if(nrow(duplicate_weeks) > 0) {
    message("\nFound duplicate weeks:")
    print(duplicate_weeks)
  }
  
  # Modified join process
  bills_with_weeks <- bills_data %>%
    select(-any_of(c("week", "start_day", "end_day", 
                     "start_month", "end_month", "year", "split_ye"))) %>%
    left_join(
      weeks_data %>% 
        distinct(joinid, .keep_all = TRUE) %>%  # Take first instance of each joinid
        select(joinid, year, split_year),
      by = "joinid"
    )
  
  message(sprintf("\nInitial rows: %d", nrow(bills_data)))
  message(sprintf("Final rows: %d", nrow(bills_with_weeks)))
  
  # Check for any missing joins
  missing_weeks <- bills_with_weeks %>%
    filter(is.na(year)) %>%
    select(joinid) %>%
    distinct()
  
  if(nrow(missing_weeks) > 0) {
    message("\nFound bills with missing week data:")
    print(missing_weeks)
  }
  
  return(bills_with_weeks)
}

# Create lookup tables
create_lookup_table <- function(data, source_name, n_descriptive_cols) {
  message(sprintf("Processing %s lookup table...", source_name))
  
  # Determine initial columns to skip based on source
  skip_cols <- if(source_name == "wellcome") 5 else 4
  
  result <- data |>
    select(!all_of(1:skip_cols)) |>
    select(
      contains("(Descriptive Text)"),
      `Unique Identifier`,
      `Start Day`,
      `Start Month`,
      `End Day`,
      `End Month`,
      Year
    ) |>
    pivot_longer(
      all_of(1:n_descriptive_cols), 
      names_to = "death_type", 
      values_to = "descriptive_text"
    ) |>
    mutate(
      # Clean up identifiers and death types
      across(where(is.character), str_trim),
      `Unique Identifier` = str_trim(`Unique Identifier`),
      death_type = str_remove(death_type, regex("\\(Descriptive Text\\)")),
      death_type = str_trim(death_type),
      # Create join ID
      join_id = paste0(
        `Start Day`,
        `Start Month`,
        `End Day`,
        `End Month`,
        Year, "-",
        death_type, "-",
        `Unique Identifier`
      )
    ) |>
    # Drop the columns we don't need anymore
    select(
      -`Start Day`,
      -`Start Month`,
      -`End Day`,
      -`End Month`,
      -Year,
      -`Unique Identifier`,
      death_type
    )
  
  return(result)
}

# Process causes of death data
process_causes_of_death <- function(data, source_name, lookup_table, skip_cols, pivot_range) {
  message(sprintf("Processing %s causes of death...", source_name))
  
  # Process main data
  result <- data |>
    select(!all_of(1:skip_cols)) |>
    select(!contains("(Descriptive")) |>
    # Convert all columns in pivot range to character before pivoting
    mutate(across(all_of(pivot_range[1]:pivot_range[2]), as.character)) |>
    pivot_longer(
      all_of(pivot_range[1]:pivot_range[2]), 
      names_to = "death", 
      values_to = "count"
    ) |>
    mutate(
      across(where(is.character), str_trim),
      death = str_trim(death),
      `Unique Identifier` = str_trim(`Unique Identifier`),
      join_id = paste0(
        `Start Day`, 
        `Start Month`, 
        `End Day`, 
        `End Month`, 
        Year, "-", 
        death, "-", 
        `Unique Identifier`
      )
    ) |>
    left_join(lookup_table, by = "join_id") |>
    select(-join_id, -death_type) |>
    rename_with(tolower) |>
    rename_with(~gsub(" ", "_", .))
  
  # Convert count back to numeric after pivoting
  result <- result |>
    mutate(count = as.numeric(count))
  
  return(result)
}

derive_causes <- function(data_sources) {
  # Validate input structure
  if (!is.list(data_sources) || !all(sapply(data_sources, function(x) "data" %in% names(x)))) {
    stop("data_sources must be a list of lists, each containing 'data' element")
  }
  
  # Define patterns to exclude
  exclude_patterns <- c(
    "^Christened \\(",
    "^Buried \\(",
    "Plague Deaths$",
    "^Increase/Decrease",
    "Parishes (Clear|Infected)",
    "Ounces in"
  )
  exclude_regex <- paste(exclude_patterns, collapse = "|")
  
  # Process all sources
  processed_causes <- map_df(data_sources, function(source) {
    source$data %>%
      mutate(
        week_number = as.numeric(week_number),
        source_name = source$name %||% "Unknown"  # Use "Unknown" if name not provided
      )
  }) %>%
    # Filter out unwanted entries
    filter(!str_detect(death, regex(exclude_regex, ignore_case = TRUE))) %>%
    # Create standardized date components
    mutate(
      start_month_num = month_to_number(start_month),
      end_month_num = month_to_number(end_month),
      start_day_pad = sprintf("%02d", start_day),
      end_day_pad = sprintf("%02d", end_day),
      # Create numeric joinid in format yyyymmddyyyymmdd
      joinid = paste0(
        year, start_month_num, start_day_pad,
        year, end_month_num, end_day_pad
      )
    ) %>%
    # Select final columns
    select(death, count, year, joinid, descriptive_text, source_name)
  
  return(processed_causes)
}

# Function to process unique deaths
process_unique_deaths <- function(data, source_name) {
  message(sprintf("Processing %s unique deaths...", source_name))
  
  # Define exclusion patterns based on source
  exclusion_patterns <- list(
    wellcome = c(
      "\\bBuried ", "\\bChristened ", "\\bPlague Deaths",
      "\\bOunces in", "\\bIncrease/Decrease",
      "\\bParishes Clear", "\\bParishes Infected"
    ),
    laxton_1700 = c(
      "\\bBuried ", "\\bChristened ", "\\bIncrease/Decrease"
    ),
    laxton = c(
      "\\bChristened ", "\\bIncrease/Decrease"
    )
  )
  
  result <- data |>
    select(death) |>
    distinct()
  
  # Apply appropriate exclusion patterns
  patterns <- exclusion_patterns[[source_name]]
  for(pattern in patterns) {
    result <- result |>
      filter(!str_detect(death, regex(pattern, ignore_case = FALSE)))
  }
  
  return(result)
}

# Separate the "-" values into tidy data for parish name and count and type and
# clean up any whitespace issues
tidy_parish_data <- function(combined_data) {
  message("Tidying parish and count type data...")
  
  # Check for whitespace issues before cleaning
  message("\nChecking for whitespace issues before cleaning:")
  check_whitespace(combined_data)
  
  result <- combined_data |>
    separate(parish_name, c("parish_name", "count_type"), sep = "[-]", 
             fill = "right", extra = "merge") |>
    mutate(
      across(where(is.character), str_trim),  # Strip whitespace from all character columns
      count_type = coalesce(count_type, "Count")
    )
  
  # Verify whitespace was cleaned
  message("\nVerifying whitespace cleaning:")
  check_whitespace(result)
  
  message(sprintf("\nDistinct parishes: %d", n_distinct(result$parish_name)))
  message(sprintf("Distinct count types: %d", n_distinct(result$count_type)))
  
  return(result)
}
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Data sources
# Each of these are separate DataScribe exports that we are preparing for
# the PostgreSQL database.
# ----------------------------------------------------------------------
## The following reads each CSV file in our directory and creates a ew variable 
## for each one based on its filename. Then, use tidyverse::read_csv to read the
## CSV file and assign it to a variable.

# Get all the CSV files in the data directory
files <- list.files("../../../bom-data/data-csvs", pattern = "*.csv", full.names = TRUE)
# Loop through the files and assign them to a variable based on the csv filename
for (file in files) {
  tryCatch({
    # Get the filename without the path
    filename <- basename(file)
    # Remove the .csv extension
    filename <- str_remove(filename, ".csv")
    # Remove the prepended date string yyyy-mm-dd from the filename so it's not
    # included as part of the variable.
    filename <- str_remove(filename, "^[0-9]{4}-[0-9]{2}-[0-9]{2}-")
    # Replace any dashes with underscores
    filename <- gsub("-", "_", filename)
    # Read the CSV file and assign it to a variable
    assign(filename, read_csv(file))
  }, error = function(e) {
    warning(sprintf("Failed to load %s: %s", file, e$message))
  })
}

# ----------------------------------------------------------------------
# Lookup tables
# We need to do several lookups and cross-references throughout our data
# preparation. To make this script a bit more readable, we're going to 
# prepare these lookup tables here.
# ----------------------------------------------------------------------

lookup_wellcome <- create_lookup_table(
  Wellcome_weeklybills_causes, 
  "wellcome", 
  n_descriptive_cols = 4
)

lookup_laxton_1700 <- create_lookup_table(
  Laxton_1700_weeklybills_causes, 
  "laxton_1700", 
  n_descriptive_cols = 8
)

lookup_laxton <- create_lookup_table(
  Laxton_old_weeklybills_causes, 
  "laxton", 
  n_descriptive_cols = 8
)

# ----------------------------------------------------------------------
# Causes of Death
# ----------------------------------------------------------------------
causes_wellcome <- process_causes_of_death(
  Wellcome_weeklybills_causes,
  "wellcome",
  lookup_wellcome,
  skip_cols = 5,
  pivot_range = c(8, 109)
)

causes_laxton_1700 <- process_causes_of_death(
  Laxton_1700_weeklybills_causes,
  "laxton_1700",
  lookup_laxton_1700,
  skip_cols = 4,
  pivot_range = c(8, 125)
)

causes_laxton <- process_causes_of_death(
  Laxton_old_weeklybills_causes,
  "laxton_pre1700",
  lookup_laxton,
  skip_cols = 4,
  pivot_range = c(8, 125)
)

# Process all causes 
deaths_data_sources <- list(
  list(
    data = causes_wellcome,
    name = "Wellcome"
  ),
  list(
    data = causes_laxton,
    name = "Laxton"
  ),
  list(
    data = causes_laxton_1700,
    name = "Laxton 1700"
  )
)
deaths_long <- derive_causes(deaths_data_sources)

# Process unique deaths
deaths_unique_wellcome <- process_unique_deaths(causes_wellcome, "wellcome")
deaths_unique_laxton_1700 <- process_unique_deaths(causes_laxton_1700, "laxton_1700")
deaths_unique_laxton <- process_unique_deaths(causes_laxton, "laxton")

# Combine unique deaths
deaths_unique <- deaths_unique_wellcome |>
  left_join(deaths_unique_laxton) |>
  left_join(deaths_unique_laxton_1700) |>
  arrange(death) |>
  mutate(death_id = row_number())

# ----------------------------------------------------------------------
# Weekly Bills
# ----------------------------------------------------------------------
# Forthcoming: British Library (BL)
wellcome_weekly <- process_weekly_bills(`1669_1670_Wellcome_weeklybills_parishes`, 
                                      "Wellcome", 
                                      has_flags = FALSE)

laxton_weekly <- process_weekly_bills(Laxton_old_weeklybills_parishes, 
                                    "Laxton", 
                                    has_flags = TRUE)

# Bring together all Bodleian versions
bodleian_versions <- list(
  list(data = BodleianV1_weeklybills_parishes, version = "Bodleian V1"),
  list(data = BodleianV2_weeklybills_parishes, version = "Bodleian V2"),
  list(data = BodleianV3_weeklybills_parishes, version = "Bodleian V3")
)

# Process all versions and store in a single dataframe
bodleian_all_versions <- map_df(bodleian_versions, function(v) {
  # First convert all potential count columns to character
  data_with_char_counts <- v$data %>%
    mutate(across(where(is.numeric), as.character))
  
  # Then process
  process_bodleian_data(data_with_char_counts, v$version) %>%
    mutate(version = v$version)
})

# Fix column names
bodleian_weekly <- bodleian_all_versions |>
  rename_with(tolower) |>
  rename_with(~str_replace_all(., " ", "_")) |>
  rename(unique_identifier = uniqueid)
rm(bodleian_all_versions)

# Combine all weekly data into a single frame
# Combine all weekly data into a single frame with consistent data types
weekly_bills <- bind_rows(
  wellcome_weekly |> 
    mutate(
      week = as.numeric(week), 
      start_day = as.numeric(start_day), 
      end_day = as.numeric(end_day),
      count = as.character(count)  # Convert to character for binding
    ), 
  laxton_weekly |> 
    mutate(
      week = as.numeric(week), 
      start_day = as.numeric(start_day), 
      end_day = as.numeric(end_day),
      count = as.character(count)  # Convert to character for binding
    ), 
  bodleian_weekly |> 
    mutate(
      week = as.numeric(week), 
      start_day = as.numeric(start_day), 
      end_day = as.numeric(end_day),
      count = as.character(count)  # Convert to character for binding
    )
) |> 
  mutate(
    bill_type = "Weekly",
    count = as.numeric(count)  # Convert back to numeric after binding
  )

# ----------------------------------------------------------------------
# General Bills
# ----------------------------------------------------------------------
# Forthcoming: Laxton general bills
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
all_christenings <- all_christenings %>% 
  mutate(start_month_num = month_to_number(start_month),
         end_month_num = month_to_number(end_month),
         start_day_pad = sprintf("%02d", start_day),
         end_day_pad = sprintf("%02d", end_day),
         # Create numeric joinid in format yyyymmddyyyymmdd
         joinid = paste0(
           year, start_month_num, start_day_pad,
           year, end_month_num, end_day_pad
         )) %>% 
  select(-start_month_num, -end_month_num, -start_day_pad, -end_day_pad)

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

# Some last minute tidying:
# 1) Replace the alternate spelling of "Alhallows"
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
all_bills <- all_bills %>% 
  mutate(start_month_num = month_to_number(start_month),
         end_month_num = month_to_number(end_month),
         start_day_pad = sprintf("%02d", start_day),
         end_day_pad = sprintf("%02d", end_day),
         # Create numeric joinid in format yyyymmddyyyymmdd
         joinid = paste0(
           year, start_month_num, start_day_pad,
           year, end_month_num, end_day_pad
  )) %>% 
  select(-start_month_num, -end_month_num, -start_day_pad, -end_day_pad)

parishes_unique <- process_unique_parishes(all_bills)
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")

# ----------------------------------------------------------------------
# Unique values with IDs
# ----------------------------------------------------------------------
weekly_data_sources <- list(
  list(data = weekly_bills, name = "weekly"),
  list(data = general_bills, name = "general"),
  list(data = causes_wellcome, name = "wellcome"),
  list(data = causes_laxton, name = "laxton"),
  list(data = causes_laxton_1700, name = "laxton")
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

# --------------------------------------------------
# Write data
# --------------------------------------------------
# Write data to csv: causes of death
write_csv(causes_wellcome, "data/wellcome_causes.csv", na = "")
write_csv(causes_laxton, "data/laxton_causes.csv", na = "")
write_csv(causes_laxton_1700, "data/laxton_causes_1700.csv", na = "")
write_csv(deaths_unique, "data/deaths_unique.csv", na = "")
write_csv(deaths_long, na = "", "data/causes_of_death.csv")

# Write data to csv: parishes and bills
write_csv(weekly_bills, "data/bills_weekly.csv", na = "")
write_csv(general_bills, "data/bills_general.csv", na = "")
write_csv(all_bills, "data/all_bills.csv", na = "")
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")
write_csv(week_unique, "data/week_unique.csv", na = "")
write_csv(year_unique, "data/year_unique.csv", na = "")

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
  
  # Store original column names to preserve parish name case
  original_cols <- names(data)
  
  # Identify metadata columns (using case-insensitive matching)
  metadata_pattern <- "year|week|unique|start|end"
  metadata_cols <- grep(metadata_pattern, tolower(original_cols), value = TRUE)
  
  # Identify parish columns (everything that's not metadata or flags)
  flag_pattern <- "^is_(illegible|missing)"
  parish_cols <- original_cols[
    !grepl(metadata_pattern, tolower(original_cols)) & 
      !grepl(flag_pattern, tolower(original_cols))
  ]
  
  # Create a mapping from lowercase to original case for parish columns
  parish_mapping <- setNames(parish_cols, tolower(parish_cols))
  
  # Handle mixed data types for flag columns
  if(has_flags) {
    # Check for character flags and convert them to logical
    flag_cols <- grep(flag_pattern, names(data), value = TRUE)
    for(col in flag_cols) {
      if(is.character(data[[col]])) {
        data[[col]] <- as.logical(data[[col]])
      }
    }
  }
  
  # Standardize types for key columns
  data <- data |>
    mutate(across(c("Year", "Week"), as.character))
  
  if(has_flags) {
    # Process data with missing/illegible flags
    result <- process_flagged_data(data, source_name)
  } else {
    # Process data without flags
    result <- process_unflagged_data(data, source_name)
  }
  
  # Restore original parish name case after pivoting
  result <- result |>
    mutate(
      parish_name = case_when(
        tolower(parish_name) %in% names(parish_mapping) ~ parish_mapping[tolower(parish_name)],
        TRUE ~ parish_name
      )
    )
  
  # Standardize column names
  result <- result |>
    rename_with(tolower, -parish_name) |>  # Don't lowercase parish_name
    rename_with(~str_replace_all(., " ", "_")) |>
    rename_with(
      ~ case_when(
        . == "unique id" ~ "unique_identifier",
        . == "unique_id" ~ "unique_identifier",
        . == "end month" ~ "end_month",
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
  # Standardize column names first to avoid case sensitivity issues
  data <- data |>
    rename_with(tolower)
  
  data <- data |> mutate(year = as.character(year))
  
  # Extract illegible flags with consistent column names
  illegible_data <- data |>
    select(!1:4) |>
    select(year, week, unique_id = contains("unique"), 
           start_day = contains("start day"), 
           start_month = contains("start month"), 
           end_day = contains("end day"), 
           end_month = contains("end month"), 
           contains("is_illegible")) |>
    pivot_longer(
      cols = starts_with("is_illegible"),
      names_to = "parish_name",
      values_to = "illegible"
    ) |>
    mutate(
      parish_name = str_remove(parish_name, "is_illegible_"),
      illegible = ifelse(is.na(illegible), FALSE, as.logical(illegible))
    )
  
  # Extract missing flags with consistent column names
  missing_data <- data |>
    select(!1:4) |>
    select(year, week, unique_id = contains("unique"), 
           start_day = contains("start day"), 
           start_month = contains("start month"), 
           end_day = contains("end day"), 
           end_month = contains("end month"), 
           contains("is_missing")) |>
    pivot_longer(
      cols = starts_with("is_missing"),
      names_to = "parish_name",
      values_to = "missing"
    ) |>
    mutate(
      parish_name = str_remove(parish_name, "is_missing_"),
      missing = ifelse(is.na(missing), FALSE, as.logical(missing))
    )
  
  # Process main data with consistent column names
  main_data <- data |>
    select(-starts_with("is_")) |>
    select(!1:4) |>
    mutate(across(where(is.numeric), as.character)) |>
    pivot_longer(
      cols = -c(year, week, contains("unique"), 
                contains("start day"), contains("start month"), 
                contains("end day"), contains("end month")),
      names_to = "parish_name",
      values_to = "count"
    ) |>
    mutate(
      count = as.numeric(count),
      missing = FALSE,
      illegible = FALSE
    )
  
  # Get common join columns
  join_cols <- intersect(
    intersect(names(main_data), names(illegible_data)),
    names(missing_data)
  )
  join_cols <- setdiff(join_cols, c("missing", "illegible", "count"))
  
  message("Using join columns: ", paste(join_cols, collapse=", "))
  
  # Combine using left_join with explicit join columns
  combined_data <- main_data |>
    left_join(
      select(illegible_data, all_of(join_cols), illegible),
      by = join_cols,
      suffix = c("", ".illegible")
    ) |>
    left_join(
      select(missing_data, all_of(join_cols), missing),
      by = join_cols,
      suffix = c("", ".missing")
    ) |>
    mutate(
      illegible = coalesce(illegible, illegible.illegible, FALSE),
      missing = coalesce(missing, missing.missing, FALSE)
    ) |>
    select(-ends_with(".illegible"), -ends_with(".missing"))
  
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
        # Ensure numeric conversion first
        start_day = as.numeric(as.character(start_day)),
        end_day = as.numeric(as.character(end_day)),
        
        # Standardize types
        year = as.integer(year),
        week_number = as.character(week_number),
        
        # Pad days with leading zeros
        start_day_pad = sprintf("%02d", start_day),
        end_day_pad = sprintf("%02d", end_day),
        
        # Create week_id
        week_tmp = str_pad(week_number, 2, pad = "0"),
        week_id = ifelse(
          as.numeric(week_number) > 15,
          paste0(year - 1, "-", year, "-", week_tmp),
          paste0(year, "-", year + 1, "-", week_tmp)
        ),
        
        # Create year range and join ID
        year_range = str_sub(week_id, 1, 9),
        start_month_num = month_to_number(start_month),
        end_month_num = month_to_number(end_month),
        
        # Create numeric joinid in format yyyymmddyyyymmdd
        joinid = paste0(
          year, start_month_num, start_day_pad,
          year, end_month_num, end_day_pad
        ),
        
        # Calculate split year
        split_year = ifelse(
          as.numeric(week_number) > 15,
          paste0(year - 1, "/", year),
          paste0(year)
        )
      ) |>
      select(-week_tmp, -start_month_num, -end_month_num, -start_day_pad, -end_day_pad) |>
      drop_na(year)
    
    # Check for years that are not four digits
    non_standard_years <- week_data |> 
      filter(nchar(as.character(year)) != 4) |>
      select(year, unique_identifier) |>
      distinct()
    
    if(nrow(non_standard_years) > 0) {
      message(sprintf("Found %d records with non-standard years in source %s. These rows have been removed:", 
                      nrow(non_standard_years), source_name))
      print(non_standard_years)
      
      # Remove records with two-digit years
      week_data <- week_data |> 
        filter(nchar(as.character(year)) == 4)
    } 
     
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
  duplicate_weeks <- weeks_data |>
    group_by(joinid) |>
    filter(n() > 1)
  
  if(nrow(duplicate_weeks) > 0) {
    message("\nFound duplicate weeks:")
    print(duplicate_weeks)
  }
  
  # Modified join process
  bills_with_weeks <- bills_data |>
    select(-any_of(c("week", "start_day", "end_day", 
                     "start_month", "end_month", "year", "split_ye"))) |>
    left_join(
      weeks_data |> 
        distinct(joinid, .keep_all = TRUE) |>  # Take first instance of each joinid
        select(joinid, year, split_year),
      by = "joinid"
    )
  
  message(sprintf("\nInitial rows: %d", nrow(bills_data)))
  message(sprintf("Final rows: %d", nrow(bills_with_weeks)))
  
  # Check for any missing joins
  missing_weeks <- bills_with_weeks |>
    filter(is.na(year)) |>
    select(joinid) |>
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
  
  # First, identify the descriptive text columns that actually exist in the data
  descriptive_cols <- names(data)[grep("\\(Descriptive Text\\)", names(data))]
  
  # Safety check - make sure n_descriptive_cols is not greater than available columns
  n_descriptive_cols <- min(n_descriptive_cols, length(descriptive_cols))
  
  if (n_descriptive_cols == 0) {
    message("Warning: No descriptive text columns found for source ", source_name)
    # Return empty lookup table if no descriptive columns found
    return(data.frame(
      join_id = character(),
      death_type = character(),
      descriptive_text = character()
    ))
  }
  
  # Convert all descriptive text columns to character type to ensure consistency
  data_converted <- data |>
    mutate(across(all_of(descriptive_cols), as.character))
  
  # Extract metadata columns safely
  result <- tryCatch({
    data_converted |>
      select(!all_of(1:skip_cols)) |>
      select(
        all_of(descriptive_cols[1:n_descriptive_cols]),  # Only take existing columns
        `Unique Identifier`,
        `Start Day`, 
        `Start Month`,
        `End Day`,
        `End Month`,
        Year
      ) |>
      pivot_longer(
        all_of(descriptive_cols[1:n_descriptive_cols]), 
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
        join_id,
        death_type,
        descriptive_text
      )
  }, error = function(e) {
    message("Error processing lookup table: ", e$message)
    # Attempt to identify key columns
    key_cols <- c("Unique Identifier", "Start Day", "Start Month", "End Day", "End Month", "Year")
    available_cols <- intersect(key_cols, names(data_converted))
    
    if (length(available_cols) < 5) {
      message("Critical metadata columns missing. Creating minimal lookup table.")
      return(data.frame(
        join_id = character(),
        death_type = character(),
        descriptive_text = character()
      ))
    }
    
    # More flexible approach - try with available columns
    message("Attempting with available columns: ", paste(available_cols, collapse=", "))
    data_converted |>
      select(!all_of(1:skip_cols)) |>
      select(
        all_of(descriptive_cols[1:n_descriptive_cols]),
        all_of(available_cols)
      ) |>
      pivot_longer(
        all_of(descriptive_cols[1:n_descriptive_cols]), 
        names_to = "death_type", 
        values_to = "descriptive_text"
      ) |>
      mutate(
        death_type = str_remove(death_type, regex("\\(Descriptive Text\\)")),
        death_type = str_trim(death_type),
        join_id = paste0(
          if("Start Day" %in% available_cols) `Start Day` else "00",
          if("Start Month" %in% available_cols) `Start Month` else "Jan",
          if("End Day" %in% available_cols) `End Day` else "00",
          if("End Month" %in% available_cols) `End Month` else "Jan",
          if("Year" %in% available_cols) Year else "0000", "-",
          death_type, "-",
          if("Unique Identifier" %in% available_cols) `Unique Identifier` else "unknown"
        )
      ) |>
      select(join_id, death_type, descriptive_text)
  })
  
  return(result)
}

process_bodleian_causes <- function(data, source_name) {
  message(sprintf("Processing %s with specialized Bodleian handler...", source_name))
  
  # First, identify death columns and descriptive text columns
  all_cols <- names(data)
  death_cols <- all_cols[!grepl("is_missing|is_illegible|Omeka|DataScribe|\\(Descriptive Text\\)|Year|Week|Unique|Start|End", all_cols)]
  descriptive_cols <- all_cols[grepl("\\(Descriptive Text\\)", all_cols)]
  
  message(sprintf("Found %d death columns and %d descriptive text columns", 
                  length(death_cols), length(descriptive_cols)))
  
  # Create a mapping from death columns to descriptive text columns
  desc_mapping <- list()
  for (desc_col in descriptive_cols) {
    # Extract the base name by removing "(Descriptive Text)"
    base_name <- str_trim(gsub("\\(Descriptive Text\\)", "", desc_col))
    if (base_name %in% death_cols) {
      desc_mapping[[base_name]] <- desc_col
    }
  }
  
  # Check if required metadata columns exist
  metadata_cols <- c("Year", "Week Number", "Unique Identifier", 
                     "Start Day", "Start Month", "End Day", "End Month")
  
  # Find the metadata columns in the dataset
  metadata_cols_found <- sapply(metadata_cols, function(col) {
    if (col %in% names(data)) {
      return(col)
    } else if (tolower(col) %in% tolower(names(data))) {
      # Find the actual case of the column
      idx <- which(tolower(names(data)) == tolower(col))
      return(names(data)[idx[1]])
    } else if (gsub(" ", "_", tolower(col)) %in% tolower(names(data))) {
      # Try with underscore
      idx <- which(tolower(names(data)) == gsub(" ", "_", tolower(col)))
      return(names(data)[idx[1]])
    } else {
      # Try fuzzy matching
      pattern <- tolower(gsub("[^a-z]", "", col))
      matches <- grep(pattern, tolower(gsub("[^a-z]", "", names(data))), value = TRUE)
      if (length(matches) > 0) {
        idx <- which(tolower(gsub("[^a-z]", "", names(data))) == matches[1])
        return(names(data)[idx[1]])
      } else {
        return(NA_character_)
      }
    }
  })
  
  # Check for missing metadata columns
  missing_metadata <- is.na(metadata_cols_found)
  if (any(missing_metadata)) {
    stop(sprintf("Missing required metadata columns: %s", 
                 paste(metadata_cols[missing_metadata], collapse=", ")))
  }
  
  # Use the found column names
  metadata_cols <- metadata_cols_found
  
  # Process each death column individually to avoid pivot issues
  result_list <- list()
  
  for (death_col in death_cols) {
    tryCatch({
      # Skip if count column doesn't exist
      if (!death_col %in% names(data)) {
        message(sprintf("Skipping %s - column not found", death_col))
        next
      }
      
      # Skip special columns that might cause issues
      if (grepl("Christened|Buried|Plague Deaths|Increase/Decrease|Parishes|Total", death_col)) {
        message(sprintf("Skipping special column: %s", death_col))
        next
      }
      
      # Create a subset with just this death and metadata
      single_death <- data |>
        select(all_of(metadata_cols), all_of(death_col))
      
      # Add descriptive text if available
      if (death_col %in% names(desc_mapping)) {
        desc_col <- desc_mapping[[death_col]]
        single_death <- single_death |>
          select(all_of(metadata_cols), all_of(death_col), all_of(desc_col)) |>
          rename(count = !!death_col, 
                 descriptive_text = !!desc_col)
      } else {
        single_death <- single_death |>
          rename(count = !!death_col) |>
          mutate(descriptive_text = NA_character_)
      }
      
      # Ensure consistent data types
      single_death <- single_death |>
        mutate(
          count = as.character(count),  # Convert all counts to character first
          death = death_col,
          source = source_name
        )
      
      # Store in our list
      result_list[[death_col]] <- single_death
      
    }, error = function(e) {
      message(sprintf("Error processing death cause %s: %s", death_col, e$message))
    })
  }
  
  if (length(result_list) == 0) {
    stop("Failed to process any death causes")
  }
  
  message(sprintf("Successfully processed %d of %d death causes", 
                  length(result_list), length(death_cols)))
  
  # First, get all unique column names across all data frames
  all_columns <- unique(unlist(lapply(result_list, names)))
  
  # Then, ensure each data frame has all columns
  for (i in seq_along(result_list)) {
    missing_cols <- setdiff(all_columns, names(result_list[[i]]))
    if (length(missing_cols) > 0) {
      for (col in missing_cols) {
        result_list[[i]][[col]] <- NA
      }
    }
  }
  
  # Combine all results
  message("Combining individual results...")
  combined_result <- tryCatch({
    do.call(rbind, result_list)
  }, error = function(e) {
    message(sprintf("Error combining results: %s", e$message))
    
    # Try with bind_rows again
    tryCatch({
      bind_rows(result_list)
    }, error = function(e2) {
      message(sprintf("Second attempt failed: %s", e2$message))
      stop("Could not combine results after two attempts")
    })
  })
  
  # Standardize column names after combining
  combined_result <- combined_result |>
    rename_with(tolower) |>
    rename_with(~gsub(" ", "_", .))
  
  # Now create the joinid using standardized column names
  combined_result <- combined_result |>
    mutate(
      # Handle month conversion
      start_month_num = month_to_number(start_month),
      end_month_num = month_to_number(end_month),
      
      # Format day values
      start_day_pad = sprintf("%02d", as.numeric(as.character(start_day))),
      end_day_pad = sprintf("%02d", as.numeric(as.character(end_day))),
     
      # Create joinid
      joinid = paste0(
        year, start_month_num, start_day_pad,
        year, end_month_num, end_day_pad
      ),
      
      count = as.numeric(count),
      
      # Standardize all key columns to consistent types
      year = as.numeric(as.character(year)),
      start_day = as.character(as.numeric(start_day)),
      end_day = as.character(as.numeric(end_day)),
      week_number = as.character(week_number),
      
      # Ensure months are consistent
      start_month = as.character(start_month),
      end_month = as.character(end_month)
    ) |>
    # Remove temporary columns
    select(-start_month_num, -end_month_num, -start_day_pad, -end_day_pad)
  
  message(sprintf("Finished processing %s - %d rows, %d columns", 
                  source_name, nrow(combined_result), ncol(combined_result)))
  
  return(combined_result)
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
  
  # Standardize data types
  result <- result |>
    mutate(
      # Ensure consistent types
      week_number = as.character(week_number),
      count = as.numeric(count),
      year = as.numeric(year),
      
      # Convert day and month columns
      start_day = as.character(as.numeric(start_day)),
      end_day = as.character(as.numeric(end_day)),
      start_month = as.character(start_month),
      end_month = as.character(end_month)
    )
  
  return(result)
}

# Update the derive_causes function to handle type mismatches
derive_causes <- function(data_sources) {
  # Validate input structure
  if (!is.list(data_sources)) {
    stop("data_sources must be a list")
  }
  
  # First, collect all datasets and standardize column types
  all_datasets <- list()
  
  for (i in seq_along(data_sources)) {
    source <- data_sources[[i]]
    
    # Check if source has the expected structure
    if (is.list(source) && "data" %in% names(source) && "name" %in% names(source)) {
      # Original expected structure
      source_data <- source$data
      source_name <- source$name
    } else if (is.list(source) && length(source) >= 1) {
      # Alternative structure - first element is data, second might be name
      source_data <- source[[1]]
      source_name <- if (length(source) >= 2) source[[2]] else "Unknown"
    } else {
      # Fallback - assume source is the data itself
      source_data <- source
      source_name <- "Unknown"
    }
    
    # Ensure consistent column types
    if ("week_number" %in% names(source_data)) {
      source_data$week_number <- as.character(source_data$week_number)
    }
    
    if ("start_day" %in% names(source_data)) {
      source_data$start_day <- as.character(source_data$start_day)
    }
    
    if ("end_day" %in% names(source_data)) {
      source_data$end_day <- as.character(source_data$end_day)
    }
    
    if ("count" %in% names(source_data)) {
      source_data$count <- as.numeric(as.character(source_data$count))
    }
    
    # Add source name
    source_data$source_name <- source_name
    
    # Store the processed dataset
    all_datasets[[i]] <- source_data
  }
  
  # Combine all datasets
  combined_data <- bind_rows(all_datasets)
  
  # Filter out unwanted entries
  exclude_patterns <- c(
    "^Christened \\(",
    "^Buried \\(",
    "Plague Deaths$",
    "^Increase/Decrease",
    "Parishes (Clear|Infected)",
    "Ounces in",
    "Found Dead",
    "Found dead",
    "Description"
  )
  exclude_regex <- paste(exclude_patterns, collapse = "|")
  
  processed_data <- combined_data
  
  # Only apply the string detection filter if 'death' column exists
  if ("death" %in% names(combined_data)) {
    processed_data <- processed_data |>
      filter(!str_detect(death, regex(exclude_regex, ignore_case = TRUE)))
  }
  
  # Create standardized date components if needed
  processed_data <- processed_data |>
    mutate(
      # Only try to create joinid if it doesn't exist and we have the necessary columns
      joinid = if ("joinid" %in% names(processed_data)) 
        joinid 
      else if (all(c("year", "start_month", "end_month", "start_day", "end_day") %in% names(processed_data)))
        paste0(
          year, month_to_number(start_month), sprintf("%02d", as.numeric(start_day)),
          year, month_to_number(end_month), sprintf("%02d", as.numeric(end_day))
        )
      else
        NA_character_
    )
 
  # Select only columns that exist
  columns_to_select <- c("death", "count", "year", "joinid", "descriptive_text", "source_name")
  existing_columns <- intersect(columns_to_select, names(processed_data))
  
  return(processed_data |> select(all_of(existing_columns)))
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

# Function to merge death definitions with causes data
add_death_definitions <- function(deaths_data, dictionary_path = "dictionary.csv") {
  message("Adding death definitions from dictionary...")
  
  # Read the dictionary file
  dictionary <- read_csv(dictionary_path) %>%
    select(Cause, Definition, Source) %>%
    rename(
      death = Cause,
      definition = Definition,
      definition_source = Source
    ) %>%
    # Ensure clean matching by standardizing
    mutate(
      death = str_trim(death),
      death_lower = tolower(death)
    )
  
  message(sprintf("Loaded %d definitions from dictionary", nrow(dictionary)))
  
  # Create lowercase death column for matching
  deaths_with_lower <- deaths_data %>%
    mutate(death_lower = tolower(death))
  
  # Join with dictionary on lowercase death name for case-insensitive matching
  deaths_with_definitions <- deaths_with_lower %>%
    left_join(
      dictionary %>% select(death_lower, definition, definition_source),
      by = "death_lower"
    ) %>%
    select(-death_lower) # Remove the temporary column
  
  # Report on match results
  matched_count <- sum(!is.na(deaths_with_definitions$definition))
  total_count <- nrow(deaths_with_definitions)
  match_rate <- round(matched_count / total_count * 100, 2)
  
  message(sprintf("Matched definitions for %d of %d deaths (%.2f%%)", 
                  matched_count, total_count, match_rate))
  
  # List unmatched deaths (if any)
  if (matched_count < total_count) {
    unmatched <- deaths_with_definitions %>%
      filter(is.na(definition)) %>%
      select(death) %>%
      distinct() %>%
      arrange(death)
    
    message(sprintf("\nFound %d unique unmatched death causes:", nrow(unmatched)))
    if (nrow(unmatched) <= 20) {
      print(unmatched)
    } else {
      print(head(unmatched, 20))
      message("... and more")
    }
  }
  
  return(deaths_with_definitions)
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

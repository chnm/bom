# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates CSV files of long tables for the
# parishes and types of death as well as extracting burials, christenings, and
# plague numbers from the transcriptions.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2025-01-07

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

# Process Bodleian exports
process_bodleian_data <- function(data, source_name) {
  # Standardize column names
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
      Year = as.integer(Year),
      Week = as.integer(Week),
      `Start Day` = as.integer(`Start Day`),
      `End Day` = as.integer(`End Day`),
      `Start Month` = as.character(`Start Month`),
      `End Month` = as.character(`End Month`)
    )
  
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
      illegible = ifelse(is.na(illegible), FALSE, TRUE)
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
      missing = ifelse(is.na(missing), FALSE, TRUE)
    )
  
  # Join the data
  combined_data <- main_data |>
    left_join(illegible_data, 
              by = c("Year", "Week", "UniqueID", "Start Day", 
                     "Start Month", "End Day", "End Month", "parish_name")) |>
    left_join(missing_data,
              by = c("Year", "Week", "UniqueID", "Start Day", 
                     "Start Month", "End Day", "End Month", "parish_name"))
  
  combined_data <- combined_data %>%
    mutate(source = source_name)
  
  message(sprintf("Processed Bodleian V%d data: %d rows", 
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
  result <- result %>%
    rename_with(tolower) %>%
    rename_with(~str_replace_all(., " ", "_")) %>%
    rename_with(
      ~ case_when(
        . == "Unique ID" ~ "UniqueID",
        . == "Unique_ID" ~ "UniqueID",
        . == "unique_id" ~ "UniqueID",
        . == "End month" ~ "End Month",
        TRUE ~ .
      )
    )
  
  # Add source identifier
  result <- result %>%
    mutate(source = source_name)
  
  return(result)
}

# Helper function for data with is_missing/is_illegible
process_flagged_data <- function(data, source_name) {
  # Extract illegible flags
  illegible_data <- data %>%
    select(!1:4) %>%
    select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) %>%
    select(Year, Week, `Unique ID`, `Start Day`, `Start Month`, 
           `End Day`, `End month`, contains("is_illegible")) %>%
    pivot_longer(
      cols = starts_with("is_illegible"),
      names_to = "parish_name",
      values_to = "illegible"
    ) %>%
    mutate(illegible = ifelse(is.na(illegible), FALSE, TRUE))
  
  # Extract missing flags
  missing_data <- data %>%
    select(!1:4) %>%
    select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) %>%
    select(Year, Week, `Unique ID`, `Start Day`, `Start Month`, 
           `End Day`, `End month`, contains("is_missing")) %>%
    pivot_longer(
      cols = starts_with("is_missing"),
      names_to = "parish_name",
      values_to = "missing"
    ) %>%
    mutate(missing = ifelse(is.na(missing), FALSE, TRUE))
  
  # Process main data
  main_data <- data %>%
    select(-starts_with("is_")) %>%
    select(!1:4) %>%
    pivot_longer(
      cols = -c(1:7),
      names_to = "parish_name",
      values_to = "count"
    )
  
  # Combine using left_join instead of bind_rows
  combined_data <- main_data %>%
    left_join(missing_data, 
              by = c("Year", "Week", "Unique ID", "Start Day", 
                     "Start Month", "End Day", "End month", "parish_name")) %>%
    left_join(illegible_data,
              by = c("Year", "Week", "Unique ID", "Start Day", 
                     "Start Month", "End Day", "End month", "parish_name"))
  
  return(combined_data)
}

# Helper function for data without is_missing/is_illegible
process_unflagged_data <- function(data, source_name) {
  result <- data %>%
    select(!1:4) %>%
    pivot_longer(
      cols = -c(1:7),
      names_to = "parish_name",
      values_to = "count"
    ) %>%
    mutate(
      missing = FALSE,
      illegible = FALSE
    )
  
  return(result)
}

# Create lookup tables
create_lookup_table <- function(data, source_name, n_descriptive_cols) {
  message(sprintf("Processing %s lookup table...", source_name))
  
  # Determine initial columns to skip based on source
  skip_cols <- if(source_name == "wellcome") 5 else 4
  
  result <- data %>%
    select(!all_of(1:skip_cols)) %>%
    select(
      contains("(Descriptive Text)"),
      `Unique Identifier`,
      `Start Day`,
      `Start Month`,
      `End Day`,
      `End Month`,
      Year
    ) %>%
    pivot_longer(
      all_of(1:n_descriptive_cols), 
      names_to = "death_type", 
      values_to = "descriptive_text"
    ) %>%
    mutate(
      # Clean up identifiers and death types
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
    ) %>%
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

process_causes_of_death <- function(data, source_name, lookup_table, skip_cols, pivot_range) {
  message(sprintf("Processing %s causes of death...", source_name))
  
  # Special handling for Laxton pre-1700 data
  if(source_name == "laxton_pre1700") {
    data <- data %>% 
      mutate(across(all_of(pivot_range[1]:pivot_range[2]), as.character))
  }
  
  # Process main data
  result <- data %>%
    select(!all_of(1:skip_cols)) %>%
    select(!contains("(Descriptive")) %>%
    pivot_longer(
      all_of(pivot_range[1]:pivot_range[2]), 
      names_to = "death", 
      values_to = "count"
    ) %>%
    mutate(
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
    ) %>%
    left_join(lookup_table, by = "join_id") %>%
    select(-join_id, -death_type) %>%
    rename_with(tolower) %>%
    rename_with(~gsub(" ", "_", .))
  
  return(result)
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
  
  result <- data %>%
    select(death) %>%
    distinct()
  
  # Apply appropriate exclusion patterns
  patterns <- exclusion_patterns[[source_name]]
  for(pattern in patterns) {
    result <- result %>%
      filter(!str_detect(death, regex(pattern, ignore_case = FALSE)))
  }
  
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

# Process unique deaths
deaths_unique_wellcome <- process_unique_deaths(causes_wellcome, "wellcome")
deaths_unique_laxton_1700 <- process_unique_deaths(causes_laxton_1700, "laxton_1700")
deaths_unique_laxton <- process_unique_deaths(causes_laxton, "laxton")

# Combine unique deaths
deaths_unique <- deaths_unique_wellcome %>%
  left_join(deaths_unique_laxton) %>%
  left_join(deaths_unique_laxton_1700) %>%
  arrange(death) %>%
  mutate(death_id = row_number())

# ----------------------------------------------------------------------
# Weekly Bills
# ----------------------------------------------------------------------
wellcome_weekly <- process_weekly_bills(`1669_1670_Wellcome_weeklybills_parishes`, 
                                      "Wellcome", 
                                      has_flags = FALSE)

laxton_weekly <- process_weekly_bills(Laxton_old_weeklybills_parishes, 
                                    "Laxton", 
                                    has_flags = TRUE)

# Bring together all Bodleian versions
bodleian_versions <- list(
  list(data = BodleianV1_weeklybills_parishes, "Bodleian V1"),
  list(data = BodleianV2_weeklybills_parishes, "Bodleian V2"),
  list(data = BodleianV3_weeklybills_parishes, "Bodleian V3")
)

# Process all versions and store in a single dataframe
bodleian_all_versions <- map_df(bodleian_versions, function(v) {
  process_bodleian_data(v$data, v$version) |>
    mutate(version = v$version)
})

# Fix column names
bodleian_weekly <- bodleian_all_versions |>
  rename_with(tolower) |>
  rename_with(~str_replace_all(., " ", "_")) |>
  rename(unique_identifier = uniqueid)
rm(bodleian_all_versions)

# Combine all weekly data into a single frame
weekly_bills <- bind_rows(
  wellcome_weekly |> mutate(week = as.numeric(week), start_day = as.numeric(start_day), end_day = as.numeric(end_day)), 
  laxton_weekly |> mutate(week = as.numeric(week), start_day = as.numeric(start_day), end_day = as.numeric(end_day)), 
  bodleian_weekly |> mutate(week = as.numeric(week), start_day = as.numeric(start_day), end_day = as.numeric(end_day))
  ) |> mutate(bill_type = "Weekly")

# This sets up cleaning text that looks something like:
# "{Christened, Buried, Plague} in the 97 Parishes within the Walls"
# To clean this up, the following separate out a parish name from the count
# type (plague vs. burial). If there's no notation for plague or burial, we assume burial.
# Whitespace is removed with str_trim().
filtered_entries <- weekly_bills |>
  filter(!str_detect(parish_name, "-"))

# We want to clean up our distinct parish names by removing any mentions of
# christenings, burials, or plague. The following detects the presence of specific
# strings and simply assigns a bool. We then use those TRUE and FALSE values
# to filter the data and remove the matching TRUE statements.
filtered_entries$christening_detect <-
  str_detect(filtered_entries$parish_name, "Christened")
filtered_entries$burials_detect <-
  str_detect(filtered_entries$parish_name, "Buried in")
filtered_entries$plague_detect <-
  str_detect(filtered_entries$parish_name, "Plague in")

christenings_tmp <- filtered_entries |>
  dplyr::filter(christening_detect == TRUE) |>
  select(-christening_detect, -burials_detect, -plague_detect)
burials_tmp <- filtered_entries |>
  dplyr::filter(burials_detect == TRUE) |>
  select(-christening_detect, -burials_detect, -plague_detect)
plague_tmp <- filtered_entries |>
  dplyr::filter(plague_detect == TRUE) |>
  select(-christening_detect, -burials_detect, -plague_detect)

# We keep the christenings_tmp data since we want to keep track of christenings
# by parish.
christenings_tmp <- christenings_tmp  |> 
    mutate(joinid = paste0(start_day, start_month, end_day, end_month, year))
write_csv(christenings_tmp, "data/christenings_by_parish.csv", na = "")

filtered_entries <- filtered_entries |>
  dplyr::filter(
    christening_detect == FALSE,
    burials_detect == FALSE,
    plague_detect == FALSE
  )

filtered_entries <- filtered_entries |>
  select(-christening_detect, -burials_detect, -plague_detect)

# We do the same for the weekly bills.
weekly_bills$christening_detect <-
  str_detect(weekly_bills$parish_name, "Christened")
weekly_bills$burials_detect <-
  str_detect(weekly_bills$parish_name, "Buried in")
weekly_bills$plague_detect <-
  str_detect(weekly_bills$parish_name, "Plague in")

christenings_tmp <- weekly_bills |>
  dplyr::filter(christening_detect == TRUE) |>
  select(-christening_detect, -burials_detect, -plague_detect)
burials_tmp <- weekly_bills |>
  dplyr::filter(burials_detect == TRUE) |>
  select(-christening_detect, -burials_detect, -plague_detect)
plague_tmp <- weekly_bills |>
  dplyr::filter(plague_detect == TRUE) |>
  select(-christening_detect, -burials_detect, -plague_detect)

weekly_bills <- weekly_bills |>
  dplyr::filter(
    christening_detect == FALSE,
    burials_detect == FALSE,
    plague_detect == FALSE
  )

weekly_bills <- weekly_bills |>
  select(-christening_detect, -burials_detect, -plague_detect)

# Remove the temp files
rm(christenings_tmp, burials_tmp, plague_tmp)

# Add count type for the filtered entries
filtered_entries <- filtered_entries |>
  mutate(count_type = "Buried")

# Separate the '- Count' and '- Parish' values into tidy format.
weekly_bills <- weekly_bills |>
  separate(parish_name, c("parish_name", "count_type"), sep = "[-]")

weekly_bills <- weekly_bills |>
  mutate(count_type = str_trim(count_type)) |>
  mutate(parish_name = str_trim(parish_name))

filtered_entries <- filtered_entries |>
  mutate(count_type = str_trim(count_type)) |>
  mutate(parish_name = str_trim(parish_name))

# Remove the missing data from weekly bills before we add the corrected
# information back in.
weekly_bills <- weekly_bills |>
  filter(!weekly_bills$parish_name %in% filtered_entries$parish_name)

# Combine our dataframes and remove filtered_entries since we no longer need it.
weekly_bills <- rbind(weekly_bills, filtered_entries)
rm(filtered_entries)

# Replace the alternate spelling of "Alhallows"
weekly_bills <- weekly_bills |>
  mutate_at("parish_name", str_replace, "Allhallows", "Alhallows")

# Check for duplicates
if(log_data_check(weekly_bills, "After combining weekly bills")) {
  # If duplicates found, check which source they came from
  weekly_bills <- weekly_bills |>
    group_by(unique_identifier, parish_name, year) |>
    filter(n() > 1) |>
    arrange(unique_identifier, parish_name, year)
  
  message("\nDetailed duplicate analysis in weekly bills:")
  print(weekly_bills)
}

# Find all unique values for parish name, week, and year. These will be
# referenced as foreign keys in PostgreSQL.
parishes_unique <- weekly_bills |>
  ungroup() |>
  select(parish_name) |>
  distinct() |>
  arrange(parish_name) |>
  mutate(parish_name = str_trim(parish_name))

# ----------------------------------------------------------------------
# General Bills
# ----------------------------------------------------------------------

millar_long <- millar_generalbills_postplague_parishes |>
  select(!1:4) |>
  pivot_longer(8:168,
    names_to = "parish_name",
    values_to = "count"
  ) |>
  # We use a nonexistant week to help with some math below
  mutate(week = 90)

millar_long <- millar_long |>
  mutate(count_type = "Total")

names(millar_long) <- tolower(names(millar_long))
names(millar_long) <- gsub(" ", "_", names(millar_long))
millar_long$year <- str_sub(millar_long$unique_identifier, 8, 11)

# Combine the general bills together
general_bills <- millar_long
general_bills <- general_bills |>
  mutate(bill_type = "General")

# Remove whitespace with str_trim().
general_bills <- general_bills |>
  mutate(parish_name = str_trim(parish_name))

# Replace the alternate spelling of "Alhallows"
general_bills <- general_bills |>
  mutate_at("parish_name", str_replace, "Allhallows", "Alhallows")

# Check for duplicates
if(log_data_check(general_bills, "After combining general bills")) {
  # If duplicates found, check which source they came from
  general_bills <- general_bills |>
    group_by(unique_identifier, parish_name, year) |>
    filter(n() > 1) |>
    arrange(unique_identifier, parish_name, year)
  
  message("\nDetailed duplicate analysis in weekly bills:")
  print(general_bills)
}

# ----------------------------------------------------------------------
# Unique values with IDs
# ----------------------------------------------------------------------

# Unique parish names
# -------------------
parishes_tmp <- left_join(parishes_unique, general_bills, by = "parish_name")
parishes_unique <- parishes_tmp |>
  select(parish_name) |>
  distinct() |>
  arrange(parish_name) |>
  mutate(parish_name = str_trim(parish_name))

# Combine unique parishes with the canonical Parish name list.
parish_canonical <- read_csv("data/London Parish Authority File.csv") |>
  select(`Canonical DBN Name`, `Omeka Parish Name`) |>
  mutate(canonical_name = `Canonical DBN Name`, parish_name = `Omeka Parish Name`) |>
  select(canonical_name, parish_name)

parishes_unique <- parishes_unique |>
  left_join(parish_canonical, by = "parish_name")

# We assign our own ID to the parish name rather than having PostgreSQL 
# generate it. This is because data transformations below expect a consistent
# ID for each parish.
parishes_unique <- parishes_unique |>
  mutate(canonical = coalesce(canonical_name, parish_name)) |>
  select(-canonical_name) |>
  mutate(canonical_name = canonical) |>
  select(-canonical) |>
  mutate(parish_id = row_number())

rm(parishes_tmp)

# Unique week values
# ------------------
week_unique_weekly <- weekly_bills |>
  ungroup() |>
  select(
    year,
    week,
    start_day,
    end_day,
    start_month,
    end_month,
    unique_identifier
  ) |>
  # distinct() |>
  mutate(year = as.integer(year)) |>
  # To get a leading zero and not mess with the math below, we create a temporary
  # column to pad the week number with a leading zero and use that for
  # creating the week ID string.
  # mutate(id = row_number()) |>
  mutate(week_tmp = str_pad(week, 2, pad = "0")) |>
  mutate(week_comparator = as.integer(week)) |>
  mutate(week_id = ifelse(week_comparator > 15,
    paste0(
      year - 1, "-", year, "-", week_tmp
    ),
    paste0(
      year, "-", year + 1, "-", week_tmp
    )
  )) |>
  mutate(year_range = str_sub(week_id, 1, 9)) |>
  select(-week_tmp, -week_comparator)

week_unique_wellcome <- causes_wellcome |>
  ungroup() |>
  select(
    year,
    week_number,
    start_day,
    end_day,
    start_month,
    end_month,
    unique_identifier
  ) |>
  # distinct() |>
  mutate(year = as.integer(year)) |>
  # To get a leading zero and not mess with the math below, we create a temporary
  # column to pad the week number with a leading zero and use that for
  # creating the week ID string.
  mutate(week_tmp = str_pad(week_number, 2, pad = "0")) |>
  mutate(week_comparator = as.integer(week_number)) |>
  mutate(week_id = ifelse(week_comparator > 15,
    paste0(
      year - 1, "-", year, "-", week_tmp
    ),
    paste0(
      year, "-", year + 1, "-", week_tmp
    )
  )) |>
  mutate(year_range = str_sub(week_id, 1, 9)) |>
  select(-week_tmp, -week_comparator)

all_laxton_weekly_causes <- bind_rows(
  causes_laxton_1700 |> mutate(week_number = as.numeric(week_number), count = as.numeric(count)),
  causes_laxton |> mutate(week_number = as.numeric(week_number), count = as.numeric(count)),
)

week_unique_laxton <- all_laxton_weekly_causes |>
  select(
    year,
    week_number,
    start_day,
    end_day,
    start_month,
    end_month,
    unique_identifier
  ) |>
  # distinct() |>
  mutate(year = as.integer(year)) |>
  mutate(week_tmp = str_pad(week_number, 2, pad = "0")) |>
  mutate(week_comparator = as.integer(week_number)) |>
  mutate(week_id = ifelse(week_comparator > 15,
    paste0(
      year - 1, "-", year, "-", week_tmp
    ),
    paste0(
      year, "-", year + 1, "-", week_tmp
    )
  )) |>
  mutate(year_range = str_sub(week_id, 1, 9)) |>
  select(-week_tmp, -week_comparator)

# If the laxton_weeks_from_causes has an NA value in week_id, we replace
# it with the unique_identifier value but remove "Laxton-" from the string.
week_unique_laxton <- week_unique_laxton |>
  mutate(week_id = ifelse(is.na(week_id),
    str_replace(unique_identifier, "Laxton-", ""),
    week_id
  ))
week_unique_laxton <- week_unique_laxton |>
  mutate(week_id = str_replace(week_id, "-verso", ""))

week_unique_general <- general_bills |>
  select(
    year,
    week,
    start_day,
    start_month,
    end_day,
    end_month,
    unique_identifier
  ) |>
  # distinct() |>
  mutate(year = as.integer(year)) |>
  mutate(week_tmp = str_pad(week, 2, pad = "0")) |>
  mutate(week_comparator = as.integer(week)) |>
  mutate(week_id = ifelse(week_comparator > 15,
    paste0(
      year - 1, "-", year, "-", week_tmp
    ),
    paste0(
      year, "-", year + 1, "-", week_tmp
    )
  )) |>
  mutate(year_range = str_sub(week_id, 1, 9)) |>
  select(-week_tmp, -week_comparator)

week_unique_general <- rename(week_unique_general, "week_number" = "week")
week_unique_weekly <- rename(week_unique_weekly, "week_number" = "week")

week_unique <- bind_rows(
  week_unique_weekly |> mutate(week_number = as.numeric(week_number)),
  week_unique_general |> mutate(week_number = as.numeric(week_number)),
  week_unique_wellcome |> mutate(week_number = as.numeric(week_number)),
  week_unique_laxton |> mutate(week_number = as.numeric(week_number))
)

# We determine here whether a year should be a split year by looking at the
# week number and determining if it falls between week 52 and week 15 as the calendar
# turns over.
week_unique <- week_unique |>
  mutate(split_year = ifelse(
    week_number > 15,
    paste0(year - 1, "/", year),
    paste0(year)
  ))

# week_unique <- week_unique |> distinct(week_id, .keep_all = TRUE)

# Filter out extraneous data and assign
# unique week IDs to the deaths long table.
wellcome_deaths_cleaned <- causes_wellcome |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE)))

all_laxton_causes <- bind_rows(
  causes_laxton |> mutate(week_number = as.numeric(week_number), count = as.numeric(count)), 
  causes_laxton_1700 |> mutate(week_number = as.numeric(week_number), count = as.numeric(count))
)

laxton_deaths_cleaned <- all_laxton_causes |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE)))

total_causes <- bind_rows(laxton_deaths_cleaned, wellcome_deaths_cleaned)
total_causes <- total_causes |>
  mutate(joinid = paste0(start_day, start_month, end_day, end_month, year))

week_unique <- week_unique |>
  mutate(joinid = paste0(start_day, start_month, end_day, end_month, year)) |> 
  distinct(joinid, .keep_all = TRUE)

# Now that we have all potential causes, we drop their date information and combine
# the unique identifiers against the week_unique joinid column to keep the date 
# information consistent. This data is joined in Postgres.
deaths_long <- total_causes |>
  select(-week_number, -start_day, -end_day, -start_month, -end_month, -year, -unique_identifier) |>
  dplyr::left_join(week_unique, by = "joinid") |>
  select(-week_number, -start_day, -end_day, -start_month, -end_month, -unique_identifier)

# Unique year values
# ------------------
year_unique <- week_unique |>
  ungroup() |>
  select(year, week_number) |>
  arrange() |>
  mutate(year = as.integer(year)) |>
  mutate(year_id = as.integer(year)) |>
  mutate(week_number = as.integer(week_number)) |>
  select(-week_number) |>
  filter(!is.na(year)) |>
  distinct() |>
  arrange(year) |>
  mutate(id = row_number())

# Match unique parish IDs with the long parish tables, and drop the parish
# name from the long table. We'll use SQL foreign keys to keep the relationship
# by parish_id in all_bills and parishes_unique.
weekly_bills <- dplyr::inner_join(weekly_bills, parishes_unique, by = "parish_name") |>
  select(-parish_name)

general_bills <- dplyr::inner_join(general_bills, parishes_unique, by = "parish_name") |>
  select(-parish_name)

# Match unique week IDs to the long parish tables, and drop the existing
# start and end months and days from long_parish so they're only referenced
# through the unique week ID.
weekly_bills <- weekly_bills |>
  select(-week, -start_day, -end_day, -start_month, -end_month, -year) |>
  dplyr::left_join(week_unique, by = "unique_identifier") |>
  drop_na(year) |>
  select(
    -week_number,
    -start_day,
    -end_day,
    -start_month,
    -end_month,
    -canonical_name
  )

general_bills <- general_bills |>
  select(-week, -start_day, -end_day, -start_month, -end_month, -year) |>
  dplyr::left_join(week_unique, by = "unique_identifier") |>
  drop_na(year) |>
  select(
    -week_number,
    -start_day,
    -end_day,
    -start_month,
    -end_month,
    -canonical_name
  )

# Match unique year IDs to the long parish table, and drop the existing
# year column from long_parishes so they're only referenced
# through the unique year ID.
weekly_bills <- weekly_bills |>
  mutate(year = as.integer(year))

general_bills <- general_bills |>
  mutate(year = as.integer(year))

general_bills <- general_bills |>
  select(-start_year, -end_year)

general_bills <- general_bills |> 
  mutate(missing = FALSE) |> 
  mutate(illegible = FALSE)

# ------------------------------------------------------------------------------
message("Weekly bills columns:")
print(names(weekly_bills))
message("\nGeneral bills columns:")
print(names(general_bills))

# Find differences in column names
message("\nColumns in weekly_bills but not in general_bills:")
print(setdiff(names(weekly_bills), names(general_bills)))
message("\nColumns in general_bills but not in weekly_bills:")
print(setdiff(names(general_bills), names(weekly_bills)))

# Check structures
message("\nStructure of weekly_bills:")
str(weekly_bills)
message("\nStructure of general_bills:")
str(general_bills)
# ------------------------------------------------------------------------------

all_bills <- bind_rows(weekly_bills, general_bills)
all_bills <- all_bills |> mutate(id = row_number())
all_bills <- all_bills |> mutate(
  missing = coalesce(missing, FALSE),
  illegible = coalesce(illegible, FALSE)
)

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

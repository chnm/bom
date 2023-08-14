# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates CSV files of long tables for the
# parishes and types of death as well as extracting burials, christenings, and
# plague numbers from the transcriptions.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2023-08-14

library(tidyverse)

# ----------------------------------------------------------------------
# Data sources
# Each of these are separate DataScribe exports that we are preparing for
# the PostgreSQL database.
# ----------------------------------------------------------------------
## The following reads each CSV file in our directory and creates a ew variable 
## for each one based on its filename. Then, use tidyverse::read_csv to read the
## CSV file and assign it to a variable.

  # Get all the CSV files in the directory
  files <- list.files("../../../bom-data/data-csvs", pattern = "*.csv", full.names = TRUE)
  # Loop through the files and assign them to a variable based on the csv filename
  for (file in files) {
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
  }


# ----------------------------------------------------------------------
# Lookup tables
# We need to do several lookups and cross-references throughout our data
# preparation. To make this script a bit more readable, we're going to 
# prepare these lookup tables here.
# ----------------------------------------------------------------------

# Wellcome Lookup
# ======================================================================
# We create a lookup table that includes the unique identifier,
# the descriptive text, Start Day, Start Month, End Day, End Month, and death type.
lookup_wellcome <- Wellcome_weeklybills_causes |>
  select(!1:5) |>
  select(
    contains("(Descriptive Text)"), 
    `Unique Identifier`, 
    `Start Day`, 
    `Start Month`, 
    `End Day`, 
    `End Month`, 
    Year
  ) |>
  pivot_longer(1:4, names_to = "death_type", values_to = "descriptive_text" ) |>
  mutate(`Unique Identifier` = str_trim(`Unique Identifier`)) |>
  # remove (Descriptive Text)
  mutate(death_type = str_remove( 
    death_type, 
    regex("\\(Descriptive Text\\)"))
  ) |>
  mutate(death_type = str_trim(death_type)) |>
  mutate(join_id = paste0(
    `Start Day`, 
    `Start Month`, 
    `End Day`, 
    `End Month`, 
    Year, "-", 
    death_type, "-", 
    `Unique Identifier`)) |>
  # We can drop the start day, start month, etc. since that will be added with 
  # the long table
  select(
    -`Start Day`, 
    -`Start Month`, 
    -`End Day`, 
    -`End Month`, 
    -Year, 
    -`Unique Identifier`, 
    death_type
  )

# Laxton Lookup (1700)
# ======================================================================
# We create a lookup table that includes the unique identifier,
# the descriptive text, Start Day, Start Month, End Day, End Month,
# and death type.
lookup_laxton_1700 <- Laxton_1700_weeklybills_causes |>
  select(!1:4) |>
  select(
    contains("(Descriptive Text)"), 
    `Unique Identifier`, 
    `Start Day`, 
    `Start Month`, 
    `End Day`, 
    `End Month`, 
    Year) |>
  pivot_longer(1:8, names_to = "death_type", values_to = "descriptive_text" ) |>
  mutate(`Unique Identifier` = str_trim(`Unique Identifier`)) |>
  # Remove (Descriptive Text) so we just have the cause of death
  mutate(death_type = str_remove( 
    death_type, 
    regex("\\(Descriptive Text\\)")) 
  ) |>
  mutate(death_type = str_trim(death_type)) |>
  mutate(join_id = paste0(
    `Start Day`, 
    `Start Month`, 
    `End Day`, 
    `End Month`, 
    Year, "-", 
    death_type, "-", 
    `Unique Identifier`)
  ) |>
  # Now we can drop the start day, start month, etc. since that will be added 
  # with the long table
  select(
    -`Start Day`, 
    -`Start Month`, 
    -`End Day`, 
    -`End Month`, 
    -Year, 
    -`Unique Identifier`, 
    death_type
  )

# Laxton Lookup
# ======================================================================
# We create a lookup table that includes the unique identifier,
# the descriptive text, Start Day, Start Month, End Day, End Month, 
# and death type.
lookup_laxton <- Laxton_weeklybills_causes |>
  select(!1:4) |>
  select(
    contains("(Descriptive Text)"), 
    `Unique Identifier`, 
    `Start Day`, 
    `Start Month`, 
    `End Day`, 
    `End Month`, 
    Year
  ) |>
  pivot_longer(1:8, 
    names_to = "death_type", 
    values_to = "descriptive_text" 
  ) |>
  mutate(`Unique Identifier` = str_trim(`Unique Identifier`)) |>
  # remove (Descriptive Text)
  mutate(death_type = str_remove(death_type, regex("\\(Descriptive Text\\)"))) |>
  mutate(death_type = str_trim(death_type)) |>
  mutate(join_id = paste0(
    `Start Day`,
    `Start Month`,
    `End Day`,
    `End Month`,
    Year, "-",
    death_type, "-",
    `Unique Identifier`)
  ) |>
  # now we can drop the start day, start month, etc. since that will be added with the long table
  select(
    -`Start Day`,
    -`Start Month`,
    -`End Day`,
    -`End Month`,
    -Year,
    -`Unique Identifier`,
    death_type
  )

# ----------------------------------------------------------------------
# Types of death table
# ----------------------------------------------------------------------
causes_wellcome <- Wellcome_weeklybills_causes |>
  select(!1:5) |>
  select(!contains("(Descriptive")) |>
  pivot_longer(8:109, names_to = "death", values_to = "count" ) |>
  mutate(death = str_trim(death)) |>
  mutate(`Unique Identifier` = str_trim(`Unique Identifier`)) |>
  mutate(join_id = paste0(
    `Start Day`, 
    `Start Month`, 
    `End Day`, 
    `End Month`, 
    Year, "-", 
    death, "-", 
    `Unique Identifier`)
  )

# Now, we left_join on the lookup table with the join_id
causes_wellcome <- causes_wellcome |>
  left_join(lookup_wellcome, by = "join_id") |>
  select(-join_id, -death_type)

# Lowercase column names and replace spaces with underscores
names(causes_wellcome) <- tolower(names(causes_wellcome))
names(causes_wellcome) <- gsub(" ", "_", names(causes_wellcome))

### Laxton causes for 1700 -----------------------------------------------
causes_laxton_1700 <- Laxton_1700_weeklybills_causes |>
  select(!1:4) |>
  select(!contains("(Descriptive")) |>
  pivot_longer(8:125, names_to = "death", values_to = "count" ) |>
  mutate(death = str_trim(death)) |>
  mutate(`Unique Identifier` = str_trim(`Unique Identifier`)) |>
  mutate(join_id = paste0( `Start Day`, `Start Month`, `End Day`, `End Month`, Year, "-", death, "-", `Unique Identifier`))

# Now, we left_join the lookup table on the join_id
causes_laxton_1700 <- causes_laxton_1700 |>
  left_join(lookup_laxton_1700, by = "join_id") |>
  select(-join_id, -death_type)

# Lowercase column names and replace spaces with underscores
names(causes_laxton_1700) <- tolower(names(causes_laxton_1700))
names(causes_laxton_1700) <- gsub(" ", "_", names(causes_laxton_1700))

### Laxton causes for pre-1700 -----------------------------------------------
causes_laxton <- Laxton_weeklybills_causes |>
  select(!1:4) |>
  select(!contains("(Descriptive")) |>
  mutate(across( 8:125, as.character )) |>
  pivot_longer(8:125, names_to = "death", values_to = "count" ) |>
  mutate(death = str_trim(death)) |>
  mutate(`Unique Identifier` = str_trim(`Unique Identifier`)) |>
  mutate(join_id = paste0( `Start Day`, `Start Month`, `End Day`, `End Month`, Year, "-", death, "-", `Unique Identifier`))

# Now, we left_join on the join_id
causes_laxton <- causes_laxton |>
  left_join(lookup_laxton, by = "join_id") |>
  select(-join_id, -death_type)

# Lowercase column names and replace spaces with underscores
names(causes_laxton) <- tolower(names(causes_laxton))
names(causes_laxton) <- gsub(" ", "_", names(causes_laxton))

# Types of death with unique ID
deaths_unique_wellcome <- causes_wellcome |>
  select(death) |>
  distinct() |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE)))

deaths_unique_laxton_1700 <- causes_laxton_1700 |>
  select(death) |>
  distinct() |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE)))

deaths_unique_laxton <- causes_laxton |>
  select(death) |>
  distinct() |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE)))

deaths_unique <- left_join(deaths_unique_wellcome, deaths_unique_laxton)
deaths_unique <- left_join(deaths_unique, deaths_unique_laxton_1700)
deaths_unique <- deaths_unique |>
  arrange(death) |>
  mutate(death_id = row_number())

# ----------------------------------------------------------------------
# Weekly Bills
# ----------------------------------------------------------------------
# To handle this data, we need to create two separate tables and then rejoin them.
# The first table removes any is_missing and is_illegible columns. The second
# includes both of those values. We then rejoin them and create a single table
# that includes all of the data.
laxton_weekly_illegible <- Laxton_weeklybills_parishes |>
  select(!1:4) |>
  select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) |> 
  select(`Year`, `Week`, `Unique ID`, `Start Day`, `Start Month`, `End Day`, `End month`, contains("is_illegible"))
laxton_weekly_missing <- Laxton_weeklybills_parishes |>
  select(!1:4) |>
  select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) |> 
  select(`Year`, `Week`, `Unique ID`, `Start Day`, `Start Month`, `End Day`, `End month`, contains("is_missing"))

# Now, we pivot the data from wide to long format.
laxton_weekly_illegible_transform <- laxton_weekly_illegible |>
  pivot_longer(8:167, names_to = "illegible_missing", values_to = "illegible") |> 
  select(!`illegible_missing`) |>
  # change NA to false and 1 to true
  mutate(illegible = ifelse(is.na(illegible), FALSE, TRUE))

laxton_weekly_missing_transform <- laxton_weekly_missing |>
  pivot_longer(8:167, names_to = "illegible_missing", values_to = "missing") |> 
  select(!`illegible_missing`) |> 
  # change NA to false and 1 to true
  mutate(missing = ifelse(is.na(missing), FALSE, TRUE))

# Then, we set up the table without the illegible or missing values
laxton_weekly_illegible_cleaned <- Laxton_weeklybills_parishes |>
  select(-c(starts_with("is_illegible")))
laxton_weekly_cleaned <- laxton_weekly_illegible_cleaned |>
  select(-c(starts_with("is_missing")))

laxton_weekly_transformed <- laxton_weekly_cleaned |> 
  select(!1:4) |>
  pivot_longer(8:167, names_to = "parish_name", values_to = "count" )

# Now we join laxton_weekly_transformed with laxton_weekly_missing_illegible
laxton_weekly <- bind_rows(laxton_weekly_transformed, laxton_weekly_missing_transform, laxton_weekly_illegible_transform)

rm(laxton_weekly_illegible)
rm(laxton_weekly_illegible_transform)
rm(laxton_weekly_missing)
rm(laxton_weekly_missing_transform)

## Bodleian V1 data prep
bodleian_weekly_illegible <- BodleianV1_weeklybills_parishes |>
  select(!1:4) |>
  select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) |> 
  select(`Year`, `Week`, `Unique ID`, `Start Day`, `Start Month`, `End Day`, `End month`, contains("is_illegible"))
bodleian_weekly_missing <- BodleianV1_weeklybills_parishes |>
  select(!1:4) |>
  select(-c(2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18, 20, 21)) |> 
  select(`Year`, `Week`, `Unique ID`, `Start Day`, `Start Month`, `End Day`, `End month`, contains("is_missing"))

# Now, we pivot the data from wide to long format.
bodleian_weekly_illegible_transform <- bodleian_weekly_illegible |>
  pivot_longer(8:266, names_to = "illegible_missing", values_to = "illegible") |> 
  select(!`illegible_missing`) |>
  # change NA to false and 1 to true
  mutate(illegible = ifelse(is.na(illegible), FALSE, TRUE))

bodleian_weekly_missing_transform <- bodleian_weekly_missing |>
  pivot_longer(8:266, names_to = "illegible_missing", values_to = "missing") |> 
  select(!`illegible_missing`) |> 
  # change NA to false and 1 to true
  mutate(missing = ifelse(is.na(missing), FALSE, TRUE))

# Then, we set up the table without the illegible or missing values
bodleian_weekly_illegible_cleaned <- BodleianV1_weeklybills_parishes |>
  select(-c(starts_with("is_illegible")))
bodleian_weekly_cleaned <- bodleian_weekly_illegible_cleaned |>
  select(-c(starts_with("is_missing")))

bodleian_weekly_transformed <- bodleian_weekly_cleaned |> 
  select(!1:4) |>
  pivot_longer(8:266, names_to = "parish_name", values_to = "count" )

# Now we join bodleian_weekly_transformed with bodleian_weekly_missing_illegible
bodleian_weekly_v1 <- bind_rows(bodleian_weekly_transformed, bodleian_weekly_missing_transform, bodleian_weekly_illegible_transform)


# Lowercase column names and replace spaces with underscores.
names(laxton_weekly) <- tolower(names(laxton_weekly))
names(laxton_weekly) <- gsub(" ", "_", names(laxton_weekly))
names(wellcome_weekly) <- tolower(names(wellcome_weekly))
names(wellcome_weekly) <- gsub(" ", "_", names(wellcome_weekly))
names(bodleian_weekly) <- tolower(names(bodleian_weekly))
names(bodleian_weekly) <- gsub(" ", "_", names(bodleian_weekly))
names(bodleian_weekly_v2) <- tolower(names(bodleian_weekly_v2))
names(bodleian_weekly_v2) <- gsub(" ", "_", names(bodleian_weekly_v2))
names(bodleian_weekly_v3) <- tolower(names(bodleian_weekly_v3))
names(bodleian_weekly_v3) <- gsub(" ", "_", names(bodleian_weekly_v3))


# The unique ID column is mis-named in the Laxton data so we fix it here
names(laxton_weekly)[3] <- "unique_identifier"
names(bodleian_weekly)[3] <- "unique_identifier"
names(bodleian_weekly_v2)[3] <- "unique_identifier"
names(bodleian_weekly_v3)[3] <- "unique_identifier"

weekly_bills <- rbind(wellcome_weekly, laxton_weekly, bodleian_weekly, bodleian_weekly_v2, bodleian_weekly_v3 ) |>
  mutate(bill_type = "Weekly")

weekly_bills <- weekly_bills |>
  mutate(start_day = as.integer(start_day)) |>
  mutate(end_day = as.integer(end_day)) |>
  mutate(week = as.integer(week))

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
write_csv(christenings_tmp, "bom-processing/scripts/bomr/data/christenings_by_parish.csv", na = "")

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

# Find all unique values for parish name, week, and year. These will be
# referenced as foreign keys in PostgreSQL.
parishes_unique <- weekly_bills |>
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
parish_canonical <- read_csv("bom-processing/scripts/bomr/data/London Parish Authority File.csv") |>
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

all_laxton_weekly_causes <- rbind(causes_laxton_1700, causes_laxton)

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

week_unique <- rbind(
  week_unique_weekly,
  week_unique_general,
  week_unique_wellcome,
  week_unique_laxton
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
  # TODO: this next line (distinct()) might be causing the bug with data not returning
  # may be better to think of this table as a week lookup rather than
  # distinct set of weeks...
  # distinct(week_id, .keep_all = TRUE) |>

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

all_laxton_causes <- rbind(causes_laxton, causes_laxton_1700)

laxton_deaths_cleaned <- all_laxton_causes |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE)))

total_causes <- rbind(laxton_deaths_cleaned, wellcome_deaths_cleaned)
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
  select(year, week_number) |>
  arrange() |>
  mutate(year = as.integer(year)) |>
  mutate(year_id = as.integer(year)) |>
  mutate(week_number = as.integer(week_number)) |>
  select(-week_number) |>
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

all_bills <- rbind(weekly_bills, general_bills)
all_bills <- all_bills |> mutate(id = row_number())

# --------------------------------------------------
# Write data
# --------------------------------------------------

# Clean up the R environment
rm(
  BodleianV1_weeklybills_parishes,
  BodleianV1_weeklybills_parishes_v2,
  BodleianV1_weeklybills_parishes_v3,
  Laxton_1700_weeklybills_causes,
  Laxton_weeklybills_causes,
  Laxton_weeklybills_parishes,
  millar_generalbills_postplague_parishes,
  Wellcome_weeklybills_causes,
  1669_1670_Wellcome_weeklybills_parishes
)

rm(
  lookup_laxton,
  lookup_laxton_1700,
  lookup_wellcome
)

rm(
  wellcome_weekly,
  wellcome_deaths_cleaned,
  week_unique_wellcome,
  week_unique_weekly,
  week_unique_laxton,
  week_unique_general,
  millar_long,
  parish_canonical,
  laxton_weekly,
  laxton_deaths_cleaned,
  deaths_unique_wellcome,
  deaths_unique_laxton_1700,
  deaths_unique_laxton,
  bodleian_weekly,
  bodleian_weekly_v2,
  bodleian_weekly_v3,
  all_laxton_causes,
  all_laxton_weekly_causes
)

# Write data to csv: causes of death
write_csv(causes_wellcome, "bom-processing/scripts/bomr/data/wellcome_causes.csv", na = "")
write_csv(causes_laxton, "bom-processing/scripts/bomr/data/laxton_causes.csv", na = "")
write_csv(causes_laxton_1700, "bom-processing/scripts/bomr/data/laxton_causes_1700.csv", na = "")
write_csv(deaths_unique, "bom-processing/scripts/bomr/data/deaths_unique.csv", na = "")
write_csv(deaths_long, na = "", "bom-processing/scripts/bomr/data/causes_of_death.csv")

# Write data to csv: parishes and bills
write_csv(weekly_bills, "bom-processing/scripts/bomr/data/bills_weekly.csv", na = "")
write_csv(general_bills, "bom-processing/scripts/bomr/data/bills_general.csv", na = "")
write_csv(all_bills, "bom-processing/scripts/bomr/data/all_bills.csv", na = "")
write_csv(parishes_unique, "bom-processing/scripts/bomr/data/parishes_unique.csv", na = "")
write_csv(week_unique, "bom-processing/scripts/bomr/data/week_unique.csv", na = "")
write_csv(year_unique, "bom-processing/scripts/bomr/data/year_unique.csv", na = "")

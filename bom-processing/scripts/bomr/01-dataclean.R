# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates CSV files of long tables for the
# parishes and types of death as well as extracting burials, christenings, and
# plague numbers from the transcriptions.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2023-02-22

library(tidyverse)

# ----------------------------------------------------------------------
# Data sources
# ----------------------------------------------------------------------
raw_wellcome_weekly <- read_csv("bom-data/data-csvs/2022-04-06-1669-1670-Wellcome-weeklybills-parishes.csv")
raw_wellcome_causes <- read_csv("bom-data/data-csvs/2022-04-06-Wellcome-weeklybills-causes.csv")
raw_laxton_weekly <- read_csv("bom-data/data-csvs/2022-11-02-Laxton-weeklybills-parishes.csv")
raw_millar_general <- read_csv("bom-data/data-csvs/2022-04-06-millar-generalbills-postplague-parishes.csv")
raw_laxton_1700_causes <- read_csv("bom-data/data-csvs/2022-06-15-Laxton-1700-weeklybills-causes.csv")
raw_laxton_causes <- read_csv("bom-data/data-csvs/2022-11-02-Laxton-weeklybills-causes.csv")
raw_laxton_1700_foodstuffs <- read_csv("bom-data/data-csvs/2022-09-19-Laxton-1700-weeklybills-foodstuffs.csv")
raw_laxton_foodstuffs <- read_csv("bom-data/data-csvs/2022-09-19-Laxton-1700-weeklybills-foodstuffs.csv")
raw_bodleian <- read_csv("bom-data/data-csvs/2023-02-22-BodleianV1-weeklybills-parishes.csv")
raw_bodleian_v2 <- read_csv("bom-data/data-csvs/2023-02-22-BodleianV2-weeklybills-parishes.csv")

# ----------------------------------------------------------------------
# Types of death table
# ----------------------------------------------------------------------
wellcome_causes_long <- raw_wellcome_causes |>
  select(!1:5) |>
  select(!contains("(Descriptive")) |>
  pivot_longer(8:109,
    names_to = "death",
    values_to = "count"
  ) |>
  mutate(death = str_trim(death))

# Lowercase column names and replace spaces with underscores
names(wellcome_causes_long) <- tolower(names(wellcome_causes_long))
names(wellcome_causes_long) <- gsub(" ", "_", names(wellcome_causes_long))

laxton_causes_1700_long <- raw_laxton_1700_causes |>
  select(!1:4) |>
  select(!contains("(Descriptive")) |>
  pivot_longer(8:125,
    names_to = "death",
    values_to = "count"
  ) |>
  mutate(death = str_trim(death))

# Lowercase column names and replace spaces with underscores
names(laxton_causes_1700_long) <- tolower(names(laxton_causes_1700_long))
names(laxton_causes_1700_long) <- gsub(" ", "_", names(laxton_causes_1700_long))

laxton_causes_long <- raw_laxton_causes |>
  select(!1:4) |>
  select(!contains("(Descriptive")) |>
  select(!contains("Christened (")) |>
  pivot_longer(8:122,
    names_to = "death",
    values_to = "count"
  ) |>
  mutate(death = str_trim(death))

# Lowercase column names and replace spaces with underscores
names(laxton_causes_long) <- tolower(names(laxton_causes_long))
names(laxton_causes_long) <- gsub(" ", "_", names(laxton_causes_long))

# Types of death with unique ID
deaths_unique_wellcome <- wellcome_causes_long |>
  select(death) |>
  distinct() |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE)))

deaths_unique_laxton_1700 <- laxton_causes_1700_long |>
  select(death) |>
  distinct() |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE)))

deaths_unique_laxton <- laxton_causes_long |>
  select(death) |>
  distinct() |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE)))

deaths_unique <- left_join(deaths_unique_wellcome, deaths_unique_laxton)
deaths_unique <- left_join(deaths_unique, deaths_unique_laxton_1700)
deaths_unique <- deaths_unique |>
  arrange(death) |>
  mutate(death_id = row_number())

# Write data
write_csv(wellcome_causes_long, "bom-processing/scripts/bomr/data/wellcome_causes.csv", na = "")
write_csv(laxton_causes_long, "bom-processing/scripts/bomr/data/laxton_causes.csv", na = "")
write_csv(laxton_causes_1700_long, "bom-processing/scripts/bomr/data/laxton_causes_1700.csv", na = "")
write_csv(deaths_unique, "bom-processing/scripts/bomr/data/deaths_unique.csv", na = "")

# ----------------------------------------------------------------------
# Weekly Bills
# ----------------------------------------------------------------------
laxton_weekly <- raw_laxton_weekly |>
  select(!1:4) |>
  pivot_longer(8:167,
    names_to = "parish_name",
    values_to = "count"
  )

wellcome_weekly <- raw_wellcome_weekly |>
  select(!1:4) |>
  pivot_longer(8:285,
    names_to = "parish_name",
    values_to = "count"
  )

bodleian_weekly <- raw_bodleian |>
  select(-c(starts_with("is_illegible")))
bodleian_weekly <- bodleian_weekly |>
  select(-c(starts_with("is_missing")))

bodleian_weekly <- bodleian_weekly |>
  select(!1:4) |>
  pivot_longer(8:266,
    names_to = "parish_name",
    values_to = "count"
  )

bodleian_weekly_v2 <- raw_bodleian_v2 |>
  select(-c(starts_with("is_illegible")))
bodleian_weekly_v2 <- bodleian_weekly_v2 |>
  select(-c(starts_with("is_missing")))

bodleian_weekly_v2 <- bodleian_weekly_v2 |>
  select(!1:4) |>
  pivot_longer(8:266,
    names_to = "parish_name",
    values_to = "count"
  )

# Lowercase column names and replace spaces with underscores.
names(laxton_weekly) <- tolower(names(laxton_weekly))
names(laxton_weekly) <- gsub(" ", "_", names(laxton_weekly))
names(wellcome_weekly) <- tolower(names(wellcome_weekly))
names(wellcome_weekly) <- gsub(" ", "_", names(wellcome_weekly))
names(bodleian_weekly) <- tolower(names(bodleian_weekly))
names(bodleian_weekly) <- gsub(" ", "_", names(bodleian_weekly))
names(bodleian_weekly_v2) <- tolower(names(bodleian_weekly_v2))
names(bodleian_weekly_v2) <- gsub(" ", "_", names(bodleian_weekly_v2))

# The unique ID column is mis-named in the Laxton data so we fix it here
names(laxton_weekly)[3] <- "unique_identifier"
names(bodleian_weekly)[3] <- "unique_identifier"
names(bodleian_weekly_v2)[3] <- "unique_identifier"

weekly_bills <- rbind(
  wellcome_weekly,
  laxton_weekly,
  bodleian_weekly,
  bodleian_weekly_v2
) |>
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

millar_long <- raw_millar_general |>
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
  distinct() |>
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

week_unique_wellcome <- wellcome_causes_long |>
  select(
    year,
    week_number,
    start_day,
    end_day,
    start_month,
    end_month,
    unique_identifier
  ) |>
  distinct() |>
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

all_laxton_weekly_causes <- rbind(laxton_causes_1700_long, laxton_causes_long)

laxton_weeks_from_causes <- all_laxton_weekly_causes |>
  select(
    year,
    week_number,
    start_day,
    end_day,
    start_month,
    end_month,
    unique_identifier
  ) |>
  distinct() |>
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
  distinct() |>
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
  week_unique_wellcome,
  laxton_weeks_from_causes,
  week_unique_general
)

# We determine here whether a year should be a split year by looking at the
# week number and determining if it falls between week 52 and week 15 as the calendar
# turns over.
week_unique <- week_unique |>
  mutate(split_year = ifelse(
    week_number > 15,
    paste0(year - 1, "/", year),
    paste0(year)
  )) |>
  distinct(week_id, .keep_all = TRUE) |>
  mutate(id = row_number())

# Filter out extraneous data and assign
# unique week IDs to the deaths long table.
wellcome_deaths_cleaned <- wellcome_causes_long |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE))) # |>

all_laxton_causes <- rbind(laxton_causes_long, laxton_causes_1700_long)

laxton_deaths_cleaned <- all_laxton_causes |>
  filter(!str_detect(death, regex("\\bBuried ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bChristened ", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bPlague Deaths", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bOunces in", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bIncrease/Decrease", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Clear", ignore_case = FALSE))) |>
  filter(!str_detect(death, regex("\\bParishes Infected", ignore_case = FALSE)))

total_causes <- rbind(laxton_deaths_cleaned, wellcome_deaths_cleaned)

# Now that we have all potential causes, we drop their date information and combine
# the unique identifiers against the unique_weeks week ID to keep the date information
# consistent. This data is joined in Postgres.
deaths_long <- total_causes |>
  select(-week_number, -start_day, -end_day, -start_month, -end_month, -year) |>
  dplyr::left_join(week_unique, by = "unique_identifier") |>
  select(-week_number, -start_day, -end_day, -start_month, -end_month) |>
  mutate(id = row_number())

write_csv(deaths_long, na = "", "bom-processing/scripts/bomr/data/causes_of_death.csv")

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

# Write data to csv
write_csv(weekly_bills, "bom-processing/scripts/bomr/data/bills_weekly.csv", na = "")
write_csv(general_bills, "bom-processing/scripts/bomr/data/bills_general.csv", na = "")
write_csv(all_bills, "bom-processing/scripts/bomr/data/all_bills.csv", na = "")
write_csv(parishes_unique, "bom-processing/scripts/bomr/data/parishes_unique.csv", na = "")
write_csv(week_unique, "bom-processing/scripts/bomr/data/week_unique.csv", na = "")
write_csv(year_unique, "bom-processing/scripts/bomr/data/year_unique.csv", na = "")

# ----------------------------------------------------------------------
# Christenings
# ----------------------------------------------------------------------
# TODO: Currently these does not reference the week_unique data as a unique id
# because the unique_identifier needs the verso side and those are not currently
# included in week_unique.

laxton_christenings <- raw_laxton_causes |>
  select(5:11)

laxton_christenings_tmp <- raw_laxton_causes |>
  select(contains("Christened ("))

laxton_christenings_1700 <- raw_laxton_1700_causes |>
  select(5:11)

laxton_christenings_1700_tmp <- raw_laxton_1700_causes |>
  select(contains("Christened ("))

laxton_christenings <- cbind(
  laxton_christenings,
  laxton_christenings_tmp)
laxton_christenings_1700 <- cbind(
  laxton_christenings_1700,
  laxton_christenings_1700_tmp)
laxton_christenings <- rbind(
  laxton_christenings,
  laxton_christenings_1700)

rm(laxton_christenings_tmp)
rm(laxton_christenings_1700_tmp)

wellcome_christenings <- raw_wellcome_causes |>
  select(6:12)
wellcome_christenings_tmp <- raw_wellcome_causes |>
  select(contains("Christened ("))
wellcome_christenings <- cbind(wellcome_christenings, wellcome_christenings_tmp)
rm(wellcome_christenings_tmp)

# Ensure values are numeric
laxton_christenings <- laxton_christenings |>
  mutate(across(
    .cols = contains("Christened "),
    .fns = ~ as.numeric(.x)
  ))

wellcome_christenings <- wellcome_christenings |>
  mutate(across(
    .cols = contains("Christened "),
    .fns = ~ as.numeric(.x)
  ))

# Pivot the data to long format
laxton_christenings_long <- laxton_christenings |>
  pivot_longer(8:10,
    names_to = "christening",
    values_to = "count"
  )

wellcome_christenings_long <- wellcome_christenings |>
  pivot_longer(8:10,
    names_to = "christening",
    values_to = "count"
  )

christenings <- rbind(wellcome_christenings_long, laxton_christenings_long)

christenings <- christenings |>
  mutate(id = row_number())

names(christenings) <- tolower(names(christenings))
names(christenings) <- gsub(" ", "_", names(christenings))

# Write data
write_csv(wellcome_christenings_long, "bom-processing/scripts/bomr/data/wellcome_christenings.csv", na = "")
write_csv(laxton_christenings, "bom-processing/scripts/bomr/data/laxton_christenings.csv", na = "")
write_csv(christenings, "bom-processing/scripts/bomr/data/all_christenings.csv", na = "")

# ----------------------------------------------------------------------
# Foodstuffs
# ----------------------------------------------------------------------

foodstuffs_laxton <- raw_laxton_foodstuffs |>
  select(!1:4) |>
  pivot_longer(8:29,
    names_to = "item",
    values_to = "value"
  )

foodstuffs_laxton <- foodstuffs_laxton |> 
  separate(item, c("item", "value_type"), sep = "[-]")

names(foodstuffs_laxton) <- tolower(names(foodstuffs_laxton))
names(foodstuffs_laxton) <- gsub(" ", "_", names(foodstuffs_laxton))

foodstuffs_laxton_1700 <- raw_laxton_1700_foodstuffs |>
  select(!1:4) |>
  pivot_longer(8:29,
    names_to = "item",
    values_to = "value"
  )

foodstuffs_laxton_1700 <-
  foodstuffs_laxton_1700 |> separate(item, c("item", "value_type"), sep = "[-]")

names(foodstuffs_laxton_1700) <- tolower(names(foodstuffs_laxton_1700))
names(foodstuffs_laxton_1700) <- gsub(" ", "_", names(foodstuffs_laxton_1700))

foodstuffs <- rbind(foodstuffs_laxton, foodstuffs_laxton_1700)

write_csv(foodstuffs, "bom-processing/scripts/bomr/data/foodstuffs.csv", na = "")
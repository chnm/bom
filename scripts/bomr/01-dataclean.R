# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates CSV files of long tables for the 
# parishes and types of death as well as extracting burials, christenings, and 
# plague numbers from the transcriptions.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2022-05-03

library(tidyverse)

# ---------------------------------------------------------------------- 
# Data sources
# ---------------------------------------------------------------------- 
raw_laxton_weekly <- read_csv("../../datascribe-exports/2022-04-21-Laxton-weeklybills-parishes.csv")
raw_wellcome_causes <- read_csv("datascribe/Wellcome-weekly-causes.csv")
raw_wellcome_weekly <- read_csv("datascribe/Wellcome-weekly-parishes.csv")
raw_millar_general <- read_csv("datascribe/Millar-general-postplague-parishes-COMPLETE.csv")
raw_laxton_general <- read_csv("datascribe/Laxton-general-parishes.csv")

# ---------------------------------------------------------------------- 
# Types of death table
# ---------------------------------------------------------------------- 
wellcome_causes_long <- raw_wellcome_causes |> 
  select(!1:5) |>
  select(!`Drowned (Descriptive Text)`) |> 
  select(!`Killed (Descriptive Text)`) |> 
  select(!`Suicide (Descriptive Text)`) |> 
  select(!`Other Casualties (Descriptive Text)`) |> 
  pivot_longer(8:109, 
               names_to = 'death', 
               values_to = 'count') |> 
  mutate(death = str_trim(death))

# Lowercase column names and replace spaces with underscores
names(wellcome_causes_long) <- tolower(names(wellcome_causes_long))
names(wellcome_causes_long) <- gsub(" ", "_", names(wellcome_causes_long))

# Types of death with unique ID
deaths_unique <- wellcome_causes_long |> 
  select(death) |> 
  distinct() |> 
  arrange(death) |> 
  mutate(death_id = row_number())

# Write data
write_csv(wellcome_causes_long, "data/wellcome_causes.csv", na = "")
write_csv(deaths_unique, "data/deaths_unique.csv", na = "")

# ---------------------------------------------------------------------- 
# Weekly Bills
# ---------------------------------------------------------------------- 

laxton_weekly <- raw_laxton_weekly |> 
  select(!1:5) |> 
  pivot_longer(7:166,
               names_to = 'parish_name',
               values_to = 'count')

wellcome_weekly <- raw_wellcome_weekly |> 
  select(!1:5) |> 
  pivot_longer(7:284,
               names_to = 'parish_name',
               values_to = 'count')

laxton_weekly <- laxton_weekly |> 
  filter(!str_detect(`Unique ID`, "e.g. Laxton-1706-27-recto")) |> 
  filter(!grepl("Laxton$$", `Unique ID`))


# Lowercase column names and replace spaces with underscores.
names(laxton_weekly) <- tolower(names(laxton_weekly))
names(laxton_weekly) <- gsub(" ", "_", names(laxton_weekly))
laxton_weekly$year <- str_sub(laxton_weekly$unique_id, 8, 11) 

# The unique ID column is mis-named in the Laxton data so we fix it here
names(laxton_weekly)[2] <- "unique_identifier"

names(wellcome_weekly) <- tolower(names(wellcome_weekly))
names(wellcome_weekly) <- gsub(" ", "_", names(wellcome_weekly))
wellcome_weekly$year <- str_sub(wellcome_weekly$unique_identifier, 1, 4)

weekly_bills <- rbind(wellcome_weekly, laxton_weekly)
weekly_bills <- weekly_bills |> 
  mutate(bill_type = "Weekly")

weekly_bills <- weekly_bills |> 
  mutate(start_day = as.integer(start_day)) |> 
  mutate(end_day = as.integer(end_day)) |> 
  mutate(week = as.integer(week))

# Separate out a parish name from the count type (plague vs. burial)
# Remove whitespace with str_trim().
weekly_bills <- weekly_bills |> separate(parish_name, c("parish_name", "count_type"), sep = "[-]")
weekly_bills <- weekly_bills |>
  mutate(count_type = str_trim(count_type)) |> 
  mutate(parish_name = str_trim(parish_name))

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
               names_to = 'parish_name',
               values_to = 'count') |> 
  # We use a nonexistant week to help with some math below
  mutate(week = 90)

millar_long <- millar_long |> 
  mutate(count_type = "Total")

laxton_long <- raw_laxton_general |> 
  select(!1:4) |> 
  pivot_longer(8:155,
               names_to = 'parish_name',
               values_to = 'count') |> 
  # We use a nonexistant week to help with some math below
  mutate(week = 90)

laxton_long <- laxton_long |> separate(parish_name, c("parish_name", "count_type"), sep = "[-]")
laxton_long <- laxton_long |>
  mutate(count_type = str_trim(count_type)) |> 
  mutate(parish_name = str_trim(parish_name))

# Lowercase column names and replace spaces with underscores.
names(laxton_long) <- tolower(names(laxton_long))
names(laxton_long) <- gsub(" ", "_", names(laxton_long))
laxton_long$year <- str_sub(laxton_long$unique_identifier, 8, 11)

names(millar_long) <- tolower(names(millar_long))
names(millar_long) <- gsub(" ", "_", names(millar_long))
millar_long$year <- str_sub(millar_long$unique_identifier, 8, 11)

# Combine the general bills together 
general_bills <- rbind(millar_long, laxton_long)
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
parishes_tmp <- left_join(parishes_unique, general_bills, by = 'parish_name')
parishes_unique <- parishes_tmp |> 
  select(parish_name) |> 
  distinct() |> 
  arrange(parish_name) |> 
  mutate(parish_name = str_trim(parish_name))

# We want to clean up our distinct parish names by removing any mentions of 
# christenings, burials, or plague. The following detects the presence of specific 
# strings and simply assigns a bool. We then use those TRUE and FALSE values 
# to filter the data and remove the matching TRUE statements.
parishes_unique$christening_detect <- str_detect(parishes_unique$parish_name, "Christened")
parishes_unique$burials_detect <- str_detect(parishes_unique$parish_name, "Buried")
parishes_unique$plague_detect <- str_detect(parishes_unique$parish_name, "Plague in")
#parishes_unique$pesthouse_detect <- str_detect(parishes_unique$parish_name, "Pesthouse")

christenings_tmp <- parishes_unique |> 
  dplyr::filter(christening_detect == TRUE) |> 
  select(-christening_detect, -burials_detect, -plague_detect)
burials_tmp <- parishes_unique |> 
  dplyr::filter(burials_detect == TRUE) |> 
  select(-christening_detect, -burials_detect, -plague_detect)
plague_tmp <- parishes_unique |> 
  dplyr::filter(plague_detect == TRUE) |> 
  select(-christening_detect, -burials_detect, -plague_detect)
#pesthouse_tmp <- parishes_unique |> 
#  dplyr::filter(pesthouse_detect == TRUE) |> 
#  select(-christening_detect, -burials_detect, -plague_detect, -pesthouse_detect)

parishes_unique <- parishes_unique |> 
  dplyr::filter(christening_detect == FALSE,
                burials_detect == FALSE,
                plague_detect == FALSE, 
                #pesthouse_detect == FALSE
  )

parishes_unique <- parishes_unique |> 
  select(-christening_detect, -burials_detect, -plague_detect) |> 
  mutate(parish_id = row_number())
rm(christenings_tmp, burials_tmp, plague_tmp)

# Combine unique parishes with the canonical Parish name list.
parish_canonical <- read_csv("data/London Parish Authority File.csv") |> 
  select(`Canonical DBN Name`, `Omeka Parish Name`) |> 
  mutate(canonical_name = `Canonical DBN Name`, parish_name = `Omeka Parish Name`) |> 
  select(canonical_name, parish_name)

parishes_unique <- parishes_unique |> 
  left_join(parish_canonical, by = "parish_name")

parishes_unique <- parishes_unique |> 
  mutate(canonical = coalesce(canonical_name, parish_name)) |> 
  select(-canonical_name) |> 
  mutate(canonical_name = canonical) |> 
  select(-canonical)

rm(parishes_tmp)
# Find all unique values for parish name, week, and year. These will be 
# referenced as foreign keys in PostgreSQL.
#parishes_unique <- weekly_bills |> 
#  select(parish_name) |> 
#  distinct() |> 
#  arrange(parish_name) |> 
#  mutate(parish_name = str_trim(parish_name))

# Unique week values
# ------------------
week_unique_weekly <- weekly_bills |> 
  select(year, week, start_day, end_day, start_month, end_month, unique_identifier) |> 
  distinct() |> 
  mutate(year = as.integer(year)) |> 
  # To get a leading zero and not mess with the math below, we create a temporary
  # column to pad the week number with a leading zero and use that for 
  # creating the week ID string.
  mutate(id = row_number()) |> 
  mutate(week_tmp = str_pad(week, 2, pad = "0")) |> 
  mutate(week = as.integer(week)) |>
  mutate(week_id = ifelse(week > 15,
                          paste0(
                            year - 1, '-', year, '-', week_tmp
                          ),
                          paste0(
                            year, '-', year + 1, '-', week_tmp
                          )
  )
  ) |> 
  mutate(year_range = str_sub(week_id, 1, 9)) |> 
  select(-week_tmp)

week_unique_general <- general_bills |> 
  select(year, week, start_day, end_day, start_month, end_month, unique_identifier) |> 
  distinct() |> 
  mutate(year = as.integer(year)) |> 
  # To get a leading zero and not mess with the math below, we create a temporary
  # column to pad the week number with a leading zero and use that for 
  # creating the week ID string.
  mutate(id = row_number()) |> 
  mutate(week_tmp = str_pad(week, 2, pad = "0")) |> 
  mutate(week = as.integer(week)) |>
  mutate(week_id = ifelse(week > 15,
                          paste0(
                            year - 1, '-', year, '-', week_tmp
                          ),
                          paste0(
                            year, '-', year + 1, '-', week_tmp
                          )
  )
  ) |> 
  mutate(year_range = str_sub(week_id, 1, 9)) |> 
  select(-week_tmp)

week_unique_wellcome <- wellcome_causes_long |> 
  select(year, week_number, start_day, end_day, start_month, end_month, unique_identifier) |> 
  distinct() |> 
  mutate(year = as.integer(year)) |> 
  # To get a leading zero and not mess with the math below, we create a temporary
  # column to pad the week number with a leading zero and use that for 
  # creating the week ID string.
  mutate(id = row_number()) |> 
  mutate(week_tmp = str_pad(week_number, 2, pad = "0")) |> 
  mutate(week = as.integer(week_number)) |>
  select(-week_number) |> 
  mutate(week_id = ifelse(week > 15,
                          paste0(
                            year - 1, '-', year, '-', week_tmp
                          ),
                          paste0(
                            year, '-', year + 1, '-', week_tmp
                          )
  )
  ) |> 
  mutate(year_range = str_sub(week_id, 1, 9)) |> 
  select(-week_tmp)

week_unique <- rbind(week_unique_general, week_unique_weekly, week_unique_wellcome)

# Assign unique week IDs to the deaths long table. 
deaths_long <- wellcome_causes_long |> 
  select(-week_number, -start_day, -end_day, -start_month, -end_month, -year) |> 
  dplyr::left_join(week_unique, by = "unique_identifier") |> 
  select(-week, -start_day, -end_day, -start_month, -end_month) |> 
  mutate(id = row_number())

write_csv(deaths_long, na ="", "data/causes_of_death.csv")
  
# Unique year values
# ------------------
year_unique <- week_unique |> 
  select(year) |> 
  distinct() |> 
  arrange() |> 
  mutate(year_id = as.integer(year)) |> 
  mutate(year = as.integer(year)) |> 
  mutate(split_year = ifelse(year > 15,
                          paste0(
                            year - 1, '/', year
                          ),
                          paste0(
                            year, '/', year + 1
                          )
  )
  )

# Match unique parish IDs with the long parish table, and drop the parish
# name from the long table. We'll use SQL foreign keys to keep the relationship
# by parish_id in weekly_bills and parishes_unique.
weekly_bills <- dplyr::inner_join(weekly_bills, parishes_unique, by = "parish_name") |> 
  select(-parish_name)

general_bills <- dplyr::inner_join(general_bills, parishes_unique, by = "parish_name") |> 
  select(-parish_name)

# Match unique week IDs to the long parish table, and drop the existing 
# start and end months and days from long_parish so they're only referenced
# through the unique week ID.
weekly_bills <- weekly_bills |> 
  select(-week, -start_day, -end_day, -start_month, -end_month, -year) |> 
  dplyr::left_join(week_unique, by = "unique_identifier") |> 
  select(-week, -start_day, -end_day, -start_month, -end_month, -unique_identifier)

general_bills <- general_bills |> 
  select(-week, -start_day, -end_day, -start_month, -end_month, -year) |> 
  dplyr::left_join(week_unique, by = "unique_identifier") |> 
  select(-week, -start_day, -end_day, -start_month, -end_month, -unique_identifier)

# Match unique year IDs to the long parish table, and drop the existing
# year column from long_parishes so they're only referenced
# through the unique year ID.
weekly_bills <- weekly_bills |> 
  mutate(year = as.integer(year))

general_bills <- general_bills |> 
  mutate(year = as.integer(year))

weekly_bills <- weekly_bills |> 
  dplyr::left_join(year_unique, by = "year") |> 
  select(-year, -canonical_name)

general_bills <- general_bills |> 
  dplyr::left_join(year_unique, by = "year") |> 
  select(-year, -canonical_name)

# After we have unique years, we need to join the year ID to the 
# unique weeks and weekly_bills. 
week_unique <- week_unique |> 
  mutate(year = as.integer(year)) |> 
  dplyr::left_join(year_unique, by = "year") |> 
  select(-year)

# Write data to csv
write_csv(weekly_bills, "data/bills_weekly.csv", na = "")
write_csv(general_bills, "data/bills_general.csv", na = "")
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")
write_csv(week_unique, "data/week_unique.csv", na = "")
write_csv(year_unique, "data/year_unique.csv", na = "")

# ---------------------------------------------------------------------- 
# Christenings, births, plague, and foodstuffs
# ---------------------------------------------------------------------- 

# Christenings
parishes_filtering <- raw_parishes |> 
  select(!1:5) |> 
  pivot_longer(7:284,
               names_to = 'parish_name',
               values_to = 'count')

parishes_filtering$christening_detect <- str_detect(parishes_filtering$parish_name, "Christened")
parishes_filtering$burials_detect <- str_detect(parishes_filtering$parish_name, "Buried in")
parishes_filtering$plague_detect <- str_detect(parishes_filtering$parish_name, "Plague in")

christenings <- parishes_filtering |> 
  dplyr::filter(christening_detect == TRUE) |> 
  select(-christening_detect, -burials_detect, -plague_detect)
burials <- parishes_filtering |> 
  dplyr::filter(burials_detect == TRUE) |> 
  select(-christening_detect, -burials_detect, -plague_detect)
plague <- parishes_filtering |> 
  dplyr::filter(plague_detect == TRUE) |> 
  select(-christening_detect, -burials_detect, -plague_detect)

names(christenings) <- tolower(names(christenings))
names(christenings) <- gsub(" ", "_", names(christenings))

christenings <- christenings |> 
  select(-week, -start_day, -end_day, -start_month, -end_month) |> 
  dplyr::left_join(week_unique, by = "unique_identifier") |> 
  select(-week, -start_day, -end_day, -start_month, -end_month, -unique_identifier, -id, -year_range, -split_year)

rm(parishes_filtering)

write_csv(christenings, "data/christenings_counts.csv")
write_csv(burials, "data/burials_counts.csv")
write_csv(plague, "data/plague_counts.csv")

# Foodstuffs
# ----------
# TODO: This section isn't working yet because we don't have this data yet. 
# The code here is only scaffolding.
parishes_filtering <- raw_parishes |> 
  select(!1:5) |> 
  pivot_longer(7:284,
               names_to = 'parish_name',
               values_to = 'count')

parishes_filtering$food_detect <- str_detect(parishes_filtering, "bread")

foodstuffs <- parishes_filtering |> 
  dplyr::filter(food_detect == TRUE) |> 
  select(-food_detect)

rm(parishes_filtering)

write_csv(foodstuffs, "data/foodstuffs_count.csv")
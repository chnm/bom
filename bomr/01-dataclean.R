# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates two CSV files of long tables for the 
# parishes and types of death.
# 
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2021-12-03

library(tidyverse)

# Data sources
# ----------------------------
deaths <- read_csv("datascribe/weekly_deaths.csv")
parishes <- read_csv("datascribe/weekly_plague.csv")

# Types of death table
# ----------------------------
deaths_long <- deaths %>% 
  select(!1:5) %>%
  select(!`Drowned (Descriptive Text)`) %>% 
  select(!`Killed (Descriptive Text)`) %>% 
  select(!`Suicide (Descriptive Text)`) %>% 
  select(!`Other Casualties (Descriptive Text)`) %>% 
  pivot_longer(8:109, 
               names_to = 'death', 
               values_to = 'count')

# Lowercase column names and replace spaces with underscores
names(deaths_long) <- tolower(names(deaths_long))
names(deaths_long) <- gsub(" ", "_", names(deaths_long))

write_csv(deaths_long, "data/deaths.csv", na = "")

# Parish list
# ----------------------------
parishes_long <- parishes %>% 
  select(!1:5) %>% 
  pivot_longer(7:284,
               names_to = 'parish_name',
               values_to = 'count')

# Lowercase column names and replace spaces with underscores.
names(parishes_long) <- tolower(names(parishes_long))
names(parishes_long) <- gsub(" ", "_", names(parishes_long))
parishes_long$year <- str_sub(parishes_long$unique_identifier, 1, 4)

# Separate out a parish name from the count type (plague vs. burial)
# Remove whitespace with str_trim().
parishes_long <- parishes_long %>% separate(parish_name, c("parish_name", "count_type"), sep = "[-]")
parishes_long <- parishes_long %>%
  mutate(count_type = str_trim(count_type))

# Find all unique values for parish name, week, and year. These will be 
# referenced as foreign keys in PostgreSQL.
## TODO: Drop parish names that include 'Christened' 'Buried' 'Plague'
parishes_unique <- parishes_long %>% 
  select(parish_name) %>% 
  distinct() %>% 
  arrange() %>% 
  mutate(id = row_number()) %>% 
  mutate(parish_id = str_pad(id, 4, pad = "0")) %>% 
  select(-id)

week_unique <- parishes_long %>% 
  select(year, week, start_day, end_day, start_month, end_month, unique_identifier) %>% 
  distinct() %>% 
  mutate(year = as.integer(year)) %>% 
  # To get a leading zero and not mess with the math below, we create a temporary
  # column to pad the week number with a leading zero and use that for 
  # creating the week ID string.
  mutate(week_tmp = str_pad(week, 2, pad = "0")) %>% 
  mutate(week = as.integer(week)) %>%
  mutate(week_id = ifelse(week > 15,
                          paste0(
                            #year - 1, '-', year, '-', week_tmp
                            year - 1, '-', year, '-', week_tmp
                          ),
                          paste0(
                            #year, '-', year + 1, '-', week_tmp
                            year, '-', year + 1, '-', week_tmp
                          )
  )
  ) %>% 
  select(-week_tmp)

year_unique <- parishes_long %>% 
  select(year) %>% 
  distinct() %>% 
  arrange() %>% 
  mutate(year_id = as.integer(year)) %>% 
  mutate(year = as.integer(year))

death_unique <- deaths_long %>% 
  select(death) %>% 
  distinct() %>% 
  arrange() %>% 
  mutate(id = row_number()) %>% 
  mutate(death_id = str_pad(id, 3, pad = "0")) %>% 
  mutate(death_id = str_replace(death_id,"(\\d{1})(\\d{1})(\\d{1})$","\\1-\\2-\\3")) %>% 
  select(-id)

# Match unique parish IDs with the long parish table, and drop the parish
# name from the long table. We'll use SQL foreign keys to keep the relationship
# by parish_id in parishes_long and parishes_unique.
parishes_long <- dplyr::inner_join(parishes_long, parishes_unique, by = "parish_name") %>% 
  select(-parish_name)

# Match unique week IDs to the long parish table, and drop the existing 
# start and end months and days from long_parish so they're only referenced
# through the unique week ID.
parishes_long <- parishes_long %>% 
  select(-week, -start_day, -end_day, -start_month, -end_month, -year) %>% 
  dplyr::left_join(week_unique, by = "unique_identifier") %>% 
  select(-week, -start_day, -end_day, -start_month, -end_month, -unique_identifier)

# Match unique year IDs to the long parish table, and drop the existing
# year column from long_parishes so they're only referenced
# through the unique year ID.
parishes_long <- parishes_long %>% 
  dplyr::left_join(year_unique, by = "year") %>% 
  select(-year)

# After we have unique years, we need to join the year ID to the 
# unique weeks and parishes_long. 
week_unique <- week_unique %>% 
  mutate(year = str_sub(week_unique$unique_identifier, 1, 4)) %>% 
  mutate(year = as.integer(year)) %>% 
  dplyr::left_join(year_unique, by = "year") %>% 
  select(-year)
  
# Write to CSV
write_csv(parishes_long, "data/parishes.csv", na = "")
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")
write_csv(week_unique, "data/week_unique.csv", na = "")
write_csv(year_unique, "data/year_unique.csv", na = "")

# Separate dataframes for christenings, births, plague, and foodstuffs
# ----------------------------
parishes_filtering <- parishes %>% 
  select(!1:5) %>% 
  pivot_longer(7:284,
               names_to = 'parish_name',
               values_to = 'count')

parishes_filtering$christening_detect <- str_detect(parishes_filtering$parish_name, "Christened")
parishes_filtering$burials_detect <- str_detect(parishes_filtering$parish_name, "Buried")
parishes_filtering$plague_detect <- str_detect(parishes_filtering$parish_name, "Plague in")

christenings <- parishes_filtering %>% 
  dplyr::filter(christening_detect == TRUE) %>% 
  select(-christening_detect, -burials_detect, -plague_detect)
burials <- parishes_filtering %>% 
  dplyr::filter(burials_detect == TRUE) %>% 
  select(-christening_detect, -burials_detect, -plague_detect)
plague <- parishes_filtering %>% 
  dplyr::filter(plague_detect == TRUE) %>% 
  select(-christening_detect, -burials_detect, -plague_detect)

rm(parishes_filtering)

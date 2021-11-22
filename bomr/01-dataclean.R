# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates two CSV files of long tables for the 
# parishes and types of death.
# 
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2021-11-22

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
  pivot_longer(9:109, 
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

# Lowercase column names and replace spaces with underscores
names(parishes_long) <- tolower(names(parishes_long))
names(parishes_long) <- gsub(" ", "_", names(parishes_long))
parishes_long$year <- str_sub(parishes_long$unique_identifier, 1, 4)

# Separate out a parish name from the count type (plague vs. burial)
parishes_long <- parishes_long %>% separate(parish_name, c("parish_name", "count_type"), sep = "[-]")

# Find all unique values for parish name, week, and year. These will be 
# referenced as foreign keys in PostgreSQL.
parishes_unique <- parishes_long %>% 
  select(parish_name) %>% 
  distinct() %>% 
  arrange() %>% 
  mutate(id = row_number()) %>% 
  mutate(parish_id = str_pad(id, 3, pad = "0")) %>% 
  mutate(parish_id = str_replace(parish_id,"(\\d{1})(\\d{1})(\\d{1})$","\\1-\\2-\\3")) %>% 
  select(-id)

week_unique <- parishes_long %>% 
  select(week, start_day, end_day, start_month, end_month, unique_identifier) %>% 
  distinct() %>% 
  mutate(id = row_number()) %>% 
  mutate(week_id = str_pad(id, 3, pad = "0")) %>% 
  mutate(week_id = str_replace(week_id,"(\\d{1})(\\d{1})(\\d{1})$","\\1-\\2-\\3")) %>% 
  select(-id)

year_unique <- parishes_long %>% 
  select(year) %>% 
  distinct() %>% 
  arrange() %>% 
  mutate(id = row_number()) %>% 
  mutate(year_id = str_pad(id, 3, pad = "0")) %>% 
  mutate(year_id = str_replace(year_id,"(\\d{1})(\\d{1})(\\d{1})$","\\1-\\2-\\3")) %>% 
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
  select(-week, -start_day, -end_day, -start_month, -end_month) %>% 
  dplyr::left_join(week_unique, by = "unique_identifier") %>% 
  select(-week, -start_day, -end_day, -start_month, -end_month, -unique_identifier)

# Match unique week IDs to the long parish table, and drop the existing
# year column from long_parishes so they're only referenced
# through the unique year ID.
parishes_long <- parishes_long %>% 
  dplyr::left_join(year_unique, by = "year") %>% 
  select(-year)

# After we have unique years, we need to join the year ID to the 
# unique weeks and parishes_long. 
week_unique <- week_unique %>% 
  mutate(year = str_sub(week_unique$unique_identifier, 1, 4)) %>% 
  dplyr::left_join(year_unique, by = "year") %>% 
  select(-year)
  
# Write to CSV
write_csv(parishes_long, "data/parishes.csv", na = "")
write_csv(parishes_unique, "data/parishes_unique.csv", na = "")
write_csv(week_unique, "data/week_unique.csv", na = "")
write_csv(year_unique, "data/year_unique.csv", na = "")

# TODO: Separate dataframes for christenings and foodstuffs
# ----------------------------
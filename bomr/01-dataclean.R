# This exists for the purpose of cleaning up and rearranging a DataScribe export
# for the Bills of Mortality. It creates two CSV files of long tables for the 
# parishes and types of death.
# 
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media

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
parishes_long$year <- paste0(1669)

# Separate out a parish name from the count type (plague vs. burial)
parishes_long <- parishes_long %>% separate(parish_name, c("parish_name", "count_type"), sep = "[-]")

write_csv(parishes_long, "data/parishes.csv", na = "")

# TODO: Separate dataframes for christenings and foodstuffs
# ----------------------------
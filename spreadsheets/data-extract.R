library(tidyverse)
library(readxl)
library(jsonlite)

data <- read_excel("1665-10.xlsx", skip=1)

parishdata <- data %>% 
  # grab our data columns for each parish 
  slice(1:48) %>% 
  rename(
    parish = ...1, burials = Bur....2, plague = Plag....3,
    parish1 = ...4, burials1 = Bur....5, plague1 = Plag....6,
    parish2 = ...7, burials2 = Bur....8, plague2 = Plag....9
  ) %>%  
  type_convert()

parishdata <- bind_rows(
  parishdata %>% select(parish, burials, plague),
  parishdata %>% select(parish = parish1, burials = burials1, plague = plague1),
  parishdata %>% select(parish = parish2, burials = burials2, plague = plague2)
) 
  
#parishdata <- parishdata %>% 
#  add_column(year = 1664, span = "1664-12-20--1664-12-27")

write_json(parishdata, "data.json")

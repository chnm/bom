# Data checks stratchpad 

# Various things are here to double check the data if we run into any Postgres
# check constraints or other errors. 

library(tidyverse)

# -----------
# Week values
# -----------

# Check the unique check constraints in the week values
week_unique |> 
  select(start_day) |> 
  distinct() |> 
  arrange(start_day) |> View()

week_unique |> 
  select(end_day) |> 
  distinct() |> 
  arrange(end_day) |> View()

week_unique |> 
  select(week_number) |> 
  distinct() |> 
  arrange(week_number) |> View()

## TODO: A week number of "07" is getting introduced into the week numbers somewhere,
## which violates the check constraint. 
## A quick, temporary fix: 
week_unique$week_number[4191] <- "7"

# -----------
# Year Values
# -----------
# Incorrect year value in the data
## TODO: There seems to be a fumble on a year, which introduces "1976" and 
## violates the year check constraint. 
## A quick, temporary fix is to remove the final row: 
year_unique <- year_unique[-nrow(year_unique), ]

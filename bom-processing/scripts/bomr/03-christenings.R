# This script handles the christenings data from the DataScribe exports.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2023-02-24

library(tidyverse)

# ----------------------------------------------------------------------
# Data sources
# ----------------------------------------------------------------------
raw_wellcome_causes <- read_csv("bom-data/data-csvs/2022-04-06-Wellcome-weeklybills-causes.csv")
raw_laxton_1700_causes <- read_csv("bom-data/data-csvs/2022-06-15-Laxton-1700-weeklybills-causes.csv")
raw_laxton_causes <- read_csv("bom-data/data-csvs/2022-11-02-Laxton-weeklybills-causes.csv")

# ----------------------------------------------------------------------
# Christenings
# ----------------------------------------------------------------------
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
write_csv(christenings, "bom-processing/scripts/bomr/data/christenings_by_gender.csv", na = "")

# This script handles the foodstuffs data from the DataScribe exports.
#
# Jason A. Heppler | jason@jasonheppler.org
# Roy Rosenzweig Center for History and New Media
# Updated: 2023-02-24

library(tidyverse)

# ----------------------------------------------------------------------
# Data sources
# ----------------------------------------------------------------------
raw_laxton_foodstuffs <- read_csv("../../../bom-data/data-csvs/2022-09-19-Laxton-1700-weeklybills-foodstuffs.csv")

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

write_csv(foodstuffs_laxton, "data/foodstuffs.csv", na = "")

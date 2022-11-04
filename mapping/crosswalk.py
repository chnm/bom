#!/usr/bin/env python3

# We need to cross-walk two tables: monarchs-bills.xlxs and cross-walk.xlsx.  
# The cross-walk.xlsx file has a column for the canoncialDBN and 
# monarchicalParish. We need to match the  monarchicalParish column to the 
# "parish" column in the monarchs-bills.xlsx file. The output should be a new 
# file that includes all of the data from monarchs-bills.xlsx plus a new column 
# for the canonicalDBN.

import pandas as pd

# Read in the two files
monarchs = pd.read_excel("monarchs-bills.xlsx", sheet_name="counts")
crosswalk = pd.read_excel("cross-walk.xlsx", sheet_name="parishes")

# Merge the two files
merged = pd.merge(monarchs, crosswalk, left_on="parish", right_on="monarchicalParish")
# Then, drop the "monarchicalParish" column
merged = merged.drop(columns=["monarchicalParish"])

# Write the output to excel and csv.
merged.to_excel("monarchs-bills-merged.xlsx", index=False)
merged.to_csv("monarchs-bills-merged.csv", index=False, na_rep="")

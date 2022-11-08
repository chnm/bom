#!/usr/bin/env python3

# We need to cross-walk two tables: monarchs-bills.xlxs and cross-walk.xlsx.  
# The cross-walk.xlsx file has a column for the canoncialDBN and 
# monarchicalParish. We need to match the  monarchicalParish column to the 
# "parish" column in the monarchs-bills.xlsx file. The output should be a new 
# file that includes all of the data from monarchs-bills.xlsx plus a new column 
# for the canonicalDBN.

import pandas as pd
import geopandas as gpd

# Read in the two files.
monarchs = pd.read_excel("monarchs-bills.xlsx", sheet_name="counts")
crosswalk = pd.read_excel("cross-walk.xlsx", sheet_name="parishes")

# Merge the two files.
merged = pd.merge(monarchs, crosswalk, left_on="parish", right_on="monarchicalParish")
# Then, drop the "monarchicalParish" column
merged = merged.drop(columns=["monarchicalParish"])

# Write the output to excel and csv.
merged.to_excel("monarchs-bills-merged.xlsx", index=False)
merged.to_csv("monarchs-bills-merged.csv", index=False, na_rep="")

# After the crosswalk is completed, we want to join the new monarchs-bills-merged.csv
# to the shapefile. We will join the csv's canoncialDBN colun to the shapefile's 
# DBN_PAR column. The output should be a new shapefile that includes all of the
# data from the shapefile plus the new columns from the csv.

# Read the shapefile
parishes = gpd.read_file("../parish-shapefiles/WithinTheBills1671/WithinTheBills1671.shp")

# Join the csv to the shapefile.
parishes = parishes.merge(merged, left_on="DBN_PAR", right_on="canonicalDBN")
# Ensure that "count", "parishTotal", and "parishPlague" are integers not floats.
parishes["count"] = parishes["count"].astype('Int64')
parishes["parishTotal"] = parishes["parishTotal"].astype('Int64')
parishes["parishPlague"] = parishes["parishPlague"].astype('Int64')
# Replace NaN with empty strings.
parishes["count"] = parishes["count"].fillna(pd.NA)
parishes["parishTotal"] = parishes["parishTotal"].fillna(pd.NA)
parishes["parishPlague"] = parishes["parishPlague"].fillna(pd.NA)

# Write the output to a new shapefile. 
parishes.to_crs(epsg=4326).to_file("parishes-merged.geojson", driver="GeoJSON")
parishes.to_file("../parish-shapefiles/merged/parishes-merged.shp", driver="ESRI Shapefile")
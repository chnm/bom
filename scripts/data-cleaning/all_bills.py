#! /usr/bin/env python3 

# This script exists for the purpose of cleaning up and rearranging a DataScribe
# export. It creates CSV files of long tables for the weekly and general bills, 
# as well as a CSV of the two tables combined.

import pandas as pd
# import os

# Read in the DataScribe exports as Pandas dataframes.
# -----------------------------------------------------
raw_wellcome_weekly = pd.read_csv('../../datascribe-exports/2022-04-06-1669-1670-Wellcome-weeklybills-parishes.csv')
raw_laxton_weekly = pd.read_csv('../../datascribe-exports/2022-11-02-Laxton-weeklybills-parishes.csv')
raw_bodleian = pd.read_csv('../../datascribe-exports/2022-11-02-Bodleian-V1-weeklybills-parishes.csv')
raw_millar_general = pd.read_csv('../../datascribe-exports/2022-04-06-millar-generalbills-postplague-parishes.csv')

# Weekly Bills
# ------------

# Extract the weekly bills from the following exports:
# 1. raw_laxton_weekly
# 2. raw_wellcome_weekly
# 3. raw_bodleian

# We want to avoid the first five columns of the raw_laxton_weekly and convert 
# to a long table for the remaining columns. Keep all columns.

# Create a new dataframe with the first five columns of raw_laxton_weekly.
# laxton_weekly = raw_laxton_weekly.iloc[:, 0:5]

# # Create a new dataframe with the remaining columns of raw_laxton_weekly.
# laxton_weekly_long = raw_laxton_weekly.iloc[:, 5:]

# # Convert the laxton_weekly_long dataframe to a long table.
# laxton_weekly_long = laxton_weekly_long.stack().reset_index()

# Extract the weekly bills from the raw_laxton_weekly.
laxton_weekly = raw_laxton_weekly.iloc[:, 5:]
laxton_weekly.stack().reset_index()
# laxton_weekly = laxton_weekly.melt(id_vars=['Unique ID'], var_name='parish', value_name='count')

# Print column names to terminal
print(laxton_weekly)

# laxton_weekly_long = raw_laxton_weekly.iloc[:,5:]
# laxton_weekly_long = laxton_weekly_long.drop(columns=['Descriptive'])
# laxton_weekly_long = laxton_weekly_long.melt(id_vars=['parish_name'], var_name='count', value_name='count')

# # laxton_weekly_long = raw_laxton_weekly.iloc[:, 8:167].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
# laxton_weekly_long['Cause'] = laxton_weekly_long['Cause'].str.strip()
# laxton_weekly_long['Death'] = laxton_weekly_long['Death'].str.strip()

# # We want to avoid the first five columns of the raw_wellcome_weekly, remove the "Descriptive" column,
# # and convert to a long table for columsn 8:109. We also want to trim white space from the "death" column.
# wellcome_weekly_long = raw_wellcome_weekly.iloc[:, 8:285].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
# wellcome_weekly_long['Cause'] = wellcome_weekly_long['Cause'].str.strip()
# wellcome_weekly_long['Death'] = wellcome_weekly_long['Death'].str.strip()

# # We want to avoid the first five columns of the raw_bodleian, remove the "Descriptive" column,
# # and convert to a long table for columsn 8:109. We also want to trim white space from the "death" column.
# bodleian_weekly_long = raw_bodleian.iloc[:, 5:109].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
# bodleian_weekly_long['Cause'] = bodleian_weekly_long['Cause'].str.strip()
# bodleian_weekly_long['Death'] = bodleian_weekly_long['Death'].str.strip()

# General bills
# -------------

# Extract the general bills from the following exports:
# 1. raw_millar_general

# We want to avoid the first five columns of the raw_millar_general, remove the "Descriptive" column,
# and convert to a long table for columsn 8:109. We also want to trim white space from the "death" column.
# millar_general_long = raw_millar_general.iloc[:, 5:109].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
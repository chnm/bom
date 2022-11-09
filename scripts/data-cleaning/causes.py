#! /usr/bin/env python3 

import pandas as pd

# Read in the DataScribe exports as Pandas dataframes.
# -----------------------------------------------------
raw_wellcome_causes = pd.read_csv('Wellcome Weekly 2020-07-01 - Causes of Death.csv')
raw_laxton_1700_causes = pd.read_csv('Laxton 1700-1799 Causes of Death.csv')
raw_laxton_causes = pd.read_csv('Laxton Causes of Death.csv')

# Causes of death tables
# ----------------------

# Extract the causes of death from the following exports:
# 1. raw_wellcome_causes
# 2. raw_laxton_1700_causes
# 3. raw_laxton_causes

# We want to avoid the first five columns of the raw_wellcome_causes, remove the "Descriptive" column,
# and convert to a long table for columsn 8:109. We also want to trim white space from the "death" column.
wellcome_causes_long = raw_wellcome_causes.iloc[:, 5:109].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
wellcome_causes_long['Cause'] = wellcome_causes_long['Cause'].str.strip()
wellcome_causes_long['Death'] = wellcome_causes_long['Death'].str.strip()

# We want to avoid the first five columns of the raw_laxton_1700_causes, remove the "Descriptive" column,
# and convert to a long table for columsn 8:109. We also want to trim white space from the "death" column.
laxton_1700_causes_long = raw_laxton_1700_causes.iloc[:, 5:109].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
laxton_1700_causes_long['Cause'] = laxton_1700_causes_long['Cause'].str.strip()
laxton_1700_causes_long['Death'] = laxton_1700_causes_long['Death'].str.strip()

# We want to avoid the first five columns of the raw_laxton_causes, remove the "Descriptive" column,
# and convert to a long table for columsn 8:109. We also want to trim white space from the "death" column.
laxton_causes_long = raw_laxton_causes.iloc[:, 5:109].melt(id_vars=['Parish', 'Year', 'Month', 'Week', 'Death'], var_name='Cause', value_name='Deaths')
laxton_causes_long['Cause'] = laxton_causes_long['Cause'].str.strip()
laxton_causes_long['Death'] = laxton_causes_long['Death'].str.strip()

# For each of the new long tables, we want to lowercase the column names and add underscores
# to the column names that contain spaces.
wellcome_causes_long.columns = wellcome_causes_long.columns.str.lower().str.replace(' ', '_')
laxton_1700_causes_long.columns = laxton_1700_causes_long.columns.str.lower().str.replace(' ', '_')
laxton_causes_long.columns = laxton_causes_long.columns.str.lower().str.replace(' ', '_')

# Now, we combine the three long tables into one.
causes_long = pd.concat([wellcome_causes_long, laxton_1700_causes_long, laxton_causes_long], ignore_index=True)
# Then, select only the distinct causes of death.
causes_long = causes_long.drop_duplicates(subset=['cause'])
# Now we need to remove any rows that contain the following: 
causes_long = causes_long[~causes_long['cause'].str.contains('\\bBuried', regex=True)]
causes_long = causes_long[~causes_long['cause'].str.contains('\\bChristened', regex=True)]
causes_long = causes_long[~causes_long['cause'].str.contains('\\bPlague Deaths', regex=True)]
causes_long = causes_long[~causes_long['cause'].str.contains('\\bOunces in', regex=True)]
causes_long = causes_long[~causes_long['cause'].str.contains('\\bIncrease/Decrease', regex=True)]
causes_long = causes_long[~causes_long['cause'].str.contains('\\bParishes Clear', regex=True)]
causes_long = causes_long[~causes_long['cause'].str.contains('\\bParishes Infected', regex=True)]

# Now, arrange the data in alphabetical order by cause of death and add a unique row ID.
causes_long = causes_long.sort_values(by=['cause'])
causes_long['id'] = causes_long.index + 1

# Now, we want to write the tables to a CSV file.
causes_long.to_csv('data/deaths_unique.csv', index=False)
wellcome_causes_long.to_csv('data/deaths_wellcome.csv', index=False)
laxton_1700_causes_long.to_csv('data/deaths_laxton_1700.csv', index=False)
laxton_causes_long.to_csv('data/deaths_laxton.csv', index=False)
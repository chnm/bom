# bomr

This directory contains R scripts for transforming raw data exports from [DataScribe](https://github.com/chnm/Datascribe-module) into CSV files used for importing into a PostgreSQL database. 

## 01-dataclean.R

This file handles most of the work in developing the datasets for importing into PostgreSQL. The file does several things to the DataScribe files: 

1. Weekly and general bills are pivoted into long tables, which also adds the columns `parish_name` and `count`
2. Mentions of plague, christenings, and burials are extracted into their own dataframes and written as CSVs.
3. With the provided data, the script generates a dataframe of unique weeks which are then assigned their own unique IDs that we use as foreign keys in PostgreSQL.

## `data/` Directory 

The data directory contains transcribed data that's been tidied.

- `all_bills.csv`: This contains all of the weekly and general bills. This data is also available in the data API. 
- `all_christenings.csv`: This contains all of the christenings data. This data is also available in the data API. These are compiled from the following datasets:
  - `laxton_christenings.csv`
  - `wellcome_christenings.csv`
- `bills_general.csv`: This is only the general bills data. It's combined with `all_bills.csv`.
- `bills_weekly.csv`: This is only the weekly bills data. It's combined with `all_bills.csv`.
- `burials_counts.csv`: This is burial data. It is not currently available in the API. 
- `causes_of_death.csv`: This is causes of death across the bills and their associated values. This data is also available in the data API. This is compiled from the following datasets: 
  - `laxton_causes_1700.csv`
  - `laxton_causes.csv`
  - `wellcome_causes.csv`
- `christenings_counts.csv`: 
- `deaths_unique.csv`: This is a list of unique deaths across the datasets.
- `foodstuffs.csv`: This is foodstuffs data extracted from the transcriptions. It is not currently available from the data API.
- `week_unique.csv`: These are the unique weeks across the datasets. This is also available in the data API.
- `year_unique.csv`: These are the unique years across the datasets.

## Makefile

This directory contains a Makefile for aiding in using [Datasette](http://datasette.io) and primarily exists here to explore and double-check the data locally. 

Requirements for using the Makefile are:

- Datasette (`brew install datasette` or `pip install datasette`)
- SQLite (`brew install sqlite`)

The commands are:

- `create`: This creates an sqlite `data.db` file, if none exists.
- `insert`: This inserts the CSV records into `data.db`.
- `schema`: This lets you look over the schema of the database.
- `serve`: This locally serves `data.db` in Datasette.

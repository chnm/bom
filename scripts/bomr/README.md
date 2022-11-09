# bomr

This directory contains R scripts for transforming raw data exports from [DataScribe](https://github.com/chnm/Datascribe-module) into CSV files used for importing into a PostgreSQL database. 

## 01-dataclean.R

This file handles most of the work in developing the datasets for importing into PostgreSQL. The file does several things to the DataScribe files: 

1. Weekly and general bills are pivoted into long tables, which also adds the columns `parish_name` and `count`
2. Mentions of plague, christenings, and burials are extracted into their own dataframes and written as CSVs.
3. With the provided data, the script generates a dataframe of unique weeks which are then assigned their own unique IDs that we use as foreign keys in PostgreSQL.

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

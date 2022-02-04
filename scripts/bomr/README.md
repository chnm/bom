# bomr

This directory contains R scripts for transforming raw data exports from [DataScribe](https://github.com/chnm/Datascribe-module) into CSV files used for importing into a PostgreSQL database. 

## 01-dataclean.R

This file handles most of the work in developing the datasets for importing into PostgreSQL. The file does several things to the DataScribe files: 

1. Weekly and general bills are pivoted into long tables, which also adds the columns `parish_name` and `count`
2. Mentions of plague, christenings, and burials are extracted into their own dataframes and written as CSVs.
3. With the provided data, the script generates a dataframe of unique weeks which are then assigned their own unique IDs that we use as foreign keys in PostgreSQL.

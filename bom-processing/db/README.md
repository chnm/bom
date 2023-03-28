# Database updates

Database updates are run throught the `insert_update.sql` file once the `bomr` scripts have transformed the data. 

Requirements: 

- `make`
- the `BOM_DB_STR` PostgreSQL query string available in your shell environment.

The `Makefile` handles the work in the following ways: 

- `make update`: runs `insert_update.sql`, copying data from the transformed CSV files and inserting the data in the appropriate database tables. 
- `make init-up`: creates the database tables and schema if there are none.
- `make init-down`: drops all database tables. This is destructive, use with caution.



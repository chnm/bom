# bom-processing

This directory contains scripts and documentation related to data processing.

- **api-docs** contains documentation for the API
- **db** contains SQL migration scripts
  - **updater**: A small Go program handling ETL from DataScribe exports.
- **mapping** contains
- **monarchical-bills** contains a catalog of extant reports to the monarch, in-progress transcriptions, and a parish name crosswalk
- **scripts** contains
  - **bomr**: R scripts for processing DataScribe outputs suitable for our PostgreSQL database. Data prepped here becomes used by the **updater** program.
  - **python-analysis**: Python scripts for analyzing and data-checking the transcribed bills.
  - The BOM Catalog Excel file is in progress and does not contain all bills known to the project; it currently focuses on bills from the 1630s-1690s. For the Bills of Mortality database code, see `/bom-db`
  - Files associated with the early stage of this project are also available at https://github.com/jmotis/billsofmortality
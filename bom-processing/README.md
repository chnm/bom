# bom-processing

This directory contains scripts and documentation related to data processing.

- **api-docs** contains documentation for the API
- **db** contains SQL migrations 
  - **updater**: A small Go program handling ETL from DataScribe exports.
- **mapping** contains
- **monarchical-bills** contains a catalog of extant reports to the monarch, in-progress transcriptions, and a parish name crosswalk
- **scripts** contains
  - **bompy**: Python package for processing DataScribe outputs suitable for our PostgreSQL database. Data prepped here becomes used by the **updater** program.
  - **python-analysis**: Python scripts for analyzing and data-checking the transcribed bills.
  - The BOM Catalog Excel file is in progress and does not contain all bills known to the project; it currently focuses on bills from the 1630s-1690s.

## Testing with Dummy Data

For our records, we stress-tested the database (2025-06-10) by generating a copy of the data as dummy data that allowed us to work with 1,600,000+ rows. We generated the extra data with the following SQL: 

```sql
INSERT INTO bom.bill_of_mortality (
    parish_id, count_type, count, year, week_id, bill_type, 
    missing, illegible, source, unique_identifier
)
SELECT 
    parish_id, 
    count_type || '_DUMMY' AS count_type,  -- Suffix count_type to make combinations unique
    count, 
    year,
    week_id, 
    bill_type,
    missing, 
    illegible, 
    'DUMMY_DATA_' || CURRENT_DATE::text AS source,
    'DUMMY_' || COALESCE(unique_identifier, id::text) AS unique_identifier
FROM bom.bill_of_mortality
WHERE source IS NULL OR source NOT LIKE 'DUMMY_DATA_%';
```

We can remove this dummy data with the following SQL: 

```sql
DELETE FROM bom.bill_of_mortality WHERE count_type LIKE '%_DUMMY';
```

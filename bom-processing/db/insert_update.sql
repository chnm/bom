-- This accepts the CSV files from scripts/bomr/data and inserts the data into their
-- respective tables.
-- The CSV files are generated by scripts/bomr/01-bills.R, 02-foodstuffs.R, and 03-christenings.R 
-- and are stored in the bomr data directory.

-- bom.years
-- This table contains the unique years in the dataset.
CREATE TEMPORARY TABLE IF NOT EXISTS temp_year (
    year text,
    year_id integer,
    id integer
);
COPY temp_year FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/year_unique.csv' DELIMITER ',' CSV HEADER;
INSERT INTO bom.year (year)
SELECT DISTINCT year FROM temp_year
ON CONFLICT DO NOTHING;

-- bom.weeks
-- This table contains the unique weeks in the dataset.
CREATE TEMPORARY TABLE IF NOT EXISTS temp_week (
    year integer,
    week_number integer,
    start_day integer,
    end_day integer,
    start_month text,
    end_month text,
    unique_identifier text,
    week_id text,
    year_range text,
    split_year text,
    joinid text

);
COPY temp_week FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/week_unique.csv' DELIMITER ',' CSV HEADER;
INSERT INTO bom.week (joinid, start_day, start_month, end_day, end_month, year, week_no, split_year)
SELECT DISTINCT joinid, start_day, start_month, end_day, end_month, year, week_number, split_year FROM temp_week
ON CONFLICT DO NOTHING;

-- -- bom.parishes
-- -- This table contains the unique parishes in the dataset.
CREATE TEMPORARY TABLE IF NOT EXISTS temp_parish (
    parish_name text NOT NULL,
    canonical_name text NOT NULL,
    parish_id integer
);
COPY temp_parish FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/parishes_unique.csv' DELIMITER ',' CSV HEADER;
INSERT INTO bom.parishes (id, parish_name, canonical_name)
SELECT DISTINCT parish_id, parish_name, canonical_name FROM temp_parish
ON CONFLICT DO NOTHING;

-- -- bom.christenings
-- -- This table contains the unique christenings in the dataset.
CREATE TEMPORARY TABLE IF NOT EXISTS temp_christening (
    year text,
    week text,
    unique_identifier text,
    start_day int,
    start_month text,
    end_day int,
    end_month text,
    parish_name text,
    count int,
    bill_type text,
    joinid text
);
COPY temp_christening FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/christenings_by_parish.csv' DELIMITER ',' CSV HEADER;
INSERT INTO bom.christenings (christening, count, week_number, start_day, start_month, end_day, end_month, year)
SELECT DISTINCT parish_name, count, week, start_day, start_month, end_day, end_month, year FROM temp_christening
ON CONFLICT DO NOTHING;

-- -- bom.cause_of_death
-- -- This table contains the unique causes of death in the dataset.
CREATE TEMPORARY TABLE IF NOT EXISTS temp_causes_of_death (
    death text,
    count int,
    descriptive_text text,
    joinid text,
    year text,
    week_id text,
    year_range text,
    split_year text
);
COPY temp_causes_of_death FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/causes_of_death.csv' DELIMITER ',' CSV HEADER;
INSERT INTO bom.causes_of_death (death, count, year, week_id, descriptive_text)
SELECT DISTINCT death, count, year, joinid, descriptive_text FROM temp_causes_of_death
ON CONFLICT DO NOTHING;

-- -- bom.bills
-- -- This table contains all the bills in the dataset.
CREATE TEMPORARY TABLE IF NOT EXISTS temp_bills (
    unique_identifier text,
    count_type text,
    count int,
    bill_type text,
    parish_id int,
    year text,
    week_id text,
    year_range text,
    split_year text,
    joinid text,
    id int
);
COPY temp_bills FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/all_bills.csv' DELIMITER ',' CSV HEADER;
INSERT INTO bom.bill_of_mortality (parish_id, count_type, count, year_id, week_id, bill_type)
SELECT DISTINCT parish_id, count_type, count, year, joinid, bill_type FROM temp_bills
ON CONFLICT DO NOTHING;

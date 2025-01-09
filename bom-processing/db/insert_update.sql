--TRUNCATE TABLE bom.bill_of_mortality RESTART IDENTITY;
--TRUNCATE TABLE bom.causes_of_death RESTART IDENTITY;
--TRUNCATE TABLE bom.christening_locations RESTART IDENTITY;
--TRUNCATE TABLE bom.christenings RESTART IDENTITY;
--TRUNCATE TABLE bom.parish_collective RESTART IDENTITY;
--TRUNCATE TABLE bom.parishes RESTART IDENTITY CASCADE;
--TRUNCATE TABLE bom.week RESTART IDENTITY CASCADE;
--TRUNCATE TABLE bom.year RESTART IDENTITY CASCADE;

CREATE TABLE IF NOT EXISTS bom.data_load_log (
   load_id serial PRIMARY KEY,
   load_date timestamp DEFAULT CURRENT_TIMESTAMP,
   operation text NOT NULL,
   table_name text NOT NULL,
   rows_before integer,
   rows_processed integer,
   rows_after integer,
   success boolean DEFAULT false,
   error_message text,
   duration interval
);

BEGIN;

CREATE OR REPLACE FUNCTION bom.log_operation(
   p_operation text,
   p_table_name text,
   p_rows_before integer,
   p_rows_processed integer,
   p_rows_after integer,
   p_success boolean,
   p_error_message text DEFAULT NULL,
   p_duration interval DEFAULT NULL
)
RETURNS void AS $$
BEGIN
   INSERT INTO bom.data_load_log (
       operation, table_name, rows_before, rows_processed, rows_after,
       success, error_message, duration
   ) VALUES (
       p_operation, p_table_name, p_rows_before, p_rows_processed, p_rows_after,
       p_success, p_error_message, p_duration
   );
END;
$$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS temp_year CASCADE;
DROP TABLE IF EXISTS temp_week CASCADE;
DROP TABLE IF EXISTS temp_parish CASCADE;
DROP TABLE IF EXISTS temp_christening CASCADE;
DROP TABLE IF EXISTS temp_causes_of_death CASCADE;
DROP TABLE IF EXISTS temp_bills CASCADE;

CREATE TEMPORARY TABLE temp_year (
   year integer NOT NULL,
   year_id integer NOT NULL,
   id integer NOT NULL,
   CONSTRAINT temp_year_check CHECK (year > 1400 AND year < 1800)
);

CREATE TEMPORARY TABLE temp_week (
   year integer,
   week_no integer,
   start_day integer,
   end_day integer,
   start_month text,
   end_month text,
   unique_identifier text,
   week_id text,
   year_range text,
   joinid text,
   split_year text,
   CONSTRAINT temp_week_check CHECK (year > 1400 AND year < 1800)
);

CREATE TEMPORARY TABLE temp_parish (
   parish_name text NOT NULL,
   canonical_name text NOT NULL,
   parish_id integer
);

CREATE TEMPORARY TABLE temp_christening (
   year integer,
   week integer,
   unique_identifier text,
   start_day int,
   start_month text,
   end_day int,
   end_month text,
   parish_name text,
   count int,
   missing boolean,
   illegible boolean,
   source text,
   bill_type text,
   joinid text,
   start_year text,
   end_year text,
   count_type text,
   CONSTRAINT temp_christening_check CHECK (year > 1400 AND year < 1800)
);

CREATE TEMPORARY TABLE temp_causes_of_death (
   death text,
   count int,
   year integer,
   joinid text,
   descriptive_text text,
   source_name text
);

CREATE TEMPORARY TABLE temp_bills (
   unique_identifier text,
   parish_name text,
   count_type text,
   count int,
   missing boolean,
   illegible boolean,
   source text,
   bill_type text,
   start_year text,
   end_year text,
   joinid text,
   parish_id integer,
   year integer,
   split_year text
);

COPY temp_year FROM 'bom/bom-processing/scripts/bomr/data/year_unique.csv' DELIMITER ',' CSV HEADER;
COPY temp_week FROM 'bom/bom-processing/scripts/bomr/data/week_unique.csv' DELIMITER ',' CSV HEADER;
COPY temp_parish FROM 'bom/bom-processing/scripts/bomr/data/parishes_unique.csv' DELIMITER ',' CSV HEADER;
COPY temp_christening FROM 'bom/bom-processing/scripts/bomr/data/christenings_by_parish.csv' DELIMITER ',' CSV HEADER;
COPY temp_causes_of_death FROM 'bom/bom-processing/scripts/bomr/data/causes_of_death.csv' DELIMITER ',' CSV HEADER;
COPY temp_bills FROM 'bom/bom-processing/scripts/bomr/data/all_bills.csv' DELIMITER ',' CSV HEADER;

DO $$
DECLARE
   start_time timestamp;
   end_time timestamp;
   rows_before integer;
   rows_processed integer;
BEGIN
   -- Years
   start_time := clock_timestamp();
   SELECT COUNT(*) INTO rows_before FROM bom.year;
   
   INSERT INTO bom.year (year)
   SELECT DISTINCT year 
   FROM temp_year
   WHERE year IS NOT NULL
   ON CONFLICT (year) DO NOTHING;
   
   GET DIAGNOSTICS rows_processed = ROW_COUNT;
   end_time := clock_timestamp();
   
   PERFORM bom.log_operation(
       'INSERT', 'bom.year', rows_before, rows_processed,
       rows_before + rows_processed, true, NULL, end_time - start_time
   );

   -- Weeks
   start_time := clock_timestamp();
   SELECT COUNT(*) INTO rows_before FROM bom.week;
   
   INSERT INTO bom.week (
       year, week_no, start_day, end_day, start_month, end_month,
       unique_identifier, week_id, year_range, joinid, split_year
   )
   WITH unique_weeks AS (
       SELECT DISTINCT ON (joinid)
           year, week_no, start_day, end_day, start_month, end_month,
           unique_identifier, week_id, year_range, joinid, split_year
       FROM temp_week
       WHERE joinid IS NOT NULL 
       ORDER BY joinid, year DESC
   )
   SELECT * FROM unique_weeks
   ON CONFLICT (joinid) 
   DO UPDATE
   SET
       start_day = EXCLUDED.start_day,
       start_month = EXCLUDED.start_month,
       end_day = EXCLUDED.end_day,
       end_month = EXCLUDED.end_month,
       year = EXCLUDED.year,
       week_no = EXCLUDED.week_no,
       split_year = EXCLUDED.split_year,
       unique_identifier = EXCLUDED.unique_identifier;
   
   GET DIAGNOSTICS rows_processed = ROW_COUNT;
   end_time := clock_timestamp();
   
   PERFORM bom.log_operation(
       'UPSERT', 'bom.week', rows_before, rows_processed,
       rows_before + rows_processed, true, NULL, end_time - start_time
   );

   -- Parishes
   start_time := clock_timestamp();
   SELECT COUNT(*) INTO rows_before FROM bom.parishes;
   
   INSERT INTO bom.parishes (id, parish_name, canonical_name)
   SELECT DISTINCT parish_id, parish_name, canonical_name 
   FROM temp_parish
   ON CONFLICT (parish_name) 
   DO UPDATE
   SET canonical_name = EXCLUDED.canonical_name
   WHERE bom.parishes.canonical_name IS DISTINCT FROM EXCLUDED.canonical_name;
   
   GET DIAGNOSTICS rows_processed = ROW_COUNT;
   end_time := clock_timestamp();
   
   PERFORM bom.log_operation(
       'UPSERT', 'bom.parishes', rows_before, rows_processed,
       rows_before + rows_processed, true, NULL, end_time - start_time
   );

   -- Christenings
   start_time := clock_timestamp();
   SELECT COUNT(*) INTO rows_before FROM bom.christenings;
   
   INSERT INTO bom.christenings (
    christening, count, week_number, start_day, start_month,
    end_day, end_month, year, missing, illegible, source,
    bill_type, joinid, unique_identifier
)
WITH deduplicated_christenings AS (
    SELECT DISTINCT ON (
        parish_name, week, start_day, start_month,
        end_day, end_month, year
    )
        parish_name, count, week, start_day, start_month,
        end_day, end_month, year, missing, illegible, 
        source, bill_type, joinid, unique_identifier
    FROM temp_christening c
    WHERE parish_name IS NOT NULL
    AND EXISTS (SELECT 1 FROM bom.week w WHERE w.joinid = c.joinid)
    ORDER BY 
        parish_name, week, start_day, start_month,
        end_day, end_month, year, count DESC
)
SELECT * FROM deduplicated_christenings
   ON CONFLICT (christening, week_number, start_day, start_month, end_day, end_month, year) 
   DO UPDATE
   SET 
       count = EXCLUDED.count,
       missing = EXCLUDED.missing,
       illegible = EXCLUDED.illegible,
       source = EXCLUDED.source,
       bill_type = EXCLUDED.bill_type,
       joinid = EXCLUDED.joinid,
       unique_identifier = EXCLUDED.unique_identifier;
   
   GET DIAGNOSTICS rows_processed = ROW_COUNT;
   end_time := clock_timestamp();
   
   PERFORM bom.log_operation(
       'UPSERT', 'bom.christenings', rows_before, rows_processed,
       rows_before + rows_processed, true, NULL, end_time - start_time
   );

   -- Causes of Death
   start_time := clock_timestamp();
   SELECT COUNT(*) INTO rows_before FROM bom.causes_of_death;
   
   INSERT INTO bom.causes_of_death (
    death, count, year, week_id, descriptive_text, source_name
)
SELECT DISTINCT 
    death, count, year, joinid, descriptive_text, source_name
FROM temp_causes_of_death c
WHERE death IS NOT NULL
AND EXISTS (SELECT 1 FROM bom.week w WHERE w.joinid = c.joinid)
ON CONFLICT (death, year, week_id) 
DO UPDATE
SET 
    count = EXCLUDED.count,
    descriptive_text = EXCLUDED.descriptive_text,
    source_name = EXCLUDED.source_name;
   
   GET DIAGNOSTICS rows_processed = ROW_COUNT;
   end_time := clock_timestamp();
   
   PERFORM bom.log_operation(
       'UPSERT', 'bom.causes_of_death', rows_before, rows_processed,
       rows_before + rows_processed, true, NULL, end_time - start_time
   );

   -- Bills of Mortality
   start_time := clock_timestamp();
   SELECT COUNT(*) INTO rows_before FROM bom.bill_of_mortality;
   
   INSERT INTO bom.bill_of_mortality (
       parish_id, count_type, count, year, week_id, bill_type,
       missing, illegible, source, unique_identifier
   )
   WITH deduplicated_bills AS (
   SELECT DISTINCT ON (parish_id, count_type, year, joinid)
       parish_id, count_type, count, year, joinid, bill_type,
       missing, illegible, source, unique_identifier
   FROM temp_bills b
   WHERE parish_id IS NOT NULL 
   AND joinid IS NOT NULL
   AND year IS NOT NULL
   AND EXISTS (SELECT 1 FROM bom.week w WHERE w.joinid = b.joinid)
   ORDER BY parish_id, count_type, year, joinid, count DESC
)
   SELECT * FROM deduplicated_bills
   ON CONFLICT (parish_id, count_type, year, week_id) 
   DO UPDATE
   SET 
       count = EXCLUDED.count,
       bill_type = EXCLUDED.bill_type,
       missing = EXCLUDED.missing,
       illegible = EXCLUDED.illegible,
       source = EXCLUDED.source,
       unique_identifier = EXCLUDED.unique_identifier;
   
   GET DIAGNOSTICS rows_processed = ROW_COUNT;
   end_time := clock_timestamp();
   
   PERFORM bom.log_operation(
       'UPSERT', 'bom.bill_of_mortality', rows_before, rows_processed,
       rows_before + rows_processed, true, NULL, end_time - start_time
   );

EXCEPTION WHEN OTHERS THEN
   PERFORM bom.log_operation(
       'ERROR', 'multiple', NULL, NULL, NULL, false,
       SQLERRM, clock_timestamp() - start_time
   );
   RAISE;
END $$;

COMMIT;

ANALYZE bom.bill_of_mortality;
ANALYZE bom.year;
ANALYZE bom.week;
ANALYZE bom.parishes;
ANALYZE bom.christenings;
ANALYZE bom.causes_of_death;

DO $$
BEGIN
   PERFORM bom.log_operation(
       'ANALYZE', 'all_tables', NULL, NULL, NULL, true, NULL, NULL
   );
END $$;


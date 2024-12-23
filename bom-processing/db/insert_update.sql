-- This accepts the CSV files from scripts/bomr/data and inserts the data into their
-- respective tables.
-- The CSV files are generated by scripts/bomr/01-bills.R, 02-foodstuffs.R, and 03-christenings.R 
-- and are stored in the bomr data directory.

-- Create a logging table
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

-- Start transaction
BEGIN;

-- Function for logging
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
        operation,
        table_name,
        rows_before,
        rows_processed,
        rows_after,
        success,
        error_message,
        duration
    ) VALUES (
        p_operation,
        p_table_name,
        p_rows_before,
        p_rows_processed,
        p_rows_after,
        p_success,
        p_error_message,
        p_duration
    );
END;
$$ LANGUAGE plpgsql;

-- Create necessary indexes
DO $$
DECLARE
    start_time timestamp;
    end_time timestamp;
BEGIN
    start_time := clock_timestamp();
    
    -- Create indexes if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_bill_mortality_parish') THEN
        CREATE INDEX CONCURRENTLY idx_bill_mortality_parish 
        ON bom.bill_of_mortality(parish_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_bill_mortality_year') THEN
        CREATE INDEX CONCURRENTLY idx_bill_mortality_year 
        ON bom.bill_of_mortality(year_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_bill_mortality_week') THEN
        CREATE INDEX CONCURRENTLY idx_bill_mortality_week 
        ON bom.bill_of_mortality(week_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_bill_mortality_composite') THEN
        CREATE INDEX CONCURRENTLY idx_bill_mortality_composite 
        ON bom.bill_of_mortality(parish_id, year_id, week_id);
    END IF;

    end_time := clock_timestamp();
    
    PERFORM bom.log_operation(
        'CREATE_INDEXES',
        'bom.bill_of_mortality',
        NULL,
        NULL,
        NULL,
        true,
        NULL,
        end_time - start_time
    );
END $$;

-- Ensure we're working with clean temporary tables
DROP TABLE IF EXISTS temp_year CASCADE;
DROP TABLE IF EXISTS temp_week CASCADE;
DROP TABLE IF EXISTS temp_parish CASCADE;
DROP TABLE IF EXISTS temp_christening CASCADE;
DROP TABLE IF EXISTS temp_causes_of_death CASCADE;
DROP TABLE IF EXISTS temp_bills CASCADE;

-- Create temporary tables with constraints
CREATE TEMPORARY TABLE temp_year (
    year integer NOT NULL,
    year_id integer NOT NULL,
    id integer NOT NULL,
    CONSTRAINT temp_year_check CHECK (year > 1400 AND year < 1800)
);
COPY temp_year FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/year_unique.csv' DELIMITER ',' CSV HEADER;


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
    CONSTRAINT temp_week_check CHECK (year > 1400 AND year < 1800)
);
COPY temp_week FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/week_unique.csv' DELIMITER ',' CSV HEADER;


CREATE TEMPORARY TABLE IF NOT EXISTS temp_parish (
    parish_name text NOT NULL,
    canonical_name text NOT NULL,
    parish_id integer
);
COPY temp_parish FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/parishes_unique.csv' DELIMITER ',' CSV HEADER;


CREATE TEMPORARY TABLE IF NOT EXISTS temp_christening (
    year integer,
    week integer,
    unique_identifier text,
    start_day int,
    start_month text,
    end_day int,
    end_month text,
    parish_name text,
    count int,
    bill_type text,
    joinid text
    CONSTRAINT temp_christening_check CHECK (year > 1400 AND year < 1800)
);
COPY temp_christening FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/christenings_by_parish.csv' DELIMITER ',' CSV HEADER;


CREATE TEMPORARY TABLE IF NOT EXISTS temp_causes_of_death (
    death text,
    count int,
    descriptive_text text,
    joinid text,
    year integer,
    week_id text,
    year_range text,
    split_year text
);
COPY temp_causes_of_death FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/causes_of_death.csv' DELIMITER ',' CSV HEADER;


CREATE TEMPORARY TABLE IF NOT EXISTS temp_bills (
    unique_identifier text,
    count_type text,
    count int,
    bill_type text,
    parish_id int,
    year integer,
    week_id text,
    year_range text,
    split_year text,
    joinid text,
    id int
);
COPY temp_bills FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/all_bills.csv' DELIMITER ',' CSV HEADER;

-- Load and process each data type within its own transaction
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
        'INSERT',
        'bom.year',
        rows_before,
        rows_processed,
        rows_before + rows_processed,
        true,
        NULL,
        end_time - start_time
    );

    -- Weeks
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO rows_before FROM bom.week;
    
    INSERT INTO bom.week (joinid, start_day, start_month, end_day, end_month, year, week_no, split_year)
    SELECT DISTINCT 
        joinid,
        start_day,
        start_month,
        end_day,
        end_month,
        year,
        week_number,
        split_year
    FROM temp_week
    ON CONFLICT (joinid) 
    DO UPDATE
    SET
        start_day = EXCLUDED.start_day,
        start_month = EXCLUDED.start_month,
        end_day = EXCLUDED.end_day,
        end_month = EXCLUDED.end_month,
        year = EXCLUDED.year,
        week_no = EXCLUDED.week_number,
        split_year = EXCLUDED.split_year
    WHERE 
        bom.week.start_day != EXCLUDED.start_day OR
        bom.week.start_month != EXCLUDED.start_month OR
        bom.week.end_day != EXCLUDED.end_day OR
        bom.week.end_month != EXCLUDED.end_month OR
        bom.week.year != EXCLUDED.year OR
        bom.week.week_no != EXCLUDED.week_number OR
        bom.week.split_year != EXCLUDED.split_year;
    
    GET DIAGNOSTICS rows_processed = ROW_COUNT;
    end_time := clock_timestamp();
    
    PERFORM bom.log_operation(
        'UPSERT',
        'bom.week',
        rows_before,
        rows_processed,
        rows_before + rows_processed,
        true,
        NULL,
        end_time - start_time
    );

    -- Continue with similar patterns for other tables...
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
        'UPSERT',
        'bom.parishes',
        rows_before,
        rows_processed,
        rows_before + rows_processed,
        true,
        NULL,
        end_time - start_time
    );

    -- Christenings
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO rows_before FROM bom.christenings;
    
    INSERT INTO bom.christenings (
        christening,
        count,
        week_number,
        start_day,
        start_month,
        end_day,
        end_month,
        year
    )
    SELECT DISTINCT 
        parish_name,
        count,
        week,
        start_day,
        start_month,
        end_day,
        end_month,
        year 
    FROM temp_christening
    ON CONFLICT (christening, week_number, start_day, start_month, end_day, end_month, year) 
    DO UPDATE
    SET count = EXCLUDED.count
    WHERE bom.christenings.count IS DISTINCT FROM EXCLUDED.count;
    
    GET DIAGNOSTICS rows_processed = ROW_COUNT;
    end_time := clock_timestamp();
    
    PERFORM bom.log_operation(
        'UPSERT',
        'bom.christenings',
        rows_before,
        rows_processed,
        rows_before + rows_processed,
        true,
        NULL,
        end_time - start_time
    );

    -- Causes of Death
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO rows_before FROM bom.causes_of_death;
    
    INSERT INTO bom.causes_of_death (
        death,
        count,
        year,
        week_id,
        descriptive_text
    )
    SELECT DISTINCT 
        death,
        count,
        year,
        joinid,
        descriptive_text 
    FROM temp_causes_of_death
    ON CONFLICT (death, year, week_id) 
    DO UPDATE
    SET 
        count = EXCLUDED.count,
        descriptive_text = EXCLUDED.descriptive_text
    WHERE bom.causes_of_death.count IS DISTINCT FROM EXCLUDED.count
       OR bom.causes_of_death.descriptive_text IS DISTINCT FROM EXCLUDED.descriptive_text;
    
    GET DIAGNOSTICS rows_processed = ROW_COUNT;
    end_time := clock_timestamp();
    
    PERFORM bom.log_operation(
        'UPSERT',
        'bom.causes_of_death',
        rows_before,
        rows_processed,
        rows_before + rows_processed,
        true,
        NULL,
        end_time - start_time
    );

    -- Bills of Mortality
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO rows_before FROM bom.bill_of_mortality;
    
    INSERT INTO bom.bill_of_mortality (
        parish_id,
        count_type,
        count,
        year_id,
        week_id,
        bill_type
    )
    SELECT DISTINCT 
        parish_id,
        count_type,
        count,
        year,
        joinid,
        bill_type 
    FROM temp_bills
    ON CONFLICT (parish_id, count_type, year_id, week_id) 
    DO UPDATE
    SET 
        count = EXCLUDED.count,
        bill_type = EXCLUDED.bill_type
    WHERE bom.bill_of_mortality.count IS DISTINCT FROM EXCLUDED.count
       OR bom.bill_of_mortality.bill_type IS DISTINCT FROM EXCLUDED.bill_type;
    
    GET DIAGNOSTICS rows_processed = ROW_COUNT;
    end_time := clock_timestamp();
    
    PERFORM bom.log_operation(
        'UPSERT',
        'bom.bill_of_mortality',
        rows_before,
        rows_processed,
        rows_before + rows_processed,
        true,
        NULL,
        end_time - start_time
    );

EXCEPTION WHEN OTHERS THEN
    PERFORM bom.log_operation(
        'ERROR',
        'multiple',
        NULL,
        NULL,
        NULL,
        false,
        SQLERRM,
        clock_timestamp() - start_time
    );
    RAISE;
END $$;

-- Clean up
DROP TABLE IF EXISTS temp_year CASCADE;
DROP TABLE IF EXISTS temp_week CASCADE;
DROP TABLE IF EXISTS temp_parish CASCADE;
DROP TABLE IF EXISTS temp_christening CASCADE;
DROP TABLE IF EXISTS temp_causes_of_death CASCADE;
DROP TABLE IF EXISTS temp_bills CASCADE;

COMMIT;

-- Add analyze after commit to update statistics
ANALYZE bom.bill_of_mortality;
ANALYZE bom.year;
ANALYZE bom.week;
ANALYZE bom.parishes;
ANALYZE bom.christenings;
ANALYZE bom.causes_of_death;

-- Log final status
DO $$
BEGIN
    PERFORM bom.log_operation(
        'ANALYZE',
        'all_tables',
        NULL,
        NULL,
        NULL,
        true,
        NULL,
        NULL
    );
END $$;

--
--
--
--
-- BEGIN;
--
-- -- bom.years
-- -- This table contains the unique years in the dataset.
-- CREATE TEMPORARY TABLE IF NOT EXISTS temp_year (
--     year integer,
--     year_id integer,
--     id integer
-- );
-- COPY temp_year FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/year_unique.csv' DELIMITER ',' CSV HEADER;
-- INSERT INTO bom.year (year)
-- SELECT DISTINCT year FROM temp_year
-- WHERE year IS NOT NULL
-- ON CONFLICT (year) DO NOTHING;
--
-- -- bom.weeks
-- -- This table contains the unique weeks in the dataset.
-- CREATE TEMPORARY TABLE IF NOT EXISTS temp_week (
--     year integer,
--     week_number integer,
--     start_day integer,
--     end_day integer,
--     start_month text,
--     end_month text,
--     unique_identifier text,
--     week_id text,
--     year_range text,
--     split_year text,
--     joinid text
--
-- );
-- COPY temp_week FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/week_unique.csv' DELIMITER ',' CSV HEADER;
-- INSERT INTO bom.week (joinid, start_day, start_month, end_day, end_month, year, week_no, split_year)
-- SELECT DISTINCT joinid, start_day, start_month, end_day, end_month, year, week_number, split_year FROM temp_week
-- ON CONFLICT (joinid) DO NOTHING;
--
-- -- -- bom.parishes
-- -- -- This table contains the unique parishes in the dataset.
-- CREATE TEMPORARY TABLE IF NOT EXISTS temp_parish (
--     parish_name text NOT NULL,
--     canonical_name text NOT NULL,
--     parish_id integer
-- );
-- COPY temp_parish FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/parishes_unique.csv' DELIMITER ',' CSV HEADER;
-- INSERT INTO bom.parishes (id, parish_name, canonical_name)
-- SELECT DISTINCT parish_id, parish_name, canonical_name FROM temp_parish
-- ON CONFLICT (parish_name) DO UPDATE
-- SET canonical_name = EXCLUDED.canonical_name;
--
-- -- -- bom.christenings
-- -- -- This table contains the unique christenings in the dataset.
-- CREATE TEMPORARY TABLE IF NOT EXISTS temp_christening (
--     year integer,
--     week integer,
--     unique_identifier text,
--     start_day int,
--     start_month text,
--     end_day int,
--     end_month text,
--     parish_name text,
--     count int,
--     bill_type text,
--     joinid text
-- );
-- COPY temp_christening FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/christenings_by_parish.csv' DELIMITER ',' CSV HEADER;
-- INSERT INTO bom.christenings (christening, count, week_number, start_day, start_month, end_day, end_month, year)
-- SELECT DISTINCT parish_name, count, week, start_day, start_month, end_day, end_month, year FROM temp_christening
-- ON CONFLICT DO NOTHING;
--
-- -- -- bom.cause_of_death
-- -- -- This table contains the unique causes of death in the dataset.
-- CREATE TEMPORARY TABLE IF NOT EXISTS temp_causes_of_death (
--     death text,
--     count int,
--     descriptive_text text,
--     joinid text,
--     year integer,
--     week_id text,
--     year_range text,
--     split_year text
-- );
-- COPY temp_causes_of_death FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/causes_of_death.csv' DELIMITER ',' CSV HEADER;
-- INSERT INTO bom.causes_of_death (death, count, year, week_id, descriptive_text)
-- SELECT DISTINCT death, count, year, joinid, descriptive_text FROM temp_causes_of_death
-- ON CONFLICT DO NOTHING;
--
-- -- -- bom.bills
-- -- -- This table contains all the bills in the dataset.
-- CREATE TEMPORARY TABLE IF NOT EXISTS temp_bills (
--     unique_identifier text,
--     count_type text,
--     count int,
--     bill_type text,
--     parish_id int,
--     year integer,
--     week_id text,
--     year_range text,
--     split_year text,
--     joinid text,
--     id int
-- );
-- COPY temp_bills FROM '/Users/jheppler/Dropbox/30-39 Projects/30.06 CHNM/Projects/Death by Numbers/bom/bom-processing/scripts/bomr/data/all_bills.csv' DELIMITER ',' CSV HEADER;
-- INSERT INTO bom.bill_of_mortality (parish_id, count_type, count, year_id, week_id, bill_type)
-- SELECT DISTINCT parish_id, count_type, count, year, joinid, bill_type FROM temp_bills
-- ON CONFLICT DO NOTHING;
--
-- -- Cleanup 
-- DROP TABLE IF EXISTS temp_year;
-- DROP TABLE IF EXISTS temp_week;
-- DROP TABLE IF EXISTS temp_parish;
-- DROP TABLE IF EXISTS temp_christening;
-- DROP TABLE IF EXISTS temp_causes_of_death;
-- DROP TABLE IF EXISTS temp_bills;
--
-- COMMIT;

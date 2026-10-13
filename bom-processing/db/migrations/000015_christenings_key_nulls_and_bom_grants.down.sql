-- Restore the original christenings key and remove the default privileges.
-- Ownership and grants on existing objects are left in place.
ALTER TABLE bom.christenings
DROP CONSTRAINT IF EXISTS christenings_unique_record;

ALTER TABLE bom.christenings
ADD CONSTRAINT christenings_unique_record
UNIQUE (christening, week_number, start_day, start_month, end_day, end_month, year, bill_type);

DO $$
DECLARE
    reader text;
BEGIN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'apiary_dev') THEN
        EXECUTE 'ALTER DEFAULT PRIVILEGES IN SCHEMA bom REVOKE SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES FROM apiary_dev';
    END IF;

    FOREACH reader IN ARRAY ARRAY['apiary_service', 'apiary_exports'] LOOP
        IF EXISTS (SELECT FROM pg_roles WHERE rolname = reader) THEN
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA bom REVOKE SELECT ON TABLES FROM %I', reader);
        END IF;
    END LOOP;
END $$;

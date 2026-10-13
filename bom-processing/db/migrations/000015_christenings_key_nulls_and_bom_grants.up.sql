-- 1. Christenings unique key: treat NULLs as equal
--
-- Christenings without a start or end date have NULLs in the unique key.
-- A plain UNIQUE constraint treats NULLs as distinct, so ON CONFLICT never
-- matches those rows and every import inserted them again. Remove exact
-- duplicates first (keeping the earliest row); if duplicates remain that
-- differ in value, adding the constraint fails rather than choosing one.
DELETE FROM bom.christenings
WHERE id IN (
    SELECT id FROM (
        SELECT id, row_number() OVER (
            PARTITION BY christening, count, week_number, start_day, start_month,
                end_day, end_month, year, missing, illegible, source, bill_type,
                joinid, unique_identifier
            ORDER BY id
        ) AS copy_number
        FROM bom.christenings
    ) numbered
    WHERE copy_number > 1
);

ALTER TABLE bom.christenings
DROP CONSTRAINT IF EXISTS christenings_unique_record;

ALTER TABLE bom.christenings
ADD CONSTRAINT christenings_unique_record
UNIQUE NULLS NOT DISTINCT (christening, week_number, start_day, start_month, end_day, end_month, year, bill_type);

-- 2. Ownership and grants for the API roles
--
-- Tables created by migrations belong to whoever runs them and get no
-- grants, so the API could not read bom.subtotals or bom.weekly_arithmetic.
-- Match the rest of the bom schema, and set default privileges so tables
-- and views that the migrating role creates in bom later are readable too.
-- Roles are checked first so databases without them still migrate.
DO $$
DECLARE
    reader text;
BEGIN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'apiary_admin') THEN
        EXECUTE 'ALTER TABLE bom.subtotals OWNER TO apiary_admin';
        EXECUTE 'ALTER VIEW bom.weekly_arithmetic OWNER TO apiary_admin';
    END IF;

    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'apiary_dev') THEN
        EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON bom.subtotals TO apiary_dev';
        EXECUTE 'GRANT SELECT ON bom.weekly_arithmetic TO apiary_dev';
        EXECUTE 'ALTER DEFAULT PRIVILEGES IN SCHEMA bom GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO apiary_dev';
    END IF;

    FOREACH reader IN ARRAY ARRAY['apiary_service', 'apiary_exports'] LOOP
        IF EXISTS (SELECT FROM pg_roles WHERE rolname = reader) THEN
            EXECUTE format('GRANT SELECT ON bom.subtotals, bom.weekly_arithmetic TO %I', reader);
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA bom GRANT SELECT ON TABLES TO %I', reader);
        END IF;
    END LOOP;
END $$;

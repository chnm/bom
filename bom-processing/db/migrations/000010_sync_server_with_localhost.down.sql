-- Rollback migration to restore server schema differences
-- This reverses all changes made in the up migration

-- 10. Drop indices on bill_of_mortality
DROP INDEX IF EXISTS bom.idx_bom_mortality_parish;
DROP INDEX IF EXISTS bom.idx_bom_mortality_year;
DROP INDEX IF EXISTS bom.idx_bom_mortality_week;

-- 9. Revert constraint naming in bill_of_mortality
ALTER TABLE bom.bill_of_mortality 
DROP CONSTRAINT IF EXISTS bill_of_mortality_parish_id_count_type_year_week_id_source_bill;

ALTER TABLE bom.bill_of_mortality 
ADD CONSTRAINT bill_of_mortality_unique_key 
UNIQUE (parish_id, count_type, year, week_id, source, bill_type);

-- 8. Remove table comment on data_load_log
COMMENT ON TABLE bom.data_load_log IS NULL;

-- 7. Revert data_load_log sequence approach
ALTER TABLE bom.data_load_log 
ALTER COLUMN load_id SET DEFAULT nextval('bom.data_load_log_load_id_seq'::regclass);

-- 6. Add back parish_id column to parishes_shp
ALTER TABLE bom.parishes_shp 
ADD COLUMN parish_id integer;

-- 5. Drop index on christenings.year
DROP INDEX IF EXISTS bom.idx_bom_christenings_year;

-- 4. Drop foreign key constraint from christenings.year
ALTER TABLE bom.christenings 
DROP CONSTRAINT IF EXISTS christenings_year_fkey;

-- 3. Revert christenings missing/illegible columns from boolean to text
ALTER TABLE bom.christenings 
ALTER COLUMN missing TYPE text,
ALTER COLUMN illegible TYPE text;

-- 2. Drop index on week.year
DROP INDEX IF EXISTS bom.idx_bom_week_year;

-- 1. Drop foreign key constraint from week.year
ALTER TABLE bom.week 
DROP CONSTRAINT IF EXISTS week_year_fkey;
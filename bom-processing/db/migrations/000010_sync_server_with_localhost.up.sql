-- Migration to sync server schema with localhost schema
-- This addresses multiple differences found between the environments

-- 1. Add missing foreign key constraint to week.year
ALTER TABLE bom.week 
ADD CONSTRAINT week_year_fkey FOREIGN KEY (year) REFERENCES bom.year(year);

-- 2. Add missing index on week.year
CREATE INDEX IF NOT EXISTS idx_bom_week_year ON bom.week(year);

-- 3. Fix christenings missing/illegible columns from text to boolean
ALTER TABLE bom.christenings 
ALTER COLUMN missing TYPE boolean USING (missing::boolean),
ALTER COLUMN illegible TYPE boolean USING (illegible::boolean);

-- 4. Add missing foreign key constraint to christenings.year
ALTER TABLE bom.christenings 
ADD CONSTRAINT christenings_year_fkey FOREIGN KEY (year) REFERENCES bom.year(year);

-- 5. Add missing index on christenings.year
CREATE INDEX IF NOT EXISTS idx_bom_christenings_year ON bom.christenings(year);

-- 6. Drop extra parish_id column from parishes_shp (not in target schema)
ALTER TABLE bom.parishes_shp 
DROP COLUMN IF EXISTS parish_id;

-- 7. Skip data_load_log sequence changes - it's already an identity column
-- No changes needed for identity columns

-- 8. Add missing table comment on data_load_log
COMMENT ON TABLE bom.data_load_log IS 'Tracks data load operations for auditing and debugging';

-- 9. Fix constraint naming in bill_of_mortality
ALTER TABLE bom.bill_of_mortality 
DROP CONSTRAINT IF EXISTS bill_of_mortality_unique_key;

ALTER TABLE bom.bill_of_mortality 
ADD CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_source_bill 
UNIQUE (parish_id, count_type, year, week_id, source, bill_type);

-- 10. Add missing indices on bill_of_mortality
CREATE INDEX IF NOT EXISTS idx_bom_mortality_parish ON bom.bill_of_mortality(parish_id);
CREATE INDEX IF NOT EXISTS idx_bom_mortality_year ON bom.bill_of_mortality(year);
CREATE INDEX IF NOT EXISTS idx_bom_mortality_week ON bom.bill_of_mortality(week_id);
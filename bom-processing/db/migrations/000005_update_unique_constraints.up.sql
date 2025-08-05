-- Update unique constraints to include source field

-- Drop existing constraints
ALTER TABLE bom.bill_of_mortality DROP CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_key;
ALTER TABLE bom.causes_of_death DROP CONSTRAINT causes_of_death_unique_record;

-- Add new constraints with source field
ALTER TABLE bom.bill_of_mortality ADD CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_source_key UNIQUE (parish_id, count_type, year, week_id, source);
ALTER TABLE bom.causes_of_death ADD CONSTRAINT causes_of_death_unique_record UNIQUE (death, year, week_id, source_name);
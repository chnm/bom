-- Add bill_type to unique constraint for better record disambiguation

-- Drop existing constraint
ALTER TABLE bom.bill_of_mortality DROP CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_source_key;

-- Add new constraint with bill_type
ALTER TABLE bom.bill_of_mortality ADD CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_source_bill_type_key UNIQUE (parish_id, count_type, year, week_id, source, bill_type);
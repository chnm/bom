-- Rollback bill_type constraint changes

-- Drop new constraint
ALTER TABLE bom.bill_of_mortality DROP CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_source_bill_type_key;

-- Restore previous constraint
ALTER TABLE bom.bill_of_mortality ADD CONSTRAINT bill_of_mortality_parish_id_count_type_year_week_id_source_key UNIQUE (parish_id, count_type, year, week_id, source);
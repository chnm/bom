-- Revert bill_type addition to christenings unique constraint

-- Drop new constraint
ALTER TABLE bom.christenings DROP CONSTRAINT christenings_unique_record;

-- Restore original constraint without bill_type
ALTER TABLE bom.christenings ADD CONSTRAINT christenings_unique_record UNIQUE (christening, week_number, start_day, start_month, end_day, end_month, year);
-- Add bill_type to christenings unique constraint for better record disambiguation

-- Drop existing constraint
ALTER TABLE bom.christenings DROP CONSTRAINT christenings_unique_record;

-- Add new constraint with bill_type
ALTER TABLE bom.christenings ADD CONSTRAINT christenings_unique_record UNIQUE (christening, week_number, start_day, start_month, end_day, end_month, year, bill_type);
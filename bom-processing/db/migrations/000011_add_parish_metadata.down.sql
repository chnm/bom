-- Remove bills_subunit, foundation_year, and notes columns from parishes table
ALTER TABLE bom.parishes
DROP COLUMN IF EXISTS bills_subunit,
DROP COLUMN IF EXISTS foundation_year,
DROP COLUMN IF EXISTS notes;

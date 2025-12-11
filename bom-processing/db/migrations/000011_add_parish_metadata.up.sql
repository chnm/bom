-- Add bills_subunit, foundation_year, and notes columns to parishes table
ALTER TABLE bom.parishes
ADD COLUMN IF NOT EXISTS bills_subunit text,
ADD COLUMN IF NOT EXISTS foundation_year text,
ADD COLUMN IF NOT EXISTS notes text;

COMMENT ON COLUMN bom.parishes.bills_subunit IS 'Bills subunit classification (e.g., "97 parishes within the walls")';
COMMENT ON COLUMN bom.parishes.foundation_year IS 'Year the parish was founded';

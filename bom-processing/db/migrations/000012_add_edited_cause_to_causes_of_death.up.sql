-- Add edited_cause column to causes_of_death table
-- This column stores the canonical/normalized cause name from edited_causes.csv
ALTER TABLE bom.causes_of_death
ADD COLUMN edited_cause TEXT;

-- Add comment to explain the column
COMMENT ON COLUMN bom.causes_of_death.edited_cause
IS 'Canonical cause of death names from controlled vocabulary. Used to group spelling variants of the same cause.';

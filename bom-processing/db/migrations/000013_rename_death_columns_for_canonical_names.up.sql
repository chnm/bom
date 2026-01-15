-- Rename columns in causes_of_death to use canonical names
-- 
-- This migration:
-- 1. Renames 'death' column to 'original_name' (the historical spelling from records)
-- 2. Renames 'edited_cause' column to 'name' (the canonical/normalized name)
--
-- This ensures the API returns canonical names as 'name' to avoid duplicates,
-- while preserving the original historical spellings in 'original_name'

-- First, rename 'death' to 'original_name'
ALTER TABLE bom.causes_of_death
RENAME COLUMN death TO original_name;

-- Then, rename 'edited_cause' to 'name'
ALTER TABLE bom.causes_of_death
RENAME COLUMN edited_cause TO name;

-- Update comments to reflect new column purposes
COMMENT ON COLUMN bom.causes_of_death.original_name
IS 'Original cause of death text as recorded in historical bills. May contain spelling variants.';

COMMENT ON COLUMN bom.causes_of_death.name
IS 'Canonical cause of death names from controlled vocabulary. Used as primary identifier to group spelling variants.';

-- Update the unique constraint to use original_name instead of death
ALTER TABLE bom.causes_of_death
DROP CONSTRAINT IF EXISTS causes_of_death_unique_record;

ALTER TABLE bom.causes_of_death
ADD CONSTRAINT causes_of_death_unique_record 
UNIQUE (original_name, year, week_id, source_name, bill_type);

-- Revert column renames in causes_of_death table

-- Revert constraint first
ALTER TABLE bom.causes_of_death
DROP CONSTRAINT IF EXISTS causes_of_death_unique_record;

ALTER TABLE bom.causes_of_death
ADD CONSTRAINT causes_of_death_unique_record 
UNIQUE (original_name, year, week_id);

-- Rename 'name' back to 'edited_cause'
ALTER TABLE bom.causes_of_death
RENAME COLUMN name TO edited_cause;

-- Rename 'original_name' back to 'death'
ALTER TABLE bom.causes_of_death
RENAME COLUMN original_name TO death;

-- Restore original comments
COMMENT ON COLUMN bom.causes_of_death.edited_cause
IS 'Canonical cause of death names from controlled vocabulary. Used to group spelling variants of the same cause.';
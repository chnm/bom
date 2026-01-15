-- Remove edited_cause column from causes_of_death table
ALTER TABLE bom.causes_of_death
DROP COLUMN edited_cause;

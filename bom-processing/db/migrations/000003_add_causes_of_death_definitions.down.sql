-- Remove definition_source column
ALTER TABLE bom.causes_of_death
DROP COLUMN IF EXISTS definition_source;

-- Remove definition column
ALTER TABLE bom.causes_of_death
DROP COLUMN IF EXISTS definition;

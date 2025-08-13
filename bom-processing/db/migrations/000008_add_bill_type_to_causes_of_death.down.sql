-- Remove bill_type from unique constraint
ALTER TABLE bom.causes_of_death 
DROP CONSTRAINT causes_of_death_unique_record;

ALTER TABLE bom.causes_of_death 
ADD CONSTRAINT causes_of_death_unique_record 
UNIQUE (death, year, week_id, source_name);

-- Remove bill_type column from causes_of_death table
ALTER TABLE bom.causes_of_death 
DROP COLUMN bill_type;
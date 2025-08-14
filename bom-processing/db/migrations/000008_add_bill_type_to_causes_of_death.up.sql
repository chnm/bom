-- Add bill_type column to causes_of_death table
ALTER TABLE bom.causes_of_death 
ADD COLUMN bill_type TEXT DEFAULT 'weekly' NOT NULL;

-- Update unique constraint to include bill_type
ALTER TABLE bom.causes_of_death 
DROP CONSTRAINT causes_of_death_unique_record;

ALTER TABLE bom.causes_of_death 
ADD CONSTRAINT causes_of_death_unique_record 
UNIQUE (death, year, week_id, source_name, bill_type);
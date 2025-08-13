-- Restore the descriptive_text column to causes_of_death table
ALTER TABLE bom.causes_of_death 
ADD COLUMN descriptive_text TEXT;
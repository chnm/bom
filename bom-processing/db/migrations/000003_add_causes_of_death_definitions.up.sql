-- Migration to add definition-related columns to the causes_of_death table

-- Add definition column to store detailed explanation of the cause of death
ALTER TABLE bom.causes_of_death
ADD COLUMN IF NOT EXISTS definition text;

-- Add definition_source column to track where the definition came from
ALTER TABLE bom.causes_of_death
ADD COLUMN IF NOT EXISTS definition_source text;

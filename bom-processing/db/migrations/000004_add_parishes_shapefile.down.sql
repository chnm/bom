-- Roll back the parishes_shp table migration

-- Drop the spatial index first
DROP INDEX IF EXISTS bom.idx_parishes_shp_geom_01;

-- Drop the sequence
DROP SEQUENCE IF EXISTS bom.parishes_shp_id_seq CASCADE;

-- Drop the table
DROP TABLE IF EXISTS bom.parishes_shp;

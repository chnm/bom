-- Return the database to empty.
-- Note: We retain bom.data_load_log

DROP TABLE IF EXISTS bom.parishes CASCADE;
DROP TABLE IF EXISTS bom.bill_of_mortality CASCADE;
DROP TABLE IF EXISTS bom.causes_of_death CASCADE;
DROP TABLE IF EXISTS bom.christenings CASCADE;
DROP TABLE IF EXISTS bom.christening_locations CASCADE;
DROP TABLE IF EXISTS bom.parish_collective CASCADE;
DROP TABLE IF EXISTS bom.week CASCADE;
DROP TABLE IF EXISTS bom.year CASCADE;


-- Migration to add parishes_shp table for shapefile data

-- Create parishes_shp table
CREATE TABLE IF NOT EXISTS bom.parishes_shp (
    id integer NOT NULL,
    par character varying(254),
    civ_par character varying(254),
    dbn_par character varying(254),
    omeka_par character varying(254),
    subunit character varying(254),
    city_cnty character varying(254),
    start_yr integer,
    geom_01 geometry(MultiPolygon,4326),
    gaz_cnty character varying,
    sp_total integer,
    sp_per double precision,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

-- Set up the identity column
ALTER TABLE bom.parishes_shp ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME bom.parishes_shp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- Add primary key constraint
ALTER TABLE ONLY bom.parishes_shp
    ADD CONSTRAINT parishes_shp_pkey PRIMARY KEY (id);

-- Add spatial index for improved query performance on geometry column
CREATE INDEX IF NOT EXISTS idx_parishes_shp_geom_01 ON bom.parishes_shp USING GIST (geom_01);

-- Table definitions for setting up the various elements of the data.
-- 1. Years
-- 2. Weeks
-- 3. Parishes
-- 4. Christenings
-- 5. Causes of death
-- 6. Bills of Mortality

CREATE SCHEMA IF NOT EXISTS bom;

-- Table Definition: Years ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.year (
    id integer GENERATED ALWAYS AS IDENTITY,
    year integer PRIMARY KEY
    CONSTRAINT year_range CHECK (year > 1400 AND year < 1800)
);

-- Table Definition: Weeks ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.week (
    id integer GENERATED ALWAYS AS IDENTITY,
    joinid text PRIMARY KEY,
    start_day integer CHECK (start_day BETWEEN 1 AND 31),
    start_month text,
    end_day integer CHECK (end_day BETWEEN 1 AND 31),
    end_month text,
    year integer REFERENCES bom.year(year),
    week_number integer CHECK (week_number BETWEEN 1 AND 90),
    split_year text,
    unique_identifier text,
    week_id text,
    year_range text,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON CONSTRAINT week_week_number_check ON bom.week 
IS 'Week numbers 1-53 for regular weeks, 90 used to denote annual records';

-- Table Definition: Parishes ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.parishes (
    id integer PRIMARY KEY,
    parish_name text NOT NULL UNIQUE,
    canonical_name text NOT NULL,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

-- Table Definition: Parish Collectives ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.parish_collective (
    id integer GENERATED ALWAYS AS IDENTITY,
    collective_name text
);

INSERT INTO bom.parish_collective (collective_name) VALUES ('London');

-- Table Definition: Christenings ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.christenings (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    christening text NOT NULL,
    count integer,
    week_number integer,
    start_month text,
    end_month text,
    year integer REFERENCES bom.year(year),
    start_day integer,
    end_day integer,
    missing boolean,
    illegible boolean,
    source text,
    bill_type text,
    joinid text REFERENCES bom.week(joinid),
    unique_identifier text,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT christenings_unique_record 
        UNIQUE (christening, week_number, start_day, start_month, end_day, end_month, year)
);

-- Table Definition: Christenings locations ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.christening_locations (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);

-- Table Definition: Causes of Death ----------------------------------------------
CREATE TABLE IF NOT EXISTS bom.causes_of_death (
    id integer GENERATED ALWAYS AS IDENTITY,
    death text,
    count integer,
    year integer REFERENCES bom.year(year),
    week_id text NOT NULL REFERENCES bom.week(joinid),
    descriptive_text text,
    source_name text,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT causes_of_death_unique_record 
        UNIQUE (death, year, week_id)
);

-- Table Definition: Bills of Mortality --------------------------
CREATE TABLE IF NOT EXISTS bom.bill_of_mortality (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parish_id integer NOT NULL REFERENCES bom.parishes(id),
    count_type text NOT NULL,
    count integer,
    year integer NOT NULL REFERENCES bom.year(year),
    week_id text NOT NULL REFERENCES bom.week(joinid),
    bill_type text,
    missing boolean,
    illegible boolean,
    source text,
    unique_identifier text,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (parish_id, count_type, year, week_id)
);

-- Create indexes for faster queries
CREATE INDEX idx_bom_week_year ON bom.week(year);
CREATE INDEX idx_bom_christenings_year ON bom.christenings(year);
CREATE INDEX idx_bom_mortality_parish ON bom.bill_of_mortality(parish_id);
CREATE INDEX idx_bom_mortality_year ON bom.bill_of_mortality(year);
CREATE INDEX idx_bom_mortality_week ON bom.bill_of_mortality(week_id);


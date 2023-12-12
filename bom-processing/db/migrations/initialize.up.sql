-- Table definitions for setting up the various elements of the data.
-- 1. Years
-- 2. Weeks
-- 3. Parishes
-- 4. Christenings
-- 5. Causes of death
-- 6. Bills of Mortality

-- Table Definition: Years ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.year (
    id integer GENERATED ALWAYS AS IDENTITY,
    year integer PRIMARY KEY
);

-- Table Definition: Weeks ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.week (
    id integer GENERATED ALWAYS AS IDENTITY,
    joinid text PRIMARY KEY,
    start_day integer,
    start_month text,
    end_day integer,
    end_month text,
    year integer REFERENCES bom.year(year),
    week_no integer,
    split_year text
);

-- Table Definition: Parishes ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.parishes (
    id integer PRIMARY KEY,
    parish_name text NOT NULL UNIQUE,
    canonical_name text NOT NULL
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
    missing text,
    illegible text
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
    descriptive_text text
);

-- Table Definition: Bills of Mortality --------------------------

CREATE TABLE IF NOT EXISTS bom.bill_of_mortality (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parish_id integer NOT NULL REFERENCES bom.parishes(id),
    collective_id integer REFERENCES bom.parish_collective(id),
    count_type text NOT NULL,
    count integer,
    year_id integer NOT NULL REFERENCES bom.year(year),
    week_id text NOT NULL REFERENCES bom.week(joinid),
    bill_type text,
    missing text,
    illegible text
);

-- Derive the christenings_location data from the christenings table
INSERT INTO bom.christening_locations(name)
SELECT DISTINCT bom.christenings.christening
FROM bom.christenings;

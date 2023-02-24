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
    year text PRIMARY KEY
);

-- Table Definition: Weeks ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.week (
    id integer GENERATED ALWAYS AS IDENTITY,
    week_id text PRIMARY KEY,
    week_no integer,
    start_day integer,
    start_month text,
    end_day integer,
    end_month text,
    year text REFERENCES bom.year(year),
    split_year text
);

-- Table Definition: Parishes ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.parishes (
    id integer GENERATED ALWAYS AS IDENTITY,
    parish_name text NOT NULL UNIQUE,
    canonical_name text NOT NULL
);

-- Table Definition: Parish Collectives ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.parish_collective (
    id integer GENERATED ALWAYS AS IDENTITY,
    collective_id text NOT NULL,
    collective_name text NOT NULL
);

-- Table Definition: Christenings ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.christenings (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    christening text NOT NULL,
    count integer,
    week_number text,
    start_month text,
    end_month text,
    year text REFERENCES bom.year(year),
    start_day integer,
    end_day integer
);

-- Table Definition: Christenings locations ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.christening_locations (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);

-- Table Definition: Causes of Death ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.causes_of_death (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    death text,
    count integer,
    week_id text REFERENCES bom.week(week_id),
    description text
);

-- Table Definition: Bills of Mortality --------------------------

CREATE TABLE IF NOT EXISTS bom.bill_of_mortality (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parish_id text NOT NULL REFERENCES bom.parishes(parish_name),
    collective_id integer REFERENCES bom.parish_collective(id),
    count_type text NOT NULL,
    count integer,
    week_id text NOT NULL REFERENCES bom.week(week_id),
    bill_type text
);
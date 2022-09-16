-- Table definitions for setting up the various elements of the data.
-- 1. Years
-- 2. Weeks
-- 3. Parishes
-- 4. Christenings
-- 5. Causes of death
-- 6. Bills of Mortality

-- Table Definition: Years ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.year (
    id integer NOT NULL,
    year_id text PRIMARY KEY,
    split_year text,
    year integer NOT NULL
);

-- Table Definition: Weeks ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.week (
    id integer NOT NULL,
    week_id text PRIMARY KEY,
    start_day integer,
    start_month text,
    end_day integer,
    end_month text,
    year_id text REFERENCES bom.year(year_id),
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
    id integer PRIMARY KEY,
    collective_id text NOT NULL
);

CREATE UNIQUE INDEX parish_collective_pkey ON bom.parish_collective(id int4_ops);


-- Table Definition: Christenings ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.christenings (
    id integer PRIMARY KEY,
    christening text NOT NULL,
    count integer,
    week_number text,
    start_month text,
    end_month text,
    year text REFERENCES bom.year(year_id),
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
    death text,
    count integer,
    year text REFERENCES bom.year(year_id),
    week_id text REFERENCES bom.week(week_id),
    id integer NOT NULL,
    death_id integer
);

-- Table Definition: Bills of Mortality --------------------------

CREATE TABLE IF NOT EXISTS bom.bill_of_mortality (
    id integer PRIMARY KEY,
    parish_id integer NOT NULL REFERENCES bom.parishes(id),
    collective_id integer REFERENCES bom.parish_collective(id),
    count_type text NOT NULL,
    count integer,
    year_id text NOT NULL REFERENCES bom.year(year_id),
    week_id text NOT NULL REFERENCES bom.week(week_id),
    bill_type text
);
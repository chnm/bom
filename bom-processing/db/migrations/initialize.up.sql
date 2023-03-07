-- Table definitions for setting up the various elements of the data.
-- 1. Years
-- 2. Weeks
-- 3. Parishes
-- 4. Christenings
-- 5. Causes of death
-- 6. Bills of Mortality

-- Table Definition: Years ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_year (
    id integer GENERATED ALWAYS AS IDENTITY,
    year integer PRIMARY KEY
);

-- Table Definition: Weeks ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_week (
    id integer GENERATED ALWAYS AS IDENTITY,
    joinid text PRIMARY KEY,
    start_day integer,
    start_month text,
    end_day integer,
    end_month text,
    year integer REFERENCES bom.test_year(year),
    week_no integer,
    split_year text
);

-- Table Definition: Parishes ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_parishes (
    id integer PRIMARY KEY,
    parish_name text NOT NULL UNIQUE,
    canonical_name text NOT NULL
);

-- Table Definition: Parish Collectives ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_parish_collective (
    id integer GENERATED ALWAYS AS IDENTITY,
    collective_name text
);

INSERT INTO bom.test_parish_collective (collective_name) VALUES ('London');

-- Table Definition: Christenings ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_christenings (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    christening text NOT NULL,
    count integer,
    week_number text,
    start_month text,
    end_month text,
    year integer REFERENCES bom.test_year(year),
    start_day integer,
    end_day integer
);

-- Table Definition: Christenings locations ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_christening_locations (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);

-- Table Definition: Causes of Death ----------------------------------------------

CREATE TABLE IF NOT EXISTS bom.test_causes_of_death (
    id integer GENERATED ALWAYS AS IDENTITY,
    death text,
    count integer,
    year integer REFERENCES bom.test_year(year),
    week_id text NOT NULL REFERENCES bom.test_week(joinid),
    descriptive_text text
);

-- Table Definition: Bills of Mortality --------------------------

CREATE TABLE IF NOT EXISTS bom.test_bill_of_mortality (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parish_id integer NOT NULL REFERENCES bom.test_parishes(id),
    collective_id integer REFERENCES bom.test_parish_collective(id),
    count_type text NOT NULL,
    count integer,
    year_id integer NOT NULL REFERENCES bom.test_year(year),
    week_id text NOT NULL REFERENCES bom.test_week(joinid),
    bill_type text
);
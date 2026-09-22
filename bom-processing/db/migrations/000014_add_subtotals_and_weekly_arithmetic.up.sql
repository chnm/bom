-- Add printed subtotals and a view comparing them with parish-summed counts
--
-- Subtotals are transcribed from the bills themselves ("Within the walls",
-- "Without the walls", "Middlesex and Surrey", "Westminster"), so they are
-- stored as source data. The parish sums and differences are derived and
-- live in the weekly_arithmetic view.

CREATE TABLE IF NOT EXISTS bom.subtotals (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subtotal_category text NOT NULL,
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
    CONSTRAINT subtotals_unique_record
        UNIQUE (subtotal_category, count_type, week_id, bill_type)
);

CREATE INDEX IF NOT EXISTS idx_bom_subtotals_year ON bom.subtotals(year);

COMMENT ON TABLE bom.subtotals
IS 'Geographic subtotals printed on the weekly and general bills.';

-- Weekly arithmetic: printed subtotals minus the sum of parish counts.
--
-- Follows the article analysis (bom-processing/notebooks/arithmetic-accuracy):
--   * weekly bills, burial and plague counts, weeks 1-55
--   * the Westminster pesthouse is excluded because the printed subtotals
--     do not include it
--   * a week is legible only when no parish count or subtotal of either
--     count type is marked illegible
--   * mixed_copies marks weeks whose figures come from more than one
--     transcribed copy of the bill, because the importer keeps the largest
--     value for each parish or subtotal when copies disagree
-- Year is kept as a grouping column so year filters reach the base tables.
CREATE OR REPLACE VIEW bom.weekly_arithmetic AS
WITH parish_rows AS NOT MATERIALIZED (
    SELECT b.year, b.week_id, b.count_type, b.count, b.illegible,
        btrim(b.unique_identifier) AS copy
    FROM bom.bill_of_mortality b
    JOIN bom.parishes p ON p.id = b.parish_id
    WHERE b.bill_type = 'weekly'
      AND b.count_type IN ('buried', 'plague')
      AND p.canonical_name <> 'Westminster Pesthouse'
),
subtotal_rows AS NOT MATERIALIZED (
    SELECT s.year, s.week_id, s.count_type, s.count, s.illegible,
        btrim(s.unique_identifier) AS copy
    FROM bom.subtotals s
    WHERE s.bill_type = 'weekly'
      AND s.count_type IN ('buried', 'plague')
),
parish_sums AS (
    SELECT year, week_id, count_type, SUM(count) AS parish_sum
    FROM parish_rows
    GROUP BY year, week_id, count_type
),
subtotal_sums AS (
    SELECT year, week_id, count_type, SUM(count) AS subtotal_sum
    FROM subtotal_rows
    GROUP BY year, week_id, count_type
),
illegible_weeks AS (
    SELECT year, week_id FROM parish_rows WHERE illegible
    UNION
    SELECT year, week_id FROM subtotal_rows WHERE illegible
),
mixed_weeks AS (
    SELECT year, week_id
    FROM (
        SELECT year, week_id, copy FROM parish_rows
        UNION
        SELECT year, week_id, copy FROM subtotal_rows
    ) copies
    GROUP BY year, week_id
    HAVING COUNT(DISTINCT copy) > 1
)
SELECT
    s.year,
    w.week_number,
    w.joinid AS week_id,
    s.count_type,
    s.subtotal_sum,
    p.parish_sum,
    s.subtotal_sum - p.parish_sum AS difference,
    i.week_id IS NULL AS legible,
    m.week_id IS NOT NULL AS mixed_copies
FROM subtotal_sums s
JOIN parish_sums p USING (year, week_id, count_type)
JOIN bom.week w ON w.joinid = s.week_id
LEFT JOIN illegible_weeks i ON i.year = s.year AND i.week_id = s.week_id
LEFT JOIN mixed_weeks m ON m.year = s.year AND m.week_id = s.week_id
WHERE w.week_number BETWEEN 1 AND 55
  AND s.subtotal_sum IS NOT NULL
  AND p.parish_sum IS NOT NULL;

COMMENT ON VIEW bom.weekly_arithmetic
IS 'Printed weekly subtotals compared with parish-summed burial and plague counts.';

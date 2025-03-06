-- Migration to create the data load logging infrastructure
CREATE SCHEMA IF NOT EXISTS bom;

-- Create the data load log table
CREATE TABLE IF NOT EXISTS bom.data_load_log (
    load_id serial PRIMARY KEY,
    load_date timestamp DEFAULT CURRENT_TIMESTAMP,
    operation text NOT NULL,
    table_name text NOT NULL,
    rows_before integer,
    rows_processed integer,
    rows_after integer,
    success boolean DEFAULT false,
    error_message text,
    duration interval
);

-- Create the log_operation function
CREATE OR REPLACE FUNCTION bom.log_operation(
    p_operation text,
    p_table_name text,
    p_rows_before integer,
    p_rows_processed integer,
    p_rows_after integer,
    p_success boolean,
    p_error_message text DEFAULT NULL,
    p_duration interval DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    INSERT INTO bom.data_load_log (
        operation, table_name, rows_before, rows_processed, rows_after,
        success, error_message, duration
    ) VALUES (
        p_operation, p_table_name, p_rows_before, p_rows_processed, p_rows_after,
        p_success, p_error_message, p_duration
    );
END;
$$ LANGUAGE plpgsql;

-- Add comments
COMMENT ON TABLE bom.data_load_log IS 'Tracks data load operations for auditing and debugging';
COMMENT ON FUNCTION bom.log_operation IS 'Helper function to log data operations with consistent format';

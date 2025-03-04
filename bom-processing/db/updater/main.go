package main

import (
	"context"
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
)

// Import configuration
type ImportConfig struct {
	DBConnString string
	DataDir      string
	Tables       []string
	DryRun       bool
}

func main() {
	// Parse command line arguments
	dbConnString := flag.String("db", "", "Database connection string (postgresql://username:password@host:port/dbname)")
	dataDir := flag.String("data", ".", "Directory containing CSV files")
	dryRun := flag.Bool("dry-run", false, "Dry run (don't actually import data)")
	flag.Parse()

	if *dbConnString == "" {
		log.Fatal("Database connection string is required")
	}

	config := ImportConfig{
		DBConnString: *dbConnString,
		DataDir:      *dataDir,
		Tables:       []string{"year", "week", "parishes", "christenings", "causes_of_death", "bills"},
		DryRun:       *dryRun,
	}

	// Connect to database
	ctx := context.Background()
	db, err := pgxpool.Connect(ctx, config.DBConnString)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Run import
	err = importData(ctx, db, config)
	if err != nil {
		log.Fatalf("Import failed: %v", err)
	}

	log.Println("Import completed successfully")
}

func importData(ctx context.Context, db *pgxpool.Pool, config ImportConfig) error {
	err := ensureLogFunctionExists(ctx, db)
	if err != nil {
		return fmt.Errorf("failed to ensure log function exists: %w", err)
	}

	// Start transaction
	tx, err := db.Begin(ctx)
	if err != nil {
		return fmt.Errorf("failed to start transaction: %w", err)
	}
	defer tx.Rollback(ctx)

	// Create temporary tables
	err = createTempTables(ctx, tx)
	if err != nil {
		return fmt.Errorf("failed to create temporary tables: %w", err)
	}

	// Import each table
	for _, table := range config.Tables {
		filename := filepath.Join(config.DataDir, getFilename(table))
		log.Printf("Importing %s from %s", table, filename)

		if config.DryRun {
			log.Printf("[DRY RUN] Would import %s", filename)
			continue
		}

		err = importTable(ctx, tx, table, filename)
		if err != nil {
			return fmt.Errorf("failed to import %s: %w", table, err)
		}
	}

	// Insert/update data from temp tables to actual tables
	if !config.DryRun {
		err = updateTables(ctx, tx)
		if err != nil {
			return fmt.Errorf("failed to update tables: %w", err)
		}

		// Commit the transaction
		err = tx.Commit(ctx)
		if err != nil {
			return fmt.Errorf("failed to commit transaction: %w", err)
		}

		// Run ANALYZE (outside of transaction)
		err = analyzeTables(ctx, db)
		if err != nil {
			return fmt.Errorf("failed to analyze tables: %w", err)
		}
	}

	return nil
}

func ensureLogFunctionExists(ctx context.Context, db *pgxpool.Pool) error {
	// Check if the bom schema exists
	var schemaExists bool
	err := db.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'bom')").Scan(&schemaExists)
	if err != nil {
		return err
	}

	if !schemaExists {
		_, err = db.Exec(ctx, "CREATE SCHEMA IF NOT EXISTS bom")
		if err != nil {
			return err
		}
	}

	// Check if the data_load_log table exists
	var tableExists bool
	err = db.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'bom' AND table_name = 'data_load_log')").Scan(&tableExists)
	if err != nil {
		return err
	}

	if !tableExists {
		_, err = db.Exec(ctx, `
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
            )
        `)
		if err != nil {
			return err
		}
	}

	// Create or replace the log_operation function
	_, err = db.Exec(ctx, `
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
    `)

	return err
}

func getFilename(table string) string {
	switch table {
	case "year":
		return "year_unique.csv"
	case "week":
		return "week_unique.csv"
	case "parishes":
		return "parishes_unique.csv"
	case "christenings":
		return "christenings_by_parish.csv"
	case "causes_of_death":
		return "causes_of_death.csv"
	case "bills":
		return "all_bills.csv"
	}
	return ""
}

func createTempTables(ctx context.Context, tx pgx.Tx) error {
	// Drop existing temp tables if they exist
	_, err := tx.Exec(ctx, `
		DROP TABLE IF EXISTS temp_year CASCADE;
		DROP TABLE IF EXISTS temp_week CASCADE;
		DROP TABLE IF EXISTS temp_parish CASCADE;
		DROP TABLE IF EXISTS temp_christening CASCADE;
		DROP TABLE IF EXISTS temp_causes_of_death CASCADE;
		DROP TABLE IF EXISTS temp_bills CASCADE;
	`)
	if err != nil {
		return err
	}

	// Create temp tables
	_, err = tx.Exec(ctx, `
		CREATE TEMPORARY TABLE temp_year (
			year integer NOT NULL,
			year_id integer NOT NULL,
			id integer NOT NULL,
			CONSTRAINT temp_year_check CHECK (year > 1400 AND year < 1800)
		);

		CREATE TEMPORARY TABLE temp_week (
			year integer,
			week_number integer,
			start_day integer,
			end_day integer,
			start_month text,
			end_month text,
			unique_identifier text,
			week_id text,
			year_range text,
			joinid text,
			split_year text,
			CONSTRAINT temp_week_check CHECK (year > 1400 AND year < 1800)
		);

		CREATE TEMPORARY TABLE temp_parish (
			parish_name text NOT NULL,
			canonical_name text NOT NULL,
			parish_id integer
		);

		CREATE TEMPORARY TABLE temp_christening (
			year integer,
			week integer,
			unique_identifier text,
			start_day int,
			start_month text,
			end_day int,
			end_month text,
			parish_name text,
			count int,
			missing boolean,
			illegible boolean,
			source text,
			bill_type text,
			joinid text,
			start_year text,
			end_year text,
			count_type text,
			CONSTRAINT temp_christening_check CHECK (year > 1400 AND year < 1800)
		);

		CREATE TEMPORARY TABLE temp_causes_of_death (
			death text,
			count int,
			year integer,
			joinid text,
			descriptive_text text,
			source_name text
		);

		CREATE TEMPORARY TABLE temp_bills (
			unique_identifier text,
			parish_name text,
			count_type text,
			count int,
			missing boolean,
			illegible boolean,
			source text,
			bill_type text,
			start_year text,
			end_year text,
			joinid text,
			parish_id integer,
			year integer,
			split_year text
		);
	`)
	return err
}

func importTable(ctx context.Context, tx pgx.Tx, table, filename string) error {
	// Open CSV file
	file, err := os.Open(filename)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	// Create CSV reader
	reader := csv.NewReader(file)
	reader.FieldsPerRecord = -1 // Allow variable number of fields

	// Read header
	header, err := reader.Read()
	if err != nil {
		return fmt.Errorf("failed to read header: %w", err)
	}

	// Prepare temp table name and column list
	tempTable := "temp_" + getTempTableName(table)

	// Insert each row using COPY protocol
	count := 0

	// Read all rows into memory
	rows := [][]interface{}{}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("failed to read row: %w", err)
		}

		values := make([]interface{}, len(record))
		for i, val := range record {
			values[i] = convertValue(val, header[i], table)
		}

		rows = append(rows, values)
		count++
	}

	// Use the correct CopyFrom signature with pgx.CopyFromRows
	_, err = tx.CopyFrom(
		ctx,
		pgx.Identifier{tempTable},
		getColumnNames(header, table),
		pgx.CopyFromRows(rows),
	)

	if err != nil {
		return fmt.Errorf("failed to copy data: %w", err)
	}

	log.Printf("Imported %d rows into %s", count, tempTable)
	return nil
}

func getTempTableName(table string) string {
	switch table {
	case "parishes":
		return "parish"
	case "christenings":
		return "christening"
	case "bills":
		return "bills"
	}
	return table
}

func getColumnNames(header []string, table string) []string {
	// Return all column names from header
	return header
}

func convertValue(val, column, table string) interface{} {
	if val == "" {
		return nil
	}

	// Convert values based on column and table
	switch {
	case column == "year" || column == "year_id" || column == "id" ||
		column == "week_number" || column == "start_day" || column == "end_day" ||
		column == "week" || column == "count" || column == "parish_id":
		num, err := strconv.Atoi(val)
		if err == nil {
			return num
		}
		return nil
	case column == "missing" || column == "illegible":
		return val == "true" || val == "t" || val == "1"
	default:
		return val
	}
}

func updateTables(ctx context.Context, tx pgx.Tx) error {
	log.Println("Updating main tables from temporary tables...")

	start := time.Now()

	// Run the SQL from your insert_update.sql that handles the insertions/updates
	// but without the COPY statements since we've already loaded data into temp tables
	_, err := tx.Exec(ctx, `
	DO $$
	DECLARE
		start_time timestamp;
		end_time timestamp;
		rows_before integer;
		rows_processed integer;
	BEGIN
		-- Years
		start_time := clock_timestamp();
		SELECT COUNT(*) INTO rows_before FROM bom.year;
		
		INSERT INTO bom.year (year)
		SELECT DISTINCT year 
		FROM temp_year
		WHERE year IS NOT NULL
		ON CONFLICT (year) DO NOTHING;
		
		GET DIAGNOSTICS rows_processed = ROW_COUNT;
		end_time := clock_timestamp();
		
		PERFORM bom.log_operation(
			'INSERT', 'bom.year', rows_before, rows_processed,
			rows_before + rows_processed, true, NULL, end_time - start_time
		);

		-- Weeks
		start_time := clock_timestamp();
		SELECT COUNT(*) INTO rows_before FROM bom.week;
		
		INSERT INTO bom.week (
			year, week_number, start_day, end_day, start_month, end_month,
			unique_identifier, week_id, year_range, joinid, split_year
		)
		WITH unique_weeks AS (
			SELECT DISTINCT ON (joinid)
				year, week_number, start_day, end_day, start_month, end_month,
				unique_identifier, week_id, year_range, joinid, split_year
			FROM temp_week
			WHERE joinid IS NOT NULL 
			ORDER BY joinid, year DESC
		)
		SELECT * FROM unique_weeks
		ON CONFLICT (joinid) 
		DO UPDATE
		SET
			start_day = EXCLUDED.start_day,
			start_month = EXCLUDED.start_month,
			end_day = EXCLUDED.end_day,
			end_month = EXCLUDED.end_month,
			year = EXCLUDED.year,
			week_number = EXCLUDED.week_number,
			split_year = EXCLUDED.split_year,
			unique_identifier = EXCLUDED.unique_identifier;
		
		GET DIAGNOSTICS rows_processed = ROW_COUNT;
		end_time := clock_timestamp();
		
		PERFORM bom.log_operation(
			'UPSERT', 'bom.week', rows_before, rows_processed,
			rows_before + rows_processed, true, NULL, end_time - start_time
		);

		-- Parishes
		start_time := clock_timestamp();
		SELECT COUNT(*) INTO rows_before FROM bom.parishes;
		
		INSERT INTO bom.parishes (id, parish_name, canonical_name)
		SELECT DISTINCT parish_id, parish_name, canonical_name 
		FROM temp_parish
		ON CONFLICT (parish_name) 
		DO UPDATE
		SET canonical_name = EXCLUDED.canonical_name
		WHERE bom.parishes.canonical_name IS DISTINCT FROM EXCLUDED.canonical_name;
		
		GET DIAGNOSTICS rows_processed = ROW_COUNT;
		end_time := clock_timestamp();
		
		PERFORM bom.log_operation(
			'UPSERT', 'bom.parishes', rows_before, rows_processed,
			rows_before + rows_processed, true, NULL, end_time - start_time
		);

		-- Christenings
		start_time := clock_timestamp();
		SELECT COUNT(*) INTO rows_before FROM bom.christenings;
		
		INSERT INTO bom.christenings (
		christening, count, week_number, start_day, start_month,
		end_day, end_month, year, missing, illegible, source,
		bill_type, joinid, unique_identifier
	)
	WITH deduplicated_christenings AS (
		SELECT DISTINCT ON (
			parish_name, week, start_day, start_month,
			end_day, end_month, year
		)
			parish_name, count, week, start_day, start_month,
			end_day, end_month, year, missing, illegible, 
			source, bill_type, joinid, unique_identifier
		FROM temp_christening c
		WHERE parish_name IS NOT NULL
		AND EXISTS (SELECT 1 FROM bom.week w WHERE w.joinid = c.joinid)
		ORDER BY 
			parish_name, week, start_day, start_month,
			end_day, end_month, year, count DESC
	)
	SELECT * FROM deduplicated_christenings
		ON CONFLICT (christening, week_number, start_day, start_month, end_day, end_month, year) 
		DO UPDATE
		SET 
			count = EXCLUDED.count,
			missing = EXCLUDED.missing,
			illegible = EXCLUDED.illegible,
			source = EXCLUDED.source,
			bill_type = EXCLUDED.bill_type,
			joinid = EXCLUDED.joinid,
			unique_identifier = EXCLUDED.unique_identifier;
		
		GET DIAGNOSTICS rows_processed = ROW_COUNT;
		end_time := clock_timestamp();
		
		PERFORM bom.log_operation(
			'UPSERT', 'bom.christenings', rows_before, rows_processed,
			rows_before + rows_processed, true, NULL, end_time - start_time
		);

		-- Causes of Death
		start_time := clock_timestamp();
		SELECT COUNT(*) INTO rows_before FROM bom.causes_of_death;
		
		INSERT INTO bom.causes_of_death (
		death, count, year, week_id, descriptive_text, source_name
	)
	SELECT DISTINCT 
		death, count, year, joinid, descriptive_text, source_name
	FROM temp_causes_of_death c
	WHERE death IS NOT NULL
	AND EXISTS (SELECT 1 FROM bom.week w WHERE w.joinid = c.joinid)
	ON CONFLICT (death, year, week_id) 
	DO UPDATE
	SET 
		count = EXCLUDED.count,
		descriptive_text = EXCLUDED.descriptive_text,
		source_name = EXCLUDED.source_name;
		
		GET DIAGNOSTICS rows_processed = ROW_COUNT;
		end_time := clock_timestamp();
		
		PERFORM bom.log_operation(
			'UPSERT', 'bom.causes_of_death', rows_before, rows_processed,
			rows_before + rows_processed, true, NULL, end_time - start_time
		);

		-- Bills of Mortality
		start_time := clock_timestamp();
		SELECT COUNT(*) INTO rows_before FROM bom.bill_of_mortality;
		
		INSERT INTO bom.bill_of_mortality (
			parish_id, count_type, count, year, week_id, bill_type,
			missing, illegible, source, unique_identifier
		)
		WITH deduplicated_bills AS (
		SELECT DISTINCT ON (parish_id, count_type, year, joinid)
			parish_id, count_type, count, year, joinid, bill_type,
			missing, illegible, source, unique_identifier
		FROM temp_bills b
		WHERE parish_id IS NOT NULL 
		AND joinid IS NOT NULL
		AND year IS NOT NULL
		AND EXISTS (SELECT 1 FROM bom.week w WHERE w.joinid = b.joinid)
		ORDER BY parish_id, count_type, year, joinid, count DESC
	)
		SELECT * FROM deduplicated_bills
		ON CONFLICT (parish_id, count_type, year, week_id) 
		DO UPDATE
		SET 
			count = EXCLUDED.count,
			bill_type = EXCLUDED.bill_type,
			missing = EXCLUDED.missing,
			illegible = EXCLUDED.illegible,
			source = EXCLUDED.source,
			unique_identifier = EXCLUDED.unique_identifier;
		
		GET DIAGNOSTICS rows_processed = ROW_COUNT;
		end_time := clock_timestamp();
		
		PERFORM bom.log_operation(
			'UPSERT', 'bom.bill_of_mortality', rows_before, rows_processed,
			rows_before + rows_processed, true, NULL, end_time - start_time
		);

	EXCEPTION WHEN OTHERS THEN
		PERFORM bom.log_operation(
			'ERROR', 'multiple', NULL, NULL, NULL, false,
			SQLERRM, clock_timestamp() - start_time
		);
		RAISE;
	END $$;
	`)

	if err != nil {
		return fmt.Errorf("failed to execute update procedure: %w", err)
	}

	log.Printf("Tables updated successfully in %s", time.Since(start))
	return nil
}

func analyzeTables(ctx context.Context, db *pgxpool.Pool) error {
	log.Println("Running ANALYZE on tables...")

	_, err := db.Exec(ctx, `
		ANALYZE bom.bill_of_mortality;
		ANALYZE bom.year;
		ANALYZE bom.week;
		ANALYZE bom.parishes;
		ANALYZE bom.christenings;
		ANALYZE bom.causes_of_death;

		DO $$
		BEGIN
			PERFORM bom.log_operation(
				'ANALYZE', 'all_tables', NULL, NULL, NULL, true, NULL, NULL
			);
		END $$;
	`)

	return err
}

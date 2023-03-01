package main

import (
	"context"
	"encoding/csv"
	"os"

	pgx "github.com/jackc/pgx/v4"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

func readCsv(filepath string) [][]string {
	f, err := os.Open(filepath)
	if err != nil {
		log.Print("Unable to read file input: "+filepath, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	records, err := csvReader.ReadAll()
	if err != nil {
		log.Print("Unable to read file as CSV for "+filepath, err)
	}
	if err == nil {
		log.Info().Msg("Successfully parsed CSV for " + filepath)
	}

	// Drop the header row
	records = records[1:]

	return records
}

func main() {

	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	// Parse the records from the CSV files
	parishRecords := readCsv("../../scripts/bomr/data/parishes_unique.csv")
	causesRecords := readCsv("../../scripts/bomr/data/causes_of_death.csv")
	allBills := readCsv("../../scripts/bomr/data/all_bills.csv")
	weekRecords := readCsv("../../scripts/bomr/data/week_unique.csv")
	yearRecords := readCsv("../../scripts/bomr/data/year_unique.csv")
	christeningRecords := readCsv("../../scripts/bomr/data/all_christenings.csv")

	// Connect to the database
	conn, err := pgx.Connect(context.Background(), os.Getenv("BOM_DB_STR_LOCAL"))
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to connect to the database.")
		return
	}
	if err == nil {
		log.Info().Msg("Sucessfully connected to the database.")
	}
	defer conn.Close(context.Background())

	// The following inserts each of the datasets into their respective
	// Postgres tables. The data is read from the CSV files above and inserted
	// into the database.
	//
	// Note: The order here is important because of foreign key constraints.

	// 1. Unique years -------------------------------------------------------------
	// Copy the data from the CSV file into the database.
	yearsQuery := `
		INSERT INTO bom.year (year)
		VALUES ($1)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	log.Info().Msg("Inserting unique years...")
	for _, yearRecord := range yearRecords {
		year := yearRecord[0]

		// Execute the query
		_, err = conn.Exec(context.Background(), yearsQuery, year)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert unique years data.")
			return
		}
		if err == nil {
			log.Info().Msg("Sucessfully inserted unique years data.")
		}
	}

	// 2. Unique weeks -------------------------------------------------------------
	// Insert the unique weeks into the bom.weeks table. On conflict, do nothing.
	weeksQuery := `
		INSERT INTO bom.week (year, week_no, start_day, start_month, end_day, end_month, week_id, split_year)
		VALUES (
			$1,
			CASE WHEN $2 = '' THEN NULL ELSE $2::int END,
			CASE WHEN $3 = '' THEN NULL ELSE $3::int END,
			$4,
			CASE WHEN $5 = '' THEN NULL ELSE $5::int END,
			$6,
			$7,
			$8
		)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file. The order here must match
	// the CSV header row. We are skipping the unique_identifier column [5] and the
	// year_range [7] column.
	log.Info().Msg("Inserting unique weeks...")
	for _, weekRecord := range weekRecords {
		year := weekRecord[0]
		weekNum := weekRecord[1]
		startDay := weekRecord[2]
		endDay := weekRecord[3]
		startMonth := weekRecord[4]
		endMonth := weekRecord[6]
		weekID := weekRecord[8]
		splitYear := weekRecord[10]

		// Execute the query
		_, err = conn.Exec(context.Background(), weeksQuery, year, weekNum, startDay, startMonth, endDay, endMonth, weekID, splitYear)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert unique weeks data.")
			return
		}
		if err == nil {
			log.Info().Msg("Sucessfully inserted unique weeks data.")
		}
	}

	// 3. Unique parish names -------------------------------------------------------
	// Insert the parishRecords into the bom.parishes table. On conflict, do nothing.
	parishNamesQuery := `
		INSERT INTO bom.parishes (parish_name, canonical_name) 
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	log.Info().Msg("Inserting parish names...")
	for _, parishRecord := range parishRecords {
		parishName := parishRecord[0]
		canonicalName := parishRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), parishNamesQuery, parishName, canonicalName)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert parish names.")
			return
		}
		if err == nil {
			log.Info().Msg("Sucessfully inserted parish: " + parishName + " (" + canonicalName + ")" + "")
		}
	}

	// 4. Causes of death ---------------------------------------------------------
	// Insert the causes of death into the bom.causes table. On conflict, do nothing.
	causesQuery := `
		INSERT INTO bom.causes_of_death (death, count, descriptive_text, week_id)
		VALUES (
			$1, 
			CASE WHEN $2 = '' THEN NULL ELSE $2::int END,
			$3, 
			$4
		)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, causeRecord := range causesRecords {
		death := causeRecord[1]
		count := causeRecord[2]
		weekID := causeRecord[4]
		description := causeRecord[7]

		// Execute the query
		_, err = conn.Exec(context.Background(), causesQuery, death, count, weekID, description)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert causes of death.")
			return
		}
		if err == nil {
			log.Info().Msg("Sucessfully inserted causes of death.")
		}
	}

	// 5. All bills ----------------------------------------------------------------
	// Insert the all bills into the bom.bills table. On conflict, do nothing.
	billsQuery := `
		INSERT INTO bom.bill_of_mortality (id, parish_id, collective_id, count_type, count, week_id, bill_type)
		VALUES (
			$1, 
			$2, 
			$3, 
			$4, 
			CASE WHEN $5 = '' THEN NULL ELSE $5::int END,
			$6, 
			$7
		)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, billRecord := range allBills {
		countType := billRecord[0]
		count := billRecord[1]
		billType := billRecord[2]
		parishID := billRecord[3]
		weekID := billRecord[4]
		collectiveID := 0 // make sure this exists in parish_collective table
		id := billRecord[8]

		// Execute the query
		_, err = conn.Exec(context.Background(), billsQuery, id, parishID, collectiveID, countType, count, weekID, billType)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert all bills.")
			return
		}
		if err == nil {
			log.Info().Msg("Sucessfully inserted all bills.")
		}
	}

	// 6. Christenings -------------------------------------------------------------
	// Insert the christenings into the bom.christenings table. On conflict, do nothing.
	// year, week_number, unique_identifier, start_day, start_month, end_day, end_month, christening, count, id
	christeningsQuery := `
		INSERT INTO bom.christenings (year, week_number, start_day, start_month, end_day, end_month, christening, count, id)
		VALUES (
			$1,
			$2,
			CASE WHEN $3 = '' THEN NULL ELSE $3::int END,
			$4,
			CASE WHEN $5 = '' THEN NULL ELSE $5::int END,
			$6,
			$7,
			CASE WHEN $8 = '' THEN NULL ELSE $8::int END,
			$9
		)
		ON CONFLICT DO NOTHING
		`

	// Assign variables to the values in the CSV file
	for _, christeningRecord := range christeningRecords {
		year := christeningRecord[0]
		weekNum := christeningRecord[1]
		startDay := christeningRecord[3]
		startMonth := christeningRecord[4]
		endDay := christeningRecord[5]
		endMonth := christeningRecord[6]
		christening := christeningRecord[7]
		count := christeningRecord[8]
		id := christeningRecord[9]

		// Execute the query
		_, err = conn.Exec(context.Background(), christeningsQuery, year, weekNum, startDay, startMonth, endDay, endMonth, christening, count, id)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert christenings data.")
			return
		}
		if err == nil {
			log.Info().Msg("Sucessfully inserted christenings data.")
		}
	}

	// Wrap up
	log.Info().Msg("Successfully inserted all data into the database.")
	log.Info().Msg("Closing connection to database.")
	conn.Close(context.Background())
}

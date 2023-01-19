package main

import (
	"context"
	"encoding/csv"
	"os"

	pgx "github.com/jackc/pgx/v4"
	log "github.com/sirupsen/logrus"
)

func readCsv(filepath string) [][]string {
	f, err := os.Open(filepath)
	if err != nil {
		log.Fatal("Unable to read file input: "+filepath, err)
	}
	defer f.Close()

	csvReader := csv.NewReader(f)
	records, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal("Unable to read file as CSV for "+filepath, err)
	}

	// Drop the header row
	records = records[1:]

	return records
}

func main() {

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
		log.Fatal("Unable to connect to database: ", err)
	}
	if err == nil {
		log.Info("Connected to database.")
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
		INSERT INTO bom.year (id, year_id, year)
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, yearRecord := range yearRecords {
		id := yearRecord[0]
		yearID := yearRecord[1]
		year := yearRecord[2]

		// Execute the query
		_, err = conn.Exec(context.Background(), yearsQuery, id, yearID, year)
		if err != nil {
			log.Fatal("Unable to insert unique years: ", err)
		}
	}

	// 2. Unique weeks -------------------------------------------------------------
	// Insert the unique weeks into the bom.weeks table. On conflict, do nothing.
	weeksQuery := `
		INSERT INTO bom.week (id, week_id, week_no, start_day, start_month, end_day, end_month, year, split_year)
		VALUES (
			CASE WHEN $1 = '' THEN NULL ELSE $1::int END, 
			$2,
			CASE WHEN $3 = '' THEN NULL ELSE $3::int END, 
			CASE WHEN $4 = '' THEN NULL ELSE $4::int END, 
			$5, 
			CASE WHEN $6 = '' THEN NULL ELSE $6::int END,
			$7, 
			$8, 
			$9
		)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file. The order here must match
	// the CSV header row. We are skipping the unique_identifier column [5] and the
	// year_range [7] column.
	for _, weekRecord := range weekRecords {
		weekNum := weekRecord[0]
		startDay := weekRecord[1]
		endDay := weekRecord[2]
		startMonth := weekRecord[3]
		endMonth := weekRecord[4]
		weekID := weekRecord[6]
		year := weekRecord[8]
		splitYear := weekRecord[9]
		id := weekRecord[10]

		// Execute the query
		_, err = conn.Exec(context.Background(), weeksQuery, id, weekID, weekNum, startDay, startMonth, endDay, endMonth, year, splitYear)
		if err != nil {
			log.Fatal("Unable to insert unique weeks data: \n\t", err)
		}
	}

	// 3. Unique parish names -------------------------------------------------------
	// Insert the parishRecords into the bom.parishes table. On conflict, do nothing.
	parishNamesQuery := `
		INSERT INTO bom.parishes (id, parish_name, canonical_name) 
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, parishRecord := range parishRecords {
		parishName := parishRecord[0]
		canonicalName := parishRecord[1]
		parishID := parishRecord[2]

		// Execute the query
		_, err = conn.Exec(context.Background(), parishNamesQuery, parishID, parishName, canonicalName)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 4. Causes of death ---------------------------------------------------------
	// Insert the causes of death into the bom.causes table. On conflict, do nothing.
	causesQuery := `
		INSERT INTO bom.causes_of_death (death, count, year, week_id, id)
		VALUES (
			$1, 
			CASE WHEN $2 = '' THEN NULL ELSE $2::int END, 
			$3, 
			$4, 
			$5
		)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, causeRecord := range causesRecords {
		death := causeRecord[1]
		count := causeRecord[2]
		year := causeRecord[3]
		weekID := causeRecord[4]
		id := causeRecord[6]

		// Execute the query
		_, err = conn.Exec(context.Background(), causesQuery, death, count, year, weekID, id)
		if err != nil {
			log.Fatal("Unable to insert causes of death: ", err)
		}
	}

	// 5. All bills ----------------------------------------------------------------
	// Insert the all bills into the bom.bills table. On conflict, do nothing.
	billsQuery := `
		INSERT INTO bom.bill_of_mortality (id, parish_id, collective_id, count_type, count, year, week_id, bill_type)
		VALUES (
			$1, 
			$2, 
			$3, 
			$4, 
			CASE WHEN $5 = '' THEN NULL ELSE $5::int END,
			$6, 
			$7, 
			$8
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
		yearID := billRecord[6]
		id := billRecord[8]

		// Execute the query
		_, err = conn.Exec(context.Background(), billsQuery, id, parishID, collectiveID, countType, count, yearID, weekID, billType)
		if err != nil {
			log.Fatal("Unable to insert all bills: \n\t", err)
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
			log.Fatal("Unable to insert christenings: \n\t", err)
		}
	}

	// Wrap up
	log.Info("Successfully inserted all data into the database.")
	log.Info("Closing connection to database.")
	conn.Close(context.Background())
}

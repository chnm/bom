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
	deathRecords := readCsv("../../scripts/bomr/data/deaths_unique.csv")
	allBills := readCsv("../../scripts/bomr/data/all_bills.csv")
	weekRecords := readCsv("../../scripts/bomr/data/week_unique.csv")
	yearRecords := readCsv("../../scripts/bomr/data/year_unique.csv")

	// Connect to the database
	conn, err := pgx.Connect(context.Background(), os.Getenv("BOM_DB_STR"))
	if err != nil {
		log.Fatal("Unable to connect to database: ", err)
	}
	defer conn.Close(context.Background())

	// The following inserts each of the data types into their respective
	// Postgres tables. The data is read from the CSV files and inserted
	// into the database.

	// 1. Unique parish names -------------------------------------------------------
	// Insert the parishRecords into the bom.parishes table. On conflict, do nothing.
	parishNamesQuery := `
		INSERT INTO bom.parishes (parish_name, canonical_name, parish_id) 
		VALUES ($1, $2, $3)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, parishRecord := range parishRecords {
		parishName := parishRecord[0]
		canonicalName := parishRecord[1]
		parishID := parishRecord[2]

		// Execute the query
		_, err = conn.Exec(context.Background(), parishNamesQuery, parishName, canonicalName, parishID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 2. Types of death ---------------------------------------------------------
	// Insert the deathRecords into the bom.deaths table. On conflict, do nothing.
	deathsQuery := `
		INSERT INTO bom.deaths (cause, cause_id)
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, deathRecord := range deathRecords {
		cause := deathRecord[0]
		causeID := deathRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), deathsQuery, cause, causeID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 3. Causes of death ---------------------------------------------------------
	// Insert the causes of death into the bom.causes table. On conflict, do nothing.
	causesQuery := `
		INSERT INTO bom.causes (cause, cause_id)
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, causeRecord := range causesRecords {
		cause := causeRecord[0]
		causeID := causeRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), causesQuery, cause, causeID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 4. All bills ----------------------------------------------------------------
	// Insert the all bills into the bom.bills table. On conflict, do nothing.
	billsQuery := `
		INSERT INTO bom.bills ()
		VALUES ()
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, billRecord := range allBills {
		cause := billRecord[0]
		causeID := billRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), billsQuery, cause, causeID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 5. Unique weeks -------------------------------------------------------------
	// Insert the unique weeks into the bom.weeks table. On conflict, do nothing.
	weeksQuery := `
		INSERT INTO bom.weeks (week, week_id)
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, weekRecord := range weekRecords {
		week := weekRecord[0]
		weekID := weekRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), weeksQuery, week, weekID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 6. Unique years -------------------------------------------------------------
	// Insert the unique years into the bom.years table. On conflict, do nothing.
	yearsQuery := `
		INSERT INTO bom.years (year, year_id)
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, yearRecord := range yearRecords {
		year := yearRecord[0]
		yearID := yearRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), yearsQuery, year, yearID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	log.Info("Successfully inserted all data into the database.")
	log.Info("Closing connection to database.")
	conn.Close(context.Background())
}

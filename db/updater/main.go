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
	christeningRecords := readCsv("../../scripts/bomr/data/christenings.csv")
	christeningsLocations := readCsv("../../scripts/bomr/data/christenings_locations.csv")

	// Connect to the database
	conn, err := pgx.Connect(context.Background(), os.Getenv("BOM_DB_STR"))
	if err != nil {
		log.Fatal("Unable to connect to database: ", err)
	}
	defer conn.Close(context.Background())

	// The following inserts each of the datasets into their respective
	// Postgres tables. The data is read from the CSV files above and inserted
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
		INSERT INTO bom.causes_of_death (death, count, year, week_id, id, death_id)
		VALUES ($1, $2, $3, $4, $5, $6)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, causeRecord := range causesRecords {
		death := causeRecord[0]
		count := causeRecord[1]
		year := causeRecord[2]
		weekID := causeRecord[3]
		id := causeRecord[4]
		deathID := causeRecord[5]

		// Execute the query
		_, err = conn.Exec(context.Background(), causesQuery, death, count, year, weekID, id, deathID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 4. All bills ----------------------------------------------------------------
	// Insert the all bills into the bom.bills table. On conflict, do nothing.
	billsQuery := `
		INSERT INTO bom.bill_of_mortality (id, parish_id, collective_id, count_type, count, year_id, week_id, bill_type)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, billRecord := range allBills {
		id := billRecord[0]
		parishID := billRecord[1]
		collectiveID := billRecord[2]
		countType := billRecord[3]
		count := billRecord[4]
		yearID := billRecord[5]
		weekID := billRecord[6]
		billType := billRecord[7]

		// Execute the query
		_, err = conn.Exec(context.Background(), billsQuery, id, parishID, collectiveID, countType, count, yearID, weekID, billType)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 5. Unique weeks -------------------------------------------------------------
	// Insert the unique weeks into the bom.weeks table. On conflict, do nothing.
	weeksQuery := `
		INSERT INTO bom.week (id, week_id, start_day, start_month, end_day, end_month, year_id, week_no, split_year)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, weekRecord := range weekRecords {
		id := weekRecord[0]
		weekID := weekRecord[1]
		startDay := weekRecord[2]
		startMonth := weekRecord[3]
		endDay := weekRecord[4]
		endMonth := weekRecord[5]
		yearID := weekRecord[6]
		weekNo := weekRecord[7]
		splitYear := weekRecord[8]

		// Execute the query
		_, err = conn.Exec(context.Background(), weeksQuery, id, weekID, startDay, startMonth, endDay, endMonth, yearID, weekNo, splitYear)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 6. Unique years -------------------------------------------------------------
	// Insert the unique years into the bom.years table. On conflict, do nothing.
	yearsQuery := `
		INSERT INTO bom.year (id, year_id, split_year, year)
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
	`

	// Assign variables to the values in the CSV file
	for _, yearRecord := range yearRecords {
		id := yearRecord[0]
		yearID := yearRecord[1]
		splitYear := yearRecord[2]
		year := yearRecord[3]

		// Execute the query
		_, err = conn.Exec(context.Background(), yearsQuery, id, yearID, splitYear, year)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 7. Christenings -------------------------------------------------------------
	// Insert the christenings into the bom.christenings table. On conflict, do nothing.
	christeningsQuery := `
		INSERT INTO bom.christenings (id, week_id, christening_desc, count, year_id)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT DO NOTHING
		`

	// Assign variables to the values in the CSV file
	for _, christeningRecord := range christeningRecords {
		id := christeningRecord[0]
		weekID := christeningRecord[1]
		christeningDesc := christeningRecord[2]
		count := christeningRecord[3]
		yearID := christeningRecord[4]

		// Execute the query
		_, err = conn.Exec(context.Background(), christeningsQuery, id, weekID, christeningDesc, count, yearID)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	// 8. Christening locations -----------------------------------------------------
	// Insert the christening locations into the bom.christening_locations table. On conflict, do nothing.
	christeningLocationsQuery := `
		INSERT INTO bom.christening_locations (id, name)
		VALUES ($1, $2)
		ON CONFLICT DO NOTHING
		`

	// Assign variables to the values in the CSV file
	for _, christeningLocationRecord := range christeningsLocations {
		id := christeningLocationRecord[0]
		name := christeningLocationRecord[1]

		// Execute the query
		_, err = conn.Exec(context.Background(), christeningLocationsQuery, id, name)
		if err != nil {
			log.Fatal("Unable to insert parish names: ", err)
		}
	}

	log.Info("Successfully inserted all data into the database.")
	log.Info("Closing connection to database.")
	conn.Close(context.Background())
}

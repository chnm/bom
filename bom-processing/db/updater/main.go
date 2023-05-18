package main

import (
	"context"
	"encoding/csv"
	"io"
	"os"
	"strconv"

	"github.com/jackc/pgx/v4/pgxpool"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

type Parish struct {
	ParishName    string
	CanonicalName string
	ParishID      int
}

type CauseOfDeath struct {
	Death          string
	Count          int
	DescriptiveTxt string
	JoinID         string
	Year           int
	WeekID         string
	YearRange      string
	SplitYear      string
}

type MortalityBill struct {
	UniqueID  string
	CountType string
	Count     int
	BillType  string
	ParishID  int
	YearID    string
	WeekID    string
	YearRange string
	SplitYear string
	JoinID    string
	ID        int
}

type Christening struct {
	Year       int
	WeekNumber int
	UniqueID   string
	StartDay   int
	StartMonth string
	EndDay     int
	EndMonth   string
	ParishName string
	Count      int
	BillType   string
	JoinID     string
}

type ChristeningLocation struct {
	ID   int
	Name string
}

type Week struct {
	Year       int
	WeekNumber int
	StartDay   int
	EndDay     int
	StartMonth string
	EndMonth   string
	UniqueID   string
	WeekID     string
	YearRange  string
	SplitYear  string
	JoinID     string
}

type Year struct {
	YearID int
	Year   int
	ID     int
}

func readParishData(pool *pgxpool.Pool) error {
	file, err := os.Open("../../scripts/bomr/data/parishes_unique.csv")
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to open file.")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, err = reader.Read()
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read file.")
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to read file.")
		}

		parishIdAsInt, err := strconv.Atoi(record[2])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert parish id to int.")
		}

		parish := Parish{
			ParishName:    record[0],
			CanonicalName: record[1],
			ParishID:      parishIdAsInt,
		}

		err = insertParishData(pool, &parish)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert parish data.")
		}
	}
	return nil
}

func insertParishData(pool *pgxpool.Pool, parish *Parish) error {
	query := `
		INSERT INTO bom.parishes (parish_name, canonical_name, id)
		VALUES ($1, $2, $3)
		ON CONFLICT (parish_name) DO NOTHING
	`

	_, err := pool.Exec(context.Background(), query, parish.ParishName, parish.CanonicalName, parish.ParishID)
	if err != nil {
		return err
	}
	return nil
}

func readYearData(pool *pgxpool.Pool) error {
	file, err := os.Open("../../scripts/bomr/data/year_unique.csv")
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to open file.")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, err = reader.Read()
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read file.")
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to read file.")
		}

		yearAsInt, err := strconv.Atoi(record[0])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert year to int.")
		}

		yearIdAsInt, err := strconv.Atoi(record[1])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert year id to int.")
		}

		idAsInt, err := strconv.Atoi(record[2])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert id to int.")
		}

		year := Year{
			Year:   yearAsInt,
			YearID: yearIdAsInt,
			ID:     idAsInt,
		}

		err = insertYearData(pool, &year)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert year data.")
		}
	}
	return nil
}

func insertYearData(pool *pgxpool.Pool, year *Year) error {
	query := `
		INSERT INTO bom.year(year)
		VALUES ($1)
		ON CONFLICT (year) DO NOTHING
	`

	_, err := pool.Exec(context.Background(), query, year.Year)
	if err != nil {
		return err
	}
	return nil
}

func readWeekData(pool *pgxpool.Pool) error {
	file, err := os.Open("../../scripts/bomr/data/week_unique.csv")
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to open file.")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, err = reader.Read()
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read file.")
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to read file.")
		}

		var yearInt int
		var weekNoInt int
		var startDayInt int
		var endDayInt int

		// Check that values are not empty. If they are, set them to NULL.
		// Check that year is not empty
		if record[0] == "" {
			record[0] = ""
		} else {
			yearAsInt, err := strconv.Atoi(record[0])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert year to int.")
			}
			yearInt = yearAsInt
		}
		// Check that week number is not empty
		if record[1] == "" {
			record[1] = ""
		} else {
			weekNoAsInt, err := strconv.Atoi(record[1])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert week no to int.")
			}
			weekNoInt = weekNoAsInt
		}
		// Check that start day is not empty
		if record[2] == "" {
			record[2] = ""
		} else {
			startDayAsInt, err := strconv.Atoi(record[2])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert start day to int.")
			}
			startDayInt = startDayAsInt
		}
		// Check that end day is not empty
		if record[3] == "" {
			record[3] = ""
		} else {
			endDayAsInt, err := strconv.Atoi(record[3])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert end day to int.")
			}
			endDayInt = endDayAsInt
		}

		// yearAsInt, err := strconv.Atoi(record[0])
		// if err != nil {
		// 	log.Error().Stack().Err(err).Msg("Unable to convert year to int.")
		// }
		// weekNoAsInt, err := strconv.Atoi(record[1])
		// if err != nil {
		// 	log.Error().Stack().Err(err).Msg("Unable to convert week no to int.")
		// }
		// startDayAsInt, err := strconv.Atoi(record[2])
		// if err != nil {
		// 	log.Error().Stack().Err(err).Msg("Unable to convert start day to int.")
		// }
		// endDayAsInt, err := strconv.Atoi(record[3])
		// if err != nil {
		// 	log.Error().Stack().Err(err).Msg("Unable to convert end day to int.")
		// }

		week := Week{
			Year:       yearInt,
			WeekNumber: weekNoInt,
			StartDay:   startDayInt,
			EndDay:     endDayInt,
			StartMonth: record[4],
			EndMonth:   record[5],
			UniqueID:   record[6],
			WeekID:     record[7],
			YearRange:  record[8],
			SplitYear:  record[9],
			JoinID:     record[10],
		}

		err = insertWeekData(pool, &week)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert week data.")
		}
	}
	return nil
}

func insertWeekData(pool *pgxpool.Pool, week *Week) error {
	query := `
		INSERT INTO bom.week(joinid, start_day, start_month, end_day, end_month, year, week_no, split_year)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		ON CONFLICT (joinid) DO NOTHING
	`

	_, err := pool.Exec(context.Background(), query, week.JoinID, week.StartDay, week.StartMonth, week.EndDay, week.EndMonth, week.Year, week.WeekNumber, week.SplitYear)
	if err != nil {
		return err
	}
	return nil
}

func readCausesData(pool *pgxpool.Pool) error {
	file, err := os.Open("../../scripts/bomr/data/causes_of_death.csv")
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to open file.")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, err = reader.Read()
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read file.")
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to read file.")
		}

		var countInt int

		if record[1] == "" {
			record[1] = ""
		} else {
			countAsInt, err := strconv.Atoi(record[1])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert count to int.")
			}
			countInt = countAsInt
		}

		// countAsInt, err := strconv.Atoi(record[1])
		// if err != nil {
		// log.Error().Stack().Err(err).Msg("Unable to convert count to int.")
		// }

		yearAsInt, err := strconv.Atoi(record[4])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert year to int.")
		}

		causes := CauseOfDeath{
			Death:          record[0],
			Count:          countInt,
			DescriptiveTxt: record[2],
			JoinID:         record[3],
			Year:           yearAsInt,
			WeekID:         record[5],
			YearRange:      record[6],
			SplitYear:      record[7],
		}

		err = insertCausesData(pool, &causes)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert causes data.")
		}
	}
	return nil
}

func insertCausesData(pool *pgxpool.Pool, causes *CauseOfDeath) error {
	query := `
		INSERT INTO bom.causes_of_death(death, count, year, week_id, descriptive_text)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT DO NOTHING
	`

	_, err := pool.Exec(context.Background(), query, causes.Death, causes.Count, causes.Year, causes.JoinID, causes.DescriptiveTxt)
	if err != nil {
		return err
	}
	return nil
}

func readChristeningsData(pool *pgxpool.Pool) error {
	file, err := os.Open("../../scripts/bomr/data/christenings_by_parish.csv")
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to open file.")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, err = reader.Read()
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read file.")
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to read file.")
		}

		var countInt int
		if record[1] == "" {
			record[1] = ""
		} else {
			countAsInt, err := strconv.Atoi(record[1])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert count to int.")
			}
			countInt = countAsInt
		}

		yearAsInt, err := strconv.Atoi(record[0])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert year to int.")
		}

		weekNumberAsInt, err := strconv.Atoi(record[1])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert week number to int.")
		}

		var startDayInt int
		var endDayInt int

		if record[3] == "" {
			record[3] = ""
		} else {
			startDayAsInt, err := strconv.Atoi(record[3])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert start day to int.")
			}
			startDayInt = startDayAsInt
		}

		if record[5] == "" {
			record[5] = ""
		} else {
			endDayAsInt, err := strconv.Atoi(record[5])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert end day to int.")
			}
			endDayInt = endDayAsInt
		}

		christenings := Christening{
			Year:       yearAsInt,
			WeekNumber: weekNumberAsInt,
			UniqueID:   record[2],
			StartDay:   startDayInt,
			StartMonth: record[4],
			EndDay:     endDayInt,
			EndMonth:   record[6],
			ParishName: record[7],
			Count:      countInt,
			BillType:   record[9],
			JoinID:     record[10],
		}

		err = insertChristeningsData(pool, &christenings)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert christenings data.")
		}
	}
	return nil
}

func insertChristeningsData(pool *pgxpool.Pool, christenings *Christening) error {
	query := `
		INSERT INTO bom.christenings(christening, count, week_number, start_month, end_month, year, start_day, end_day)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		ON CONFLICT DO NOTHING
	`

	_, err := pool.Exec(context.Background(), query, christenings.ParishName, christenings.Count, christenings.WeekNumber, christenings.StartMonth, christenings.EndMonth, christenings.Year, christenings.StartDay, christenings.EndDay)
	if err != nil {
		return err
	}
	return nil
}

func readMortalityBill(pool *pgxpool.Pool) error {
	file, err := os.Open("../../scripts/bomr/data/all_bills.csv")
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to open file.")
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, err = reader.Read()
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read file.")
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to read file.")
		}

		parishIdAsInt, err := strconv.Atoi(record[4])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert parish id to int.")
		}
		idAsInt, err := strconv.Atoi(record[10])
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to convert id to int.")
		}

		var countInt int
		if record[2] == "" {
			record[2] = ""
		} else {
			countAsInt, err := strconv.Atoi(record[2])
			if err != nil {
				log.Error().Stack().Err(err).Msg("Unable to convert count to int.")
			}
			countInt = countAsInt
		}

		mortalitybills := MortalityBill{
			//0 unique_identifier,
			//1 count_type,
			//2 count,
			//3 bill_type,
			//4 parish_id,
			//5 year,
			//6 week_id,
			//7 year_range,
			//8 split_year,
			//9 joinid,
			//10 id
			UniqueID:  record[0],
			CountType: record[1],
			Count:     countInt,
			BillType:  record[3],
			ParishID:  parishIdAsInt,
			YearID:    record[5],
			WeekID:    record[6],
			YearRange: record[7],
			SplitYear: record[8],
			JoinID:    record[9],
			ID:        idAsInt,
		}

		err = insertMortalityBill(pool, &mortalitybills)
		if err != nil {
			log.Error().Stack().Err(err).Msg("Unable to insert mortality bill data.")
		}

	}
	return nil
}

func insertMortalityBill(pool *pgxpool.Pool, mortalitybills *MortalityBill) error {
	query := `
		INSERT INTO bom.bill_of_mortality(parish_id, count_type, count, year_id, week_id, bill_type)
		VALUES ($1, $2, $3, $4, $5, $6)
		ON CONFLICT DO NOTHING
	`

	_, err := pool.Exec(context.Background(), query, mortalitybills.ParishID, mortalitybills.CountType, mortalitybills.Count, mortalitybills.YearID, mortalitybills.JoinID, mortalitybills.BillType)
	if err != nil {
		return err
	}
	return nil
}

func main() {
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	// Create the connection pool.
	connStr := os.Getenv("BOM_DB_STR_LOCAL")
	log.Info().Msg("Connecting to database...")
	pool, err := pgxpool.Connect(context.Background(), connStr)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to connect to database.")
	}
	defer pool.Close()

	log.Info().Msg("Reading and inserting Parish data...")
	err = readParishData(pool)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read parish data.")
	}

	log.Info().Msg("Reading and inserting Year data...")
	err = readYearData(pool)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read year data.")
	}

	log.Info().Msg("Reading and inserting Week data...")
	err = readWeekData(pool)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read week data.")
	}

	log.Info().Msg("Reading and inserting Causes of Death data...")
	err = readCausesData(pool)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read causes data.")
	}

	log.Info().Msg("Reading and inserting Christenings data...")
	err = readChristeningsData(pool)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read christenings data.")
	}

	log.Info().Msg("Reading and inserting Bills of Mortality data...")
	err = readMortalityBill(pool)
	if err != nil {
		log.Error().Stack().Err(err).Msg("Unable to read mortality bill data.")
	}

	log.Info().Msg("Done!")
}

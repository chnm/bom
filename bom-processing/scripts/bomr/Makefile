# Database update
# The following inserts updated data into the bom tables.
# TODO: Implement the script here.

# Datasette ---------------------------------------------------------------
# The following is for simple spot-checking the data files.
# Dependencies: sqlite, sqlite-utils, datasette

create : # if data.db doesn't exist, create it
	if [ ! -f data.db ]; then \
		touch data.db; \
	fi

insert :
	echo "Inserting all bills:"; \
	sqlite-utils insert data.db bills data/all_bills.csv --csv; \
	sqlite-utils insert data.db general data/bills_general.csv --csv; \
	sqlite-utils insert data.db weekly data/bills_weekly.csv --csv; \
	sqlite-utils insert data.db causes data/causes_of_death.csv --csv; \
	sqlite-utils insert data.db parishes data/parishes_unique.csv --csv;

schema :
	sqlite-utils tables data.db --schema --table

serve :
	datasette data.db

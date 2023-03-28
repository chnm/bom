all : 
	@echo "Please specify a target. Available targets are:"
	@echo "  update - Updates the database with new data"
	@echo "  init-up - Rebuilds the database tables"
	@echo "  init-down - Drops the database tables"
	
update :
	@echo "Inserting new SQL data..."
	psql ${BOM_DB_STR} -f insert_update.sql 
	@echo "Finished inserting new SQL data."

check : 
	@echo "Are you sure? [Y/n] " && read ans && if [ $${ans:-'Y'} = 'n' ]; then \
        printf $(_ERROR) "KO" "Stopping" ; \
        exit 1 ; \
    else \
        printf $(_SUCCESS) "OK" "Continuing" ; \
        exit 0; \
    fi

init-up : check
	@echo "\nBuilding database tables..."
	psql ${BOM_DB_STR} -f migrations/initialize.up.sql
	@echo "Finished rebuilding database tables."

init-down : check
	@echo "\nDropping database tables..."
	psql ${BOM_DB_STR} -f migrations/initialize.down.sql
	@echo "Finished dropping database tables."

.PHONY : all update init-up init-down

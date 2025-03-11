# Note: This makefile depends on golang-migrate 
# https://github.com/golang-migrate/migrate

BINARY_NAME=bom-importer
MAIN_PACKAGE=./updater
BINARY_DIR=bin
BUILD_DIR=updater
GOPATH=$(shell go env GOPATH)
VERSION=$(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
LDFLAGS=-ldflags "-X main.Version=$(VERSION)"

# Use .env to set environment variables
# Set DB_CONN_STR and DATA_DIR
ifneq (,$(wildcard .env))
    include .env
else
    $(error No .env file found. Please create one, reference .env.example for details)
endif

all : help

# Help command
help:
	@echo "Make targets:"
	@echo "  all          - Help information"
	@echo "  build        - Build the application"
	@echo "  fmt          - Format the code"
	@echo "  vet          - Run go vet"
	@echo "  dry-run      - Run in dry-run mode (no database changes)"
	@echo "  deps         - Download dependencies"
	@echo "  db-update    - Insert a data update"
	@echo "  db-up        - Run database migrations up"
	@echo "  db-down      - Run database migrations down"

# Create the bin directory if it doesn't exist
$(BINARY_DIR):
	mkdir -p $(MAIN_PACKAGE)/$(BINARY_DIR)

deps:
	go mod download

build: $(BINARY_DIR)
	cd $(MAIN_PACKAGE) && go build $(LDFLAGS) -o bin/$(BINARY_NAME) .

fmt:
	cd $(MAIN_PACKAGE) && go fmt ./...

vet:
	cd $(MAIN_PACKAGE) && go vet ./...

# Database operations
check:
	@echo "Are you sure? [Y/n] \nYou are connecting to $(DB_CONN_STR) " && read ans && \
	if [ "$${ans:-Y}" = "n" ]; then \
		printf "$(_ERROR)KO: Stopping\n\n"; \
		exit 1; \
	else \
		printf "$(_SUCCESS)OK: Continuing\n\n"; \
	fi

dry-run : check 
	@echo "Dry-run mode enabled. No database changes will be made."
	cd $(MAIN_PACKAGE) && ./$(BINARY_DIR)/$(BINARY_NAME) -db ${DB_CONN_STR} -data ${DATA_DIR} --dry-run

db-test:
	@echo "Testing connection to database..."
	@echo "Using connection string: $(DB_CONN_STRING)"
	@if command -v psql >/dev/null 2>&1; then \
		psql "$(DB_CONN_STRING)" -c "SELECT 1 AS connected" && \
		echo -e "\n\033[0;32m✓ Connection successful\033[0m\n"; \
	elif command -v pg_isready >/dev/null 2>&1; then \
		(pg_isready -d "$(subst postgresql://,,$(DB_CONN_STRING))") && \
		echo -e "\n\033[0;32m✓ Connection successful\033[0m\n"; \
	else \
		echo -e "\n\033[0;31m✗ Error: psql or pg_isready command not found. Please install PostgreSQL client tools.\033[0m\n"; \
		exit 1; \
	fi

db-update : check
	@echo "Inserting new SQL data..."
	cd $(MAIN_PACKAGE) && ./$(BINARY_DIR)/$(BINARY_NAME) -db ${DB_CONN_STR} -data ${DATA_DIR}
	@echo "Finished inserting new SQL data."

db-up: check
	@echo "Running database migrations..."
	migrate -path ./migrations -database ${DB_CONN_STR} up

db-down: check
	@echo "Reverting database migrations..."
	migrate -path ./migrations -database ${DB_CONN_STR} down


.PHONY : all build fmt vet check dry-run db-update db-up db-down

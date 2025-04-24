# Bills of Mortality Data Importer

## Overview

This provides a data import tool for historical Bills of Mortality data, allowing you to load and process CSV files into a PostgreSQL database.

## Prerequisites

- Go (1.16+)
- PostgreSQL
- `golang-migrate` for database migrations
- Make

### Required Tools

1. **Go**: Download and install from [golang.org](https://golang.org/dl/)
2. **PostgreSQL**: Install from [postgresql.org](https://www.postgresql.org/download/)
3. **golang-migrate**: 
   ```bash
   go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest
   ```

## Configuration

### Environment Setup

1. Create a `.env` file in the project root based on the `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set:
   - `DB_CONN_STR`: PostgreSQL connection string
     - Format: `postgresql://username:password@host:port/dbname`
   - `DATA_DIR`: Directory containing your CSV files

### Database Preparation

Before importing data, ensure your database is prepared:

```bash
# Run database migrations
make db-up
```

## Usage

### Import Commands

1. **Dry Run (Test Import)**:
   ```bash
   make dry-run
   ```
   This will simulate the import process without making any database changes.

2. **Full Data Import**:
   ```bash
   make db-update
   ```
   This will import data from the CSV files specified in `DATA_DIR`.

### Development Commands

- `make build`: Compile the application
- `make fmt`: Format Go code
- `make vet`: Run Go code analysis
- `make deps`: Download project dependencies

### Database Management

- `make db-up`: Apply database migrations
- `make db-down`: Revert database migrations
- `make db-test`: Test database connection

## Imported Data Tables

The importer populates the following tables in the `bom` schema:

1. **Years**: Historical year records
2. **Weeks**: Weekly records with identifiers
3. **Parishes**: Location information
4. **Christenings**: Baptism records
5. **Causes of Death**: Mortality cause details
6. **Bills of Mortality**: Comprehensive mortality records

## Error Handling

- The importer uses transactions to ensure data integrity
- Duplicate records are handled with "upsert" logic
- Detailed logging is provided for each import operation

## Logging

Import operations are logged in a custom `bom.log_operation` table, tracking:
- Operation type
- Table affected
- Rows processed
- Timestamp
- Execution time

## Performance Considerations

- The importer uses PostgreSQL's `COPY` protocol for efficient data loading
- `ANALYZE` is run after import to update table statistics

## Troubleshooting

1. Ensure CSV files match the expected format
2. Check database connection string
3. Verify data directory path
4. Review import logs for specific errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request



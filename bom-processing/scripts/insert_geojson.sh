#!/bin/bash
# ===========================================================================
# GeoJSON to PostgreSQL Import Script
# ===========================================================================
#
# DESCRIPTION:
#   This script imports GeoJSON files located in the geoJSON-files directory
#   into a PostgreSQL database with PostGIS extension. Each GeoJSON file
#   represents historical parish boundaries for London parishes within the
#   Bills of Mortality for different years.
#
# USAGE:
#   ./insert_geojson.sh [source_directory] [database_name] [database_user]
#
# ARGUMENTS:
#   source_directory - Optional. Path to the directory containing GeoJSON files.
#                      If not provided, defaults to '../../bom-data/geoJSON-files'.
#   database_name    - Optional. Name of the PostgreSQL database.
#                      If not provided, defaults to 'bom'.
#   database_user    - Optional. PostgreSQL user to connect with.
#                      If not provided, defaults to 'postgres'.
#
# DIRECTORY STRUCTURE:
#   Source directory should contain individual GeoJSON files for each year/period,
#   with filenames like 'WithinTheBills1582.geojson', 'WithinTheBills1603.geojson', etc.
#   We generate these with the create_geojson.sh script before these inserts are done.
#
# REQUIREMENTS:
#   - GDAL/OGR tools (ogr2ogr) must be installed
#   - PostgreSQL with PostGIS extension must be running
#   - Database user must have privileges to create/modify tables
#   - Proper permissions to read source GeoJSON files
#
# EXAMPLE:
#   ./insert_geojson.sh ../../bom-data/geoJSON-files bom postgres
#
# ===========================================================================

# Set default parameters if not provided
SOURCE_DIR="${1:-../../bom-data/geoJSON-files}"
DB_NAME="${2:-bom}"
DB_USER="${3:-postgres}"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Directory '$SOURCE_DIR' does not exist."
  echo "Usage: $0 [source_directory] [database_name] [database_user]"
  exit 1
fi

# Check if ogr2ogr is available
if ! command -v ogr2ogr &>/dev/null; then
  echo "Error: ogr2ogr command not found. Please install GDAL/OGR tools."
  exit 1
fi

echo "Starting import of GeoJSON files from '$SOURCE_DIR' into PostgreSQL database '$DB_NAME'..."

# Counters
TOTAL_FILES=0
SUCCESSFUL=0
FAILED=0

# Process each GeoJSON file in the source directory
for GEOJSON_FILE in "$SOURCE_DIR"/WithinTheBills*.geojson; do
  if [ -f "$GEOJSON_FILE" ]; then
    ((TOTAL_FILES++))
    BASE_NAME=$(basename "$GEOJSON_FILE" .geojson)
    TABLE_NAME="bom.parishes_shp" # Convert to lowercase for table name

    echo "Importing: $GEOJSON_FILE → $TABLE_NAME"

    # Import GeoJSON to PostgreSQL
    # -f "PostgreSQL" (output format)
    # PG:"dbname=... user=..." (connection string)
    # -nln (new layer name)
    # -update (update an existing record)
    # -append (append to existing table)
    if ogr2ogr -f "PostgreSQL" PG:"dbname=$DB_NAME user=$DB_USER" "$GEOJSON_FILE" -nln "$TABLE_NAME" -update -append; then
      ((SUCCESSFUL++))
      echo "  Success: Imported $GEOJSON_FILE to $TABLE_NAME"
    else
      ((FAILED++))
      echo "  Error: Failed to import $GEOJSON_FILE"
    fi
  fi
done

# Summary
echo ""
echo "Import Complete"
echo "==============="
echo "Total GeoJSON files found: $TOTAL_FILES"
echo "Successful imports: $SUCCESSFUL"
echo "Failed imports: $FAILED"

exit 0

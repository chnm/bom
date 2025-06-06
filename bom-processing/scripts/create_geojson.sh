#!/bin/bash
# ===========================================================================
# Shapefile to GeoJSON Conversion Script
# ===========================================================================
#
# DESCRIPTION:
#   This script converts shapefiles (.shp) located in subdirectories of the
#   parish-shapefiles directory into GeoJSON files. The resulting GeoJSON
#   files are prepared for upload into a PostGIS database.
#
# USAGE:
#   ./create_geojson.sh [target_directory]
#
# ARGUMENTS:
#   target_directory - Optional. Path to the directory containing shapefile
#                      subdirectories. If not provided, defaults to
#                      '../bom-data/parish-shapefiles'.
#
# DIRECTORY STRUCTURE:
#   Target directory should contain subdirectories
#   Each subdirectory should contain shapefiles (.shp) that will be converted.
#
# REQUIREMENTS:
#   - GDAL/OGR tools (ogr2ogr) must be installed
#   - Proper permissions to read source files and write GeoJSON files
#
# EXAMPLE:
#   ./create_geojson.sh ../path/to/parish-shapefiles
#
# ===========================================================================

# Set default target directory if not provided
TARGET_DIR="${1:-../../bom-data/parish-shapefiles}"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Directory '$TARGET_DIR' does not exist."
  echo "Usage: $0 [target_directory]"
  exit 1
fi

# Check if ogr2ogr is available
if ! command -v ogr2ogr &>/dev/null; then
  echo "Error: ogr2ogr command not found. Please install GDAL/OGR tools."
  exit 1
fi

echo "Starting conversion of shapefiles to GeoJSON in '$TARGET_DIR'..."

# Change to the target directory
cd "$TARGET_DIR" || exit 1

# Counters
TOTAL_DIRS=0
TOTAL_FILES=0
SUCCESSFUL=0
FAILED=0

# Process each subdirectory
for FOLDER in */; do
  # Skip directories named "Archived" or "merged"
  if [[ "$FOLDER" == "Archived/" || "$FOLDER" == "merged/" ]]; then
    echo "Skipping excluded directory: $FOLDER"
    continue
  fi

  if [ -d "$FOLDER" ]; then
    ((TOTAL_DIRS++))
    echo "Processing directory: $FOLDER"

    # Find all shapefiles in the current folder and convert them to GeoJSON
    find "$FOLDER" -name '*.shp' | while read -r SHAPEFILE; do
      ((TOTAL_FILES++))
      BASE_NAME=$(basename "$SHAPEFILE" .shp)
      OUTPUT_FILE="${FOLDER}${BASE_NAME}.geojson"

      echo "  Converting: $SHAPEFILE → $OUTPUT_FILE"

      # Convert shapefile to GeoJSON
      # -f "GeoJSON" (output format)
      # -t_srs "EPSG:4326" (ensure output is in WGS84)
      if ogr2ogr -f "GeoJSON" -t_srs "EPSG:4326" "$OUTPUT_FILE" "$SHAPEFILE"; then
        ((SUCCESSFUL++))
        echo "  Success: Created $OUTPUT_FILE"
      else
        ((FAILED++))
        echo "  Error: Failed to convert $SHAPEFILE"
      fi
    done
  fi
done

# Summary
echo ""
echo "Conversion Complete"
echo "==================="
echo "Directories processed: $TOTAL_DIRS"
echo "Total shapefiles found: $TOTAL_FILES"
echo "Successful conversions: $SUCCESSFUL"
echo "Failed conversions: $FAILED"

# Return to original directory
cd - >/dev/null

exit 0

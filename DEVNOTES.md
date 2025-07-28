# Death by Numbers Development Notes

## Shapefile to PostGIS Workflow

### 1. Converting Shapefiles to GeoJSON

The first step in our workflow is to convert shapefiles to GeoJSON format using the `create_geojson.sh` script located in `bom-processing/scripts/`:

```bash
cd bom-processing/scripts
./create_geojson.sh [target_directory]
```

This script:
- Takes shapefiles from the subdirectories in `bom-data/parish-shapefiles/` (or specified target directory)
- Converts them to GeoJSON format using `ogr2ogr` from GDAL
- Saves the GeoJSON files in the same subdirectories as the source shapefiles
- Skips "Archived" and "merged" directories
- Provides a summary of conversion operations

The script automatically:
- Ensures output is in WGS84 (EPSG:4326) projection
- Processes each subdirectory containing shapefiles
- Creates corresponding GeoJSON files for each shapefile

### 2. Uploading Data to PostGIS Database

To import the generated GeoJSON files into PostgreSQL/PostGIS, use the `insert_geojson.sh` script:

```bash
# Make sure you're in the /scripts folder before you run this!
cd bom-processing/scripts
# You can optionally include arguments, but running this alone will default to the correct directories
./insert_geojson.sh [source_directory] [database_name] [database_user]
```

This script:
- Takes GeoJSON files from `bom-data/geoJSON-files/` (or specified source directory)
- Imports each individual year's GeoJSON file into the PostgreSQL database
- Creates separate tables for each historical period (e.g., WithinTheBills1582, WithinTheBills1603)
- Provides a summary of import operations

## NOTE: Ensure the shapefile database includes an ID to the parish table. 

If the `parishes_shp`` data is ever updated, be sure to run this one-time command to make sure the shapefiles include the unique parish IDs that we use for joining data. 

```sql
UPDATE bom.parishes_shp ps
  SET parish_id = p.id
  FROM bom.parishes p
  WHERE ps.dbn_par = p.canonical_name;

```

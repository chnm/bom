# Death by Numbers: London Bills of Mortality

**[Death by Numbers](https://deathbynumbers.org)** is a digital scholarly research project examining the London Bills of Mortality, historical documents that recorded deaths and births in London from 1636 to 1754. Developed by the Roy Rosenzweig Center for History and New Media (RRCHNM) at George Mason University, this project provides comprehensive data analysis, visualizations, and scholarly research.

## Project Overview

The London Bills of Mortality represent one of the earliest systematic attempts to collect demographic data. These weekly and general bills, published by parish clerks and the Company of Parish Clerks, documented:

- **Deaths by cause** (plague, smallpox, consumption, etc.)
- **Parish-level mortality data** across London's parishes
- **Christening records** (births/baptisms)
- **Seasonal patterns** and mortality crises
- **Food price data** from historical markets

## Repository Structure

### 📊 [bom-data/](./bom-data/)
**Historical datasets and geographic data**
- **CSV datasets** from transcribed Bills of Mortality
- **Death dictionary** with cause-of-death definitions
- **Parish shapefiles** for our historical periods
- **Network data** for plague spread over time

Key datasets:
- Weekly bills with parish-level death counts
- General bills with city-wide statistics
- Christening records by parish and gender
- Food price data from historical markets
- Authority files for canonical parish names

See the repo's own README for details about the data files.

### [bom-processing/](./bom-processing/)
**Data processing pipeline and database tools**

#### Python Pipeline ([bompy/](./bom-processing/scripts/bompy/))
Data processing system that transforms historical CSV files developed in DataScribe into PostgreSQL-ready formats.

```bash
# Quick start
make setup           # Install dependencies
make process-all     # Process all data
make show-stats      # View results
```

#### R Scripts ([bomr/](./bom-processing/scripts/bomr/))
**Legacy R processing pipeline** for data transformation and analysis:
- DataScribe export processing
- Data pivoting and normalization
- Week ID generation and validation
- Local Datasette exploration tools

The R scripts are no longer used or updated.

#### Database Infrastructure ([db/](./bom-processing/db/))
- **PostgreSQL migrations** for schema management
- **Go ETL updater** for efficient data imports
- **PostGIS integration** for spatial data
- **API data serving** infrastructure

### [bom-website/](./bom-website/)
**Hugo-based scholarly website with interactive visualizations**

**Tech Stack:**
- Hugo v0.107.0 (static site generator)
- TailwindCSS v3.2.4 (utility-first CSS)
- Alpine.js v3.14.1 (lightweight JavaScript)
- D3.js v7.9.0 (data visualizations)

The website includes:
- **Research analyses** with interactive data visualizations
- **Historical context** essays and interpretations
- **Technical methodologies** and documentation
- **Educational resources** and teaching materials
- **Project blog** with updates and announcements

```bash
# Development commands
make preview      # Start local server
make build        # Build for development
make build-prod   # Build for production
make tailwind     # Compile TailwindCSS
```

## Data Architecture

### Historical Sources
- **Laxton Collection**
- **British Library**
- **Bodleian Library**
- **Wellcome Collection**
- **Huntington Library**

### Database Schema
PostgreSQL database with spatial extensions:
- **bom.bill_of_mortality**: Individual bill records (1M+ rows)
- **bom.parishes**: Parish lookup with canonical names (156 parishes)
- **bom.weeks**: Unique week records with historical dating (5,393 weeks)
- **bom.causes_of_death**: Death cause definitions and records
- **bom.christenings**: Birth/baptism records with gender data
- **bom.parishes_shp**: Spatial parish boundaries for 8+ time periods

### API Access
RESTful API serving processed data:
- **Base URL**: `https://data.chnm.org/bom/`
- **Endpoints**: `/bills`, `/parishes`, `/weeks`, `/causes`, `/christenings`
- **Formats**: JSON, CSV export capabilities
- **Filtering**: By year, parish, cause of death, bill type

## Quick Start Guides

### For Researchers
1. **Explore the data**: Visit [deathbynumbers.org/database](https://deathbynumbers.org/database)
2. **Download datasets**: Use the [downloads page](https://deathbynumbers.org/downloads)
3. **Access the API**: See [API documentation](https://deathbynumbers.org/api-docs)

### For Website Contributors
```bash
# Sparse checkout for website-only development
git clone --depth 1 --filter=blob:none --sparse https://github.com/chnm/bom
cd bom
git sparse-checkout set bom-website
cd bom-website
make preview
```

### For Developers
```bash
# Complete setup for all components
git clone https://github.com/chnm/bom.git
cd bom

# Process data
cd bom-processing/scripts/bompy && make setup && make process-all

# Run website locally
cd ../../bom-website && make preview

# Set up database (requires PostgreSQL)
cd ../bom-processing/db && make db-up
```

## Development Workflows

### Data Processing Pipeline
1. **Raw data** (CSV files from DataScribe transcriptions)
2. **Python processing** (`bompy` package) → PostgreSQL-ready CSVs
3. **Go updater** → Database import with validation
4. **API serving** → JSON endpoints for website and researchers

### Website Development
1. **Content creation** in Markdown with YAML frontmatter
2. **Hugo processing** → Static HTML with interactive components
3. **TailwindCSS compilation** → Optimized stylesheets
4. **JavaScript bundling** → D3.js visualizations and Alpine.js interactivity

### Geographic Data Workflow
1. **Shapefiles** → GeoJSON conversion (`create_geojson.sh`)
2. **PostGIS import** → Spatial database tables (`insert_geojson.sh`)
3. **API integration** → Geographic data serving
4. **Visualization** → Interactive maps and parish boundaries

## Technical Infrastructure
- **Modern web stack**: Hugo, TailwindCSS, Alpine.js, D3.js
- **Robust database**: PostgreSQL with PostGIS spatial extensions
- **RESTful API**: JSON endpoints with filtering and pagination
- **Automated deployment**: Docker containerization, Ansible orchestration

## Project Team

**Principal Investigator**: Jessica Otis (George Mason University)  
**Technical Lead**: Jason Heppler (Roy Rosenzweig Center for History and New Media)

See our [Team page](https://deathbynumbers.org/team/) for the full list of contributors.

## License

This project is open source and available under the [MIT License](LICENSE). Historical data is provided for educational and research purposes.

## Contact

- **General inquiries**: [Jessica Otis](mailto:jotis2@gmu.edu)
- **Technical questions**: [Jason Heppler](mailto:jheppler@gmu.edu)  
- **Website**: [deathbynumbers.org](https://deathbynumbers.org/)
- **Institution**: [Roy Rosenzweig Center for History and New Media](https://rrchnm.org/)

---

*For detailed technical documentation, please consult the individual README files in each directory.*

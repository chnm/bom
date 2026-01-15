# AGENTS.md

Guide for AI agents working in the Death by Numbers codebase.

## Project Overview

**Death by Numbers** is a digital scholarly research project examining the London Bills of Mortality (1636-1754). The repository contains three main components:

1. **bom-data/**: Historical datasets, shapefiles, and GeoJSON files
2. **bom-processing/**: Data processing pipeline (Python) and database tools (Go)
3. **bom-website/**: Hugo-based static site with D3.js visualizations

The project transforms historical CSV data into a PostgreSQL database and serves it via a REST API to power interactive visualizations on the public website.

---

## Repository Structure

```
bom/
├── bom-data/              # Historical datasets and geographic data
│   ├── data-csvs/         # Raw CSV exports from DataScribe
│   ├── geoJSON-files/     # Parish boundaries by time period
│   ├── parish-shapefiles/ # Source shapefiles for GIS data
│   ├── parish-networks/   # Network data for plague spread
│   └── deathdictionary.csv
├── bom-processing/        # Data processing pipeline
│   ├── db/                # PostgreSQL migrations and Go ETL updater
│   │   ├── migrations/    # golang-migrate SQL files
│   │   └── updater/       # Go program for database imports
│   ├── scripts/
│   │   ├── bompy/         # Python data processing package
│   │   └── bomr/          # Legacy R scripts (no longer used)
│   └── api-docs/          # API documentation
└── bom-website/           # Hugo static site
    ├── content/           # Markdown content (blog, analysis, context)
    ├── themes/dbn/        # Custom TailwindCSS theme
    ├── assets/            # JavaScript and visualizations
    │   ├── js/            # Services and Alpine.js components
    │   └── visualizations/ # D3.js/Observable Plot charts
    └── static/            # Static assets (images)
```

---

## Essential Commands

### Website Development (bom-website/)

```bash
# Preview site locally with drafts and live reload
make preview

# Build for development (dev.deathbynumbers.org)
make build

# Build for production with minification
make build-prod

# Compile TailwindCSS after layout changes
make tailwind
# OR from themes/dbn/:
npm run build-tw
```

**Theme Development:**
```bash
cd themes/dbn
npm install -y          # Install TailwindCSS dependencies
npm run build-tw        # Build TailwindCSS
```

### Data Processing (bom-processing/scripts/bompy/)

```bash
# Setup and install dependencies (uses uv/Poetry)
make setup              # or: make install

# Process all CSV data files
make process-all        # Runs Python pipeline

# View processing results
make show-stats         # Show record counts and file sizes
make show-logs          # List recent log files
make tail-logs          # Follow latest log file

# Data management
make clean-data         # Remove output CSVs
make clean-logs         # Remove log files
make copy-data          # Copy raw data from bom-data/ to bompy/data-raw/

# Code quality
make format             # Format with black and isort
make lint               # Check formatting
make typecheck          # Run mypy type checking
make test               # Run pytest tests
```

**Manual processing commands:**
```bash
uv run process_all_data.py              # Main processing script
uv run tests/test_bills_processor.py    # Test bills processor
uv run tests/test_schema_alignment.py   # Test schema alignment
```

### Database Operations (bom-processing/db/)

**Prerequisites:**
- golang-migrate: `brew install golang-migrate` (macOS)
- PostgreSQL client tools
- Go 1.20+
- Create `.env` file with `DB_CONN_STR` and `DATA_DIR`

```bash
# Run database migrations
make db-up              # Apply all migrations
make db-down            # Revert migrations
make db-version         # Show current migration version

# Import data
make db-update          # Run Go importer (imports processed CSVs)
make dry-run            # Preview import without changes

# Build Go importer
make build              # Compiles to updater/bin/bom-importer

# Code quality
make fmt                # Format Go code
make vet                # Run go vet
```

### Geographic Data Processing (bom-processing/scripts/)

```bash
# Convert shapefiles to GeoJSON
./create_geojson.sh [target_directory]
# Default: ../../bom-data/parish-shapefiles

# Import GeoJSON to PostGIS database
./insert_geojson.sh [source_directory] [database_name] [database_user]
# Default source: ../../bom-data/geoJSON-files
```

**Important:** After updating `parishes_shp` data, run this one-time SQL:
```sql
UPDATE bom.parishes_shp ps
  SET parish_id = p.id
  FROM bom.parishes p
  WHERE ps.dbn_par = p.canonical_name;
```

---

## Tech Stack

### Website (bom-website/)
- **Hugo**: v0.107.0 (static site generator)
- **TailwindCSS**: v3.2.4 (utility-first CSS)
- **Alpine.js**: v3.14.1 (reactive JavaScript framework)
- **D3.js**: v7.9.0 (data visualizations)
- **Observable Plot**: v0.6.16 (declarative charting)
- **Leaflet**: v1.9.4 (mapping)
- **Pagefind**: Search indexing (run via npx)

### Data Processing (bom-processing/)
- **Python**: 3.10+ with uv/Poetry
  - pandas 2.0
  - pydantic 2.0
  - loguru 0.7
  - typer, rich (CLI tools)
- **Go**: 1.20+
  - pgx/v4 (PostgreSQL driver)

### Database
- **PostgreSQL** with **PostGIS** extension
- **golang-migrate** for schema management
- Schema: `bom` with tables for bills, parishes, weeks, causes, christenings, parishes_shp

---

## Code Patterns and Conventions

### Python (bompy/)

**Organization:**
- Package structure: `src/bom/` with submodules (`models`, `loaders`, `processors`, `extractors`, `utils`)
- Dataclass-based models with type hints
- Configuration-driven: `config.py` for constants and patterns

**Conventions:**
- **Naming**: `snake_case` for variables, functions, files
- **Type hints**: All function signatures (`Optional[int]`, `List[str]`, `Dict[str, Any]`)
- **Logging**: loguru for structured logging (`logger.info()`, `logger.warning()`, `logger.error()`)
- **Documentation**: Google/NumPy style docstrings

**Common patterns:**
```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from loguru import logger

@dataclass
class BillRecord:
    parish_id: int
    count: Optional[int]
    year: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for pandas DataFrame."""
        return {
            'parish_id': self.parish_id,
            'count': self.count,
            'year': self.year
        }

# Pandas DataFrame processing
df = pd.DataFrame([record.to_dict() for record in records])
df = df.dropna(subset=['required_column'])
```

**Key classes:**
- `CSVLoader`: Load and validate CSV files
- `SchemaValidator`: Validate against database schema
- `BillsProcessor`, `ChristeningsProcessor`: Transform data
- `ParishExtractor`: Extract parish mappings

**Code quality:**
- Format: `black` (88 char line length)
- Imports: `isort` (black profile)
- Type checking: `mypy` (strict mode)
- Testing: `pytest`

### JavaScript (bom-website/assets/)

**Organization:**
- **ES6 modules** with imports/exports
- **Service layer**: `DataService`, `URLService`, `ChartService`, `CacheService`
- **Visualization base class**: `Visualization` (extended by specific charts)
- **Alpine.js components**: Reactive state management

**Conventions:**
- **Naming**: `camelCase` for variables/functions, `PascalCase` for classes
- **Async/await**: For all data fetching
- **Namespacing**: Services on `window` object (e.g., `window.dataService`)
- **Caching**: Multi-level (browser cache, service cache, request deduplication)

**Common patterns:**
```javascript
// Visualization class
import * as d3 from 'd3';

export default class DeathsChart extends Visualization {
  constructor(id, data, dimensions) {
    super(id, data, dimensions, {top: 20, right: 30, bottom: 40, left: 50});
  }
  
  render() {
    const svg = d3.select(`#${this.id}`)
      .append('svg')
      .attr('width', this.width)
      .attr('height', this.height);
    // D3.js rendering code
  }
}

// Alpine.js component
Alpine.data('databaseExplorer', () => ({
  selectedParishes: [],
  loading: false,
  
  init() {
    this.fetchData();
  },
  
  async fetchData() {
    this.loading = true;
    try {
      const data = await window.dataService.getBills({
        parishes: this.selectedParishes
      });
      this.updateChart(data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      this.loading = false;
    }
  }
}));
```

**Data fetching patterns:**
- Promise.all for parallel requests
- AbortController for cancellation
- Caching to prevent duplicate API calls
- Service layer abstracts API communication

**Observable Plot usage:**
```javascript
import * as Plot from '@observablehq/plot';

const chart = Plot.plot({
  marks: [
    Plot.line(data, {x: 'date', y: 'deaths', stroke: 'cause'}),
    Plot.ruleY([0])
  ],
  width: dimensions.width,
  height: dimensions.height
});
```

### Go (updater/)

**Organization:**
- Single `main.go` file for ETL program
- Flag-based CLI configuration
- Context-driven operations
- Transaction-based imports with temporary tables

**Conventions:**
- **Naming**: `PascalCase` for exported, `camelCase` for unexported
- **Error handling**: Explicit returns with wrapping (`fmt.Errorf("operation: %w", err)`)
- **Cleanup**: `defer` for resource cleanup
- **Database**: pgx/v4 for PostgreSQL

**Common patterns:**
```go
import (
    "context"
    "flag"
    "fmt"
    "github.com/jackc/pgx/v4"
)

func main() {
    dbConn := flag.String("db", "", "Database connection string")
    dataDir := flag.String("data", "", "Data directory")
    dryRun := flag.Bool("dry-run", false, "Preview without changes")
    flag.Parse()
    
    ctx := context.Background()
    conn, err := pgx.Connect(ctx, *dbConn)
    if err != nil {
        return fmt.Errorf("failed to connect: %w", err)
    }
    defer conn.Close(ctx)
    
    if err := importData(ctx, conn, *dataDir, *dryRun); err != nil {
        return fmt.Errorf("import failed: %w", err)
    }
}

func importData(ctx context.Context, conn *pgx.Conn, dataDir string, dryRun bool) error {
    tx, err := conn.Begin(ctx)
    if err != nil {
        return fmt.Errorf("begin transaction: %w", err)
    }
    defer tx.Rollback(ctx) // Safe to call even after commit
    
    // Create temp tables, import, validate
    
    if !dryRun {
        if err := tx.Commit(ctx); err != nil {
            return fmt.Errorf("commit: %w", err)
        }
    }
    return nil
}
```

### Hugo Templates (bom-website/themes/dbn/)

**Organization:**
- `layouts/_default/baseof.html`: Base template with blocks
- `layouts/partials/`: Reusable components (header, footer, nav)
- `layouts/shortcodes/`: Content shortcodes (figures, citations, alerts)
- `layouts/section/`: Section-specific templates

**Conventions:**
- **Go template syntax**: `{{ .Title }}`, `{{ range }}`, `{{ with }}`
- **TailwindCSS**: Inline utility classes
- **Alpine.js**: For interactivity (`x-data`, `x-show`, `@click`)
- **Hugo pipes**: Asset processing with fingerprinting

**Common patterns:**
```html
<!-- Template definition -->
{{ define "main" }}
<div class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-dbn-green">{{ .Title }}</h1>
  <div class="prose prose-lg max-w-none">
    {{ .Content }}
  </div>
</div>
{{ end }}

<!-- Asset pipeline -->
{{ $js := resources.Get .Params.script | js.Build | resources.Fingerprint }}
<script src="{{ $js.Permalink }}" defer></script>

<!-- Alpine.js interactivity -->
<div x-data="{ open: false }" class="relative">
  <button @click="open = !open" class="btn-primary">
    Toggle Menu
  </button>
  <div x-show="open" class="absolute z-10 mt-2">
    <!-- Menu content -->
  </div>
</div>

<!-- Shortcode usage in content -->
{{< figure src="/images/plague-chart.png" 
    caption="Weekly plague deaths, 1665" 
    alt="Line chart showing spike in deaths during Great Plague" >}}
```

---

## Database Schema

**Namespace:** `bom`

**Core Tables:**
- `bill_of_mortality`: Individual bill records (1M+ rows)
  - Unique constraint: `(parish_id, count_type, year, week_id, bill_type)`
- `parishes`: Parish lookup with canonical names (156 parishes)
- `weeks`: Unique week records with historical dating (5,393 weeks)
- `causes_of_death`: Death cause definitions and records
- `christenings`: Birth/baptism records with gender data
- `parishes_shp`: PostGIS spatial data for 8+ time periods with `parish_id` foreign key

**Import order (respects foreign keys):**
1. `years`
2. `parishes`
3. `weeks`
4. `all_bills` (becomes `bill_of_mortality`)

**Migration files:**
- Located in `bom-processing/db/migrations/`
- Format: `NNNNNN_description.up.sql` / `NNNNNN_description.down.sql`
- Use golang-migrate for management

---

## Data Flow

1. **Historical transcription** → CSV files in `bom-data/data-csvs/`
2. **Python processing** (`bompy`) → Normalized CSVs in `bompy/data/`
3. **Go ETL updater** → PostgreSQL import with validation
4. **REST API** → JSON endpoints at `https://data.chnm.org/bom/`
5. **Website visualizations** → D3.js charts fetch and render data

---

## API Information

**Base URL:** `https://data.chnm.org/bom/`

**Endpoints:**
- `/bills` - Bill of mortality records
- `/parishes` - Parish lookup
- `/weeks` - Week records
- `/causes` - Cause of death data
- `/christenings` - Birth/baptism records

**Query parameters:**
- `year`, `parish`, `cause`, `bill_type` - Filtering
- `limit`, `offset` - Pagination
- Response format: JSON

---

## Content Management

### Creating Blog Posts

**File naming:** `YYYY-MM-DD-short-title.md` in `bom-website/content/blog/`

**Required YAML frontmatter:**
```yaml
---
title: "Post Title"
date: "2025-01-15"
author:
  - fname lname
tags:
  - tag1
  - tag2
categories:
  - category
---
```

**Including images:**
1. Upload to `bom-website/static/images/`
2. Use Hugo shortcode:
```html
{{< figure src="/images/filename.jpg" 
    caption="Image caption" 
    alt="Descriptive alt text for accessibility" >}}
```

**Content sections:**
- `/content/blog/` - Blog posts and announcements
- `/content/analysis/` - Research analysis articles
- `/content/context/` - Historical context essays
- `/content/methodologies/` - Technical documentation

### Branch-based Workflow

1. Create feature branch from `main`
2. Add/edit content or code
3. Commit with descriptive messages
4. Tag @hepplerj on Slack for preview on dev site
5. Senior developer or sysadmin deploys to production

---

## Important Gotchas

### Data Processing

1. **Import order matters**: Years → Parishes → Weeks → Bills (foreign key dependencies)
2. **Parish ID synchronization**: After updating `parishes_shp`, run the UPDATE query to link `parish_id`
3. **Dummy data cleanup**: Use `DELETE FROM bom.bill_of_mortality WHERE count_type LIKE '%_DUMMY'` to remove test data
4. **Copy data before processing**: Run `make copy-data` from bompy/ to pull latest CSVs from bom-data/
5. **Schema validation**: Python processors validate against expected PostgreSQL schema

### Website Development

1. **Hugo version**: Project requires Hugo v0.107.0 - newer versions may have breaking changes
2. **TailwindCSS compilation**: Must run `make tailwind` after adding/modifying Tailwind classes in templates
3. **Asset fingerprinting**: Production builds use Hugo's asset pipeline with fingerprinting for cache busting
4. **Draft posts**: Use `make preview` to see drafts locally; `make build-prod` excludes drafts
5. **Unsafe HTML**: Markdown renderer has `unsafe: true` to allow embedded visualizations
6. **Search index**: Pagefind builds search index after Hugo build completes
7. **Environment-specific builds**: 
   - Dev: `--buildDrafts --buildFuture --baseURL http://dev.deathbynumbers.org/`
   - Prod: `--minify --baseURL https://deathbynumbers.org/`

### Geographic Data

1. **Shapefile directory exclusions**: Processing scripts skip "Archived" and "merged" directories
2. **GeoJSON projection**: Output is always WGS84 (EPSG:4326)
3. **GDAL requirement**: Must have `ogr2ogr` installed for shapefile conversion

### Code Quality

1. **Pre-commit hooks**: Website has pre-commit config for JSON, YAML, trailing whitespace
2. **Python formatting**: Black (88 char), isort (black profile), mypy (strict)
3. **Go formatting**: Use `go fmt`, `go vet` before committing
4. **No deployment from local**: Production deployment only by senior developer/sysadmin via Ansible

---

## Testing

### Python
```bash
cd bom-processing/scripts/bompy
make test               # Run pytest
make test-bills         # Test bills processor
make test-schema        # Test schema alignment
```

### Go
```bash
cd bom-processing/db
make dry-run            # Preview database import without changes
```

### Website
```bash
cd bom-website
make preview            # Manual testing with live server
# Check visualizations, responsive design, content rendering
```

**No automated test suite for website** - relies on manual QA and production-like previews.

---

## Deployment

**Production deployment:**
- Handled by Ansible playbooks
- Only accessible to senior developer or systems administrator
- Docker containerization with nginx
- Builds to `/public/` directory

**Do NOT:**
- Push directly to production
- Deploy from local machine
- Modify deployment configs without approval

**Process:**
1. Complete work on feature branch
2. Test locally with `make preview`
3. Tag @hepplerj on Slack for dev deployment
4. After approval, senior dev deploys to production

---

## Useful Resources

**Documentation:**
- Main README: `/README.md`
- Processing README: `/bom-processing/README.md`
- Website README: `/bom-website/README.md`
- Data README: `/bom-data/README.md`
- Dev notes: `/DEVNOTES.md`
- Contributing guide: `/bom-website/CONTRIBUTING.md`

**External Links:**
- Website: https://deathbynumbers.org
- API base: https://data.chnm.org/bom/
- GitHub: https://github.com/chnm/bom
- Hugo docs: https://gohugo.io/documentation/
- TailwindCSS: https://tailwindcss.com/docs
- D3.js: https://d3js.org/
- Alpine.js: https://alpinejs.dev/

**Tools:**
- Markdown guide: https://markdownguide.org
- golang-migrate: https://github.com/golang-migrate/migrate
- GDAL/OGR: https://gdal.org/

---

## Contact

- **Principal Investigator**: Jessica Otis (jotis2@gmu.edu)
- **Technical Lead**: Jason Heppler (@hepplerj on Slack, jheppler@gmu.edu)
- **Institution**: Roy Rosenzweig Center for History and New Media (RRCHNM)

---

## Quick Reference

**Most common workflows:**

```bash
# Start website locally
cd bom-website && make preview

# Process new data
cd bom-processing/scripts/bompy
make copy-data && make process-all && make show-stats

# Import to database
cd bom-processing/db
make db-update

# Update TailwindCSS
cd bom-website && make tailwind

# Create blog post
# 1. Create branch in GitHub UI
# 2. Add file: content/blog/YYYY-MM-DD-title.md
# 3. Add YAML frontmatter and content
# 4. Upload images to static/images/
# 5. Commit and tag @hepplerj for preview
```

**Emergency commands:**

```bash
# Remove all dummy test data
psql $DB_CONN_STR -c "DELETE FROM bom.bill_of_mortality WHERE count_type LIKE '%_DUMMY';"

# Rebuild everything
cd bom-processing/scripts/bompy && make clean && make process-all
cd ../../../bom-website && make build-prod

# Reset Python environment
cd bom-processing/scripts/bompy && make reset && make setup
```

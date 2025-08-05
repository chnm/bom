# Bills of Mortality - Analysis Notebooks

This directory contains Jupyter notebooks for exploring and analyzing the processed Bills of Mortality data. Each notebook focuses on different aspects of the historical mortality data.

## Available Notebooks

### 1. Data Exploration (`01_data_exploration.ipynb`)
**Purpose**: Comprehensive overview of the dataset structure and basic statistics

**Key Features**:
- Dataset summary and structure analysis
- Basic mortality statistics and distributions  
- Parish overview and sample data exploration
- Temporal coverage assessment
- Initial data quality checks

**Best for**: Getting familiar with the dataset, understanding data structure, initial exploration

---

### 2. Temporal Analysis (`02_temporal_analysis.ipynb`)
**Purpose**: Analysis of mortality patterns over time

**Key Features**:
- Long-term mortality trends and crisis detection
- Seasonal mortality patterns (winter vs summer)
- Year-over-year mortality changes
- Statistical crisis identification (using z-scores)
- Interactive time series visualizations (Plotly)
- Historical context validation (plague years, etc.)

**Best for**: Understanding temporal patterns, identifying crisis periods, seasonal analysis

---

### 3. Parish Analysis (`03_parish_analysis.ipynb`)
**Purpose**: Geographic and parish-level mortality patterns

**Key Features**:
- Parish mortality rankings and comparisons
- Parish clustering analysis (k-means)
- Vulnerability assessment (crisis vs normal mortality)
- Parish name analysis and geographic patterns
- Correlation analysis between parishes
- Comparative mortality profiles

**Best for**: Understanding spatial patterns, identifying vulnerable areas, comparative analysis

---

### 4. Data Quality Assessment (`04_data_quality.ipynb`)
**Purpose**: Comprehensive data quality evaluation and cleaning recommendations

**Key Features**:
- Missing data pattern analysis
- Data consistency checks and validation
- Statistical outlier detection (IQR, z-score methods)
- Historical plausibility assessment
- Data completeness analysis by time/parish
- Quality scoring and cleaning recommendations

**Best for**: Assessing data reliability, identifying quality issues, planning data cleaning

---

## Getting Started

### Prerequisites
```bash
# Install dependencies (if not already done)
make setup

# Ensure data has been processed
make process-all
```

### Running Notebooks

#### Launch Jupyter Lab
```bash
make notebooks
```
This will open Jupyter Lab in your browser with the notebooks directory.

#### Execute All Notebooks
```bash
make notebook-run-all
```
Runs all notebooks programmatically (useful for batch processing).

#### Generate HTML Reports
```bash
make notebook-convert
```
Creates HTML versions of all notebooks in `notebooks/reports/`.

#### Clean Notebook Outputs
```bash
make notebook-clean
```
Clears all cell outputs and checkpoints (useful before committing to git).

### Notebook Information
```bash
make notebook-info
```
Shows details about available notebooks.

---

## Analysis Workflow

### Recommended Order:
1. **Data Exploration** - Start here to understand the dataset
2. **Data Quality** - Assess data reliability and identify issues  
3. **Temporal Analysis** - Examine patterns over time
4. **Parish Analysis** - Explore geographic/spatial patterns

### Custom Analysis:
- Each notebook is self-contained and can be run independently
- Modify notebooks for specific research questions
- Create new notebooks following the naming convention: `05_custom_analysis.ipynb`

---

## Dependencies

The notebooks use these key libraries:
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **matplotlib** - Basic plotting
- **seaborn** - Statistical visualizations
- **plotly** - Interactive visualizations (optional)
- **scipy** - Statistical functions
- **scikit-learn** - Machine learning (clustering, etc.)

### Optional Libraries:
- **wordcloud** - Parish name word clouds
- **networkx** - Network analysis (future use)

Install optional libraries:
```bash
poetry add plotly wordcloud networkx
```

---

## Data Sources

The notebooks analyze processed data from:
- `data/all_bills.csv` - Main mortality records
- `data/parishes.csv` - Parish lookup table
- `data/years.csv` - Year definitions
- `data/weeks.csv` - Week definitions

Ensure data has been processed by running `make process-all` before using notebooks.

---

## Output and Results

### Generated Files:
- **HTML Reports**: `notebooks/reports/*.html` (via `make notebook-convert`)
- **Figures**: Saved to notebook outputs (can be extracted)
- **Analysis Results**: Displayed in notebook cells

### Key Insights to Look For:
- **Crisis Years**: Periods of unusually high mortality
- **Seasonal Patterns**: Winter vs summer mortality differences  
- **Parish Vulnerability**: Which areas were most affected by crises
- **Data Quality Issues**: Problems that might affect analysis
- **Long-term Trends**: Demographic changes over time

---

## Research Applications

These notebooks support various research questions:

### Historical Demography:
- Population dynamics and mortality crises
- Seasonal disease patterns
- Urban vs suburban mortality differences

### Epidemiological History:
- Plague outbreak analysis
- Disease transmission patterns  
- Public health interventions

### Social History:
- Parish-level social conditions
- Geographic inequality in mortality
- Community resilience and vulnerability

### Digital Humanities:
- Large-scale quantitative analysis of historical records
- Data quality assessment for historical datasets
- Reproducible research workflows

---

## Contributing

### Adding New Notebooks:
1. Follow naming convention: `##_descriptive_name.ipynb`
2. Include comprehensive documentation and comments
3. Add summary to this README
4. Test with `make notebook-run-all`

### Best Practices:
- Clear markdown documentation for each section
- Informative plot titles and labels
- Error handling for missing data
- Save important figures and results
- Include historical context and interpretation

---

## Support and Documentation

- **Main Project Documentation**: See main README.md
- **Data Processing**: See `src/bom/` for processing pipeline
- **Issues**: Report problems via project issue tracker
- **Questions**: Contact project maintainers

For technical issues with notebooks, check:
1. Data has been processed (`make process-all`)
2. All dependencies installed (`make setup`)
3. Jupyter Lab can access data files
4. Python path includes src directory
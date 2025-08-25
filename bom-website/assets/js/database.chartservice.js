/**
 * database.chartservice.js
 * Handles chart rendering and visualization functionality
 */

const ChartService = {
  /**
   * Loads the Plot library if not already loaded
   * @returns {Promise} - Resolves with the Plot library
   */
  loadPlotLibrary() {
    if (window.Plot) {
      console.log("Plot library already loaded");
      return Promise.resolve(window.Plot);
    }

    console.log("Loading Plot library");
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.type = "module";
      script.textContent =
        'import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm"; window.Plot = Plot; document.dispatchEvent(new Event("plot-loaded"));';
      document.head.appendChild(script);

      document.addEventListener(
        "plot-loaded",
        () => {
          console.log("Plot library loaded successfully");
          resolve(window.Plot);
        },
        { once: true },
      );

      setTimeout(() => {
        if (!window.Plot) {
          console.error("Timeout loading Plot library");
          reject(new Error("Failed to load Plot library"));
        }
      }, 5000);
    });
  },

  /**
   * Creates a bar chart for parish yearly data
   * @param {HTMLElement} container - Container element for the chart
   * @param {Array} data - Yearly data for the parish
   * @param {Object} options - Chart options
   */
  createParishYearlyBarChart(container, data, options = {}) {
    if (!container || !data || !window.Plot) {
      console.error("Missing requirements for chart rendering");
      return;
    }

    try {
      // Clear previous content
      container.innerHTML = "";

      // Filter out any data points with no burials
      const validData = data.filter((d) => d.total_buried > 0);

      // Sort data by year to ensure proper display
      validData.sort((a, b) => a.year - b.year);

      // Get all years from the data
      const years = validData.map((d) => d.year);

      // Set default options
      const defaultOptions = {
        width: container.clientWidth || 400,
        height: 60,
        marginTop: 0,
        marginRight: 0,
        marginBottom: 0,
        marginLeft: 0,
        color: "#6b7280",
      };

      // Merge with provided options
      const chartOptions = { ...defaultOptions, ...options };

      // Create histogram
      const chart = window.Plot.plot({
        width: chartOptions.width,
        height: chartOptions.height,
        marginTop: chartOptions.marginTop,
        marginRight: chartOptions.marginRight,
        marginBottom: chartOptions.marginBottom,
        marginLeft: chartOptions.marginLeft,
        x: {
          type: "band",
          domain: years,
          padding: 0.05, // minimal padding to maximize bar width
          axis: null,
        },
        y: {
          domain: [0, Math.max(...validData.map((d) => d.total_buried))],
          axis: null,
          grid: false,
        },
        marks: [
          window.Plot.barY(validData, {
            x: "year",
            y: "total_buried",
            fill: chartOptions.color,
          }),
        ],
      });

      // Add to DOM
      container.appendChild(chart);

      return chart;
    } catch (error) {
      console.error("Error creating chart:", error);
      container.innerHTML = `<div class="text-red-500">Error creating chart: ${error.message}</div>`;
    }
  },

  /**
   * Creates an interactive detailed chart for the modal view with faceted weekly/general views
   * @param {HTMLElement} container - Container element for the chart
   * @param {Array} data - Yearly data for the parish, death, or christening
   * @param {string} dataType - Type of data: 'parish', 'death', or 'christening'
   * @param {Object} options - Chart options
   */
  createModalDetailChart(container, data, dataType = 'parish', options = {}) {
    if (!container || !data || !window.Plot) {
      console.error("Missing requirements for modal chart rendering");
      return;
    }

    try {
      // Clear the chart container
      container.innerHTML = "";

      // For parish data, we'll show side-by-side comparison of weekly vs general bills
      if (dataType === 'parish') {
        return this.createFacetedParishChart(container, data, options);
      } else {
        // For non-parish data (deaths, christenings), use single chart approach
        return this.createSingleModalChart(container, data, dataType, options);
      }
    } catch (error) {
      console.error("Error creating modal chart:", error);
      container.innerHTML = `<div class="text-center text-red-500 py-4">Error drawing chart: ${error.message}</div>`;
    }
  },

  /**
   * Creates a faceted chart showing buried vs plague deaths as separate charts
   * @param {HTMLElement} container - Container element for the chart
   * @param {Array} data - Parish yearly data
   * @param {Object} options - Chart options
   */
  createFacetedParishChart(container, data, options = {}) {
    // Filter data to only include records with burial data
    const validData = data.filter(d => d.total_buried > 0).sort((a, b) => a.year - b.year);
    
    if (validData.length === 0) {
      container.innerHTML = '<div class="text-center py-8 text-gray-500">No burial data available for this parish</div>';
      return;
    }

    // Create main container with flexbox layout
    const mainContainer = document.createElement("div");
    mainContainer.className = "flex flex-col gap-4";

    // Create faceted chart layout
    const chartsContainer = document.createElement("div");
    chartsContainer.className = "grid grid-cols-1 lg:grid-cols-2 gap-6";

    // Create individual chart containers
    const buriedContainer = document.createElement("div");
    buriedContainer.className = "facet-chart";
    const buriedTitle = document.createElement("h4");
    buriedTitle.className = "text-sm font-semibold text-gray-700 mb-2 text-center";
    buriedTitle.textContent = "Total Buried";
    buriedContainer.appendChild(buriedTitle);

    const plagueContainer = document.createElement("div");
    plagueContainer.className = "facet-chart";
    const plagueTitle = document.createElement("h4");
    plagueTitle.className = "text-sm font-semibold text-gray-700 mb-2 text-center";
    plagueTitle.textContent = "Plague Deaths";
    plagueContainer.appendChild(plagueTitle);

    // Add containers to layout
    chartsContainer.appendChild(buriedContainer);
    chartsContainer.appendChild(plagueContainer);
    mainContainer.appendChild(chartsContainer);
    container.appendChild(mainContainer);

    // Calculate shared Y-axis domain for comparison
    const buriedValues = validData.map(d => d.total_buried || 0);
    const plagueValues = validData.map(d => d.total_plague || 0);
    const maxValue = Math.max(...buriedValues, ...plagueValues) * 1.1;

    // Get the full year range for consistent X-axis domains
    const allYears = validData.map(d => d.year).sort((a, b) => a - b);
    const yearRange = { min: allYears[0], max: allYears[allYears.length - 1] };

    // Create charts for each facet
    const charts = [];

    // Buried chart
    charts.push(this.createSingleDataFacetChart(buriedContainer, validData, 'buried', maxValue, yearRange));

    // Plague chart  
    charts.push(this.createSingleDataFacetChart(plagueContainer, validData, 'plague', maxValue, yearRange));

    return {
      charts: charts,
      redraw: () => charts.forEach(chart => chart && chart.redraw && chart.redraw())
    };
  },

  /**
   * Creates a single facet chart for buried or plague data
   * @param {HTMLElement} container - Container for the chart
   * @param {Array} data - Data for this facet
   * @param {string} dataType - 'buried' or 'plague'
   * @param {number} maxValue - Maximum value for Y-axis
   * @param {Object} yearRange - Object with min and max years for consistent X-axis
   */
  createSingleDataFacetChart(container, data, dataType, maxValue, yearRange) {
    const sortedData = data.sort((a, b) => a.year - b.year);
    
    // Create chart container
    const chartContainer = document.createElement("div");
    chartContainer.className = "chart-content";
    container.appendChild(chartContainer);

    // Prepare data based on facet type - include ALL years in range, even with zero values
    let chartData, color, yField, label;
    
    // Create full year range array
    const fullYearRange = [];
    for (let year = yearRange.min; year <= yearRange.max; year++) {
      fullYearRange.push(year);
    }
    
    if (dataType === 'buried') {
      chartData = fullYearRange.map(year => {
        const dataPoint = sortedData.find(d => d.year === year);
        return {
          year: year,
          value: dataPoint ? Math.max(0, dataPoint.total_buried || 0) : 0
        };
      });
      color = "#96ADC8";
      yField = "value";
      label = "Total Buried";
    } else if (dataType === 'plague') {
      chartData = fullYearRange.map(year => {
        const dataPoint = sortedData.find(d => d.year === year);
        return {
          year: year,
          value: dataPoint ? Math.max(0, dataPoint.total_plague || 0) : 0
        };
      });
      color = "#EF3054";
      yField = "value";
      label = "Plague Deaths";
    }

    // Create the chart - make it wider for modal
    const chart = window.Plot.plot({
      width: 450, // Increased from 300
      height: 220, // Slightly taller
      marginTop: 20,
      marginRight: 40,
      marginBottom: 50,
      marginLeft: 60,
      x: {
        type: "band",
        domain: fullYearRange, // Use full year range for consistent alignment
        padding: 0.1,
        label: "Year",
        tickRotate: -45,
        tickFormat: (d, i) => i % 5 === 0 ? d.toString() : "",
      },
      y: {
        grid: true,
        label: "Count",
        domain: [0, maxValue],
        tickFormat: d => d.toLocaleString()
      },
      marks: [
        window.Plot.barY(chartData.filter(d => d.value > 0), { // Only show bars for non-zero values
          x: "year",
          y: yField,
          fill: color,
          title: (d) => `${d.year}: ${d.value.toLocaleString()} ${label.toLowerCase()}`
        }),
        window.Plot.ruleY([0]),
        window.Plot.tip(
          chartData.filter(d => d.value > 0),
          window.Plot.pointerX({
            x: "year",
            y: yField,
            title: (d) => `${d.year}: ${d.value.toLocaleString()} ${label.toLowerCase()}`
          })
        )
      ]
    });

    chartContainer.appendChild(chart);
    return { 
      chart, 
      redraw: () => {
        chartContainer.innerHTML = "";
        return this.createSingleDataFacetChart(container, data, dataType, maxValue, yearRange);
      }
    };
  },

  /**
   * Creates a single modal chart for non-parish data types
   * @param {HTMLElement} container - Container element for the chart
   * @param {Array} data - Data array
   * @param {string} dataType - Type of data ('death' or 'christening')
   * @param {Object} options - Chart options
   */
  createSingleModalChart(container, data, dataType, options = {}) {
    let allData, noDataMessage, color, yField, labelSingular, labelPlural;
    
    if (dataType === 'death') {
      allData = data.filter(d => d.total_deaths > 0).sort((a, b) => a.year - b.year);
      noDataMessage = 'No death data available for this cause';
      color = "#DC2626";
      yField = "total_deaths";
      labelSingular = "death";
      labelPlural = "deaths";
    } else if (dataType === 'christening') {
      allData = data.filter(d => d.total_christenings > 0).sort((a, b) => a.year - b.year);
      noDataMessage = 'No christening data available for this type';
      color = "#059669";
      yField = "total_christenings";
      labelSingular = "christening";
      labelPlural = "christenings";
    }

    if (!allData || allData.length === 0) {
      container.innerHTML = `<div class="text-center py-8 text-gray-500">${noDataMessage}</div>`;
      return;
    }

    const years = allData.map(d => d.year);
    const maxValue = Math.max(...allData.map(d => d[yField])) * 1.1;

    const chart = window.Plot.plot({
      width: container.clientWidth || 400,
      height: 250,
      marginTop: 20,
      marginRight: 40,
      marginBottom: 50,
      marginLeft: 60,
      x: {
        type: "band",
        domain: years,
        padding: 0.1,
        label: "Year",
        tickRotate: -45,
        tickFormat: (d, i) => i % 5 === 0 ? d.toString() : "",
      },
      y: {
        grid: true,
        label: `Number of ${labelPlural}`,
        domain: [0, maxValue],
        tickFormat: d => d.toLocaleString()
      },
      marks: [
        window.Plot.barY(allData, {
          x: "year",
          y: yField,
          fill: color,
          title: (d) => `${d.year}: ${d[yField].toLocaleString()} ${d[yField] === 1 ? labelSingular : labelPlural}`
        }),
        window.Plot.ruleY([0]),
        window.Plot.tip(
          allData,
          window.Plot.pointerX({
            x: "year",
            y: yField,
            title: (d) => `${d.year}: ${d[yField].toLocaleString()} ${d[yField] === 1 ? labelSingular : labelPlural}`
          })
        )
      ]
    });

    container.appendChild(chart);

    return {
      chart,
      redraw: () => this.createSingleModalChart(container, data, dataType, options)
    };
  },

  /**
   * Creates a simple bar chart for data counts
   * @param {HTMLElement} container - Container element for the chart
   * @param {Array} data - Data array with year and count properties
   * @param {Object} options - Chart options
   */
  createDataCountsBarChart(container, data, options = {}) {
    if (!container || !data || !window.Plot) {
      console.error("Missing requirements for data counts chart rendering");
      return;
    }

    try {
      // Clear previous content
      container.innerHTML = "";

      // Filter and sort data
      const chartData = data
        .filter((d) => d.count > 0)
        .sort((a, b) => a.year - b.year);

      if (chartData.length === 0) {
        container.innerHTML = '<div class="text-center py-8 text-gray-500">No data available</div>';
        return;
      }

      // Set default options
      const defaultOptions = {
        width: container.clientWidth || 800,
        height: 400,
        marginTop: 20,
        marginRight: 40,
        marginBottom: 60,
        marginLeft: 60,
        color: "#7f5a83",
      };

      // Merge with provided options
      const chartOptions = { ...defaultOptions, ...options };

      // Create the chart
      const chart = window.Plot.plot({
        width: chartOptions.width,
        height: chartOptions.height,
        marginTop: chartOptions.marginTop,
        marginRight: chartOptions.marginRight,
        marginBottom: chartOptions.marginBottom,
        marginLeft: chartOptions.marginLeft,
        
        x: {
          type: "band",
          domain: chartData.map(d => d.year),
          padding: 0.1,
          label: "Year",
          tickRotate: 45,
          tickFormat: (d) => {
            // Show years every 5 years to reduce clutter
            return d % 5 === 0 ? d.toString() : "";
          }
        },
        
        y: {
          grid: true,
          label: "Number of Records",
          domain: [0, Math.max(...chartData.map(d => d.count)) * 1.1],
          tickFormat: d => d.toLocaleString()
        },
        
        marks: [
          window.Plot.barY(chartData, {
            x: "year",
            y: "count",
            fill: chartOptions.color,
            title: (d) => `${d.year}: ${d.count.toLocaleString()} records`
          }),
          window.Plot.ruleY([0]),
          
          // Add interactive tooltip
          window.Plot.tip(
            chartData,
            window.Plot.pointerX({
              x: "year",
              y: "count",
              title: (d) => `Transcribed bills for ${d.year}\nTotal rows of data: ${d.count.toLocaleString()}`
            })
          )
        ]
      });

      // Add to DOM
      container.appendChild(chart);

      return chart;
    } catch (error) {
      console.error("Error creating data counts chart:", error);
      container.innerHTML = `<div class="text-red-500 text-center py-4">Error creating chart: ${error.message}</div>`;
    }
  },
};

// Export the service
window.ChartService = ChartService;

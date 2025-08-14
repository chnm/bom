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
   * Creates an interactive detailed chart for the modal view
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

      // Define a chart container div
      const chartContainer = document.createElement("div");
      chartContainer.className = "chart-container";

      // Process data based on type
      let allData, noDataMessage, legendItems, yField, titleField;
      
      if (dataType === 'parish') {
        // Keep all data in a variable for redrawing
        allData = data
          .filter((d) => d.total_buried > 0)
          .sort((a, b) => a.year - b.year);
        noDataMessage = 'No burial data available for this parish';
        legendItems = [
          { type: "plague", color: "#EF3054", field: "total_plague" },
          { type: "buried", color: "#96ADC8", field: "total_buried" },
        ];
      } else if (dataType === 'death') {
        allData = data
          .filter((d) => d.total_deaths > 0)
          .sort((a, b) => a.year - b.year);
        noDataMessage = 'No death data available for this cause';
        legendItems = [
          { type: "deaths", color: "#DC2626", field: "total_deaths" },
        ];
      } else if (dataType === 'christening') {
        allData = data
          .filter((d) => d.total_christenings > 0)
          .sort((a, b) => a.year - b.year);
        noDataMessage = 'No christening data available for this type';
        legendItems = [
          { type: "christenings", color: "#059669", field: "total_christenings" },
        ];
      }

      if (allData.length === 0) {
        container.innerHTML = `<div class="text-center py-4 text-gray-500">${noDataMessage}</div>`;
        return;
      }

      // State for category visibility (initialize based on data type)
      const categoryVisibility = {};
      legendItems.forEach(item => {
        categoryVisibility[item.type] = true;
      });

      // Create custom interactive legend
      const legendContainer = document.createElement("div");
      legendContainer.className =
        "custom-legend flex justify-center gap-6 mb-3 mt-1";

      legendItems.forEach((item) => {
        const itemEl = document.createElement("div");
        itemEl.className = "flex items-center gap-2 cursor-pointer select-none";
        itemEl.dataset.type = item.type;

        // Color swatch - made larger and more visible
        const swatch = document.createElement("div");
        swatch.className = "inline-block w-4 h-4 rounded";
        swatch.style.backgroundColor = item.color;
        swatch.style.opacity = categoryVisibility[item.type] ? 1 : 0.3;
        swatch.style.border = "1px solid #ddd";

        // Label
        const label = document.createElement("span");
        label.textContent = item.type;
        label.className = "text-sm font-medium";
        label.style.opacity = categoryVisibility[item.type] ? 1 : 0.5;
        label.style.textDecoration = categoryVisibility[item.type]
          ? "none"
          : "line-through";

        // Add click handler to toggle visibility
        itemEl.addEventListener("click", () => {
          categoryVisibility[item.type] = !categoryVisibility[item.type];

          // Update legend appearance
          swatch.style.opacity = categoryVisibility[item.type] ? 1 : 0.3;
          label.style.opacity = categoryVisibility[item.type] ? 1 : 0.5;
          label.style.textDecoration = categoryVisibility[item.type]
            ? "none"
            : "line-through";

          // Redraw chart with updated visibility
          drawChart();
        });

        itemEl.appendChild(swatch);
        itemEl.appendChild(label);
        legendContainer.appendChild(itemEl);
      });

      // Add custom legend above chart
      container.appendChild(legendContainer);
      container.appendChild(chartContainer);

      // Function to draw/redraw the chart based on visibility
      const drawChart = () => {
        // Always clear the chart container before redrawing
        chartContainer.innerHTML = "";

        // Create long-form data for stacked chart based on visibility and data type
        const longFormData = [];
        allData.forEach((d) => {
          if (dataType === 'parish') {
            // Add plague deaths (if visible and exists)
            if (categoryVisibility.plague && d.total_plague) {
              longFormData.push({
                year: d.year,
                type: "plague",
                value: d.total_plague,
                total: d.total_buried,
              });
            }

            // Add non-plague deaths (if visible)
            if (categoryVisibility.buried) {
              const nonplague = d.total_buried - (d.total_plague || 0);
              longFormData.push({
                year: d.year,
                type: "buried",
                value: nonplague,
                total: d.total_buried,
              });
            }
          } else if (dataType === 'death') {
            // Add deaths data
            if (categoryVisibility.deaths && d.total_deaths) {
              longFormData.push({
                year: d.year,
                type: "deaths",
                value: d.total_deaths,
                total: d.total_deaths,
              });
            }
          } else if (dataType === 'christening') {
            // Add christenings data
            if (categoryVisibility.christenings && d.total_christenings) {
              longFormData.push({
                year: d.year,
                type: "christenings",
                value: d.total_christenings,
                total: d.total_christenings,
              });
            }
          }
        });

        // Ensure we have data to plot
        if (longFormData.length === 0) {
          const noDataMessage = document.createElement("div");
          noDataMessage.className = "text-center py-10 text-gray-500";
          noDataMessage.textContent =
            "No data to display - please enable at least one category";
          chartContainer.appendChild(noDataMessage);
          return;
        }

        const years = [...new Set(longFormData.map((d) => d.year))].sort();

        // Calculate max value for y domain
        const maxValue = Math.max(...longFormData.map((d) => d.value)) * 1.1;

        // Create the chart
        const chart = window.Plot.plot({
          width: container.clientWidth || 400,
          height: 220,
          marginTop: 20,
          marginRight: 40,
          marginBottom: 50,
          marginLeft: 50,
          x: {
            type: "band",
            domain: years,
            padding: 0.1,
            label: "Year",
            tickRotate: -45,
            tickAnchor: "end",
            tickFormat: (d, i) =>
              i % 5 === 0 ? d.toString().replace(/,/g, "") : "",
          },
          y: {
            grid: true,
            label: "Count",
            domain: [0, maxValue],
          },
          color: {
            domain: legendItems
              .map((item) => item.type)
              .filter((type) => categoryVisibility[type]),
            range: legendItems
              .filter((item) => categoryVisibility[item.type])
              .map((item) => item.color),
          },
          marks: [
            window.Plot.barY(longFormData, {
              x: "year",
              y: "value",
              fill: "type",
              title: (d) => {
                const yearStr = d.year.toString().replace(/,/g, "");
                if (dataType === 'parish') {
                  if (d.type === "plague") {
                    return `${yearStr}: ${d.value} plague deaths (${d.total} total deaths)`;
                  } else {
                    return `${yearStr}: ${d.value} burials (${d.total} total burials)`;
                  }
                } else if (dataType === 'death') {
                  return `${yearStr}: ${d.value} deaths from this cause`;
                } else if (dataType === 'christening') {
                  return `${yearStr}: ${d.value} christenings of this type`;
                }
                return `${yearStr}: ${d.value} ${d.type}`;
              },
              stack: true,
            }),
            window.Plot.ruleY([0]),
            window.Plot.tip(
              longFormData,
              window.Plot.pointerX({
                x: "year",
                y: "value",
                title: (d) => `${d.year}: ${d.value} ${d.type.toLowerCase()}`,
              }),
            ),
          ],
        });

        // Add the chart to the dedicated chart container
        chartContainer.appendChild(chart);
      };

      // Initial chart render
      drawChart();

      return {
        updateVisibility: (type, visible) => {
          categoryVisibility[type] = visible;

          // Update legend appearance
          const legendItem = legendContainer.querySelector(
            `[data-type="${type}"]`,
          );
          if (legendItem) {
            const swatch = legendItem.querySelector("div");
            const label = legendItem.querySelector("span");
            if (swatch) swatch.style.opacity = visible ? 1 : 0.3;
            if (label) {
              label.style.opacity = visible ? 1 : 0.5;
              label.style.textDecoration = visible ? "none" : "line-through";
            }
          }

          drawChart();
        },
        redraw: () => drawChart(),
      };
    } catch (error) {
      console.error("Error creating modal chart:", error);
      container.innerHTML = `<div class="text-center text-red-500 py-4">Error drawing chart: ${error.message}</div>`;
    }
  },
};

// Export the service
window.ChartService = ChartService;

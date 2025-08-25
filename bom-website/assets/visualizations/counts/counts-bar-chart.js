export default class PlagueBillsBarChart {
  constructor(selector, data, options = {}) {
    this.selector = selector;
    this.data = data;
    this.options = {
      width: 960,
      height: 500,
      marginTop: 20,
      marginRight: 40,
      marginBottom: 60,
      marginLeft: 50,
      color: "#7f5a83",
      ...options
    };
    
    // Load Observable Plot if not available
    this.plotPromise = this.loadPlot();
  }

  async loadPlot() {
    // Use existing ChartService if available
    if (window.ChartService && window.ChartService.loadPlotLibrary) {
      return await window.ChartService.loadPlotLibrary();
    }

    if (window.Plot) {
      return window.Plot;
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.type = "module";
      script.textContent = `
        import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";
        window.Plot = Plot;
        document.dispatchEvent(new Event("plot-loaded"));
      `;
      document.head.appendChild(script);

      document.addEventListener(
        "plot-loaded",
        () => resolve(window.Plot),
        { once: true }
      );

      setTimeout(() => {
        if (!window.Plot) {
          reject(new Error("Failed to load Observable Plot"));
        }
      }, 5000);
    });
  }

  async render() {
    try {
      // Wait for Plot to load
      await this.plotPromise;

      // Remove any loading message
      const loadingElement = document.querySelector(".loading_rows");
      if (loadingElement) {
        loadingElement.remove();
      }

      // Clear the container
      const container = document.querySelector(this.selector);
      if (!container) {
        throw new Error(`Container not found: ${this.selector}`);
      }
      container.innerHTML = "";

      // Prepare the data
      const chartData = this.data.plague || [];
      
      if (chartData.length === 0) {
        container.innerHTML = '<div class="text-center py-8 text-gray-500">No data available</div>';
        return;
      }

      // Sort data by year to ensure proper display
      chartData.sort((a, b) => a.year - b.year);

      // Create the Observable Plot chart
      const chart = window.Plot.plot({
        width: this.options.width,
        height: this.options.height,
        marginTop: this.options.marginTop,
        marginRight: this.options.marginRight,
        marginBottom: this.options.marginBottom,
        marginLeft: this.options.marginLeft,
        
        x: {
          type: "band",
          domain: chartData.map(d => d.year),
          padding: 0.1,
          label: "Year",
          tickRotate: 45,
          tickFormat: (d, i) => {
            // Show years every 5 years to reduce clutter
            return d % 5 === 0 ? d.toString() : "";
          }
        },
        
        y: {
          grid: true,
          label: "Number of Rows",
          domain: [0, Math.max(...chartData.map(d => d.count)) * 1.1]
        },
        
        marks: [
          window.Plot.barY(chartData, {
            x: "year",
            y: "count",
            fill: this.options.color,
            title: (d) => `Transcribed bills for ${d.year}\nTotal rows of data: ${d.count.toLocaleString()}`
          }),
          window.Plot.ruleY([0]),
          
          // Add interactive tooltip
          window.Plot.tip(
            chartData,
            window.Plot.pointerX({
              x: "year",
              y: "count",
              title: (d) => `${d.year}: ${d.count.toLocaleString()} rows of data`
            })
          )
        ]
      });

      // Append the chart to the container
      container.appendChild(chart);

      return chart;
    } catch (error) {
      console.error("Error rendering chart:", error);
      const container = document.querySelector(this.selector);
      if (container) {
        container.innerHTML = `<div class="text-center text-red-500 py-4">Error rendering chart: ${error.message}</div>`;
      }
      throw error;
    }
  }
}

import * as d3 from "d3";
import * as Plot from "@observablehq/plot";

// Global variables to store data
let allData = null;
let cachedPlots = {};
let processedData = {};

// Add loading indicator to DOM
document.getElementById("facets").innerHTML =
  '<div id="loading">Loading data...</div>';

// Fetch data only once and store it
fetchData().then(() => {
  renderPage("original", "burials");
});

// Fetch data function - separated from rendering for better caching
async function fetchData() {
  if (allData !== null) return allData;

  try {
    console.log("Fetching data...");
    const response = await d3.json(
      "https://data.chnm.org/bom/statistics?type=parish-yearly",
    );
    allData = response;
    return allData;
  } catch (error) {
    console.error("Error fetching data:", error);
    document.getElementById("facets").innerHTML =
      "<div>Error loading data. Please try again later.</div>";
    return null;
  }
}

// Process data and render page
function renderPage(dataFormat, countType) {
  if (!allData) return;

  // Show loading indicator
  document.getElementById("facets").innerHTML =
    '<div id="loading">Processing data...</div>';

  // Use setTimeout to allow the loading indicator to render
  setTimeout(() => {
    // Process data
    const cacheKey = `${dataFormat}-${countType}`;
    if (cachedPlots[cacheKey]) {
      // Use cached plot if available
      d3.select("#facets").selectAll("*").remove();
      document.getElementById("facets").appendChild(cachedPlots[cacheKey]);
      return;
    }

    // Process data only once and store for reuse
    if (!processedData[cacheKey]) {
      const tidy = Object.keys(allData[1])
        .slice(2)
        .flatMap((count) =>
          allData.map((d) => ({
            year: d.year,
            parish_name: d.parish_name,
            count,
            amount: d[count],
          })),
        );
      processedData[cacheKey] = tidy;
    }

    // Create the plot with a loading indicator
    document.getElementById("facets").innerHTML =
      '<div id="loading">Building visualization...</div>';

    // Render charts in next microtask to allow UI update
    setTimeout(() => {
      makeGraphs(dataFormat, countType, processedData[cacheKey]);
    }, 10);
  }, 10);
}

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  // Get data format value
  const dataButtons = document.querySelectorAll('input[name="data-format"]');
  let dataFormat = undefined;
  for (const dataButton of dataButtons) {
    if (dataButton.checked) {
      dataFormat = dataButton.value;
      break;
    }
  }

  // Get count type value
  const countButtons = document.querySelectorAll('input[name="count-type"]');
  let countType = undefined;
  for (const countButton of countButtons) {
    if (countButton.checked) {
      countType = countButton.value;
      break;
    }
  }

  renderPage(dataFormat, countType);
});

// Add event listener to the reset button
document.getElementById("reset-button").addEventListener("click", () => {
  const allRadioButtons = document.querySelectorAll('input[type="radio"]');
  // Reset each radio button to its original state
  for (var i = 0; i < allRadioButtons.length; i++)
    // 6 buttons, 0 = original data, 3 = burials
    if (i === 0 || i === 3) {
      allRadioButtons[i].checked = true;
    } else {
      allRadioButtons[i].checked = false;
    }

  console.log("Reset to default values");

  // Render with default values
  renderPage("original", "burials");
});

// Optimize the dataset before plotting
function optimizeDataset(tidy, format, count) {
  // Filter data based on selected count type
  const filteredData =
    count === "plague"
      ? tidy.filter((d) => d.count === "total_plague")
      : count === "both"
        ? tidy
        : tidy.filter((d) => d.count === "total_buried");

  // Pre-calculate transformations
  if (format === "log10(x+1)") {
    return filteredData.map((d) => ({
      ...d,
      transformed_amount: Math.log10(d.amount + 1),
    }));
  }

  return filteredData;
}

// Optimized approach to render the plots with better performance
function makeGraphs(format, count, tidy) {
  // Clear the container first
  d3.select("#facets").selectAll("*").remove();

  // Create container for the visualization
  const container = document.createElement("div");
  container.className = "visualization-container";

  // Add the container to the DOM
  document.getElementById("facets").appendChild(container);

  try {
    // Get all parishes
    const allParishes = Array.from(new Set(tidy.map((d) => d.parish_name)));
    console.log(`Rendering ${allParishes.length} parishes`);

    // Create the optimized dataset
    const dataToPlot = optimizeDataset(tidy, format, count);

    // Create the plot config with 3 columns for better readability
    const plotConfig = createPlotConfig(format, count, dataToPlot, allParishes);

    // Create the plot - this is the expensive operation
    const plot = Plot.plot(plotConfig);

    // Add the plot to the container
    container.appendChild(plot);

    // Cache for future use
    const cacheKey = `${format}-${count}`;
    cachedPlots[cacheKey] = container;
  } catch (e) {
    console.error("Error creating visualization:", e);
    container.innerHTML = `<div style="color: red; padding: 20px;">Error creating visualization: ${e.message}</div>`;
  }
}

// Create the plot configuration
function createPlotConfig(format, count, tidy, allParishes) {
  const n = 5;
  const keys = allParishes;
  const index = new Map(keys.map((key, i) => [key, i]));
  const fx = (key) => index.get(key) % n;
  const fy = (key) => Math.floor(index.get(key) / n);

  // Custom colors
  const plagueColor = "rgb(239, 48, 84)";
  const burialColor = "rgb(150, 173, 200)";

  // Create configuration with color scale for the "both" mode
  const config = {
    height: Math.max(500, Math.ceil(keys.length / n) * 120),
    width: 1100, // Adjusted width for 3 columns
    axis: null,
    color:
      count === "both"
        ? {
            type: "categorical",
            domain: ["total_plague", "total_buried"],
            range: [plagueColor, burialColor],
            legend: true,
          }
        : null,
    style: { fontSize: 13 },
    y: { insetTop: 10 },
    fx: { padding: 0.03 },
    title:
      count === "plague"
        ? "Total plague deaths for each parish"
        : count === "both"
          ? "Total plague and burial deaths for each parish"
          : "Total burials for each parish",
    subtitle:
      format === "normalized"
        ? "Data has been normalized"
        : format === "log10(x+1)"
          ? "Data has been transformed by log10(x+1)"
          : "Original data",
    marks: [],
  };

  // Define the marks depending on format type
  if (format === "normalized") {
    config.marks.push(
      Plot.barY(
        count === "plague"
          ? tidy.filter((d) => d.count === "total_plague")
          : count === "both"
            ? tidy
            : tidy.filter((d) => d.count === "total_buried"),
        Plot.normalizeY("extent", {
          x: "year",
          y: "amount",
          fx: (d) => fx(d.parish_name),
          fy: (d) => fy(d.parish_name),
          stroke:
            count === "both"
              ? "count"
              : count === "plague"
                ? plagueColor
                : burialColor,
          fill:
            count === "both"
              ? "count"
              : count === "plague"
                ? plagueColor
                : burialColor,
        }),
      ),
    );
  } else if (format === "log10(x+1)") {
    config.marks.push(
      Plot.barY(
        count === "plague"
          ? tidy.filter((d) => d.count === "total_plague")
          : count === "both"
            ? tidy
            : tidy.filter((d) => d.count === "total_buried"),
        {
          x: "year",
          y: (d) => d.transformed_amount || Math.log10(d.amount + 1),
          fx: (d) => fx(d.parish_name),
          fy: (d) => fy(d.parish_name),
          stroke:
            count === "both"
              ? "count"
              : count === "plague"
                ? plagueColor
                : burialColor,
          fill:
            count === "both"
              ? "count"
              : count === "plague"
                ? plagueColor
                : burialColor,
        },
      ),
    );
  } else {
    config.marks.push(
      Plot.barY(
        count === "plague"
          ? tidy.filter((d) => d.count === "total_plague")
          : count === "both"
            ? tidy
            : tidy.filter((d) => d.count === "total_buried"),
        {
          x: "year",
          y: "amount",
          fx: (d) => fx(d.parish_name),
          fy: (d) => fy(d.parish_name),
          stroke:
            count === "both"
              ? "count"
              : count === "plague"
                ? plagueColor
                : burialColor,
          fill:
            count === "both"
              ? "count"
              : count === "plague"
                ? plagueColor
                : burialColor,
        },
      ),
    );
  }

  // Add axes and other marks
  config.marks.push(
    Plot.axisX({
      ticks: [1636, 1665, 1701, 1730, 1752],
      tickFormat: "",
      tickRotate: 50,
      tickPadding: 5,
      labelOffset: 42,
    }),
    Plot.axisY({ labelArrow: "none" }),
    Plot.text(keys, { fx, fy, frameAnchor: "top-left", dx: 6, dy: 2 }),
    Plot.frame(),
  );

  return config;
}

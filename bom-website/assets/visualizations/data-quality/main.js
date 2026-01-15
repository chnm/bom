import * as d3 from "d3";
import DataQualityCalendar from "./data-quality-calendar";

// Function to populate the year dropdown with available years
function populateYearDropdown() {
  const yearDropdown = d3.select("#year");

  // Clear existing options
  yearDropdown.selectAll("option").remove();

  // Add years from 1636 to 1754
  for (let year = 1636; year <= 1754; year++) {
    yearDropdown.append("option").attr("value", year).text(year);
  }

  // Set default year
  yearDropdown.property("value", 1636);
}

// Data type is fixed to bills only since other types lack quality fields
const DATA_TYPE = "bills";

// Function to populate quality type dropdown
function populateQualityTypeDropdown() {
  const qualityTypeSelect = document.getElementById("quality-type");
  const qualityTypes = [
    { value: "illegible", label: "Illegible Records" },
    { value: "missing", label: "Missing Records" },
  ];

  qualityTypeSelect.innerHTML = "";
  qualityTypes.forEach((type) => {
    const option = document.createElement("option");
    option.value = type.value;
    option.textContent = type.label;
    qualityTypeSelect.appendChild(option);
  });

  // Set default to missing
  qualityTypeSelect.value = "missing";
}

// Function to fetch data and render the calendar
function fetchDataAndRender(year, qualityType = "missing") {
  if (!year) return;

  // Show loading indicator
  d3.select("#chart").selectAll("*").remove();
  d3.select("#chart")
    .append("div")
    .attr("class", "loading_chart")
    .text("Loading data quality information...");

  const url = `https://data.chnm.org/bom/${DATA_TYPE}?start-year=${year}&end-year=${year}&limit=10000`;

  d3.json(url)
    .then((response) => {
      const data = response.data || response; // Handle different response formats
      d3.select("#chart").selectAll("*").remove();

      if (!data || data.length === 0) {
        // Display a message if no data is available
        d3.select("#chart")
          .append("div")
          .style("text-align", "center")
          .style("padding", "60px 20px")
          .style("font-size", "18px")
          .style("color", "#dc2626")
          .text("No data available for this year and data type.");
      } else {
        // Filter out records without week_number as they can't be plotted
        const validData = data.filter(
          (d) => d.week_number && d.week_number > 0,
        );

        if (validData.length === 0) {
          d3.select("#chart")
            .append("div")
            .style("text-align", "center")
            .style("padding", "60px 20px")
            .style("font-size", "18px")
            .style("color", "#dc2626")
            .text(
              "No valid weekly data available for this year and data type.",
            );
          return;
        }

        // Calculate summary statistics
        const totalRecords = validData.length;
        const qualityIssueRecords = validData.filter(
          (d) => d[qualityType] === true,
        ).length;
        const overallRate =
          totalRecords > 0 ? (qualityIssueRecords / totalRecords) * 100 : 0;

        // Update summary statistics
        updateSummaryStats(
          totalRecords,
          qualityIssueRecords,
          overallRate,
          qualityType,
        );

        // Calculate height based on number of unique parishes
        const uniqueParishes = [...new Set(validData.map((d) => d.name))];
        const dynamicHeight = Math.max(600, uniqueParishes.length * 35 + 200);

        const calendar = new DataQualityCalendar(
          "#chart",
          validData,
          { width: 960, height: dynamicHeight },
          qualityType,
        );
        calendar.render();
      }

      // Update the chart title
      const qualityTypeLabel = getQualityTypeLabel(qualityType);
      updateChartTitle(year, qualityTypeLabel);
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
      d3.select("#chart").selectAll("*").remove();
      d3.select("#chart")
        .append("div")
        .style("text-align", "center")
        .style("padding", "60px 20px")
        .style("font-size", "18px")
        .style("color", "#dc2626")
        .text("Error loading data. Please try again or contact support.");
    });
}

// Data type is fixed to parish records
const DATA_TYPE_LABEL = "Parish Records";

// Helper function to get quality type label
function getQualityTypeLabel(qualityType) {
  const labels = {
    illegible: "Illegible Records",
    missing: "Missing Records",
  };
  return labels[qualityType] || qualityType;
}

// Function to update chart title
function updateChartTitle(year, qualityTypeLabel) {
  d3.select("#chart-title").html(
    `${qualityTypeLabel} in Weekly Bills Data for <span class="underline">${year}</span>`,
  );
}

// Function to update summary statistics
function updateSummaryStats(total, qualityIssueCount, rate, qualityType) {
  const summaryContainer = d3.select("#summary-stats");

  if (summaryContainer.empty()) {
    // Create summary container if it doesn't exist
    d3.select("#chart")
      .insert("div", ":first-child")
      .attr("id", "summary-stats")
      .attr(
        "class",
        "bg-gray-50 rounded-lg p-4 mb-6 grid grid-cols-3 gap-4 text-center",
      );
  }

  const summary = d3.select("#summary-stats");
  summary.selectAll("*").remove();

  const qualityLabel = qualityType === "illegible" ? "Illegible" : "Missing";
  const qualityRateLabel =
    qualityType === "illegible" ? "Illegibility Rate" : "Missing Data Rate";

  // Total records
  summary.append("div").html(`
      <div class="text-2xl font-bold text-gray-900">${total.toLocaleString()}</div>
      <div class="text-sm text-gray-600">Total Records</div>
    `);

  // Quality issue records
  summary.append("div").html(`
      <div class="text-2xl font-bold text-amber-600">${qualityIssueCount.toLocaleString()}</div>
      <div class="text-sm text-gray-600">${qualityLabel} Records</div>
    `);

  // Quality issue rate
  const rateColor =
    rate > 20
      ? "text-red-600"
      : rate > 10
        ? "text-amber-600"
        : "text-green-600";
  summary.append("div").html(`
      <div class="text-2xl font-bold ${rateColor}">${rate.toFixed(1)}%</div>
      <div class="text-sm text-gray-600">${qualityRateLabel}</div>
    `);
}

// Initialize the page
populateYearDropdown();
populateQualityTypeDropdown();

// Load initial data with default values
fetchDataAndRender(1636, "missing");

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  const qualityType = document.getElementById("quality-type").value;
  fetchDataAndRender(year, qualityType);
});


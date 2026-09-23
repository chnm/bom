import * as d3 from "d3";
import renderDataQuality from "./data-quality-calendar";
import { redrawOnResize } from "../common/responsive";

const chart = document.getElementById("chart");
let current = null; // data and quality type on screen, kept for redraws on resize

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

function showMessage(text) {
  current = null;
  chart.innerHTML = "";
  d3.select(chart).append("p").attr("class", "viz-message is-error").text(text);
}

// Function to fetch data and render the calendar
function fetchDataAndRender(year, qualityType = "missing") {
  if (!year) return;

  // Show loading indicator
  d3.select("#summary-stats").selectAll("*").remove();
  chart.innerHTML = "";
  d3.select(chart).append("div").attr("class", "loading_chart").text("Loading data quality information...");

  const url = `https://data.chnm.org/bom/${DATA_TYPE}?start-year=${year}&end-year=${year}&limit=10000`;

  d3.json(url)
    .then((response) => {
      const data = response.data || response; // Handle different response formats
      d3.selectAll(".loading_chart").remove();

      if (!data || data.length === 0) {
        showMessage("No data available for this year and data type.");
      } else {
        // Filter out records without week_number as they can't be plotted
        const validData = data.filter((d) => d.week_number && d.week_number > 0);

        if (validData.length === 0) {
          showMessage("No valid weekly data available for this year and data type.");
          return;
        }

        // Calculate summary statistics
        const totalRecords = validData.length;
        const qualityIssueRecords = validData.filter((d) => d[qualityType] === true).length;
        const overallRate = totalRecords > 0 ? (qualityIssueRecords / totalRecords) * 100 : 0;

        updateSummaryStats(totalRecords, qualityIssueRecords, overallRate, qualityType);

        current = { data: validData, qualityType };
        renderDataQuality(chart, validData, qualityType);
      }

      // Update the chart title
      const qualityTypeLabel = getQualityTypeLabel(qualityType);
      updateChartTitle(year, qualityTypeLabel);
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
      showMessage("Error loading data. Please try again or contact support.");
    });
}

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
  d3.select("#chart-title").html(`${qualityTypeLabel} in Weekly Bills Data for <u>${year}</u>`);
}

// Function to update summary statistics
function updateSummaryStats(total, qualityIssueCount, rate, qualityType) {
  const summary = d3.select("#summary-stats");
  summary.selectAll("*").remove();

  const qualityLabel = qualityType === "illegible" ? "Illegible" : "Missing";
  const qualityRateLabel = qualityType === "illegible" ? "Illegibility Rate" : "Missing Data Rate";

  // Total records
  summary.append("div").html(`
      <div class="viz-stat-value">${total.toLocaleString()}</div>
      <div class="viz-stat-label">Total Records</div>
    `);

  // Quality issue records
  summary.append("div").html(`
      <div class="viz-stat-value is-warning">${qualityIssueCount.toLocaleString()}</div>
      <div class="viz-stat-label">${qualityLabel} Records</div>
    `);

  // Quality issue rate
  const rateColor = rate > 20 ? "is-bad" : rate > 10 ? "is-warning" : "";
  summary.append("div").html(`
      <div class="viz-stat-value ${rateColor}">${rate.toFixed(1)}%</div>
      <div class="viz-stat-label">${qualityRateLabel}</div>
    `);
}

// Redraw at the new width when the chart's box changes size
redrawOnResize(chart, () => current && renderDataQuality(chart, current.data, current.qualityType));

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

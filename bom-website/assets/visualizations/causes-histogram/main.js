import * as d3 from "d3";
import renderHistogram from "./causes-histogram";
import { redrawOnResize } from "../common/responsive";

const chart = document.getElementById("chart");
let current = null; // data and cause on screen, kept for redraws on resize

// Function to fetch the list of causes and populate the dropdown
function populateCausesDropdown(billType = 'weekly') {
  const url = `https://data.chnm.org/bom/list-deaths?bill-type=${billType}`;

  d3.json(url)
    .then((data) => {
      const causeDropdown = d3.select("#cause");
      causeDropdown.selectAll("option").remove(); // Clear existing options

      // Populate the dropdown with fetched causes
      data.forEach((cause) => {
        causeDropdown
          .append("option")
          .attr("value", cause.name)
          .text(cause.name);
      });

      // Set default value to "aged"
      causeDropdown.property("value", "aged");
    })
    .catch((error) => {
      console.error("There was an error fetching the list of causes.", error);
    });
}

// Fill the year dropdown with the years that have data for `cause`, keeping the
// chosen year when the new cause has it.
function populateYearsDropdown(cause, billType = 'weekly') {
  const url = `https://data.chnm.org/bom/causes?bill-type=${billType}&start-year=1636&end-year=1754&id=${encodeURIComponent(cause)}`;

  d3.json(url)
    .then((data) => {
      const yearDropdown = d3.select("#year");
      const chosen = yearDropdown.property("value") || "1668";
      yearDropdown.selectAll("option").remove(); // Clear existing options

      const years = [...new Set(data.map(d => d.year))].sort((a, b) => a - b);
      years.forEach((year) => {
        yearDropdown
          .append("option")
          .attr("value", year)
          .text(year);
      });

      if (years.map(String).includes(chosen)) yearDropdown.property("value", chosen);
    })
    .catch((error) => {
      console.error("There was an error fetching the list of years.", error);
    });
}

// Function to fetch data and render the histogram
function fetchDataAndRender(year, cause, billType = 'weekly') {
  const url = `https://data.chnm.org/bom/causes?bill-type=${billType}&start-year=${year}&end-year=${year}&limit=9000`;

  d3.json(url)
    .then((data) => {
      d3.select(".loading_chart").remove();
      current = data.length ? { data, cause } : null;
      if (current) {
        renderHistogram(chart, data, cause);
      } else {
        chart.innerHTML = '<p class="viz-message">No data available for this year.</p>';
      }

      // Update the chart title
      d3.select("#chart-title").html(
        `Cause of death <u>${cause}</u> for the year <u>${year}</u>`,
      );
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Redraw at the new width when the chart's box changes size
redrawOnResize(chart, () => current && renderHistogram(chart, current.data, current.cause));

// Initial population of the dropdowns
populateCausesDropdown();
populateYearsDropdown("aged");
document.getElementById("cause").addEventListener("change", (e) => populateYearsDropdown(e.target.value));

// Initial fetch and render
fetchDataAndRender(1668, "aged");

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  const cause = document.getElementById("cause").value;
  fetchDataAndRender(year, cause);
});


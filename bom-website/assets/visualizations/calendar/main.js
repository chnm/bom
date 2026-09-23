import * as d3 from "d3";
import renderCalendar from "./calendar";
import { redrawOnResize } from "../common/responsive";

const chart = document.getElementById("chart");
let current = null; // data for the year on screen, kept for redraws on resize

// Function to populate the year dropdown with available years
function populateYearDropdown() {
  const url = `https://data.chnm.org/bom/causes?bill-type=weekly`;

  d3.json(url)
    .then((data) => {
      // Extract unique years and sort them
      const years = [...new Set(data.map((d) => d.year))].sort((a, b) => a - b);

      const yearSelect = document.getElementById("year");
      if (!yearSelect) {
        console.error("Year select element not found!");
        return;
      }

      yearSelect.innerHTML = ""; // Clear loading option

      // Add years as options
      years.forEach((year) => {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
      });

      // Set the first available year as default and render chart
      if (years.length > 0) {
        yearSelect.value = years[0];
        fetchDataAndRender(years[0]);
      }
    })
    .catch((error) => {
      console.error("Error loading available years:", error);
      const yearSelect = document.getElementById("year");
      if (yearSelect) {
        yearSelect.innerHTML = '<option value="">Error loading years</option>';
      }
    });
}

// Fetch one year of weekly causes and draw it
function fetchDataAndRender(year) {
  if (!year) return;

  const url = `https://data.chnm.org/bom/causes?bill-type=weekly&start-year=${year}&end-year=${year}`;

  d3.json(url)
    .then((data) => {
      d3.select(".loading_chart").remove();
      current = data.length ? data : null;
      if (current) {
        renderCalendar(chart, current);
      } else {
        chart.innerHTML = '<p class="viz-message">No data available for this year.</p>';
      }
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Redraw at the new width when the chart's box changes size
redrawOnResize(chart, () => current && renderCalendar(chart, current));

// Initialize the page
populateYearDropdown();

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  fetchDataAndRender(year);
});

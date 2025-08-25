import * as d3 from "d3";
import SeasonalityChart from "./causes-seasonality";

// Function to fetch the list of causes and populate the dropdowns
function populateCausesDropdowns() {
  const url = `https://data.chnm.org/bom/list-deaths`;

  d3.json(url)
    .then((data) => {
      const cause1Dropdown = d3.select("#cause1");
      const cause2Dropdown = d3.select("#cause2");

      // Clear existing options
      cause1Dropdown.selectAll("option").remove();
      cause2Dropdown.selectAll("option:not([value=''])").remove();

      // Add 'All Causes' option to the first dropdown
      cause1Dropdown
        .append("option")
        .attr("value", "All Causes")
        .text("All Causes");

      // Populate both dropdowns with fetched causes
      data.forEach((cause) => {
        cause1Dropdown
          .append("option")
          .attr("value", cause.name)
          .text(cause.name);

        cause2Dropdown
          .append("option")
          .attr("value", cause.name)
          .text(cause.name);
      });

      // Set default values
      cause1Dropdown.property("value", "aged");
      cause2Dropdown.property("value", "consumption");

      // Add event listener to handle dropdown state changes
      cause1Dropdown.on("change", function () {
        const selectedValue = this.value;
        const cause2Dropdown = d3.select("#cause2");

        if (selectedValue === "All Causes") {
          // Disable and clear the comparison dropdown
          cause2Dropdown.property("disabled", true);
          cause2Dropdown.property("value", "");
        } else {
          // Enable the comparison dropdown
          cause2Dropdown.property("disabled", false);
        }
      });
    })
    .catch((error) => {
      console.error("There was an error fetching the list of causes.", error);
    });
}

// Function to populate the year dropdown
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

// Function to fetch data and render the seasonality chart
function fetchDataAndRender(year, cause1, cause2) {
  const url = `https://data.chnm.org/bom/causes?start-year=${year}&end-year=${parseInt(year) + 1}&limit=50000`;

  d3.json(url)
    .then((data) => {
      d3.select("#chart").selectAll("*").remove();
      d3.select(".comparison-legend").remove();

      if (data.length === 0) {
        // Display a message if no data is available
        d3.select("#chart")
          .append("text")
          .attr("x", 480)
          .attr("y", 300)
          .attr("text-anchor", "middle")
          .style("font-size", "18px")
          .style("fill", "#666")
          .text("No data available for the selected year.");
      } else {
        const seasonalityChart = new SeasonalityChart("#chart", data, {
          width: 960,
          height: 500,
        });
        seasonalityChart.selectedCause1 = cause1;
        seasonalityChart.selectedCause2 = cause2 || null;
        seasonalityChart.render();
      }

      // Update the chart title with colored text
      const colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b"];
      let title;
      if (cause1 === "All Causes") {
        title = `Seasonality of <span style="color: ${colors[0]}; font-weight: 600;">All Causes</span> (${year})`;
      } else {
        title = `Seasonality of <span style="color: ${colors[0]}; font-weight: 600;">${cause1}</span>`;
        if (cause2) {
          title += ` compared to <span style="color: ${colors[1]}; font-weight: 600;">${cause2}</span>`;
        }
        title += ` (${year})`;
      }

      d3.select("#chart-title").html(title);
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Initial population of the dropdowns
populateCausesDropdowns();
populateYearDropdown();

// Initial fetch and render
fetchDataAndRender(1648, "aged", "consumption");

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  const cause1 = document.getElementById("cause1").value;
  const cause2 = document.getElementById("cause2").value;

  // Don't pass cause2 if cause1 is "All Causes"
  const finalCause2 = cause1 === "All Causes" ? null : cause2 || null;

  fetchDataAndRender(year, cause1, finalCause2);
});

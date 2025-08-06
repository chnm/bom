import * as d3 from "d3";
import HistogramChart from "./causes-histogram";

// Function to fetch the list of causes and populate the dropdown
function populateCausesDropdown() {
  const url = `https://data.chnm.org/bom/list-deaths`;

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

// Function to fetch data and render the histogram
function fetchDataAndRender(year, cause) {
  const url = `https://data.chnm.org/bom/causes?start-year=${year}&end-year=${year}&limit=9000`;

  d3.json(url)
    .then((data) => {
      d3.select("#chart").selectAll("*").remove();

      if (data.length === 0) {
        // Display a message if no data is available
        d3.select("#chart")
          .append("text")
          .attr("x", 480) // Center the text horizontally
          .attr("y", 300) // Center the text vertically
          .attr("text-anchor", "middle")
          .style("font-size", "24px")
          .style("fill", "red")
          .text("No data available for this year.");
      } else {
        const histogram = new HistogramChart("#chart", data, {
          width: 960,
          height: 500,
        });
        histogram.selectedCause = cause; // Set the selected cause
        histogram.render();
      }

      // Update the chart title
      d3.select("#chart-title").html(
        `Cause of death <span class="underline">${cause}</span> for the year <span class="underline">${year}</span>`,
      );
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Initial population of the causes dropdown
populateCausesDropdown();

// Initial fetch and render
fetchDataAndRender(1668, "aged");

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  const cause = document.getElementById("cause").value;
  fetchDataAndRender(year, cause);
});


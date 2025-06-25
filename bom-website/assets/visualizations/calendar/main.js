import * as d3 from "d3";
import CalendarChart from "./calendar";

// Function to populate the year dropdown with available years
function populateYearDropdown() {
  const url = `https://data.chnm.org/bom/causes`;
  
  d3.json(url)
    .then((data) => {
      // Extract unique years and sort them
      const years = [...new Set(data.map(d => d.year))].sort((a, b) => a - b);
      
      const yearSelect = document.getElementById("year");
      if (!yearSelect) {
        console.error("Year select element not found!");
        return;
      }
      
      yearSelect.innerHTML = ""; // Clear loading option
      
      // Add years as options
      years.forEach(year => {
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

// Function to fetch data and render the histogram
function fetchDataAndRender(year) {
  if (!year) return;
  
  const url = `https://data.chnm.org/bom/causes?start-year=${year}&end-year=${year}`;
  
  d3.json(url)
    .then((data) => {
      d3.select("#chart").selectAll("*").remove();

      if (data.length === 0) {
        // Display a message if no data is available
        d3.select("#chart").append("text")
          .attr("x", 480) // Center the text horizontally
          .attr("y", 300) // Center the text vertically
          .attr("text-anchor", "middle")
          .style("font-size", "24px")
          .style("fill", "red")
          .text("No data available for this year.");
      } else {
        const calendar = new CalendarChart(
          "#chart",
          data,
          { width: 960, height: 2000 }
        );
        calendar.selectedYear = year; // Set the selected year
        calendar.render();
      }
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Initialize the page
populateYearDropdown();

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  fetchDataAndRender(year);
});

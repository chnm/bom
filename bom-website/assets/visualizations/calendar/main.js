import * as d3 from "d3";
import CalendarChart from "./calendar";

// Function to fetch data and render the histogram
function fetchDataAndRender(year) {
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

// Initial fetch and render
fetchDataAndRender(1636);

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const year = document.getElementById("year").value;
  fetchDataAndRender(year);
});

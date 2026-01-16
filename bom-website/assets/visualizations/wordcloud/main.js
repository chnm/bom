import * as d3 from "d3";
import WordCloudChart from "./wordcloud";

// Function to fetch data and render the word cloud
function fetchDataAndRender(startYear, endYear, billType = 'weekly') {
  const url = `https://data.chnm.org/bom/causes?bill-type=${billType}&start-year=${startYear}&end-year=${endYear}`;

  d3.json(url)
    .then((data) => {
      // Extract unique years from the data
      const years = Array.from(new Set(data.map(d => d.year))).sort((a, b) => a - b);
      populateYearDropdowns(years);

      // Clear the existing word cloud
      d3.select("#chart").selectAll("*").remove();

      const wordcloud = new WordCloudChart(
        "#chart",
        { causes: data },
        { width: 960, height: 500 }
      );
      wordcloud.render();
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Populate year dropdowns
function populateYearDropdowns(years) {
  const startYearSelect = document.getElementById("start-year");
  const endYearSelect = document.getElementById("end-year");

  // Clear existing options
  startYearSelect.innerHTML = "";
  endYearSelect.innerHTML = "";

  years.forEach((year) => {
    const optionStart = document.createElement("option");
    optionStart.value = year;
    optionStart.text = year;
    startYearSelect.appendChild(optionStart);

    const optionEnd = document.createElement("option");
    optionEnd.value = year;
    optionEnd.text = year;
    endYearSelect.appendChild(optionEnd);
  });

  // Set default values
  startYearSelect.value = years[0];
  endYearSelect.value = years[years.length - 1];
}

// Initial fetch and render
fetchDataAndRender(1629, 1754);

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const startYear = document.getElementById("start-year").value;
  const endYear = document.getElementById("end-year").value;
  fetchDataAndRender(startYear, endYear);
});

// Add event listener to the reset button
document.getElementById("reset-button").addEventListener("click", () => {
  // Reset the dropdowns to the original values
  document.getElementById("start-year").value = 1629;
  document.getElementById("end-year").value = 1754;
  // Fetch and render the original data
  fetchDataAndRender(1629, 1754);
});
import * as d3 from "d3";
import WordCloudChart from "./wordcloud";

// Function to fetch data and render the word cloud
function fetchDataAndRender(startYear, endYear) {
  const url = `https://data.chnm.org/bom/causes?start-year=${startYear}&end-year=${endYear}&limit=9000`;
  
  d3.json(url)
    .then((data) => {
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

// Initial fetch and render
fetchDataAndRender(1648, 1754);

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const startYear = document.getElementById("start-year").value;
  const endYear = document.getElementById("end-year").value;
  fetchDataAndRender(startYear, endYear);
});

// Add event listener to the reset button
document.getElementById("reset-button").addEventListener("click", () => {
  // Reset the input fields to the original values
  document.getElementById("start-year").value = 1648;
  document.getElementById("end-year").value = 1754;
  // Fetch and render the original data
  fetchDataAndRender(1648, 1754);
});
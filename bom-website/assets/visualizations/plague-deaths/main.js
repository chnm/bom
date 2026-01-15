import * as d3 from "d3";
import DeathsChart from "visualizations/plague-deaths/deaths-bar-chart";

// Load data - Weekly bills only
const urls = [
  "https://data.chnm.org/bom/causes?start-year=1636&end-year=1754&bill-type=weekly",
];

// Once the data is loaded, initialize the visualization.
Promise.all(urls.map((url) => d3.json(url)))
  .then((data) => {
    // Calculate width based on container, with max of 1750px to fit within breakout
    const containerWidth = document.getElementById("row").clientWidth;
    const chartWidth = Math.min(containerWidth - 80, 1750);

    const deathschart = new DeathsChart(
      "#chart",
      { causes: data[0] },
      { width: chartWidth, height: 4000 }
    );
    deathschart.render();
  })
  .catch((error) => {
    console.error("There was an error fetching the data.", error);
  });

import * as d3 from "d3";
import DeathsChart from "visualizations/plague-deaths/deaths-bar-chart";

// Load data
const urls = [
  "https://data.chnm.org/bom/causes?start-year=1648&end-year=1754&limit=9000",
];
const promises = [];
urls.forEach((url) => promises.push(d3.json(url)));

// Once the data is loaded, initialize the visualization.
Promise.all(urls.map((url) => d3.json(url)))
  .then((data) => {
    const deathschart = new DeathsChart(
      "#chart",
      { causes: data[0] },
      { width: 960, height: 2000 }
    );
    deathschart.render();
  })
  .catch((error) => {
    console.error("There was an error fetching the data.", error);
  });

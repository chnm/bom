import * as d3 from 'd3';
import DeathsChart from './deaths-bar-chart';

// Load the data
const urls = [
  'https://data.chnm.org/catholic-dioceses/',
  'https://data.chnm.org/catholic-dioceses/per-decade/',
  'https://data.chnm.org/ne/globe?location=North+America',
];
const promises = [];
urls.forEach((url) => promises.push(d3.json(url)));

// Once all the data is loaded, initialize and render the visualizations
Promise.all(promises)
  .then((data) => {
    const deathsChart = new DeathsChart(
      '#chrono-map',
      { dioceses: data[0], northamerica: data[2] },
      { width: 1000, height: 525 },
    );
    deathsChart.render();

    // Listen for changes to the slider
    d3.select('#year').on('input', function updateViz() {
      const year = this.valueAsNumber;
      deathsChart.update(year);
    });
  });
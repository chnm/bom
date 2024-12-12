import * as d3 from 'd3';
import * as Plot from '@observablehq/plot';
import Visualization from '../common/visualization';

export default class DeathsChart extends Visualization {
  constructor(id, data, dim) {
    const margin = {
      top: 0, right: 40, bottom: 40, left: 10,
    };
    super(id, data, dim, margin);
  }

  // Draw the plot
  render() {
    const aggregatedData = Array.from(
      d3.rollup(
        this.data.causes,
        v => d3.sum(v, d => d.count), // Sum the count for each (year, death) combination
        d => d.year,
        d => d.death
      ),
      ([year, deaths]) => Array.from(deaths, ([death, count]) => ({ year, death, count }))
    ).flat();

    const colorThreshold = d3.scaleThreshold()
      .domain([1600])
      .range(["black", "white"]);

    const plot = Plot.plot({
      padding: 0,
      width: 800,
      height: 4000,
      marginLeft: 150,
      grid: true,
      x: {
        axis: "top",
        label: "Year",
        tickFormat: d3.format("d"), // remove commas
        ticks: 10,
        tickSize: 6,
        tickPadding: 3,
        tickValues: d3.range(d3.min(aggregatedData, d => d.year), d3.max(aggregatedData, d => d.year) + 1)
      },
      y: {label: "Cause"},
      color: {type: "linear", scheme: "Reds"},
      marks: [
        Plot.cell(aggregatedData, {x: "year", y: "death", fill: "count", inset: 0.5}),
        Plot.text(aggregatedData, {
          x: "year", 
          y: "death", 
          text: d => d.count,
          fill: d => colorThreshold(d.count),
          inset: 0.5
        }),
        Plot.axisX({ // Add an additional x-axis at the bottom
          label: "Year",
          tickFormat: d3.format("d"), // remove commas
          ticks: 10,
          tickSize: 6,
          tickPadding: 3,
          tickValues: d3.range(d3.min(aggregatedData, d => d.year), d3.max(aggregatedData, d => d.year) + 1),
          anchor: "bottom"
        })
      ]
    });


    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

  }
}

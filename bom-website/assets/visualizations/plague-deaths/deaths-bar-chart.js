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
    const plot = Plot.plot({
      width: 800,
      height: 1100,
      marginLeft: 150,
      marginBottom: 50,
      x: {
        tickFormat: d3.format("d")
      },
      y: {
        label: 'Cause',
      },
      color: {
        scheme: 'reds',
        reverse: false,
      },
      marks: [Plot.cell(this.data.causes, { x: "year", y: "death", fill: "count" })],
    });


    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

  }
}

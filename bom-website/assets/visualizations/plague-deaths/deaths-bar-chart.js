import * as d3 from 'd3';
import Visualization from '../common/visualization';

// Take in a year and get back the decade.
function getDecade(year) {
  return Math.trunc(year / 10) * 10;
}

export default class DiocesesBarChart extends Visualization {
  constructor(id, data, dim) {
    const margin = {
      top: 0, right: 40, bottom: 40, left: 10,
    };
    super(id, data, dim, margin);
    this.year = d3.select('#year').node().valueAsNumber;
    this.xScale = d3.scaleBand()
      .domain(d3.range(this.data.diocesesByDecade.length))
      .range([0, this.width])
      .padding(0.1);
    this.xAxis = d3.axisBottom()
      .scale(this.xScale)
      .tickValues(this.xScale.domain().filter((d, i) => !((i + 0) % 5)))
      .tickFormat((i) => this.data.diocesesByDecade[i].decade);
    this.yScale = d3.scaleLinear(
      [0, d3.max(this.data.diocesesByDecade, (d) => d.n)],
      [this.height, 0],
    );
    this.yAxis = d3.axisRight()
      .scale(this.yScale)
      .ticks(10);
  }

  // Draw the unchanging parts of the visualization
  render() {
    this.viz
      .append('g')
      .attr('class', 'x axis')
      .attr('transform', `translate(0,${this.height})`)
      .call(this.xAxis);

    this.viz
      .append('g')
      .attr('class', 'y axis')
      .attr('transform', `translate(${this.width},0)`)
      .call(this.yAxis);

    this.viz
      .selectAll('rect')
      .data(this.data.diocesesByDecade)
      .enter()
      .append('rect')
      .attr('x', (d, i) => this.xScale(i))
      .attr('y', (d) => this.yScale(d.n))
      .attr('width', this.xScale.bandwidth())
      .attr('height', (d) => this.yScale(0) - this.yScale(d.n));

    // On first render, draw the stuff that gets updated
    this.update(this.year);
  }

  // Draw the changing parts of the visualization
  update(year) {
    this.viz
      .selectAll('rect')
      .data(this.data.diocesesByDecade)
      .classed('active', false)
      .filter((d) => d.decade === getDecade(year))
      .classed('active', true);
  }
}

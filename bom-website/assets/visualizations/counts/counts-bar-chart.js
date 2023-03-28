import * as d3 from "d3";
import Visualization from "../common/visualization";

export default class PlagueBillsBarChart extends Visualization {
  constructor(el, data, options) {
    const margin = {
      top: 0,
      right: 40,
      bottom: 40,
      left: 10,
    };
    super(el, data, options, margin);

    this.xScale = d3
      .scaleBand()
      .domain(d3.range(this.data.plague.length))
      .range([0, this.width])
      .padding(0.1);

    this.xAxis = d3
      .axisBottom()
      .scale(this.xScale)
      .tickValues(this.xScale.domain())
      .tickFormat((d) => this.data.plague[d].year);

    this.yScale = d3
      .scaleLinear()
      .domain([0, d3.max(this.data.plague, (d) => d.count)])
      .range([this.height, 0]);

    this.yAxis = d3.axisRight().scale(this.yScale).ticks(10);

    this.tooltipRender = (e, d) => {
      const text = `Transcribed bills for <strong>${d.year}</strong>
        <br>Total rows of data: ${d.count}`;
      this.tooltip.html(text);
      this.tooltip.style("visibility", "visible");
    };
  }

  render() {
    this.viz
      .append("g")
      .attr("class", "x axis")
      .attr("transform", `translate(0, ${this.height})`)
      .call(this.xAxis)
      .selectAll("text")
      .attr("y", 0)
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "rotate(90)")
      .style("text-anchor", "start");

    this.viz
      .append("g")
      .attr("class", "y axis")
      .attr("transform", `translate(${this.width},0)`)
      .call(this.yAxis);

    // Remove the loading message.
    d3.select(".loading_rows").remove();

    this.viz
      .selectAll("rect")
      .data(this.data.plague)
      .enter()
      .append("rect")
      .style("fill", "#7f5a83")
      .attr("x", (d, i) => this.xScale(i))
      .attr("y", (d) => this.yScale(d.count))
      .attr("width", this.xScale.bandwidth())
      .attr("height", (d) => this.height - this.yScale(d.count));

    // Add the tooltip.
    this.tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "tooltip")
      .attr("id", "chart-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden");

    this.viz
      .selectAll("rect")
      .on("mouseover", this.tooltipRender)
      .on("mousemove", () => {
        // Show the tooltip to the right of the mouse, unless we are
        // on the rightmost 25% of the browser.
        if (event.clientX / this.width >= 0.75) {
          this.tooltip
            .style("top", `${event.pageY - 10}px`)
            .style(
              "left",
              `${
                event.pageX -
                this.tooltip.node().getBoundingClientRect().width -
                10
              }px`
            );
        } else {
          this.tooltip
            .style("top", `${event.pageY - 10}px`)
            .style("left", `${event.pageX + 10}px`);
        }
      })
      .on("mouseout", () => this.tooltip.style("visibility", "hidden"));
  }
}

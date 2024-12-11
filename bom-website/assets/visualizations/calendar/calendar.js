import * as d3 from 'd3';
import * as Plot from '@observablehq/plot';
import Visualization from '../common/visualization';

export default class CalendarChart extends Visualization {
  constructor(id, data, dim) {
    const margin = {
      top: 0, right: 40, bottom: 40, left: 10,
    };
    super(id, data, dim, margin);
    this.dim = dim;
  }

  // Draw the plot
  render() {
    const data = this.data;
    console.log(data);

    const plot = Plot.plot({
        padding: 0,
        width: this.dim.width,
        height: this.dim.height,
        marginLeft: 120,
        // grid: true,
        x: {
          axis: "top",
          label: "Week Number",
        //   tickFormat: d3.format("d"), // remove commas
          ticks: 10,
          tickSize: 6,
          tickPadding: 3,
          tickValues: d3.range(d3.min(data, d => d.week_no), d3.max(data, d => d.week_no) + 1)
        },
        y: {label: "Cause of Death"},
        color: {type: "linear", scheme: "Reds"},
        marks: [
          Plot.cell(data, {x: "week_no", y: "death", fill: "count", inset: 0.5}),
          Plot.axisX({ // Add an additional x-axis at the bottom
            label: "Week Number",
            // tickFormat: d3.format("d"), // remove commas
            ticks: 10,
            tickSize: 6,
            tickPadding: 3,
            tickValues: d3.range(d3.min(data, d => d.week_no), d3.max(data, d => d.week_no) + 1),
            anchor: "bottom"
          })
        ]
      });

    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

    const tooltip = d3.select("body").append("div")
     .attr("class", "tooltip")
     .style("position", "absolute")
     .style("visibility", "hidden")
     .style("background", "#fff")
     .style("border", "1px solid #ccc")
     .style("padding", "10px")
     .style("border-radius", "4px")
     .style("box-shadow", "0 0 10px rgba(0, 0, 0, 0.1)");
    
     this.svg.selectAll("rect")
        .data(data)
        .on("mouseover", (event, d) => {
        tooltip.style("visibility", "visible")
            .html(`Week number: ${d.week_no}<br>Count: ${d.count}`);
        d3.select(event.currentTarget)
            .style("stroke", "#3E3E32")
            .style("stroke-width", "2px");
        })
     .on("mousemove", (event) => {
        // Show the tooltip to the right of the mouse, unless we are
        // on the rightmost 25% of the browser.
        if (event.clientX / this.width >= 0.75) {
          tooltip
            .style("top", `${event.pageY - 10}px`)
            .style(
              "left",
              `${
                event.pageX -
                tooltip.node().getBoundingClientRect().width -
                10
              }px`
            );
        } else {
          tooltip
            .style("top", `${event.pageY - 10}px`)
            .style("left", `${event.pageX + 10}px`);
        }
      })
     .on("mouseout", () => {
       tooltip.style("visibility", "hidden");
       d3.select(event.currentTarget)
       .style("stroke", null)
       .style("stroke-width", null);
     });
  }
}
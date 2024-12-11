import * as d3 from 'd3';
import * as Plot from '@observablehq/plot';
import Visualization from '../common/visualization';

export default class HistogramChart extends Visualization {
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

    // Filter data based on the selected cause
    const filteredData = data.filter(d => d.death === this.selectedCause);

    // Group data by year, week number, and cause of death
    const groupedData = d3.groups(filteredData, d => d.year, d => d.week_no, d => d.death);

    // Flatten the grouped data for plotting
    const flattenedData = groupedData.flatMap(([year, weeks]) =>
      weeks.flatMap(([week_no, deaths]) =>
        deaths.map(([death, records]) => ({
          year,
          week_no,
          death,
          count: d3.sum(records, d => d.count)
        }))
      )
    );

    // Create the histogram plot
    const plot = Plot.plot({
      marks: [
        Plot.rectY(flattenedData, { x: "week_no", y: "count", }),
        Plot.ruleY([0]),
        Plot.axisY({
          label: "Count",
          tickFormat: d3.format("d"),
        }),
        Plot.axisX({
          label: "Week number",
          tickFormat: d3.format("d"),
        }),
      ],
      width: this.dim.width,
      height: this.dim.height,
      marginRight: 150,
    });

    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

     // Add tooltips
    const tooltip = d3.select("body").append("div")
     .attr("class", "tooltip")
     .style("position", "absolute")
     .style("visibility", "hidden")
     .style("background", "#fff")
     .style("border", "1px solid #ccc")
     .style("padding", "10px")
     .style("border-radius", "4px")
     .style("box-shadow", "0 0 10px rgba(0, 0, 0, 0.1)");

   // Bind data to rect elements and add event listeners for tooltips
   this.svg.selectAll("rect")
     .data(flattenedData)
     .on("mouseover", (event, d) => {
       tooltip.style("visibility", "visible")
         .html(`Week number: ${d.week_no}<br>Count: ${d.count}`);
        d3.select(event.currentTarget)
         .style("fill", "#c75000ff");
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
          .style("fill", "");
     });
  }
}
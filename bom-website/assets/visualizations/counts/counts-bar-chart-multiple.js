import * as d3 from "d3";
import Visualization from "../common/visualization";

export default class PlagueBillsBarChartWeekly extends Visualization {
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
      .domain(d3.range(this.data.plagueByWeek.length))
      .range([0, this.width])
      .padding(0.1);

    // Show years every 5 years to reduce clutter
    const tickIndices = this.xScale.domain().filter((d, i) => {
      const year = this.data.plagueByWeek[d].year;
      return year % 5 === 0; // Show years divisible by 5 (1640, 1645, 1650, etc.)
    });

    this.xAxis = d3
      .axisBottom()
      .scale(this.xScale)
      .tickValues(tickIndices)
      .tickFormat((d) => this.data.plagueByWeek[d].year);

    this.yScale = d3
      .scaleLinear()
      .domain([0, d3.max(this.data.plagueByWeek, (d) => d.weeksCompleted)])
      .range([this.height, 0]);

    this.yAxis = d3.axisRight().scale(this.yScale).ticks(10);

    this.tooltipRender = (e, d) => {
      // tooltip gets data from the stack, not the original data
      // so we need to find the original data
      const originalData = this.data.plagueByWeek.find(
        (item) => item.year === d.data.year,
      );
      const text = `Transcribed bills for <strong>${d.data.year}</strong>
        <br>Total weeks in the data: ${originalData.totalCount}
        <br>Weeks completed: ${originalData.weeksCompleted}`;
      //   const text = ``
      this.tooltip.html(text);
      this.tooltip.style("visibility", "visible");
    };
  }

  render() {
    const stack = d3.stack().keys(["weeksCompleted", "totalCount"])(
      this.data.plagueByWeek,
    );

    console.log("stack", stack);

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
    d3.select(".loading_stack").remove();

    // Render the stacked bars.
    this.viz
      .append("g")
      .selectAll("g")
      // Enter in the stack data = loop key per key = group per group
      .data(stack)
      .enter()
      .append("g")
      .attr("fill", (d) => {
        if (d.key === "weeksCompleted") {
          return "#7f5a83";
        }
        return "#f7f4f3";
      })
      .selectAll("rect")
      // enter a second time = loop subgroup per subgroup to add all rectangles
      .data(function (d) {
        return d;
      })
      .enter()
      .append("rect")
      .attr("x", (d, i) => this.xScale(i))
      .attr("y", (d) => this.yScale(d[1]))
      .attr("height", (d) => this.yScale(d[0]) - this.yScale(d[1]))
      .attr("width", this.xScale.bandwidth());

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
              }px`,
            );
        } else {
          this.tooltip
            .style("top", `${event.pageY - 10}px`)
            .style("left", `${event.pageX + 10}px`);
        }
      })
      .on("mouseout", () => this.tooltip.style("visibility", "hidden"));

    // Add dotted baseline at 52 weeks
    this.viz
      .append("line")
      .attr("class", "baseline-52")
      .attr("x1", 0)
      .attr("x2", this.width)
      .attr("y1", this.yScale(52))
      .attr("y2", this.yScale(52))
      .attr("stroke", "#666")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "3,3");
  }
}

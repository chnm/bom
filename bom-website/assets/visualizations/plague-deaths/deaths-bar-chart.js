import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import Visualization from "../common/visualization";

export default class DeathsChart extends Visualization {
  constructor(id, data, dim) {
    const margin = {
      top: 40,
      right: 40,
      bottom: 60,
      left: 10,
    };
    super(id, data, dim, margin);
    this.dim = dim;
  }

  // Draw the plot
  render() {
    const aggregatedData = Array.from(
      d3.rollup(
        this.data.causes,
        (v) => d3.sum(v, (d) => d.count), // Sum the count for each (year, death) combination
        (d) => d.year,
        (d) => d.name,
      ),
      ([year, deaths]) =>
        Array.from(deaths, ([name, count]) => ({ year, name, count })),
    ).flat();

    const colorThreshold = d3
      .scaleThreshold()
      .domain([5000])
      .range(["black", "white"]);

    // Calculate tick values for every 5 years
    const minYear = d3.min(aggregatedData, (d) => d.year);
    const maxYear = d3.max(aggregatedData, (d) => d.year);
    const startYear = Math.floor(minYear / 5) * 5;
    const yearTicks = d3.range(startYear, maxYear + 1, 5);
    console.log("Year ticks:", yearTicks);

    const plot = Plot.plot({
      padding: 0,
      width: this.dim.width,
      height: this.dim.height,
      marginLeft: 260,
      marginTop: 60,
      marginBottom: 80,
      marginRight: 20,
      grid: true,
      style: {
        fontSize: "16px", // Increase base font size
        ".axis text": {
          fontSize: "18px", // Larger axis text
        },
        ".axis-label": {
          fontSize: "22px", // Even larger axis labels
          fontWeight: "bold",
        },
        ".tick text": {
          fontSize: "16px", // Larger tick text
        },
        ".plot-d-tip": {
          fontSize: "16px",
          background: "rgba(0, 0, 0, 0.8)",
          color: "white",
          padding: "10px",
          borderRadius: "5px",
          textAlign: "left",
          lineHeight: "1.4",
        },
      },
      x: {
        axis: "top",
        label: "Year",
        labelAnchor: "right",
        labelOffset: 80,
        tickFormat: d3.format("d"), // remove commas
        tickSize: 8,
        tickPadding: 12,
        ticks: yearTicks,
        tickRotate: 90,
      },
      y: {
        label: null, // Remove y-axis label
        tickSize: 8,
        tickPadding: 12,
      },
      color: {
        type: "log", // Use log scale for the wide range of values
        scheme: "Reds",
      },
      marks: [
        Plot.cell(aggregatedData, {
          x: "year",
          y: "name",
          fill: "count",
          stroke: "#444",
          strokeOpacity: 0,
          strokeWidth: 1,
        }),
        Plot.tip(
          aggregatedData,
          Plot.pointer({
            x: "year",
            y: "name",
            title: (d) =>
              `Year: ${d.year}\nCause: ${d.name}\nDeaths: ${d.count.toLocaleString()}`,
          }),
        ),
        Plot.axisX({
          // Add an additional x-axis at the bottom
          labelAnchor: "right",
          labelOffset: 80,
          tickFormat: d3.format("d"),
          tickSize: 8,
          tickPadding: 12,
          ticks: yearTicks,
          anchor: "bottom",
          tickRotate: 90,
        }),
      ],
    });

    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

    // Set cursor to pointer on cells and handle label truncation
    setTimeout(() => {
      const cells = d3.selectAll("rect.plot-cell");
      cells.style("cursor", "pointer");

      // Create tooltip div for labels
      let labelTooltip = d3.select("body").select(".label-tooltip");
      if (labelTooltip.empty()) {
        labelTooltip = d3.select("body").append("div")
          .attr("class", "label-tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.9)")
          .style("color", "white")
          .style("padding", "8px 12px")
          .style("border-radius", "4px")
          .style("font-size", "14px")
          .style("pointer-events", "none")
          .style("opacity", 0)
          .style("z-index", 1000)
          .style("max-width", "300px")
          .style("word-wrap", "break-word");
      }

      // Truncate y-axis labels and add custom tooltips
      const maxLabelLength = 25; // Maximum characters before truncation
      d3.selectAll('g[aria-label="y-axis tick label"] text').each(function() {
        const textElement = d3.select(this);
        const fullText = textElement.text();

        // Truncate if too long
        if (fullText.length > maxLabelLength) {
          textElement.text(fullText.substring(0, maxLabelLength) + "...");

          // Add hover events for custom tooltip
          textElement
            .style("cursor", "help")
            .on("mouseover", function(event) {
              labelTooltip
                .html(fullText)
                .style("opacity", 1)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
            })
            .on("mousemove", function(event) {
              labelTooltip
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
            })
            .on("mouseout", function() {
              labelTooltip.style("opacity", 0);
            });
        }
      });
    }, 100);
  }
}

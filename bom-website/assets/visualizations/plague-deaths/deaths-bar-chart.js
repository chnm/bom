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
  }

  // Draw the plot
  render() {
    const aggregatedData = Array.from(
      d3.rollup(
        this.data.causes,
        (v) => d3.sum(v, (d) => d.count), // Sum the count for each (year, death) combination
        (d) => d.year,
        (d) => d.death,
      ),
      ([year, deaths]) =>
        Array.from(deaths, ([death, count]) => ({ year, death, count })),
    ).flat();

    const colorThreshold = d3
      .scaleThreshold()
      .domain([5000])
      .range(["black", "white"]);

    const plot = Plot.plot({
      padding: 0,
      width: 1200, // Reduce width to fit in div
      height: 4000,
      marginLeft: 180,
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
        ticks: 10,
        tickSize: 8,
        tickPadding: 12,
        tickValues: d3.range(
          d3.min(aggregatedData, (d) => d.year),
          d3.max(aggregatedData, (d) => d.year) + 1,
        ),
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
          y: "death",
          fill: "count",
          stroke: "#444",
          strokeOpacity: 0,
          strokeWidth: 1,
        }),
        Plot.tip(
          aggregatedData,
          Plot.pointer({
            x: "year",
            y: "death",
            title: (d) =>
              `Year: ${d.year}\nCause: ${d.death}\nDeaths: ${d.count.toLocaleString()}`,
          }),
        ),
        Plot.axisX({
          // Add an additional x-axis at the bottom
          labelAnchor: "right",
          labelOffset: 80,
          tickFormat: d3.format("d"),
          ticks: 10,
          tickSize: 8,
          tickPadding: 12,
          tickValues: d3.range(
            d3.min(aggregatedData, (d) => d.year),
            d3.max(aggregatedData, (d) => d.year) + 1,
          ),
          anchor: "bottom",
          tickRotate: 90,
        }),
      ],
    });

    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

    // Set cursor to pointer on cells
    setTimeout(() => {
      const cells = d3.selectAll("rect.plot-cell");
      cells.style("cursor", "pointer");
    }, 100);
  }
}

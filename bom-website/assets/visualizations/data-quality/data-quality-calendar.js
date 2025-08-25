import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import Visualization from "../common/visualization";

export default class DataQualityCalendar extends Visualization {
  constructor(id, data, dim, qualityType = "missing") {
    const margin = {
      top: 0,
      right: 40,
      bottom: 40,
      left: 10,
    };
    super(id, data, dim, margin);
    this.dim = dim;
    this.qualityType = qualityType; // 'illegible' or 'missing'
  }

  // Process the data to calculate data quality status by parish and week
  processData(data) {
    // Group data by parish name and week_number (bills data only)
    const parishWeekStats = d3.group(
      data,
      (d) => d.name,
      (d) => d.week_number,
    );

    const processedData = [];

    parishWeekStats.forEach((weekData, parishName) => {
      weekData.forEach((records, weekNumber) => {
        const totalRecords = records.length;
        const qualityIssueRecords = records.filter(
          (d) => d[this.qualityType] === true,
        ).length;

        // Determine categorical status
        let status, statusValue, statusColor;
        if (totalRecords === 0) {
          status = "No Data";
          statusValue = 0;
          statusColor = "#f3f4f6";
        } else if (qualityIssueRecords === 0) {
          status = "Good";
          statusValue = 1;
          statusColor = "#10b981";
        } else if (qualityIssueRecords < totalRecords) {
          status = "Partial Issues";
          statusValue = 2;
          statusColor = "#f59e0b";
        } else {
          status = "All Issues";
          statusValue = 3;
          statusColor = "#ef4444";
        }

        processedData.push({
          parish: parishName,
          week_number: parseInt(weekNumber),
          total_records: totalRecords,
          quality_issue_records: qualityIssueRecords,
          quality_type: this.qualityType,
          status: status,
          status_value: statusValue,
          status_color: statusColor,
        });
      });
    });

    return processedData;
  }

  // Get color scheme for categorical data
  getColorScale() {
    return d3
      .scaleOrdinal()
      .domain(["No Data", "Good", "Partial Issues", "All Issues"])
      .range(["#f3f4f6", "#10b981", "#f59e0b", "#ef4444"]); // Gray, Green, Amber, Red
  }

  // Draw the plot
  render() {
    const processedData = this.processData(this.data);
    console.log("Processed data quality data:", processedData);
    console.log("Raw data:", this.data);

    if (processedData.length === 0) {
      console.error("No processed data available");
      d3.select(".loading_chart").remove();
      d3.select("#chart")
        .append("div")
        .style("text-align", "center")
        .style("padding", "60px 20px")
        .style("font-size", "18px")
        .style("color", "#dc2626")
        .text("No data available after processing.");
      return;
    }

    // Get unique parishes for height calculation
    const uniqueParishes = [...new Set(processedData.map((d) => d.parish))];
    const qualityTypeLabel =
      this.qualityType === "illegible" ? "Illegibility" : "Missing Data";
    const colorScale = this.getColorScale();

    // Use the height passed from main.js
    console.log(
      `Parishes: ${uniqueParishes.length}, Using height: ${this.dim.height}`,
    );

    const plot = Plot.plot({
      padding: 0,
      width: this.dim.width,
      height: this.dim.height, // Use passed height
      marginLeft: 200, // More space for parish names
      marginBottom: 60,
      x: {
        axis: "top",
        label: "Week Number",
        tickSize: 6,
        tickPadding: 3,
        ticks: 10,
        tickValues: d3.range(
          d3.min(processedData, (d) => d.week_number),
          d3.max(processedData, (d) => d.week_number) + 1,
        ),
      },
      y: {
        label: "Parish",
        tickSize: 6,
        fontSize: 12,
      },
      marks: [
        Plot.cell(processedData, {
          x: "week_number",
          y: "parish",
          fill: "status_color",
          inset: 0.5,
        }),
        Plot.axisX({
          label: "Week Number",
          tickSize: 6,
          tickPadding: 3,
          ticks: 10,
          tickValues: d3.range(
            d3.min(processedData, (d) => d.week_number),
            d3.max(processedData, (d) => d.week_number) + 1,
          ),
          anchor: "bottom",
        }),
      ],
    });

    // Remove loading indicator and add the plot
    d3.select(".loading_chart").remove();
    this.svg.node().append(plot);

    // Add enhanced tooltip functionality
    this.addTooltipInteraction(processedData);
  }

  addTooltipInteraction(data) {
    // Create tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "data-quality-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background", "#fff")
      .style("border", "1px solid #ccc")
      .style("padding", "12px")
      .style("border-radius", "6px")
      .style("box-shadow", "0 4px 12px rgba(0, 0, 0, 0.15)")
      .style("font-size", "14px")
      .style("line-height", "1.4")
      .style("max-width", "300px");

    const qualityTypeLabel =
      this.qualityType === "illegible" ? "Illegible" : "Missing";
    const recordsLabel =
      this.qualityType === "illegible"
        ? "Illegible Records"
        : "Missing Records";

    // Add interaction to cells
    this.svg
      .selectAll("rect")
      .data(data)
      .on("mouseover", (event, d) => {
        const content = `
          <div style="margin-bottom: 8px;">
            <strong>${d.parish}</strong>
          </div>
          <div style="margin-bottom: 4px;">
            <strong>Week:</strong> ${d.week_number}
          </div>
          <div style="margin-bottom: 4px;">
            <strong>Status:</strong> ${d.status}
          </div>
          <div style="margin-bottom: 4px;">
            <strong>${recordsLabel}:</strong> ${d.quality_issue_records}
          </div>
          <div style="margin-bottom: 4px;">
            <strong>Total Records:</strong> ${d.total_records}
          </div>
        `;

        tooltip.style("visibility", "visible").html(content);

        d3.select(event.currentTarget)
          .style("stroke", "#d97706")
          .style("stroke-width", "2px");
      })
      .on("mousemove", (event) => {
        // Position tooltip intelligently
        const tooltipWidth = tooltip.node().getBoundingClientRect().width;
        const windowWidth = window.innerWidth;

        let leftPosition = event.pageX + 10;
        if (event.clientX + tooltipWidth + 20 > windowWidth) {
          leftPosition = event.pageX - tooltipWidth - 10;
        }

        tooltip
          .style("top", `${event.pageY - 10}px`)
          .style("left", `${leftPosition}px`);
      })
      .on("mouseout", (event) => {
        tooltip.style("visibility", "hidden");
        d3.select(event.currentTarget)
          .style("stroke", null)
          .style("stroke-width", null);
      });
  }
}

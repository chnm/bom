import * as d3 from 'd3';
import * as Plot from '@observablehq/plot';
import Visualization from '../common/visualization';

export default class SeasonalityChart extends Visualization {
  constructor(id, data, dim) {
    const margin = {
      top: 20, right: 40, bottom: 60, left: 60,
    };
    super(id, data, dim, margin);
    this.dim = dim;
    this.selectedCause1 = null;
    this.selectedCause2 = null;
  }

  processSeasonalData() {
    const data = this.data;
    
    // Filter data based on selected causes
    let filteredData;
    if (this.selectedCause1 === 'All Causes') {
      // Show all causes when 'All Causes' is selected
      filteredData = data;
    } else {
      // Filter by specific causes
      filteredData = data.filter(d => {
        return d.death === this.selectedCause1 || 
               (this.selectedCause2 && d.death === this.selectedCause2);
      });
    }

    // Group by cause and week number, summing counts
    const weeklyData = d3.rollup(
      filteredData,
      v => d3.sum(v, d => d.count),
      d => d.death,
      d => d.week_number
    );

    // Convert to array format for plotting
    const plotData = [];
    weeklyData.forEach((weeks, cause) => {
      weeks.forEach((count, week) => {
        plotData.push({
          cause,
          week: +week,
          count,
          // Determine season based on week number
          season: this.getSeasonFromWeek(+week)
        });
      });
    });

    return plotData;
  }

  getSeasonFromWeek(weekNumber) {
    // Approximate seasons based on week numbers (52 weeks per year)
    // Week 1-13: Winter -> Spring
    // Week 14-26: Spring -> Summer  
    // Week 27-39: Summer -> Fall
    // Week 40-52: Fall -> Winter
    if (weekNumber >= 1 && weekNumber <= 13) return 'Winter/Spring';
    if (weekNumber >= 14 && weekNumber <= 26) return 'Spring/Summer';
    if (weekNumber >= 27 && weekNumber <= 39) return 'Summer/Fall';
    if (weekNumber >= 40 && weekNumber <= 52) return 'Fall/Winter';
    return 'Unknown';
  }

  render() {
    const plotData = this.processSeasonalData();
    
    if (plotData.length === 0) {
      this.renderNoDataMessage();
      return;
    }

    // Create color scale for causes
    const causes = [...new Set(plotData.map(d => d.cause))];
    const colorScale = d3.scaleOrdinal()
      .domain(causes)
      .range(['#3b82f6', '#ef4444', '#10b981', '#f59e0b']);

    // Create the plot marks
    const marks = [
      Plot.ruleY([0]),
      Plot.axisX({
        label: "Week of Year",
        tickFormat: d3.format("d"),
      }),
      Plot.axisY({
        label: "Number of Deaths",
        tickFormat: d3.format("d"),
      })
    ];

    // Add line marks for each cause
    causes.forEach(cause => {
      const causeData = plotData.filter(d => d.cause === cause);
      marks.push(
        Plot.line(causeData, {
          x: "week",
          y: "count",
          stroke: colorScale(cause),
          strokeWidth: 2,
          title: d => `${d.cause}\nWeek ${d.week}: ${d.count} deaths`
        })
      );
      marks.push(
        Plot.dot(causeData, {
          x: "week",
          y: "count",
          fill: colorScale(cause),
          r: 3,
          title: d => `${d.cause}\nWeek ${d.week}: ${d.count} deaths`
        })
      );
    });

    // Create the plot
    const plot = Plot.plot({
      marks,
      width: this.dim.width,
      height: this.dim.height,
      marginBottom: 60,
      marginLeft: 60,
      marginRight: 80,
      style: {
        fontSize: "12px"
      }
    });

    // Clear previous content and add new plot
    d3.select(".loading_chart").remove();
    this.svg.selectAll("*").remove();
    this.svg.node().appendChild(plot);

    // Always add legend
    this.addLegend(causes, colorScale);
  }

  addLegend(causes, colorScale) {
    // Remove existing legend
    d3.select("#chart").selectAll(".comparison-legend").remove();
    
    // Add legend container
    const legend = d3.select("#chart")
      .insert("div", "svg")
      .attr("class", "comparison-legend")
      .style("justify-content", "center")
      .style("margin", "20px 0");

    causes.forEach(cause => {
      const legendItem = legend.append("div")
        .attr("class", "legend-item");
      
      legendItem.append("div")
        .attr("class", "legend-color")
        .style("background-color", colorScale(cause));
      
      legendItem.append("span")
        .style("font-weight", "500")
        .text(cause);
    });
  }

  renderNoDataMessage() {
    d3.select(".loading_chart").remove();
    this.svg.selectAll("*").remove();
    
    this.svg.append("text")
      .attr("x", this.dim.width / 2)
      .attr("y", this.dim.height / 2)
      .attr("text-anchor", "middle")
      .style("font-size", "18px")
      .style("fill", "#666")
      .text("No data available for the selected criteria.");
  }
}
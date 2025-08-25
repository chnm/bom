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

    // Filter out data with week_number above 54
    filteredData = filteredData.filter(d => d.week_number <= 54);

    // Group by cause and week number, summing counts
    const weeklyData = d3.rollup(
      filteredData,
      v => d3.sum(v, d => d.count),
      d => d.death,
      d => d.week_number
    );

    // Convert to array format with proper interpolation
    const plotData = [];
    weeklyData.forEach((weeks, cause) => {
      // Get sorted weeks with data
      const realWeeks = Array.from(weeks.keys()).sort((a, b) => a - b);
      
      // Create array of all weeks 1-52 with interpolation
      for (let week = 1; week <= 52; week++) {
        const hasData = weeks.has(week);
        let count = 0;
        let isInterpolated = false;
        
        if (hasData) {
          count = weeks.get(week);
        } else {
          // Linear interpolation between nearest data points
          const prevWeek = realWeeks.filter(w => w < week).pop();
          const nextWeek = realWeeks.find(w => w > week);
          
          if (prevWeek !== undefined && nextWeek !== undefined) {
            // Interpolate between two points
            const prevCount = weeks.get(prevWeek);
            const nextCount = weeks.get(nextWeek);
            const ratio = (week - prevWeek) / (nextWeek - prevWeek);
            count = prevCount + ratio * (nextCount - prevCount);
            isInterpolated = true;
          }
          // If no surrounding data points, count stays 0
        }
        
        plotData.push({
          cause,
          week,
          count,
          hasData,
          isInterpolated,
          season: this.getSeasonFromWeek(week)
        });
      }
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

    // Create consistent color scale for causes
    const causes = [...new Set(plotData.map(d => d.cause))];
    
    // Create consistent color mapping based on selection order
    const colorScale = d3.scaleOrdinal();
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'];
    
    // Assign colors based on selection priority: selectedCause1 gets first color, selectedCause2 gets second
    const colorMap = new Map();
    if (this.selectedCause1 && this.selectedCause1 !== 'All Causes') {
      colorMap.set(this.selectedCause1, colors[0]);
    }
    if (this.selectedCause2) {
      colorMap.set(this.selectedCause2, colors[1]);
    }
    
    // For 'All Causes', assign colors in alphabetical order
    if (this.selectedCause1 === 'All Causes') {
      const sortedCauses = causes.sort();
      sortedCauses.forEach((cause, i) => {
        colorMap.set(cause, colors[i % colors.length]);
      });
    }
    
    // Fill in any remaining causes
    let colorIndex = this.selectedCause1 === 'All Causes' ? 0 : (this.selectedCause2 ? 2 : 1);
    causes.forEach(cause => {
      if (!colorMap.has(cause)) {
        colorMap.set(cause, colors[colorIndex % colors.length]);
        colorIndex++;
      }
    });
    
    colorScale.domain(causes).range(causes.map(cause => colorMap.get(cause)));

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

    // Add line marks for each cause with different styles for gaps
    causes.forEach(cause => {
      const causeData = plotData.filter(d => d.cause === cause);
      
      // Create separate segments for solid (real data) and dashed (interpolated) lines
      const solidSegments = [];
      const dashedSegments = [];
      let currentSolid = [];
      let currentDashed = [];
      
      for (let i = 0; i < causeData.length - 1; i++) {
        const point = causeData[i];
        const nextPoint = causeData[i + 1];
        
        // Determine if this line segment should be solid or dashed
        const isSegmentInterpolated = point.isInterpolated || nextPoint.isInterpolated;
        
        if (isSegmentInterpolated) {
          // End any current solid segment
          if (currentSolid.length > 1) {
            solidSegments.push([...currentSolid]);
          }
          currentSolid = [];
          
          // Add to dashed segment
          if (currentDashed.length === 0) currentDashed.push(point);
          currentDashed.push(nextPoint);
        } else {
          // End any current dashed segment
          if (currentDashed.length > 1) {
            dashedSegments.push([...currentDashed]);
          }
          currentDashed = [];
          
          // Add to solid segment
          if (currentSolid.length === 0) currentSolid.push(point);
          currentSolid.push(nextPoint);
        }
      }
      
      // Add any remaining segments
      if (currentSolid.length > 1) {
        solidSegments.push(currentSolid);
      }
      if (currentDashed.length > 1) {
        dashedSegments.push(currentDashed);
      }
      
      // Draw solid line segments
      solidSegments.forEach(segment => {
        marks.push(
          Plot.line(segment, {
            x: "week",
            y: "count",
            stroke: colorScale(cause),
            strokeWidth: 2,
            title: d => `${d.cause}\nWeek ${d.week}: ${d.count.toFixed(1)} deaths`
          })
        );
      });
      
      // Draw dashed line segments
      dashedSegments.forEach(segment => {
        marks.push(
          Plot.line(segment, {
            x: "week",
            y: "count",
            stroke: colorScale(cause),
            strokeWidth: 2,
            strokeDasharray: "4,4",
            strokeOpacity: 0.7,
            title: d => `${d.cause}\nWeek ${d.week}: ${d.count.toFixed(1)} deaths (interpolated)`
          })
        );
      });
      
      // Add dots only for actual data points
      const realData = causeData.filter(d => d.hasData);
      marks.push(
        Plot.dot(realData, {
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
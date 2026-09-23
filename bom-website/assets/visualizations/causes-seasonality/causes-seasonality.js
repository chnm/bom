import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style, textWidth } from "../common/responsive";

const COLORS = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b"];

// Draws weekly counts of one or two causes (or all causes) into `container`:
// a legend, then a line per cause, dashed where weeks are interpolated.
export default function renderSeasonality(container, data, cause1, cause2) {
  const plotData = processSeasonalData(data, cause1, cause2);

  if (plotData.length === 0) {
    container.innerHTML = '<p class="viz-message">No data available for the selected criteria.</p>';
    return;
  }

  const causes = [...new Set(plotData.map((d) => d.cause))];
  const colorOf = colorScale(causes, cause1, cause2);
  const width = container.clientWidth;

  const marks = [
    Plot.ruleY([0]),
    Plot.axisX({ label: "Week of Year", tickFormat: d3.format("d"), ticks: width < 500 ? 6 : undefined }),
    Plot.axisY({ label: "Number of Deaths", tickFormat: d3.format("d") }),
  ];

  causes.forEach((cause) => {
    const causeData = plotData.filter((d) => d.cause === cause);
    const { solid, dashed } = splitSegments(causeData);
    const stroke = colorOf(cause);

    solid.forEach((segment) => {
      marks.push(Plot.line(segment, { x: "week", y: "count", stroke, strokeWidth: 2 }));
    });
    dashed.forEach((segment) => {
      marks.push(
        Plot.line(segment, { x: "week", y: "count", stroke, strokeWidth: 2, strokeDasharray: "4,4", strokeOpacity: 0.7 }),
      );
    });

    // Dots only for actual data points
    marks.push(Plot.dot(causeData.filter((d) => d.hasData), { x: "week", y: "count", fill: stroke, r: 3 }));
  });

  marks.push(
    Plot.tip(
      plotData.filter((d) => d.hasData || d.isInterpolated),
      Plot.pointer({
        x: "week",
        y: "count",
        title: (d) =>
          d.isInterpolated
            ? `${d.cause}\nWeek ${d.week}: ${d.count.toFixed(1)} deaths (interpolated)`
            : `${d.cause}\nWeek ${d.week}: ${d.count} ${d.count === 1 ? "death" : "deaths"}`,
      }),
    ),
  );

  const maxCount = d3.max(plotData, (d) => d.count);
  const plot = Plot.plot({
    width,
    height: width < 500 ? 320 : 420,
    marginLeft: textWidth([d3.format("d")(maxCount)]) + 14,
    marginRight: 12,
    marginBottom: 40,
    style,
    marks,
  });

  // Past four causes the colors repeat, so a legend can't tell them apart
  if (causes.length <= COLORS.length) container.replaceChildren(legend(causes, colorOf), plot);
  else container.replaceChildren(plot);
}

function legend(causes, colorOf) {
  const el = document.createElement("div");
  el.className = "comparison-legend";
  for (const cause of causes) {
    const item = document.createElement("div");
    item.className = "legend-item";
    const swatch = document.createElement("div");
    swatch.className = "legend-color";
    swatch.style.backgroundColor = colorOf(cause);
    const label = document.createElement("span");
    label.textContent = cause;
    item.append(swatch, label);
    el.append(item);
  }
  return el;
}

// selectedCause1 gets the first color and selectedCause2 the second;
// 'All Causes' assigns colors in alphabetical order.
function colorScale(causes, cause1, cause2) {
  const colorMap = new Map();
  if (cause1 && cause1 !== "All Causes") colorMap.set(cause1, COLORS[0]);
  if (cause2) colorMap.set(cause2, COLORS[1]);
  if (cause1 === "All Causes") {
    [...causes].sort().forEach((cause, i) => colorMap.set(cause, COLORS[i % COLORS.length]));
  }

  let colorIndex = cause1 === "All Causes" ? 0 : cause2 ? 2 : 1;
  causes.forEach((cause) => {
    if (!colorMap.has(cause)) {
      colorMap.set(cause, COLORS[colorIndex % COLORS.length]);
      colorIndex++;
    }
  });
  return (cause) => colorMap.get(cause);
}

// Split a cause's weekly series into solid runs (real data) and dashed runs
// (touching an interpolated week).
function splitSegments(causeData) {
  const solid = [];
  const dashed = [];
  let currentSolid = [];
  let currentDashed = [];

  for (let i = 0; i < causeData.length - 1; i++) {
    const point = causeData[i];
    const nextPoint = causeData[i + 1];

    if (point.isInterpolated || nextPoint.isInterpolated) {
      if (currentSolid.length > 1) solid.push(currentSolid);
      currentSolid = [];
      if (currentDashed.length === 0) currentDashed.push(point);
      currentDashed.push(nextPoint);
    } else {
      if (currentDashed.length > 1) dashed.push(currentDashed);
      currentDashed = [];
      if (currentSolid.length === 0) currentSolid.push(point);
      currentSolid.push(nextPoint);
    }
  }
  if (currentSolid.length > 1) solid.push(currentSolid);
  if (currentDashed.length > 1) dashed.push(currentDashed);
  return { solid, dashed };
}

function processSeasonalData(data, cause1, cause2) {
  // 'All Causes' shows everything; otherwise just the selected causes
  let filteredData =
    cause1 === "All Causes" ? data : data.filter((d) => d.death === cause1 || (cause2 && d.death === cause2));

  filteredData = filteredData.filter((d) => d.week_number <= 54);

  // Group by cause and week number, summing counts
  const weeklyData = d3.rollup(
    filteredData,
    (v) => d3.sum(v, (d) => d.count),
    (d) => d.death,
    (d) => d.week_number,
  );

  const plotData = [];
  weeklyData.forEach((weeks, cause) => {
    const realWeeks = Array.from(weeks.keys()).sort((a, b) => a - b);

    // Every week 1-52, linearly interpolating gaps between real data points
    for (let week = 1; week <= 52; week++) {
      const hasData = weeks.has(week);
      let count = 0;
      let isInterpolated = false;

      if (hasData) {
        count = weeks.get(week);
      } else {
        const prevWeek = realWeeks.filter((w) => w < week).pop();
        const nextWeek = realWeeks.find((w) => w > week);
        if (prevWeek !== undefined && nextWeek !== undefined) {
          const prevCount = weeks.get(prevWeek);
          const nextCount = weeks.get(nextWeek);
          const ratio = (week - prevWeek) / (nextWeek - prevWeek);
          count = prevCount + ratio * (nextCount - prevCount);
          isInterpolated = true;
        }
        // With no surrounding data points, count stays 0
      }

      plotData.push({ cause, week, count, hasData, isInterpolated });
    }
  });

  return plotData;
}

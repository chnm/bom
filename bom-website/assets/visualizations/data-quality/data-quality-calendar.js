import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style, textWidth } from "../common/responsive";

const ROW = 18; // height of one parish row
const MIN_CELL = 16; // narrowest a week column may get before the grid scrolls sideways
const MARGIN_Y = 36; // room for the week axes above and below

// Quality status of each parish in each week. qualityType is 'illegible' or 'missing'.
function processData(data, qualityType) {
  const processedData = [];

  d3.group(data, (d) => d.name, (d) => d.week_number).forEach((weekData, parish) => {
    weekData.forEach((records, weekNumber) => {
      const totalRecords = records.length;
      const qualityIssueRecords = records.filter((d) => d[qualityType] === true).length;

      // Colors match the key in content/visualizations/data-quality/index.md.
      let status, statusColor;
      if (qualityIssueRecords === 0) {
        status = "Good";
        statusColor = "#047857";
      } else if (qualityIssueRecords < totalRecords) {
        status = "Partial Issues";
        statusColor = "#b45309";
      } else {
        status = "All Issues";
        statusColor = "#b91c1c";
      }

      processedData.push({
        parish,
        week_number: parseInt(weekNumber),
        total_records: totalRecords,
        quality_issue_records: qualityIssueRecords,
        status,
        status_color: statusColor,
      });
    });
  });

  return processedData;
}

// Draws the parish × week grid into `container`: a fixed column of parish names
// beside a grid of weekly cells that scrolls sideways when narrow.
export default function renderDataQuality(container, data, qualityType = "missing") {
  const cells = processData(data, qualityType);
  if (cells.length === 0) {
    container.innerHTML = '<p class="viz-message is-error">No data available after processing.</p>';
    return;
  }

  const parishes = d3.sort(new Set(cells.map((d) => d.parish)));
  const weeks = d3.sort(new Set(cells.map((d) => d.week_number)));
  const recordsLabel = qualityType === "illegible" ? "Illegible Records" : "Missing Records";

  const labelsW = textWidth(parishes) + 14;
  const frameW = container.clientWidth;
  const gridW = Math.max(frameW - labelsW, weeks.length * MIN_CELL + 8);
  const height = parishes.length * ROW + MARGIN_Y * 2;

  const y = { domain: parishes, label: null };
  // Label every week when there's room, else every 2nd, 3rd… so labels never overlap
  const every = Math.ceil(24 / (gridW / weeks.length));
  const weekAxis = {
    ticks: weeks.filter((w, i) => i % every === 0),
    tickSize: 4,
    tickPadding: 3,
    label: "Week Number",
    labelAnchor: "left",
  };

  const labels = Plot.plot({
    width: labelsW,
    height,
    marginTop: MARGIN_Y,
    marginBottom: MARGIN_Y,
    marginLeft: labelsW,
    marginRight: 0,
    style,
    y,
    marks: [Plot.axisY({ tickSize: 0, tickPadding: 6 })],
  });

  const grid = Plot.plot({
    width: gridW,
    height,
    marginTop: MARGIN_Y,
    marginBottom: MARGIN_Y,
    marginLeft: 0,
    marginRight: 8,
    padding: 0,
    style,
    x: { type: "band", domain: weeks, axis: null },
    y: { ...y, axis: null },
    marks: [
      Plot.axisX({ ...weekAxis, anchor: "top" }),
      Plot.axisX({ ...weekAxis, anchor: "bottom" }),
      Plot.cell(cells, {
        x: "week_number",
        y: "parish",
        fill: "status_color",
        inset: 0.5,
        tip: true,
        title: (d) =>
          `${d.parish}\nWeek: ${d.week_number}\nStatus: ${d.status}\n` +
          `${recordsLabel}: ${d.quality_issue_records}\nTotal Records: ${d.total_records}`,
      }),
    ],
  });

  const labelsCol = document.createElement("div");
  labelsCol.className = "chart-labels";
  labelsCol.append(labels);

  const scroller = document.createElement("div");
  scroller.className = "chart-scroll";
  scroller.tabIndex = 0; // lets keyboard users scroll the grid
  scroller.setAttribute("role", "region");
  scroller.setAttribute("aria-label", "Data quality by parish and week; scroll sideways for more weeks");
  scroller.append(grid);

  const body = document.createElement("div");
  body.className = "chart-body";
  body.append(labelsCol, scroller);

  container.replaceChildren(body);
  container.classList.toggle("is-scrollable", gridW > frameW - labelsW);
}

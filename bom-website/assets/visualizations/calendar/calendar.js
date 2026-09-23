import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style, textWidth } from "../common/responsive";

const ROW = 18; // height of one cause row
const MIN_CELL = 14; // narrowest a week column may get before the grid scrolls sideways
const MARGIN_Y = 36; // room for the week axes above and below

// Draws the calendar into `container`: a color legend, then a fixed column of
// cause names beside a grid of weekly cells that scrolls sideways when narrow.
export default function renderCalendar(container, data) {
  const cells = data.filter((d) => d.week_number !== 90);
  const causes = d3.sort(new Set(cells.map((d) => d.death)));
  const weeks = d3.sort(new Set(cells.map((d) => d.week_number)), d3.ascending);
  const maxCount = d3.max(cells, (d) => d.count);

  const labelsW = textWidth(causes) + 14;
  const frameW = container.clientWidth;
  const gridW = Math.max(frameW - labelsW, weeks.length * MIN_CELL + 8);
  const height = causes.length * ROW + MARGIN_Y * 2;

  const y = { domain: causes, label: null };
  const color = { type: "linear", scheme: "Reds", domain: [0, maxCount] };
  const weekAxis = { tickSize: 4, tickPadding: 3, label: "Week", labelAnchor: "left" };

  const legend = Plot.legend({
    color: { ...color, label: "Deaths in the week" },
    style,
    width: 300,
    marginLeft: 12,
  });

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
    color,
    marks: [
      Plot.axisX({ ...weekAxis, anchor: "top" }),
      Plot.axisX({ ...weekAxis, anchor: "bottom" }),
      Plot.cell(cells, {
        x: "week_number",
        y: "death",
        fill: "count",
        inset: 0.5,
        tip: true,
        title: (d) => `${d.death}\nWeek ${d.week_number}: ${d3.format(",")(d.count)} ${d.count === 1 ? "death" : "deaths"}`,
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
  scroller.setAttribute("aria-label", "Weekly counts by cause; scroll sideways for more weeks");
  scroller.append(grid);

  const body = document.createElement("div");
  body.className = "chart-body";
  body.append(labelsCol, scroller);

  container.replaceChildren(legend, body);
  container.classList.toggle("is-scrollable", gridW > frameW - labelsW);
}

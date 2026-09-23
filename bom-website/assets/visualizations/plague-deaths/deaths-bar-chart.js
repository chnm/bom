import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style, textWidth } from "../common/responsive";

const ROW = 16; // height of one cause row
const MIN_CELL = 4.5; // narrowest a year column may get before the grid scrolls sideways
const MARGIN_Y = 36; // room for the year axes above and below
const MAX_LABEL = 25; // longer cause names are cut short; the full name shows on hover

const truncate = (s) => (s.length > MAX_LABEL ? s.slice(0, MAX_LABEL) + "…" : s);

// Sum the counts for each (year, cause) pair.
export function aggregate(causes) {
  return Array.from(
    d3.rollup(causes, (v) => d3.sum(v, (d) => d.count), (d) => d.year, (d) => d.name),
    ([year, deaths]) => Array.from(deaths, ([name, count]) => ({ year, name, count })),
  ).flat();
}

// Draws the heatmap into `container`: a fixed column of cause names beside a
// grid of yearly cells that scrolls sideways when narrow.
export default function renderDeaths(container, data) {
  const causes = d3.sort(new Set(data.map((d) => d.name)));
  // Every year in the span, so years with no bills show as gaps rather than vanish
  const years = d3.range(d3.min(data, (d) => d.year), d3.max(data, (d) => d.year) + 1);

  const labelsW = textWidth(causes.map(truncate)) + 14;
  const frameW = container.clientWidth;
  const gridW = Math.max(frameW - labelsW, years.length * MIN_CELL + 16);
  const height = causes.length * ROW + MARGIN_Y * 2;

  // A tick every 5 years, or every 10 when the columns are too narrow for that
  const step = (gridW / years.length) * 5 < 40 ? 10 : 5;
  const yearAxis = {
    ticks: years.filter((y) => y % step === 0),
    tickFormat: "d",
    tickSize: 4,
    tickPadding: 3,
    label: "Year",
    labelAnchor: "left",
  };
  const y = { domain: causes, label: null };

  const labels = Plot.plot({
    width: labelsW,
    height,
    marginTop: MARGIN_Y,
    marginBottom: MARGIN_Y,
    marginLeft: labelsW,
    marginRight: 0,
    style,
    y,
    marks: [Plot.axisY({ tickSize: 0, tickPadding: 6, tickFormat: truncate, title: (d) => d })],
  });

  const grid = Plot.plot({
    width: gridW,
    height,
    marginTop: MARGIN_Y,
    marginBottom: MARGIN_Y,
    marginLeft: 0,
    marginRight: 16,
    padding: 0,
    grid: true,
    style,
    x: { type: "band", domain: years, axis: null },
    y: { ...y, axis: null },
    color: { type: "log", scheme: "Reds" },
    marks: [
      Plot.axisX({ ...yearAxis, anchor: "top" }),
      Plot.axisX({ ...yearAxis, anchor: "bottom" }),
      Plot.cell(data, {
        x: "year",
        y: "name",
        fill: "count",
        tip: true,
        title: (d) => `Year: ${d.year}\nCause: ${d.name}\nDeaths: ${d.count.toLocaleString()}`,
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
  scroller.setAttribute("aria-label", "Deaths by cause and year; scroll sideways for more years");
  scroller.append(grid);

  const body = document.createElement("div");
  body.className = "chart-body";
  body.append(labelsCol, scroller);

  container.replaceChildren(body);
  container.classList.toggle("is-scrollable", gridW > frameW - labelsW);
}

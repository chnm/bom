import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import renderFacets from "./facets";
import { redrawOnResize } from "../common/responsive";

const chart = document.getElementById("facets");
const plagueColor = "rgb(239, 48, 84)";
const burialColor = "rgb(150, 173, 200)";

let tidy = null; // one row per parish, year and count type
let current = ["original", "burials"]; // [data format, count type] on screen

chart.innerHTML = '<p class="viz-message">Loading data…</p>';

d3.json("https://data.chnm.org/bom/statistics?type=parish-yearly")
  .then((data) => {
    tidy = Object.keys(data[1])
      .slice(2)
      .flatMap((count) =>
        data.map((d) => ({
          year: d.year,
          parish_name: d.parish_name,
          count,
          amount: d[count],
        })),
      );
    renderPage(...current);
  })
  .catch((error) => {
    console.error("Error fetching data:", error);
    chart.innerHTML =
      '<p class="viz-message is-error">Error loading data. Please try again later.</p>';
  });

function renderPage(format, count) {
  current = [format, count];
  if (!tidy) return;

  const data =
    count === "plague"
      ? tidy.filter((d) => d.count === "total_plague")
      : count === "both"
        ? tidy
        : tidy.filter((d) => d.count === "total_buried");
  const color = count === "both" ? "count" : count === "plague" ? plagueColor : burialColor;
  const bar = { x: "year", y: "amount", fill: color, stroke: color };

  renderFacets(chart, {
    data,
    keys: Array.from(new Set(tidy.map((d) => d.parish_name))),
    key: (d) => d.parish_name,
    years: [1665, 1701, 1730],
    color:
      count === "both"
        ? {
            type: "categorical",
            domain: ["total_plague", "total_buried"],
            range: [plagueColor, burialColor],
            tickFormat: (d) => (d === "total_plague" ? "Plague deaths" : "Burials"),
            legend: true,
          }
        : null,
    title:
      count === "plague"
        ? "Total plague deaths for each parish"
        : count === "both"
          ? "Total plague and burial deaths for each parish"
          : "Total burials for each parish",
    subtitle:
      format === "normalized"
        ? "Data has been normalized"
        : format === "log10(x+1)"
          ? "Data has been transformed by log10(x+1)"
          : "Original data",
    marks: (rows, facet, peak = peakYear(rows)) => [
      format === "normalized"
        ? Plot.barY(rows, { ...bar, ...facet, y: (d) => d.amount / peak })
        : format === "log10(x+1)"
          ? Plot.barY(rows, { ...bar, ...facet, y: (d) => Math.log10(d.amount + 1) })
          : Plot.barY(rows, { ...bar, ...facet }),
    ],
  });
}

// A parish's largest yearly total, summing the stacked counts. Dividing by it
// puts the busiest year at 1 even when plague and burials are stacked.
function peakYear(rows) {
  const totals = d3.rollup(rows, (v) => d3.sum(v, (d) => d.amount), (d) => d.year);
  return d3.max(totals.values()) || 1;
}

redrawOnResize(chart, () => renderPage(...current));

document.getElementById("update-button").addEventListener("click", () => {
  const format = document.querySelector('input[name="data-format"]:checked')?.value;
  const count = document.querySelector('input[name="count-type"]:checked')?.value;
  renderPage(format, count);
});

document.getElementById("reset-button").addEventListener("click", () => {
  document.getElementById("original").checked = true;
  document.getElementById("burials").checked = true;
  renderPage("original", "burials");
});

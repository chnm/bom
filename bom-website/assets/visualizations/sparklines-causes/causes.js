import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import renderFacets from "../sparklines/facets";
import { redrawOnResize } from "../common/responsive";

// Sparklines of yearly deaths per cause, shared by the weekly and general bills
// pages. `field` is the property holding the cause name in the API response.
export default function causeSparklines(url, field) {
  const chart = document.getElementById("facets");
  let draw = null; // redraws the chart on screen, kept for resizes
  let loading = null; // the tidied data, fetched once and reused on Update/Reset

  function fetchDataAndRender(dataFormat) {
    if (!loading) {
      chart.innerHTML = '<p class="viz-message">Loading data…</p>';
      loading = d3
        .json(url)
        .then((data) => tidyFormat(data, field).sort((a, b) => a.death.localeCompare(b.death)));
      loading.catch(() => (loading = null)); // let a later click retry
    }
    loading
      .then((tidy) => {
        const noPlague = document.getElementById("plague").checked;
        const rows = noPlague ? tidy.filter((d) => d.death != "plague") : tidy;
        draw = () => makeGraphs(dataFormat, noPlague, rows);
        draw();
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        chart.innerHTML =
          '<p class="viz-message is-error">Error loading data. Please try again later.</p>';
      });
  }

  function makeGraphs(dataFormat, noPlague, data) {
    const bar = { x: "year", y: "count", fill: "red", stroke: "red" };
    renderFacets(chart, {
      data,
      keys: Array.from(new Set(data.map((d) => d.death))),
      key: (d) => d.death,
      years: [1665, 1700, 1730],
      title: noPlague ? "Causes of Death (without Plague)" : "Causes of Death",
      subtitle:
        dataFormat === "normalized"
          ? "Data has been normalized"
          : dataFormat === "log10(x+1)"
            ? "Data has been transformed by log10(x+1)"
            : "Original data",
      marks: (rows, facet) => [
        dataFormat === "normalized"
          ? Plot.barY(rows, Plot.normalizeY("mean", { ...bar, ...facet }))
          : dataFormat === "log10(x+1)"
            ? Plot.barY(rows, { ...bar, ...facet, y: (d) => Math.log10(d.count + 1) })
            : Plot.barY(rows, { ...bar, ...facet }),
      ],
    });
  }

  redrawOnResize(chart, () => draw && draw());

  document.getElementById("update-button").addEventListener("click", () => {
    const dataFormat = document.querySelector('input[name="data-format"]:checked')?.value;
    fetchDataAndRender(dataFormat);
  });

  document.getElementById("reset-button").addEventListener("click", () => {
    document.getElementById("original").checked = true;
    document.getElementById("plague").checked = false;
    fetchDataAndRender("original");
  });

  fetchDataAndRender("original");
}

// Sum counts per year and cause.
function tidyFormat(data, field) {
  const totals = d3.rollup(
    data,
    (v) => d3.sum(v, (d) => d.count),
    (d) => d.year,
    (d) => d[field],
  );
  return Array.from(totals, ([year, causes]) =>
    Array.from(causes, ([death, count]) => ({ year, death, count })),
  ).flat();
}

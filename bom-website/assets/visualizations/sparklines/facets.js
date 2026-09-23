import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style } from "../common/responsive";

// Shared by the parish and causes-of-death sparkline pages.

const MIN_FACET = 150; // narrowest a facet may get before we drop a column
const MAX_COLS = 5;
const GAP = 8; // space between facets, matches .facet-grid gap
const PLOT_H = 64; // one facet's chart, including its year ticks
const compact = new Intl.NumberFormat("en", { notation: "compact" }).format; // 150K fits the margin

// Draws a grid of small bar charts into `container`, one per key, at the
// container's real width. Each facet is its own plot with its own y scale, so a
// small parish's shape is as visible as a large one's; all share the same years.
// The number of columns follows the width, so text never shrinks.
//
// `marks(rows, facet)` returns the marks for one facet's rows; spread `facet`
// into each mark's options to give it the shared tip.
export default function renderFacets(
  container,
  { data, keys, key, years, title, subtitle, color, marks },
) {
  const width = container.clientWidth;
  const cols = Math.max(1, Math.min(MAX_COLS, Math.floor((width + GAP) / (MIN_FACET + GAP))));
  const facetW = Math.floor((width - GAP * (cols - 1)) / cols);

  const byKey = d3.group(data, key);
  const x = { domain: d3.sort(new Set(data.map((d) => d.year))), axis: null };
  const facet = { tip: { format: { x: "d" } } };

  const head = document.createElement("div");
  head.className = "facet-head";
  head.innerHTML = `<h4></h4><p class="viz-hint"></p>`;
  head.querySelector("h4").textContent = title;
  head.querySelector("p").textContent = `${subtitle}. Each chart has its own vertical scale.`;
  if (color) head.append(Plot.legend({ color, style }));

  const grid = document.createElement("div");
  grid.className = "facet-grid";
  grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

  for (const k of keys) {
    const figure = document.createElement("figure");
    figure.className = "facet";
    const caption = document.createElement("figcaption");
    caption.textContent = caption.title = k; // full name on hover when truncated
    figure.append(
      caption,
      Plot.plot({
        width: facetW,
        height: PLOT_H,
        marginTop: 4,
        marginRight: 6,
        marginBottom: 18,
        marginLeft: 36,
        style,
        color: color && { ...color, legend: false },
        x,
        y: { ticks: 2, tickFormat: compact, label: null, nice: true },
        marks: [
          ...marks(byKey.get(k) ?? [], facet),
          // Ticks sit away from the edges so they never run into the next facet.
          Plot.axisX({ ticks: years, tickSize: 3, tickFormat: "", label: null }),
          Plot.frame({ stroke: "currentColor", strokeOpacity: 0.25 }),
        ],
      }),
    );
    grid.append(figure);
  }

  container.replaceChildren(head, grid);
}

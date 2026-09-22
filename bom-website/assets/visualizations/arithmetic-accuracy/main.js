import * as d3 from "d3";
import * as Plot from "@observablehq/plot";

const DATA_URL = "/data/arithmetic-accuracy/data.json";
const COLORS = {
  positive: "#c44e35",
  positiveLight: "#f2ddd5",
  negative: "#087e8b",
  negativeLight: "#d8ecee",
  exact: "#f7f1e6",
  missing: "#d9dde0",
  ink: "#27231f",
  muted: "#6d665e",
  grid: "#ded8cf",
};

const root = document.querySelector("#arithmetic-explorer");
const status = document.querySelector("#explorer-status");
const errorBox = document.querySelector("#explorer-error");
const countSelect = document.querySelector("#count-type");
const scopeSelect = document.querySelector("#data-scope");
const yearSelect = document.querySelector("#detail-year");

const query = new URLSearchParams(window.location.search);
const state = {
  countType: ["buried", "plague"].includes(query.get("count"))
    ? query.get("count")
    : "buried",
  scope: ["all", "legible"].includes(query.get("scope"))
    ? query.get("scope")
    : "all",
  year: Number(query.get("year")) || 1665,
};

let dataset;
let resizeTimer;

function differenceLabel(value) {
  if (value === 0) return "Exact match";
  if (value > 0) return `Printed subtotal larger by ${d3.format(",")(value)}`;
  return `Parish sum larger by ${d3.format(",")(Math.abs(value))}`;
}

function updateUrl() {
  const next = new URLSearchParams();
  next.set("count", state.countType);
  next.set("scope", state.scope);
  next.set("year", state.year);
  window.history.replaceState({}, "", `${window.location.pathname}?${next}`);
}

function plotWidth(selector) {
  return Math.max(640, Math.floor(document.querySelector(selector).clientWidth));
}

function replacePlot(selector, plot, label) {
  const container = document.querySelector(selector);
  container.replaceChildren(plot);
  plot.setAttribute("role", "img");
  plot.setAttribute("aria-label", label);
}

function summaryCard(label, value, note = "") {
  return `<div class="summary-card"><span>${label}</span><strong>${value}</strong>${note ? `<small>${note}</small>` : ""}</div>`;
}

function setSummary(selector, cards) {
  document.querySelector(selector).innerHTML = cards.join("");
}

function syncControls() {
  countSelect.value = state.countType;
  scopeSelect.value = state.scope;
}

function availableYears() {
  const rows = dataset.weekly.filter(
    (row) => row.count_type === state.countType
      && (state.scope === "all" || row.legible),
  );
  return Array.from(new Set(rows.map((row) => row.year))).sort(d3.ascending);
}

function populateYears() {
  const years = availableYears();
  if (!years.includes(state.year)) {
    state.year = years.includes(1665) ? 1665 : years[0];
  }
  yearSelect.replaceChildren(...years.map((year) => {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    return option;
  }));
  yearSelect.value = state.year;
}

function weeklyColorScale(rows) {
  const transformed = rows
    .map((row) => Math.log1p(Math.abs(row.difference)))
    .filter(Number.isFinite)
    .sort(d3.ascending);
  const ceiling = d3.quantile(transformed, 0.98) || 1;
  const positive = d3.scaleLinear()
    .domain([0, ceiling])
    .range([COLORS.positiveLight, COLORS.positive])
    .clamp(true);
  const negative = d3.scaleLinear()
    .domain([0, ceiling])
    .range([COLORS.negativeLight, COLORS.negative])
    .clamp(true);
  return (row) => {
    if (!row.observation) return COLORS.missing;
    if (row.difference === 0) return COLORS.exact;
    const magnitude = Math.log1p(Math.abs(row.difference));
    return row.difference > 0 ? positive(magnitude) : negative(magnitude);
  };
}

function renderWeeklyOverview() {
  const allRows = dataset.weekly.filter((row) => row.count_type === state.countType);
  const visibleRows = allRows.filter((row) => state.scope === "all" || row.legible);
  const visibleByWeek = new Map(
    visibleRows.map((row) => [`${row.year}-${row.week_number}`, row]),
  );
  const allByWeek = new Map(
    allRows.map((row) => [`${row.year}-${row.week_number}`, row]),
  );
  const grid = [];
  for (let year = dataset.metadata.year_min; year <= dataset.metadata.year_max; year += 1) {
    for (let week = 1; week <= 55; week += 1) {
      const key = `${year}-${week}`;
      const observation = visibleByWeek.get(key);
      const original = allByWeek.get(key);
      grid.push({
        year,
        week_number: week,
        observation: Boolean(observation),
        excluded: Boolean(original && !observation),
        difference: observation ? observation.difference : null,
        subtotal_sum: observation ? observation.subtotal_sum : null,
        parish_sum: observation ? observation.parish_sum : null,
        legible: observation ? observation.legible : false,
      });
    }
  }
  const color = weeklyColorScale(visibleRows);
  const title = state.countType === "buried" ? "burial" : "plague";
  document.querySelector("#weekly-overview-title").textContent =
    `Weekly ${title} differences, ${state.scope === "all" ? "all comparable bills" : "legible bills only"}`;

  const plot = Plot.plot({
    width: plotWidth("#weekly-overview"),
    height: 470,
    marginLeft: 58,
    marginBottom: 52,
    style: { fontSize: "12px", background: "transparent" },
    x: {
      label: "Year",
      domain: [dataset.metadata.year_min, dataset.metadata.year_max + 1],
      ticks: d3.range(1640, dataset.metadata.year_max + 1, 10).map((year) => year + 0.5),
      tickFormat: (value) => String(Math.floor(value)),
    },
    y: {
      label: "Week number",
      domain: [1, 56],
      ticks: [1, ...d3.range(5, 56, 5)].map((week) => week + 0.5),
      tickFormat: (value) => String(Math.floor(value)),
    },
    marks: [
      Plot.rect(grid, {
        x: "year",
        y: "week_number",
        interval: 1,
        fill: color,
        inset: 0.18,
        title: (row) => {
          if (!row.observation) {
            return `${row.year}, week ${row.week_number}\n${row.excluded ? "Excluded because the week contains an illegible value" : "No comparable observation"}`;
          }
          return `${row.year}, week ${row.week_number}\nPrinted subtotal: ${d3.format(",")(row.subtotal_sum)}\nParish sum: ${d3.format(",")(row.parish_sum)}\n${differenceLabel(row.difference)}\n${row.legible ? "Entire week legible" : "Contains an illegible value"}`;
        },
        tip: true,
      }),
      Plot.rect([state.year], {
        x1: (year) => year,
        x2: (year) => year + 1,
        y1: 1,
        y2: 56,
        fill: "none",
        stroke: COLORS.ink,
        strokeWidth: 2,
        pointerEvents: "none",
      }),
      Plot.frame({ stroke: COLORS.grid }),
    ],
  });
  plot.style.cursor = "pointer";
  plot.addEventListener("click", () => {
    if (!plot.value || plot.value.year === state.year) return;
    state.year = plot.value.year;
    yearSelect.value = state.year;
    renderWeeklyOverview();
    renderWeeklyDetail();
    updateUrl();
  });
  replacePlot(
    "#weekly-overview",
    plot,
    `Heatmap of weekly ${title} arithmetic differences from ${dataset.metadata.year_min} to ${dataset.metadata.year_max}`,
  );

  const errors = visibleRows.filter((row) => row.arithmetic_error);
  const exact = visibleRows.length - errors.length;
  const coverage = 100 * visibleRows.length / ((dataset.metadata.year_max - dataset.metadata.year_min + 1) * 55);
  setSummary("#weekly-summary", [
    summaryCard("Comparable weeks", d3.format(",")(visibleRows.length)),
    summaryCard("Arithmetic errors", d3.format(",")(errors.length), `${d3.format(".1f")(100 * errors.length / visibleRows.length)}% of comparable weeks`),
    summaryCard("Exact matches", d3.format(",")(exact), `${d3.format(".1f")(100 * exact / visibleRows.length)}% of comparable weeks`),
    summaryCard("Calendar coverage", `${d3.format(".1f")(coverage)}%`, "Missing weeks remain explicit"),
  ]);
}

function renderWeeklyDetail() {
  const rows = dataset.weekly
    .filter((row) => row.count_type === state.countType
      && row.year === state.year
      && (state.scope === "all" || row.legible))
    .sort((a, b) => d3.ascending(a.week_number, b.week_number));
  const title = state.countType === "buried" ? "Burial" : "Plague";
  document.querySelector("#weekly-detail-title").textContent = `${title} differences in ${state.year}`;

  const nonzero = rows.filter((row) => row.difference !== 0);
  const exact = rows.filter((row) => row.difference === 0);
  const plot = Plot.plot({
    width: plotWidth("#weekly-detail"),
    height: 360,
    marginLeft: 72,
    marginBottom: 52,
    style: { fontSize: "12px", background: "transparent" },
    x: { domain: [1, 55], label: "Week number", ticks: 11 },
    y: {
      type: "symlog",
      constant: 5,
      ticks: 6,
      grid: true,
      label: "Printed subtotal minus parish sum",
    },
    marks: [
      Plot.ruleY([0], { stroke: COLORS.ink }),
      Plot.ruleX(nonzero, {
        x: "week_number",
        y1: 0,
        y2: "difference",
        strokeWidth: 5,
        stroke: (row) => row.difference > 0 ? COLORS.positive : COLORS.negative,
      }),
      Plot.dot(exact, {
        x: "week_number",
        y: "difference",
        r: 3.2,
        fill: COLORS.ink,
      }),
      Plot.tip(rows, Plot.pointerX({
        x: "week_number",
        y: "difference",
        title: (row) => `Week ${row.week_number}\n${row.difference === 0 ? `Exact match: ${d3.format(",")(row.subtotal_sum)}` : `Printed subtotal: ${d3.format(",")(row.subtotal_sum)}\nParish sum: ${d3.format(",")(row.parish_sum)}\n${differenceLabel(row.difference)}`}\n${row.legible ? "Entire week legible" : "Contains an illegible value"}`,
      })),
    ],
  });
  replacePlot(
    "#weekly-detail",
    plot,
    `${title} arithmetic differences for each comparable week in ${state.year}`,
  );

  const tableBody = document.querySelector("#weekly-table-body");
  tableBody.replaceChildren(...rows.map((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.week_number}</td><td>${d3.format(",")(row.subtotal_sum)}</td><td>${d3.format(",")(row.parish_sum)}</td><td class="${row.difference > 0 ? "positive-value" : row.difference < 0 ? "negative-value" : ""}">${d3.format("+,")(row.difference)}</td><td>${row.legible ? "Yes" : "No"}</td>`;
    return tr;
  }));
}

function render() {
  if (!dataset) return;
  syncControls();
  populateYears();
  renderWeeklyOverview();
  renderWeeklyDetail();
  updateUrl();
  status.textContent = "Visualization ready. Hover or focus chart marks for exact values.";
}

countSelect.addEventListener("change", () => {
  state.countType = countSelect.value;
  render();
});

scopeSelect.addEventListener("change", () => {
  state.scope = scopeSelect.value;
  render();
});

yearSelect.addEventListener("change", () => {
  state.year = Number(yearSelect.value);
  renderWeeklyOverview();
  renderWeeklyDetail();
  updateUrl();
});

window.addEventListener("resize", () => {
  window.clearTimeout(resizeTimer);
  resizeTimer = window.setTimeout(render, 180);
});

d3.json(DATA_URL)
  .then((loaded) => {
    dataset = loaded;
    document.querySelector("#snapshot-label").textContent =
      `${dataset.metadata.dataset}; repository revision ${dataset.metadata.dataset_ref.slice(0, 12)}`;
    root.setAttribute("aria-busy", "false");
    render();
  })
  .catch((error) => {
    console.error("Unable to load arithmetic-accuracy data", error);
    root.setAttribute("aria-busy", "false");
    status.classList.add("is-hidden");
    errorBox.classList.remove("is-hidden");
    errorBox.textContent = "The archived visualization data could not be loaded. Please try again later or use one of the CSV downloads.";
  });


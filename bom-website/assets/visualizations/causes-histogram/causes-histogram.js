import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style, textWidth } from "../common/responsive";

const HEIGHT = 400;

// Draws weekly counts of one cause into `container` as a bar per week.
export default function renderHistogram(container, data, cause) {
  const filtered = data.filter((d) => d.death === cause);

  // Sum counts per year, week and cause
  const weekly = d3
    .flatRollup(filtered, (v) => d3.sum(v, (d) => d.count), (d) => d.year, (d) => d.week_number, (d) => d.death)
    .map(([year, week_number, death, count]) => ({ year, week_number, death, count }));

  const width = container.clientWidth;
  const marginLeft = textWidth(weekly.map((d) => d.count)) + 12;

  // Label every week if they fit, otherwise every 2nd, 5th or 10th week
  const weeks = d3.sort(new Set(weekly.map((d) => d.week_number)), d3.ascending);
  const step = (width - marginLeft - 8) / weeks.length;
  const every = [1, 2, 5, 10].find((n) => n * step >= textWidth(weeks) + 6) ?? 20;

  const plot = Plot.plot({
    width,
    height: HEIGHT,
    marginLeft,
    marginRight: 8,
    marginBottom: 40,
    style,
    marks: [
      Plot.rectY(weekly, {
        x: "week_number",
        y: "count",
        tip: true,
        title: (d) => `Week number: ${d.week_number}\nCount: ${d.count}`,
      }),
      Plot.ruleY([0]),
      Plot.axisY({ label: "Count", tickFormat: d3.format("d") }),
      Plot.axisX({
        label: "Week number",
        tickFormat: d3.format("d"),
        ticks: weeks.filter((w) => w % every === 0),
      }),
    ],
  });

  container.replaceChildren(plot);
}

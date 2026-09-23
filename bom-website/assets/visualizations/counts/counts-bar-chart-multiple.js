import * as d3 from "d3";
import * as Plot from "@observablehq/plot";
import { chartStyle as style, textWidth } from "../common/responsive";

const TICK_STEPS = [5, 10, 20, 25, 50]; // years between x labels, thinned as the chart narrows

// Draws one bar per year into `container`: the full bar is the weeks in the
// data, filled by the weeks transcribed, with a dotted line at 52 weeks.
export default function renderCounts(container, data) {
  const width = container.clientWidth;
  const years = data.map((d) => d.year);
  const marginLeft = 8;
  const marginRight = textWidth(["52"]) + 14; // y axis sits on the right

  // Thin the year labels until each fits in the space between them
  const step = (width - marginLeft - marginRight) / years.length;
  const labelW = textWidth(["0000"]) + 10;
  const every = TICK_STEPS.find((n) => n * step >= labelW) ?? 100;

  const plot = Plot.plot({
    width,
    height: width < 600 ? 300 : 420,
    marginLeft,
    marginRight,
    marginBottom: 32,
    style,
    x: {
      type: "band",
      domain: years,
      padding: 0.1,
      label: null,
      ticks: years.filter((y) => y % every === 0),
      tickFormat: "d",
    },
    y: { axis: "right", domain: [0, d3.max(data, (d) => Math.max(d.totalCount, d.weeksCompleted))], label: null },
    marks: [
      Plot.barY(data, { x: "year", y: "totalCount", fill: "#f7f4f3" }),
      Plot.barY(data, { x: "year", y: (d) => d.weeksCompleted || 0, fill: "#7f5a83" }),
      Plot.ruleY([52], { stroke: "#666", strokeDasharray: "3,3" }),
      Plot.tip(
        data,
        Plot.pointerX({
          x: "year",
          y: "totalCount",
          title: (d) =>
            `Transcribed bills for ${d.year}\nTotal weeks in the data: ${d.totalCount}\nWeeks completed: ${d.weeksCompleted}`,
        }),
      ),
    ],
  });

  container.replaceChildren(plot);
}

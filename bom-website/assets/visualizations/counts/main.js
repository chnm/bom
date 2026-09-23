import * as d3 from "d3";
import renderCounts from "./counts-bar-chart-multiple";
import { redrawOnResize } from "../common/responsive";

const chart = document.getElementById("barchart-multiple");

d3.json("https://data.chnm.org/bom/statistics?type=yearly")
  .then((data) => {
    d3.select(".loading_stack").remove();
    renderCounts(chart, data);
    // Redraw at the new width when the chart's box changes size
    redrawOnResize(chart, () => renderCounts(chart, data));
  })
  .catch((error) => console.error("Error fetching data:", error));

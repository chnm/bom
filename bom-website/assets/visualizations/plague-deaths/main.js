import * as d3 from "d3";
import renderDeaths, { aggregate } from "./deaths-bar-chart";
import { redrawOnResize } from "../common/responsive";

// Weekly bills only
const url = "https://data.chnm.org/bom/causes?start-year=1636&end-year=1754&bill-type=weekly";
const chart = document.getElementById("chart");

d3.json(url)
  .then((causes) => {
    const data = aggregate(causes);
    d3.select(".loading_chart").remove();
    renderDeaths(chart, data);
    redrawOnResize(chart, () => renderDeaths(chart, data));
  })
  .catch((error) => {
    console.error("There was an error fetching the data.", error);
  });

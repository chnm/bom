import * as d3 from "d3";
import PlagueBillsBarChartWeekly from "./counts-bar-chart-multiple";

d3.json("https://data.chnm.org/bom/statistics?type=yearly")
  .then((data) => {
    const chart = new PlagueBillsBarChartWeekly(
      "#barchart-multiple",
      { plagueByWeek: data },
      { width: 960, height: 500 }
    );
    chart.render();
  })
  .catch((error) => console.error("Error fetching data:", error));

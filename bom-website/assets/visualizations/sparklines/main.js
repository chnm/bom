import * as d3 from "d3";
import * as Plot from '@observablehq/plot';

//original fetch
fetchDataAndRender("original", "burials");

//fetches data and renders the sparklines graphs
function fetchDataAndRender(dataFormat, countType) {
    d3.json('https://data.chnm.org/bom/statistics?type=parish-yearly')
        .then((data) => {
            const tidy = Object.keys(data[1]).slice(2).flatMap((count) => data.map(d => ({year: d.year, parish_name: d.parish_name, count, amount: d[count]})))
            d3.select("#facets").selectAll("*").remove();
            makeGraphs(dataFormat, countType, tidy)

        });

}

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
    //get data format value
    const dataButtons = document.querySelectorAll('input[name="data-format"]');
    let dataFormat = undefined;
    for (const dataButton of dataButtons) {
        if (dataButton.checked) {
            dataFormat = dataButton.value;
            break;
        }
    }

    //get count type value
    const countButtons = document.querySelectorAll('input[name="count-type"]');
    let countType = undefined;
    for (const countButton of countButtons) {
        if (countButton.checked) {
            countType = countButton.value;
            break;
        }
    }
    fetchDataAndRender(dataFormat, countType);
  });
  
  
  // Add event listener to the reset button
  document.getElementById("reset-button").addEventListener("click", () => {
    const allRadioButtons = document.querySelectorAll('input[type="radio"]');
    // Reset each radio button to its original state
    for(var i=0;i<allRadioButtons.length;i++)
      // 6 buttons, 0 = original data, 3 = burials 
      if (i===0 || i===3) {
            allRadioButtons[i].checked = true;
        }
        else {
            allRadioButtons[i].checked = false;
      }
    
    console.log('Reset to default values');

    // Fetch and render the data in the original format
    fetchDataAndRender("original", "burials");
  });

  function makeGraphs(format, count, tidy){
    const plot = Plot.plot((() => {
        const n = 5; // number of facet columns
        const keys = Array.from(d3.union(tidy.map((d) => d.parish_name)));
        const index = new Map(keys.map((key, i) => [key, i]));
        const fx = (key) => index.get(key) % n;
        const fy = (key) => Math.floor(index.get(key) / n);
        return {
          height: 2500,
          width: 1300,
          axis: null,
          color: {legend: count === "both" ? true :false},
          style: {fontSize: 13},
          y: {insetTop: 10},
          fx: {padding: 0.03},
          title: count === 'plague' ? "Total plague deaths for each parish" : count === 'both' ? "Total plague and burial deaths for each parish" : "Total burials for each parish",
          subtitle: format === 'normalized' ? "Data has been normalized" : format === 'log10(x+1)' ? "Data has been transformed by log10(x+1)" : "Original data",
          tip: true,
          marks: [
            format === 'normalized' ?
            Plot.barY(count === 'plague' ? tidy.filter(d => d.count === "total_plague") : count === "both" ? tidy : tidy.filter(d => d.count === "total_buried"), Plot.normalizeY( 'extent', {
              x: "year",
              y: "amount",
              fx: (d) => fx(d.parish_name),
              fy: (d) => fy(d.parish_name), 
              stroke: count === "both" ? "count" :"blue",
              fill: count === "both" ? "count" :"blue",
              title: (d) =>
                `${d.parish_name} \n year: ${d.year} \n amount: ${d.amount}` // tooltip
            })) : format === 'log10(x+1)' ?
            Plot.barY(count === 'plague' ? tidy.filter(d => d.count === "total_plague") : count === "both" ? tidy : tidy.filter(d => d.count === "total_buried"), {
              x: "year",
              y: d => Math.log10(d.amount + 1),
              fx: (d) => fx(d.parish_name),
              fy: (d) => fy(d.parish_name), 
              stroke: count === "both" ? "count" :"blue",
              fill: count === "both" ? "count" :"blue",
              title: (d) =>
                `${d.parish_name} \n year: ${d.year} \n amount: ${d.amount}` // tooltip
            }) :
            Plot.barY(count === 'plague' ? tidy.filter(d => d.count === "total_plague") : count === "both" ? tidy : tidy.filter(d => d.count === "total_buried"), {
              x: "year",
              y: "amount",
              fx: (d) => fx(d.parish_name),
              fy: (d) => fy(d.parish_name), 
              stroke: count === "both" ? "count" :"blue",
              fill: count === "both" ? "count" :"blue",
              title: (d) =>
                `${d.parish_name} \n year: ${d.year} \n amount: ${d.amount}` // tooltip
            }       ),
            Plot.axisX({ticks: [1636, 1665, 1701, 1730, 1752], tickFormat: "", tickRotate: 50, tickPadding: 5, labelOffset: 42}),
            Plot.axisY({labelArrow: "none"}),
            Plot.text(keys, {fx, fy, frameAnchor: "top-left", dx: 6, dy: 2}),
            Plot.frame()
          ]
        };
      })())
    let chart = document.getElementById("facets")
    //chart.removeChild(chart.firstChild)
    chart.append(plot)
  }
import * as d3 from "d3";
import * as Plot from '@observablehq/plot';

//original fetch
fetchDataAndRender("original")
//fetches data and renders the sparklines graphs - Weekly bills only
function fetchDataAndRender(dataFormat) {
    d3.json("https://data.chnm.org/bom/causes?start-year=1648&end-year=1754&bill-type=weekly")
      .then((data) => {
        //format data into tidy format for facetting
        const tidy = tidyFormat(data)

        //sort data alphabetically
        let sortedResult = [...tidy].sort((a, b) => {
          return a.death.localeCompare(b.death);
        });

        //check if "remove plague" is checked; if so remove plague from tidy and sorted data
        //make the graphs
        let checkbox = document.getElementById('plague')
        let noPlague = sortedResult.filter((d) => d.death != "plague")
        d3.select("#facets").selectAll("*").remove();
        if (checkbox.checked ){
          makeGraphs(dataFormat, checkbox, noPlague)
        } else {
          makeGraphs(dataFormat, checkbox, sortedResult)
        }
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
  fetchDataAndRender(dataFormat);
});
  
  
  // Add event listener to the reset button
document.getElementById("reset-button").addEventListener("click", () => {
  const allRadioButtons = document.querySelectorAll('input[type="radio"]');
  // Reset each radio button to its original state
  for(var i=0;i<allRadioButtons.length;i++)
    // 6 buttons, 0 = original data
    if (i===0) {
      allRadioButtons[i].checked = true;
    }
    else {
      allRadioButtons[i].checked = false;
    }

  //need to do for plague check box; make check off
  const plagueCheck = document.getElementById('plague')
  plagueCheck.checked = false
    
  // Fetch and render the data in the original format
  fetchDataAndRender("original");
});

function tidyFormat(data) {
  const resultMap = new Map();
    
  // Accumulate totals using Map with composite key
  for (const item of data) {
    const key = `${item.year}-${item.death}`;
      
    if (!resultMap.has(key)) {
      resultMap.set(key, {
        year: item.year,
        death: item.death,
        count: 0
      });
    }
      
    const entry = resultMap.get(key);
    entry.count += item.count;
  }
    
  // Convert to array
  return Array.from(resultMap.values());
}

function makeGraphs(dataFormat, countType, data) {
  const plot = Plot.plot((() => {
    const n = 5; // number of facet columns
    const keys = Array.from(d3.union(data.map((d) => d.death)));
    const index = new Map(keys.map((key, i) => [key, i]));
    const fx = (key) => index.get(key) % n;
    const fy = (key) => Math.floor(index.get(key) / n);
    return {
      height: 2100,
      width: 1300,
      axis: null,
      style: {fontSize: 15},
      marginLeft: 50,
      y: {insetTop: 10},
      fx: {padding: 0.03},
      title: countType.checked ? "Causes of Death (without Plague)" : "Causes of Death",
      subtitle: dataFormat === 'normalized' ? "Data has been normalized" : dataFormat === 'log10(x+1)' ? "Data has been transformed by log10(x+1)" : "Original data",
      marginBottom: 50,
      marks: [
        dataFormat === 'normalized' ? 
        Plot.barY(data, Plot.normalizeY("mean", {
          x: "year",
          y: "count",
          fx: (d) => fx(d.death),
          fy: (d) => fy(d.death), 
          fill: "red",
          stroke: "red",
          tip: {
            format: {
              year: true,
              count: true,
              stroke: false
            }
          }
        })) : dataFormat === 'log10(x+1)' ? 
        Plot.barY(data, {
          x: "year",
          y: (d) =>  Math.log10(d.count + 1),
          fx: (d) => fx(d.death),
          fy: (d) => fy(d.death), 
          fill: "red",
          stroke: "red",
          tip: {
            format: {
              year: true,
              count: true,
              stroke: false
            }
          }
        }) : 
        Plot.barY(data, {
          x: "year",
          y: "count",
          fx: (d) => fx(d.death),
          fy: (d) => fy(d.death), 
          fill: "red",
          stroke: "red",
          tip: {
            format: {
              year: true,
              count: true,
              stroke: false
            }
          }
        }), 
        Plot.axisX({ticks: [1650, 1665, 1700, 1752], tickFormat: "", tickRotate: 50, tickPadding: 5, labelOffset: 35}),
        Plot.axisY({labelArrow: "none", label: "count"}),
        Plot.text(keys, {fx, fy, frameAnchor: "top-left", dx: 6, dy: 2}),
        Plot.frame()
      ]
    };
  })())
  let chart = document.getElementById("facets")
  //chart.removeChild(chart.firstChild)
  chart.append(plot)
}
  
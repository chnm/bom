import * as d3 from "d3";

const map = makeMap()
populateCountTypeDropdown()
// Function to fetch data and render the word cloud
function fetchDataAndRender(startYear, endYear, countType) {
  //https://data.chnm.org/bom/bills?start-year="+form.option1+"&end-year="+form.option2+"&bill-type="+form.option3+"&count-type="+form.option4
    const url = `https://data.chnm.org/bom/bills?start-year=${startYear}&end-year=${endYear}&bill-type=Weekly&count-type=${countType}`;
  
  d3.json(url)
    .then((data) => {
      // Extract unique years from the data
      const years = Array.from(new Set(data.map(d => d.year))).sort((a, b) => a - b);
      populateDropdowns(years);

      endYear = document.getElementById("end-year").value

      let list = [data, startYear, endYear, countType]

      render(list);
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

// Populate year dropdowns
function populateDropdowns(years) {
  const startYearSelect = document.getElementById("start-year");
  const endYearSelect = document.getElementById("end-year");

  // Clear existing options
  startYearSelect.innerHTML = "";
  endYearSelect.innerHTML = "";

  years.forEach((year) => {
    const optionStart = document.createElement("option");
    optionStart.value = year;
    optionStart.text = year;
    startYearSelect.appendChild(optionStart);

    const optionEnd = document.createElement("option");
    optionEnd.value = year;
    optionEnd.text = year;
    endYearSelect.appendChild(optionEnd);
  });

  // Set default values
  startYearSelect.value = years[0];
  endYearSelect.value = years[years.length - 1];
}

function populateCountTypeDropdown() {
  const countTypeSelect = document.getElementById("count-type");

  const optionCountType1 = document.createElement("option");
  optionCountType1.value = 'Buried';
  optionCountType1.text = 'Buried';
  countTypeSelect.appendChild(optionCountType1) 

  const optionCountType2 = document.createElement("option");
  optionCountType2.value = 'Plague';
  optionCountType2.text = 'Plague';
  countTypeSelect.appendChild(optionCountType2)
}

// Initial fetch and render
fetchDataAndRender(1636, 1754, 'Buried');

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const startYear = document.getElementById("start-year").value;
  const endYear = document.getElementById("end-year").value;
  const countType = document.getElementById("count-type").value;
  fetchDataAndRender(startYear, endYear, countType);
});

// Add event listener to the reset button
document.getElementById("reset-button").addEventListener("click", () => {
  // Reset the dropdowns to the original values
  document.getElementById("start-year").value = 1648;
  document.getElementById("end-year").value = 1754;
  document.getElementById("count-type").value = 'Buried';
  // Fetch and render the original data
  fetchDataAndRender(1636, 1754, 'Buried');
});

//initialize map
function makeMap() {
  const container = document.getElementById('map');
  container.style.width = `${document.width}px`;
  container.style.height = `700px`

  let map = L.map(container);
  let osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map); 

  return map
}

//render data on map
function render(d){
  //user input 
  const data = d[0];
  const startYr = d[1];
  const endYr = d[2];
  const countType = d[3];
  
  //get shapefiles and join with bills data
  d3.json('https://data.chnm.org/bom/geometries')
    .then((parish_shp) => {
      console.log(parish_shp)                  
      return joinParishData(parish_shp, data); // Return the joined data
    })
    .then((joinedData) => {
      //color range values 
      function getColor(d, f) {
        return f > endYr ? '#d0d3d4' : 
          d > 1000 ? '#800026' :
          d > 500  ? '#BD0026' :
          d > 200  ? '#E31A1C' :
          d > 100  ? '#FC4E2A' :
          d > 50   ? '#FD8D3C' :
          d > 20   ? '#FEB24C' :
          d > 10   ? '#FED976' :
                    '#FFEDA0';
      }
          
    //variable for different types of death
    let death = ''
    if (countType === 'Buried') {
      death = 'Burials'
    } else {
      death = 'Plague Deaths'
    }
  
    //style shapefiles based on data
    let districts = L.geoJson(joinedData, {
      onEachFeature: onEachFeature,
      style: d => {
        return { 
          weight: 1,
          color: "#000000", //"#e7298a"
          fillOpacity: 1, //0.7
          fillColor: getColor(d.properties.totalDeaths, d.properties.start_yr),
        }
      }
    }).addTo(map);
    
    map.fitBounds(districts.getBounds()); 

    //remove old title 
    if (document.getElementById("title")) {
      document.getElementById("title").remove()
    }

    //make title div
    var title = L.control({position: 'topright'});
    
    title.onAdd = function (map) {
      this._div = L.DomUtil.create("div", "title");
      this._div.id = "title"
      this._div.style.backgroundColor = "#fff";
      this._div.style.padding = "10px";
      this._div.innerHTML = "<h2> Total " + death + " per Parish</h2>" + "</n><h3>Between " + startYr + "-" + endYr + "</h3>"
      return this._div;
    };
    title.addTo(map);

    //remove old info on update
    if (document.getElementById("info")) {
      document.getElementById("info").remove()
    }
    
    // control that shows state info on hover
    const info = L.control();
    
    info.onAdd = function (map) {
      this._div = L.DomUtil.create("div", "info");
      this._div.id = "info"
      this._div.style.backgroundColor = "#fff";
      this._div.style.padding = "10px";
      this.update();
      return this._div;
    };
    
    info.update = function (props) {
      this._div.innerHTML =
        "<h4>Parish Information</h4>" +
          (props
            ? 
              "Parish: " +
              props.dbn_par +
              "<br/>Total deaths: " +
              props.totalDeaths +
              "<br/>Start year: " +
              props.start_yr +
              "<br/>Subunit: " +
              props.subunit + 
              "</br>City/County: " +
              props.city_cnty || 'N/A'
            : "Hover over a parish");
    };
    
    info.addTo(map);
    
    function highlightFeature(e) {
      let layer = e.target;
    
      layer.setStyle({
        stroke: true,
        weight: 2,
        color: "#FFFFFF",
        dashArray: "",
        fillOpacity: 0.7
      });
    
      if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
      }
    
      info.update(layer.feature.properties);
    }
    
    function resetHighlight(e) {
      districts.resetStyle(e.target);
        info.update();
    }
    
    function zoomToFeature(e) {
      map.fitBounds(e.target.getBounds());
    }
            
    function onEachFeature(feature, layer) {
      layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
      });
    }

    //remove previous legend on update
    if (document.getElementById("legend")) {
      document.getElementById("legend").remove()
    }

    //make legend 
    var legend = L.control({position: 'bottomright'});
    
    legend.onAdd = function (map) {
      this._div = L.DomUtil.create("div", "legend");
      this._div.id = "legend"
      this._div.style.backgroundColor = "#fff";
      this._div.style.padding = "10px";
      this._div.innerHTML = "<h4>Total Deaths per Parish</h4"
      this.update();
      return this._div;
    };
    
    legend.update = function (map) {
      let grades = [0, 10, 20, 50, 100, 200, 500, 1000];
      let labels = [];
      for (var i = 0; i < grades.length; i++) {
        this._div.innerHTML +=
          '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
      }  
      this._div.innerHTML += '<br><i style="background:#d0d3d4"></i> ' + 'not in yr range'
        return this._div;
      } 
    legend.addTo(map);
  })

}

function joinParishData(geometries, bills) {
  // Group bills by parish name
  // NB: acc is short for 'accumulator,' a common convention in JS when using .reduce()
  const billsByParish = bills.reduce((acc, bill) => {
  const name = bill.name;
    // If we haven't seen this parish before, create a new array for it
    if (!acc[name]) {
      acc[name] = [];
    }
    // Add this bill to the parish's array
    acc[name].push(bill);
    return acc;
  }, {});
  
  // Join with geometries
  // Create the output structure, maintaining the GeoJSON FeatureCollection format
  return {
    type: "FeatureCollection",
    // Map over each geometry feature to add the bill data
    features: geometries.features.map(feature => {
      // Get the parish name from the geometry's properties
      const parishName = feature.properties.dbn_par;
      // Find all bills for this parish (or empty array if none found)
      const parishBills = billsByParish[parishName] || [];
        
      // Calculate the total number of burials for this parish
      // by adding up the 'count' from each bill
      const totalDeaths = parishBills.reduce((sum, bill) => sum + bill.count, 0);
        
      // Create an array of weekly data points
      // This simplifies the bill data to just the essential fields
      const weeklyData = parishBills.map(bill => ({
        week_id: bill.week_id,
        count: bill.count,
        year: bill.year
      }));
        
      // Return the feature with additional properties
      return {
        ...feature,
        properties: {
          ...feature.properties, // Keep all existing properties
          weeklyData, // Add the array of weekly data
          totalDeaths // Add the total burial count
        }
      };
    })
  };
}
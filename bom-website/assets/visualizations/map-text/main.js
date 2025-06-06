import * as d3 from "d3";

const map = makeMap()
populateDropdowns()
fetchDataAndRender()

// Function to fetch data and render the map
function fetchDataAndRender() {
    //const url = `https://data.chnm.org/bom/bills?start-year=${startYear}&end-year=${endYear}&bill-type=Weekly&count-type=${countType}`;
  const file = "counts.json"
  d3.json(file)
    .then((data) => {
        let cause = document.getElementById("cause").value;
        let yrRange = document.getElementById("year-range").value;

      let list = [data, cause, yrRange]

      render(list);
    })
    .catch((error) => {
      console.error("There was an error fetching the data.", error);
    });
}

function populateDropdowns() {
    //causes
    const causeSelect = document.getElementById("cause");
  
    const optionCauseType1 = document.createElement("option");
    optionCauseType1.value = 'Drowned';
    optionCauseType1.text = 'Drowned';
    causeSelect.appendChild(optionCauseType1) 
  
    const optionCauseType2 = document.createElement("option");
    optionCauseType2.value = 'Killed';
    optionCauseType2.text = 'Killed';
    causeSelect.appendChild(optionCauseType2) 

    const optionCauseType3 = document.createElement("option");
    optionCauseType3.value = 'Suicide';
    optionCauseType3.text = 'Suicide';
    causeSelect.appendChild(optionCauseType3)

    //year ranges
    const yrRangeSelect = document.getElementById("year-range");
  
    const yrRange1 = document.createElement("option");
    yrRange1.value = '1636-1649';
    yrRange1.text = '1636-1649';
    yrRangeSelect.appendChild(yrRange1) 
  
    const yrRange2 = document.createElement("option");
    yrRange2.value = '1649-1659';
    yrRange2.text = '1649-1659';
    yrRangeSelect.appendChild(yrRange2)

    const yrRange3 = document.createElement("option");
    yrRange3.value = '1659-1677';
    yrRange3.text = '1659-1677';
    yrRangeSelect.appendChild(yrRange3)
  }

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

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
    fetchDataAndRender();
  });


// filter data from query
function filterData(data) {
    const cause = document.getElementById("cause").value
    const yrRange = document.getElementById("year-range").value;
    if (cause === "Drowned") {
      data = data.filter((d) => d.cause === "drowned")
    } 
    else if (cause === "Killed") {
      data = data.filter((d) => d.cause === "killed")
    }
    else if (cause === "Suicide") {
      data = data.filter((d) => d.cause === "suicide")
    }
    if (yrRange === "1636-1649") {
      data = data.filter((d) => d.yrRange === "1636-1649")
    }   
    else if (yrRange === "1649-1659") {
      data = data.filter((d) => d.yrRange === "1649-1659")
    }
    else if (yrRange === "1659-1677") {
      data = data.filter((d) => d.yrRange === "1659-1677")
    }
    return data;
}

//join shapefiles and bills data
function joinParishData(geometries, bills) {
  // Group bills by parish name
  // NB: acc is short for 'accumulator,' a common convention in JS when using .reduce()
  const billsByParish = bills.reduce((acc, bill) => {
    const name = bill.parish;
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
        cause: bill.cause,
        yrRange: bill.yrRange,
        count: bill.count,
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

//render data on map
function render(d){
    //user input 
    const data = d[0];
    const cause = d[1];
    const yrRange = d[2];
    console.log(yrRange)
    console.log(yrRange.slice(-4))

    let filteredData = filterData(data)
    console.log(filteredData)
    d3.json('https://data.chnm.org/bom/geometries')
        .then((parish_shp) => {
            let filtered_shp = ({type: "FeatureCollection", features: parish_shp.features.filter((d) => d.properties.start_yr < yrRange.slice(-4))})             
            return joinParishData(filtered_shp, filteredData); // Return the joined data
        })
        .then((joinedData) => {
            function getColorDrowned(d) {
                return d > 100 ? '#800026' :
                       d > 75  ? '#BD0026' :
                       d > 50  ? '#E31A1C' :
                       d > 25  ? '#FC4E2A' :
                       d > 15  ? '#FD8D3C' :
                       d > 10  ? '#FEB24C' :
                       d > 5   ? '#FED976' :
                      d > 0   ? '#FFEDA0' :
                                  '#FFFFFF';
            }
            function getColorKilled(d) {
                return d > 50 ? '#800026' :
                       d > 40  ? '#BD0026' :
                       d > 30  ? '#E31A1C' :
                       d > 20  ? '#FC4E2A' :
                       d > 15  ? '#FD8D3C' :
                       d > 10  ? '#FEB24C' :
                       d > 5   ? '#FED976' :
                      d > 0   ? '#FFEDA0' :
                                  '#FFFFFF';
            }
            function getColorSuicide(d) {
                return d > 12 ? '#BD0026' :
                       d > 10  ? '#E31A1C' :
                       d > 8 ? '#FC4E2A' :
                       d > 6  ? '#FD8D3C' :
                       d > 4  ? '#FEB24C' :
                       d > 2  ? '#FED976' :
                      d > 0   ? '#FFEDA0' :
                                  '#FFFFFF';
            }
            
            let districts = L.geoJson(joinedData, { //was joinedFiltered //joinedDoubleFiltered
                onEachFeature: onEachFeature,
                style: d => {
                  return { 
                    weight: 1,
                    color: "black",
                    fillOpacity: 0.7,
                    //fillColor: getColor(Number(d.properties.totalDeaths)),
                    fillColor: cause === "Drowned" ? getColorDrowned(d.properties.totalDeaths) :
                  cause === "Killed" ? getColorKilled(d.properties.totalDeaths) : getColorSuicide(d.properties.totalDeaths),
                  }
                }
            }).addTo(map);
            
            map.fitBounds(districts.getBounds()); 
            
            // control that shows state info on hover
            const info = L.control();
            
            //remove old title 
            if (document.getElementById("title")) {
                document.getElementById("title").remove()
            }

            var title = L.control({position: 'topright'});
            
            title.onAdd = function (map) {
                this._div = L.DomUtil.create("div", "title");
                this._div.id = "title"
                this._div.style.backgroundColor = "#fff";
                this._div.style.padding = "10px";
                this._div.innerHTML = cause === "Drowned" ? "<h2>Deaths by Drowning</h2>" + "</n><h3>From " + yrRange + "</h3>" :
                  cause === "Killed" ? "<h2>Deaths by Murder</h2>" + "</n><h3>From " + yrRange + "</h3>" :
                  "<h2>Deaths by Suicide</h2>" + "</n><h3>From " + yrRange + "</h3>";
                return this._div;
              };
            title.addTo(map);

            //remove old info on update
            if (document.getElementById("info")) {
                document.getElementById("info").remove()
            }
            
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
                      "<br/>Total Deaths: " +
                      props.totalDeaths +
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
                  weight: 4,
                  color: "#FF0000",
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
                //console.log("test-here")
                document.getElementById("legend").remove()
            }

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
                let grades = []
                cause === "Drowned" ? grades = [0, 5, 10, 15, 25, 50, 75, 100]: 
                  cause === "Killed" ? grades = [0, 5, 10, 15, 20, 30, 40, 50] :
                  grades = [0, 2, 4, 6, 8, 10, 12]; 
                let labels = [];
                this._div.innerHTML += '<i style="background:#FFFFFF;"></i> ' + '0<br>'
                for (var i = 0; i < grades.length; i++) {
                    this._div.innerHTML += 
                      cause === "Drowned" ?   
                      '<i style="background:' + getColorDrowned(grades[i] + 1) + '"></i> ' +
                        grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+') :
                      cause === "Killed" ? '<i style="background:' + getColorKilled(grades[i] + 1) + '"></i> ' +
                        grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+') :
                      '<i style="background:' + getColorSuicide(grades[i] + 1) + '"></i> ' +
                        grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
                }
                return this._div;
            }
            legend.addTo(map);
    
        })

}
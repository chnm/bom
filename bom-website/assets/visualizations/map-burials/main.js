import * as d3 from "d3";

// Initialize map once with global scope
let map;

// Make sure DOM is ready before initializing map
document.addEventListener("DOMContentLoaded", function () {
  map = makeMap();
});

populateCountTypeDropdown();

// Function to fetch data and render the map
function fetchDataAndRender(startYear, endYear, countType) {
  // Check if map is initialized
  if (!map) {
    map = makeMap();
    if (!map) return;
  }

  // Add loading indicator
  const mapContainer = document.getElementById("map");
  const loadingDiv = document.createElement("div");
  loadingDiv.id = "loading";
  loadingDiv.innerHTML = "Loading data...";
  mapContainer.appendChild(loadingDiv);

  // Construct URL with parameters
  const url = `https://data.chnm.org/bom/shapefiles?start-year=${startYear}&end-year=${endYear}&bill-type=Weekly&count-type=${countType}`;

  d3.json(url)
    .then((geojsonData) => {
      // Remove loading indicator
      const loadingDiv = document.getElementById("loading");
      if (loadingDiv) loadingDiv.remove();

      // Validate data
      if (!geojsonData) {
        showError("No data received from API.");
        return;
      }

      // Create GeoJSON if needed - handle array format
      if (Array.isArray(geojsonData) && !geojsonData.type) {
        const features = geojsonData.map((item) => ({
          type: "Feature",
          properties: item,
          geometry: item.geometry || null,
        }));

        geojsonData = {
          type: "FeatureCollection",
          features: features,
        };
      }

      // Validate GeoJSON structure
      if (!geojsonData.type) {
        showError("Invalid GeoJSON: missing type property.");
        return;
      }

      if (!geojsonData.features) {
        showError("Invalid GeoJSON: missing features array.");
        return;
      }

      if (geojsonData.features.length === 0) {
        showError("No data available for this time range.");
        return;
      }

      // Verify features have geometry
      const sampleFeature = geojsonData.features[0];
      if (!sampleFeature.geometry) {
        showError("Invalid GeoJSON: features are missing geometry.");
        return;
      }

      // Extract unique years from the data metadata
      const years = [];

      if (
        geojsonData.metadata &&
        geojsonData.metadata.start_year &&
        geojsonData.metadata.end_year
      ) {
        // Get years from metadata
        for (
          let year = geojsonData.metadata.start_year;
          year <= geojsonData.metadata.end_year;
          year++
        ) {
          years.push(year);
        }
      } else {
        // Extract years from features if no metadata
        const yearSet = new Set();

        geojsonData.features.forEach((feature) => {
          const startYr = feature.properties?.start_yr;
          if (startYr && typeof startYr === "number") {
            yearSet.add(startYr);
          }
        });

        // Use default range if no years found
        if (yearSet.size === 0) {
          for (let year = 1640; year <= 1750; year++) {
            years.push(year);
          }
        } else {
          years.push(...Array.from(yearSet).sort((a, b) => a - b));
        }
      }

      // Remember the current selections before updating
      const currentStartYear = document.getElementById("start-year").value;
      const currentEndYear = document.getElementById("end-year").value;

      // Populate dropdowns with years but preserve selections
      populateDropdowns(years, currentStartYear, currentEndYear);

      // Get the current end year from the dropdown (should be preserved now)
      endYear = document.getElementById("end-year").value;

      // Render the map directly with the GeoJSON data
      renderDirectGeoJSON(geojsonData, startYear, endYear, countType);
    })
    .catch((error) => {
      // Remove loading indicator
      const loadingDiv = document.getElementById("loading");
      if (loadingDiv) loadingDiv.remove();

      // Show error message
      showError(
        `Error loading data: ${error.message || "Unknown error"}.<br>Please try again with different parameters.`,
      );
    });
}

// Helper function to show errors
function showError(message) {
  const errorDiv = document.createElement("div");
  errorDiv.style.position = "absolute";
  errorDiv.style.top = "50%";
  errorDiv.style.left = "50%";
  errorDiv.style.transform = "translate(-50%, -50%)";
  errorDiv.style.backgroundColor = "white";
  errorDiv.style.color = "red";
  errorDiv.style.padding = "20px";
  errorDiv.style.borderRadius = "5px";
  errorDiv.style.boxShadow = "0 0 15px rgba(0,0,0,0.2)";
  errorDiv.style.zIndex = "1000";
  errorDiv.innerHTML = message;

  document.getElementById("map").appendChild(errorDiv);
}

// Populate year dropdowns
function populateDropdowns(
  years,
  selectedStartYear = null,
  selectedEndYear = null,
) {
  const startYearSelect = document.getElementById("start-year");
  const endYearSelect = document.getElementById("end-year");

  // Remember current selections before clearing
  if (selectedStartYear === null && startYearSelect.value) {
    selectedStartYear = startYearSelect.value;
  }

  if (selectedEndYear === null && endYearSelect.value) {
    selectedEndYear = endYearSelect.value;
  }

  // Clear existing options
  startYearSelect.innerHTML = "";
  endYearSelect.innerHTML = "";

  // Add year options to both dropdowns
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

  // Set values based on selected years if available
  if (selectedStartYear && years.includes(parseInt(selectedStartYear))) {
    startYearSelect.value = selectedStartYear;
  } else {
    startYearSelect.value = years[0];
  }

  if (selectedEndYear && years.includes(parseInt(selectedEndYear))) {
    endYearSelect.value = selectedEndYear;
  } else {
    endYearSelect.value = years[years.length - 1];
  }
}

function populateCountTypeDropdown() {
  const countTypeSelect = document.getElementById("count-type");

  const optionCountType1 = document.createElement("option");
  optionCountType1.value = "Buried";
  optionCountType1.text = "Buried";
  countTypeSelect.appendChild(optionCountType1);

  const optionCountType2 = document.createElement("option");
  optionCountType2.value = "Plague";
  optionCountType2.text = "Plague";
  countTypeSelect.appendChild(optionCountType2);
}

// Initial fetch and render - but only after map is initialized
document.addEventListener("DOMContentLoaded", function () {
  // Give a little time for map to initialize
  setTimeout(() => {
    fetchDataAndRender(1636, 1754, "Buried");
  }, 500);
});

// Add event listener to the update button
document.getElementById("update-button").addEventListener("click", () => {
  const startYear = document.getElementById("start-year").value;
  const endYear = document.getElementById("end-year").value;
  const countType = document.getElementById("count-type").value;

  // Pass the selected values to the fetch function
  fetchDataAndRender(startYear, endYear, countType);
});

// Add event listener to the reset button
document.getElementById("reset-button").addEventListener("click", () => {
  // Get available year options
  const startYearSelect = document.getElementById("start-year");
  const endYearSelect = document.getElementById("end-year");

  if (startYearSelect.options.length > 0 && endYearSelect.options.length > 0) {
    // Set to first and last available years
    const firstYear = startYearSelect.options[0].value;
    const lastYear =
      endYearSelect.options[endYearSelect.options.length - 1].value;

    // Reset the dropdowns to the min/max values
    startYearSelect.value = firstYear;
    endYearSelect.value = lastYear;
  }

  // Reset to Buried count type
  document.getElementById("count-type").value = "Buried";

  // Get the selected years (or fall back to defaults)
  const startYear = startYearSelect.value || 1636;
  const endYear = endYearSelect.value || 1754;

  // Fetch and render with selected or default years
  fetchDataAndRender(startYear, endYear, "Buried");
});

//initialize map
function makeMap() {
  try {
    const container = document.getElementById("map");
    if (!container) {
      return null;
    }

    // Check if Leaflet is loaded
    if (typeof L === "undefined") {
      container.innerHTML =
        '<div style="color: red; padding: 20px; text-align: center;">Map library (Leaflet) not loaded. Please refresh the page.</div>';
      return null;
    }

    // Set container dimensions
    container.style.width = "100%";
    container.style.height = "700px";

    // Create map with London as default view
    const mapInstance = L.map(container, {
      center: [51.505, -0.09],
      zoom: 10,
      minZoom: 8,
      maxZoom: 18,
    });

    // Add OpenStreetMap tile layer
    let osmLayer = L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      },
    ).addTo(mapInstance);

    // Add fallback for tile loading errors
    osmLayer.on("tileerror", function (error, tile) {
      // Try another tile provider if the default fails
      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        },
      ).addTo(mapInstance);
    });

    return mapInstance;
  } catch (e) {
    // Show error message in the map container
    document.getElementById("map").innerHTML =
      '<div style="color: red; padding: 20px; text-align: center;">Error initializing map. Please try refreshing the page.</div>';
    // Return a dummy map object to prevent errors
    return { fitBounds: () => {}, remove: () => {} };
  }
}

// Function to render GeoJSON data on the map
function renderDirectGeoJSON(geojsonData, startYr, endYr, countType) {
  // Remove any existing loading indicator
  const loadingDiv = document.getElementById("loading");
  if (loadingDiv) {
    loadingDiv.remove();
  }

  // Validate map object
  if (!map || !map.eachLayer) {
    showError("Map initialization error. Please refresh the page.");
    return;
  }

  // Clear existing layers except base tile layer
  try {
    map.eachLayer(function (layer) {
      if (!(layer instanceof L.TileLayer)) {
        map.removeLayer(layer);
      }
    });
  } catch (e) {
    showError("Error clearing map layers. Please refresh the page.");
    return;
  }

  // Function to get color for choropleth map
  function getColor(d) {
    // Set default value for d if it's undefined or NaN
    d = typeof d === "number" && !isNaN(d) ? d : 0;

    // Use different color schemes for plague vs buried
    if (countType === "Plague") {
      // Red color scheme for plague deaths
      return d > 1000
        ? "#67000d"
        : d > 500
          ? "#a50f15"
          : d > 200
            ? "#cb181d"
            : d > 100
              ? "#ef3b2c"
              : d > 50
                ? "#fb6a4a"
                : d > 20
                  ? "#fc9272"
                  : d > 10
                    ? "#fcbba1"
                    : "#fee5d9";
    } else {
      // Blue color scheme for general burials
      return d > 1000
        ? "#084594"
        : d > 500
          ? "#2171b5"
          : d > 200
            ? "#4292c6"
            : d > 100
              ? "#6baed6"
              : d > 50
                ? "#9ecae1"
                : d > 20
                  ? "#c6dbef"
                  : d > 10
                    ? "#deebf7"
                    : "#f7fbff";
    }
  }

  // Set title text based on count type
  const titleText = countType === "Plague" ? "Plague Deaths" : "Burials";

  // Create GeoJSON layer
  try {
    let districts = L.geoJson(geojsonData, {
      onEachFeature: onEachFeature,
      style: (feature) => {
        try {
          // Get total deaths from the feature properties
          const deaths =
            countType === "Plague"
              ? feature.properties?.total_plague || 0
              : feature.properties?.total_buried || 0;

          return {
            weight: 1,
            color: "#000000",
            fillOpacity: 0.8,
            fillColor: getColor(deaths),
          };
        } catch (styleError) {
          return {
            weight: 1,
            color: "#000000",
            fillOpacity: 0.8,
            fillColor: "#cccccc", // Default gray for errors
          };
        }
      },
    });

    // Add layer to map
    districts.addTo(map);

    map.setView([51.505, -0.09], 12);
  } catch (e) {
    showError("Error creating map: " + e.message);
    return;
  }

  // Map has been fit to bounds above

  // Remove old title if it exists
  if (document.getElementById("title")) {
    document.getElementById("title").remove();
  }

  // Create title div
  var titleControl = L.control({ position: "topright" });

  titleControl.onAdd = function (map) {
    this._div = L.DomUtil.create("div", "title");
    this._div.id = "title";
    this._div.innerHTML = `<h2>Total ${titleText} per Parish</h2><h3>Between ${startYr}-${endYr}</h3>`;
    return this._div;
  };
  titleControl.addTo(map);

  // Remove old info panel if it exists
  if (document.getElementById("info")) {
    document.getElementById("info").remove();
  }

  // Create info panel for hover details
  const info = L.control();

  info.onAdd = function (map) {
    this._div = L.DomUtil.create("div", "info");
    this._div.id = "info";
    this.update();
    return this._div;
  };

  info.update = function (props) {
    const deathCount =
      countType === "Plague"
        ? props?.total_plague || 0
        : props?.total_buried || 0;
    this._div.innerHTML =
      "<h4>Parish Information</h4>" +
      (props
        ? `Parish: ${props.dbn_par || props.civ_par || "Unknown"}<br/>
             Total ${countType === "Plague" ? "plague deaths" : "burials"}: ${deathCount}<br/>`
        : "Hover over a parish");
  };

  info.addTo(map);

  // Functions for interactive features
  function highlightFeature(e) {
    let layer = e.target;

    layer.setStyle({
      stroke: true,
      weight: 2,
      color: "#AAAAAA",
      dashArray: "",
      fillOpacity: 0.9,
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
      layer.bringToFront();
    }

    info.update(layer.feature.properties);
  }

  function resetHighlight(e) {
    // Get the current layer
    const layer = e.target;

    // Apply the original style directly instead of using resetStyle
    layer.setStyle({
      weight: 1,
      color: "#000000",
      fillOpacity: 0.8,
      fillColor: getColor(
        countType === "Plague"
          ? layer.feature.properties?.total_plague || 0
          : layer.feature.properties?.total_buried || 0,
      ),
    });

    info.update();
  }

  function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
  }

  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: zoomToFeature,
    });
  }

  // Remove previous legend if it exists
  if (document.getElementById("legend")) {
    document.getElementById("legend").remove();
  }

  // Create legend
  var legend = L.control({ position: "bottomright" });

  legend.onAdd = function (map) {
    this._div = L.DomUtil.create("div", "legend");
    this._div.id = "legend";
    this._div.innerHTML = "<h4>Total Deaths per Parish</h4>";
    this.update();
    return this._div;
  };

  legend.update = function () {
    let grades = [0, 10, 20, 50, 100, 200, 500, 1000];

    // Reset legend content
    this._div.innerHTML = "<h4>Total Deaths per Parish</h4>";

    for (var i = 0; i < grades.length; i++) {
      const grade = grades[i] + 1;
      this._div.innerHTML +=
        '<i style="background:' +
        getColor(grade) +
        '"></i> ' +
        grades[i] +
        (grades[i + 1] ? "&ndash;" + grades[i + 1] + "<br>" : "+");
    }
    return this._div;
  };

  legend.addTo(map);
}

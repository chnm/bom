---
title: "Mapping Burials and Plague"
date: 2025-02-27
updated: 2025-02-27
abstract: "Mapping plague and non-plague deaths"
summary: "Interactive choropleth map of London showing burial and plague death patterns across parishes, with controls to filter by year range and count type for geographical mortality analysis."
script: visualizations/map-burials/main.js
styles: visualizations/map-burials/style.css
layout: visualizations
thumbnail: map-burials.png
thumbdesc: "A screenshot showing a choropleth map of London"
author:
- Savannah Scott
- Jason Heppler
category: "geographic-mapping"
---
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
     crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
     integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
     crossorigin=""></script>

<div id="row">
    <h3>Mapping Burials and Plague Deaths</h3>
    <div class="viz-controls is-wrapping">
          <div class="viz-field is-spaced">
            <label class="viz-label is-large" for="start-year">
              Start Year:
            </label>
            <select class="viz-select" id="start-year"></select>
          </div>
          <div class="viz-field is-spaced">
            <label class="viz-label is-large" for="end-year">
              End Year:
            </label>
            <select class="viz-select" id="end-year"></select>
          </div>
          <div class="viz-field is-spaced">
            <label class="viz-label is-large" for="count-type">
              Count Type:
            </label>
            <select class="viz-select" id="count-type"></select>
          </div>
          <div class="viz-field is-spaced">
            <label class="viz-label is-large" aria-hidden="true">
              Actions
            </label>
            <div class="viz-actions is-pair">
              <button id="update-button" type="button" class="viz-button is-large">Update</button>
              <button id="reset-button" type="button" class="viz-button is-large">Reset</button>
            </div>
          </div>
    </div>
</div><br>
<div id="chart"><div id="map"></div></div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

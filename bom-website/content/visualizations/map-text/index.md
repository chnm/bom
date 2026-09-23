---
title: "Mapping Suicides, Drownings, and Killings in the Bills of Mortality"
date: 2025-04-22
updated: 2025-06-06
abstract: "Mapping text analysis on suicides, drownings, and killings in the Bills of Mortality."
summary: "Interactive choropleth map analyzing geographical patterns of suicides, drownings, and killings in London parishes, with filtering options by cause and year range based on text analysis research."
script: visualizations/map-text/main.js
styles: visualizations/map-text/style.css
layout: visualizations
thumbnail: map-text.png
thumbdesc: "A screenshot of a choropleth map of London parishes."
author:
- Savannah Scott
- Hernan Adasme
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
    <h3>Suicides, Drownings, and Killings in the Bills of Mortality</h3>
    <p>The following visualization is an interactive version of map visualizations first created by <a href="https://deathbynumbers.org/authors/hernan-adasme/">Hernán Adasme</a> in his post "<a href="https://deathbynumbers.org/analysis/death-by-words/">Death by Numbers</a>." </p>
    <div class="viz-controls is-gapped">
          <div class="viz-field is-spaced">
            <label class="viz-label is-large" for="cause">
              Cause:
            </label>
            <select class="viz-select is-roomy" id="cause"></select>
          </div>
          <div class="viz-field is-spaced">
            <label class="viz-label is-large" for="year-range">
              Year Range:
            </label>
            <select class="viz-select is-roomy" id="year-range"></select>
          </div>
          <div class="viz-actions">
          <button id="update-button" type="button" class="viz-button is-large">Update</button>
          </div>
    </div>
</div><br>
<div id="chart"><div id="map"></div></div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

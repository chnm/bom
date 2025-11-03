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
    <div class="flex flex-wrap items-center space-x-4 mb-6">
          <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-base font-bold" for="cause">
              Cause:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-5 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="cause"></select>
          </div>
          <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-base font-bold" for="year-range">
              Year Range:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-5 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="year-range"></select>
          </div>
          <div class="flex space-x-2 ml-auto mt-5">
          <button id="update-button" type="button" class="rounded border border-gray-200 bg-white text-base font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
          </div>
    </div>
</div><br>
<div id="chart"><div id="map"></div></div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

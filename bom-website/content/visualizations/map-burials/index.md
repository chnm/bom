---
title: "Mapping Burials and Plague"
created: 2025-02-27
updated: 2025-02-27
abstract: "Mapping plague and non-plague deaths"
script: visualizations/map-burials/main.js
styles: visualizations/map-burials/style.css
layout: visualizations
thumbnail: map-burials.png
thumbdesc: "A screenshot showing a choropleth map of London"
author:
---
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
     crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
     integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
     crossorigin=""></script>

<div id="row">
    <h3>Mapping Burials and Plague Deaths</h3>
    <div class="flex flex-wrap items-center space-x-4 mb-6">
          <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-base font-bold" for="start-year">
              Start Year:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="start-year"></select>
          </div>
          <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-base font-bold" for="end-year">
              End Year:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="end-year"></select>
          </div>
          <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-base font-bold" for="count-type">
              Count Type:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="count-type"></select>
          </div>
          <div class="flex space-x-2 ml-auto mt-5">
          <button id="update-button" type="button" class="rounded-l-lg border border-gray-200 bg-white text-base font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
          <button id="reset-button" type="button" class="rounded-r-md border border-gray-200 bg-white text-base font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Reset</button>
          </div>
    </div>
</div><br>
<div id="chart"><div id="map"></div></div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}
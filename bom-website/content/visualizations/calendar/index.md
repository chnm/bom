---
title: "Calendar of Causes"
date: 2024-10-04
updated: 2024-10-04
abstract: "Graphing the causes of death over time"
script: visualizations/calendar/main.js
styles: visualizations/calendar/style.css
layout: visualizations
thumbnail: calendar.png
thumbdesc: "A screenshot showing the causes of death visualization."
author:
- Jason Heppler
---

This visualization illustrates the causes of death per week for a given year. This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3 id="chart-title">Individual Causes of Death by Week</h3>
    <div class="flex flex-row space-x-4 mb-6">
    <div class="flex flex-col w-32">
        <label for="year" class="block text-gray-700 text-sm font-bold">Year:</label>
        <select id="year" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
            <option value="">Loading years...</option>
        </select>
    </div>
    <div class="flex items-end">
        <button id="update-button" type="button" class="rounded-lg border border-gray-200 bg-white text-sm font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
    </div>
</div>
    <div class="loading_chart">Loading data...</div>
    <svg id="chart"></svg>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

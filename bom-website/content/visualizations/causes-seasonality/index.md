---
title: "Causes Seasonality"
date: 2025-07-02
updated: 2025-07-02
abstract: "Visualizing the seasonality of causes of death"
script: visualizations/causes-seasonality/main.js
styles: visualizations/causes-seasonality/style.css
layout: visualizations
thumbnail: seasonality.png
thumbdesc: "A screenshot showing the causes of death seasonality visualization."
author:
- Jason Heppler
---

This visualization illustrates the seasonality of causes of death across the year, allowing you to analyze patterns and compare different causes. You can select a single cause to view its seasonal distribution, or compare two causes side by side.

<div id="row">
    <h3 id="chart-title">Seasonality of Causes of Death</h3>
    <div class="flex flex-row space-x-4 mb-6">
        <div class="flex flex-col">
            <label for="year" class="block text-gray-700 text-sm font-bold">Year:</label>
            <select id="year" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight w-32 focus:outline-none focus:shadow-outline"></select>
        </div>
        <div class="flex flex-col">
            <label for="cause1" class="block text-gray-700 text-sm font-bold">Primary Cause:</label>
            <select id="cause1" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"></select>
        </div>
        <div class="flex flex-col">
            <label for="cause2" class="block text-gray-700 text-sm font-bold">Compare with (optional):</label>
            <select id="cause2" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                <option value="">None</option>
            </select>
        </div>
        <div class="flex items-end">
            <button id="update-button" type="button" class="rounded border border-gray-200 bg-white text-sm font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
        </div>
    </div>
    <div class="loading_chart">Loading data...</div>
    <svg id="chart"></svg>
    <figcaption>This figure shows the seasonal patterns of causes of death across the selected year range. Data updates regularly as new bills are transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

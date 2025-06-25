---
title: "Causes of Death as a Cloud"
date: 2023-06-27
updated: 2025-06-24
abstract: "Charting the causes of death"
script: visualizations/wordcloud/main.js
styles: visualizations/wordcloud/style.css
layout: visualizations
thumbnail: wordcloud.png
thumbdesc: "A screenshot showing..."
author:
- Jason Heppler
---

The following visualization displays a word cloud of causes of death within the Plague Bills. The size of the text indicates a greater number of occurances. This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3>Word Cloud of Causes of Death</h3>
    <div class="flex flex-wrap items-center space-x-4 mb-6">
      <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-sm font-bold" for="start-year">
              Start year:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="start-year"></select>
          </div>
          <div class="flex flex-col space-y-2">
            <label class="block text-gray-700 text-sm font-bold" for="end-year">
              End year:
            </label>
            <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="end-year"></select>
          </div>
  <div class="flex space-x-2 ml-auto mt-5">
    <button id="update-button" type="button" class="rounded-l-lg border border-gray-200 bg-white text-sm font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
    <button id="reset-button" type="button" class="rounded-r-md border border-gray-200 bg-white text-sm font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Reset</button>
  </div>
</div>
    <div class="loading_chart">Loading data...</div>
    <p id="word-info">Mouse over a word to see its count</p>
    <svg id="chart"></svg>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

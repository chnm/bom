---
title: "Data Quality Analysis"
date: 2025-08-25
updated: 2025-08-25
abstract: "Visualizing data quality and illegibility patterns over time"
script: visualizations/data-quality/main.js
styles: visualizations/data-quality/style.css
layout: visualizations
thumbnail: data-quality.png
thumbdesc: "A calendar heatmap showing data quality patterns over time."
author:
- Jason Heppler
category: "project-data"
---

This visualization shows the data quality patterns for Bills of Mortality records by parish and week. You can examine either illegible records (difficult to read or transcribe) or missing records (incomplete data) to understand temporal and geographic patterns in data quality issues.

<div id="row">
    <h3 id="chart-title">Data Quality by Week</h3>
    <div class="flex flex-row space-x-4 mb-6">
        <div class="flex flex-col w-32">
            <label for="year" class="block text-gray-700 text-sm font-bold">Year:</label>
            <select id="year" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                <option value="">Loading years...</option>
            </select>
        </div>
        <div class="flex flex-col w-40">
            <label for="quality-type" class="block text-gray-700 text-sm font-bold">Quality Issue:</label>
            <select id="quality-type" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
                <option value="">Loading...</option>
            </select>
        </div>
        <div class="flex items-end">
            <button id="update-button" type="button" class="rounded-lg border border-gray-200 bg-white text-sm font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
        </div>
    </div>
    <div class="loading_chart">Loading data quality information...</div>
    <svg id="chart"></svg>
    <div class="bg-gray-50 rounded-lg p-4 mt-4 text-sm text-gray-600">
        <strong>Color Legend:</strong> 
        <span style="color: #10b981;">■ Good</span> (no data quality issues), 
        <span style="color: #f59e0b;">■ Partial Issues</span> (some records have issues), 
        <span style="color: #ef4444;">■ All Issues</span> (all records have issues), 
        <span style="color: #9ca3af;">■ No Data</span> (no records available).
    </div>
    <figcaption>This visualization helps identify temporal patterns in data quality, which may correspond to different scribes, paper quality issues, or historical events affecting record-keeping. The number of records refers to whether one of the "buried" values or "plague" values or both are missing for a given parish. The data updates regularly as new transcriptions are added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

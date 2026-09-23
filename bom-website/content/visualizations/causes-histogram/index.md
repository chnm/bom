---
title: "Causes Histograms"
date: 2024-10-04
updated: 2024-10-04
abstract: "Graphing the causes of death per week"
summary: "Histogram visualization displaying weekly mortality data by specific causes of death, with interactive controls to filter by year and individual causes."
script: visualizations/causes-histogram/main.js
styles: visualizations/causes-histogram/style.css
layout: visualizations
thumbnail: histogram.png
thumbdesc: "A screenshot showing the causes of death visualization."
author:
- Jason Heppler
category: "temporal"
---

This visualization illustrates the causes of death per week for a given year. This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3 id="chart-title">Individual Causes of Death by Week</h3>
    <div class="viz-controls is-gapped">
    <div class="viz-field">
        <label for="year" class="viz-label">Year:</label>
        <select id="year" class="viz-select"></select>
    </div>
    <div class="viz-field">
        <label for="cause" class="viz-label">Cause of death:</label>
        <select id="cause" class="viz-select"></select>
    </div>
    <div class="viz-actions">
        <button id="update-button" type="button" class="viz-button">Update</button>
    </div>
</div>
    <div class="loading_chart">Loading data...</div>
    <div id="chart"></div>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

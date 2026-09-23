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
category: "temporal"
summary: "This visualization illustrates the seasonality of causes of death across the year, allowing you to analyze patterns and compare different causes. You can select a single cause to view its seasonal distribution, or compare two causes side by side. Dashed lines indicate areas where there are gaps in the data, and represent an interpolation between existing data."
---

This visualization illustrates the seasonality of causes of death across the year, allowing you to analyze patterns and compare different causes. You can select a single cause to view its seasonal distribution, or compare two causes side by side. Dashed lines indicate areas where there are gaps in the data, and represent an interpolation between existing data. 

<div id="row">
    <h3 id="chart-title">Seasonality of Causes of Death</h3>
    <div class="viz-controls is-gapped">
        <div class="viz-field">
            <label for="year" class="viz-label">Year:</label>
            <select id="year" class="viz-select is-narrow"></select>
        </div>
        <div class="viz-field">
            <label for="cause1" class="viz-label">Primary Cause:</label>
            <select id="cause1" class="viz-select"></select>
        </div>
        <div class="viz-field">
            <label for="cause2" class="viz-label">Compare with (optional):</label>
            <select id="cause2" class="viz-select">
                <option value="">None</option>
            </select>
        </div>
        <div class="viz-actions">
            <button id="update-button" type="button" class="viz-button">Update</button>
        </div>
    </div>
    <div class="loading_chart">Loading data...</div>
    <div id="chart"></div>
    <figcaption>This figure shows the seasonal patterns of causes of death across the selected year range. Data updates regularly as new bills are transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

---
title: "Calendar of Causes"
date: 2024-10-04
updated: 2024-10-04
abstract: "Graphing the causes of death over time"
summary: "Interactive calendar visualization showing weekly causes of death data for any selected year, allowing users to explore temporal patterns in mortality."
script: visualizations/calendar/main.js
styles: visualizations/calendar/style.css
layout: visualizations
thumbnail: calendar.png
thumbdesc: "A screenshot showing the causes of death visualization."
author:
- Jason Heppler
category: "temporal"
---

This visualization illustrates the causes of death per week for a given year. This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3 id="chart-title">Individual Causes of Death by Week</h3>
    <div class="viz-controls">
    <div class="viz-field is-narrow">
        <label for="year" class="viz-label">Year:</label>
        <select id="year" class="viz-select">
            <option value="">Loading years...</option>
        </select>
    </div>
    <div class="viz-actions">
        <button id="update-button" type="button" class="viz-button is-rounded">Update</button>
    </div>
</div>
    <div class="loading_chart">Loading data...</div>
    <div id="chart" class="chart-frame"></div>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

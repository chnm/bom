---
title: "Counting the Causes of Death"
created: 2023-06-06
updated: 2023-06-07
abstract: "Charting the causes of death"
script: visualizations/plague-deaths/main.js
styles: visualizations/plague-deaths/style.css
layout: visualizations
thumbnail: deathcount.png
thumbdesc: "A screenshot showing..."
author:
---

This visualization illustrates the causes of death over time. The darker the shade of red indicates a higher number of deaths for a particular cause. Each column corresponds to a year in the database (listed on the x-axis label at the bottom of the graphic) and it's corresponding cause (on the y-axis).This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3>Causes of Death by Year</h3>
    <div class="loading_chart">Loading data...</div>
    <svg id="chart"></svg>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}
---
title: "Counting the Causes of Death"
date: 2023-06-06
updated: 2024-10-03
abstract: "Charting the causes of death"
summary: "Heat map visualization showing causes of death over time, with darker red shades indicating higher death counts for each cause by year, updating regularly as new transcriptions are added."
script: visualizations/plague-deaths/main.js
styles: visualizations/plague-deaths/style.css
layout: visualizations
thumbnail: deathcount.png
thumbdesc: "A screenshot showing the causes of death visualization."
author:
- Jason Heppler
category: "temporal"
---

This visualization illustrates the causes of death over time. The darker the shade of red indicates a higher number of deaths for a particular cause. Each column corresponds to a year in the database (listed on the x-axis label at the bottom of the graphic) and it's corresponding cause (on the y-axis). This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3>Causes of Death by Year</h3>
    <div class="loading_chart">Loading data...</div>
    <p class="text-gray-600 mb-2 italic"><small>Hover over cells to see detailed information</small></p>
    <svg id="chart"></svg>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

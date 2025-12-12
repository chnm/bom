---
title: "Counting the Causes of Death (General Bills)"
date: 2024-12-12
updated: 2024-12-12
abstract: "Charting the causes of death from general bills"
summary: "Heat map visualization showing causes of death over time from annual general bills, with darker red shades indicating higher death counts for each cause by year, updating regularly as new transcriptions are added."
script: visualizations/plague-deaths-general/main.js
styles: visualizations/plague-deaths-general/style.css
layout: visualizations
thumbnail: deathcount.png
thumbdesc: "A screenshot showing the causes of death visualization."
author:
- Jason Heppler
category: "temporal"
---

This visualization illustrates the causes of death over time from the annual general bills of mortality. The darker the shade of red indicates a higher number of deaths for a particular cause. Each column corresponds to a year in the database (listed on the x-axis label at the bottom of the graphic) and it's corresponding cause (on the y-axis). This graphic updates regularly as new bills are added to the database.

For causes of death from the weekly bills, see the [Weekly Bills visualization](/visualizations/deaths/).

<div id="row">
    <h3>Causes of Death by Year (General Bills)</h3>
    <div class="loading_chart">Loading data...</div>
    <p class="text-gray-600 mb-2 italic"><small>Hover over cells to see detailed information</small></p>
    <svg id="chart"></svg>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

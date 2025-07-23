---
title: "Counting the Transcribed Bills"
date: 2023-03-27
updated: 2025-06-24
abstract: "Charting the completeness of our transcriptions"
script: visualizations/counts/main.js
styles: visualizations/counts/style.css
layout: visualizations
thumbnail: plaguechart.png
thumbdesc: "A screenshot showing a bar chart of transcribed bills counts."
author:
- Jason Heppler
category: "project-data"
---

This visualization is our "dashboard" for visualizing our progress transcribing the Plague Bills. The chart indicates the total number of weeks, while the bar fills to count the number of weeks that have been transcribed. Mouse over the bars to see the raw data. This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3>Transcribed Bills by Year</h3>
    <div class="loading_stack">Loading data...</div>
    <svg id="barchart-multiple" width="100%"></svg>
    <figcaption>This figure updates regularly as new data is transcribed and added to the database.</figcaption>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

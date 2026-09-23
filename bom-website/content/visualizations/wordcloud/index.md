---
title: "Causes of Death as a Cloud"
date: 2023-06-27
updated: 2025-06-24
abstract: "Charting the causes of death"
summary: "Interactive word cloud visualization displaying causes of death from the Plague Bills, with text size representing frequency of occurrence and year range filtering capabilities."
script: visualizations/wordcloud/main.js
styles: visualizations/wordcloud/style.css
layout: visualizations
thumbnail: wordcloud.png
thumbdesc: "A screenshot showing..."
author:
- Jason Heppler
category: "cause-analysis"
---

The following visualization displays a word cloud of causes of death within the Plague Bills. The size of the text indicates a greater number of occurrences. This graphic updates regularly as new bills are added to the database.

<div id="row">
    <h3>Word Cloud of Causes of Death</h3>
    <div class="viz-controls is-wrapping">
      <div class="viz-field is-spaced">
            <label class="viz-label" for="start-year">
              Start year:
            </label>
            <select class="viz-select" id="start-year"></select>
          </div>
          <div class="viz-field is-spaced">
            <label class="viz-label" for="end-year">
              End year:
            </label>
            <select class="viz-select" id="end-year"></select>
          </div>
  <div class="viz-actions is-pair">
    <button id="update-button" type="button" class="viz-button">Update</button>
    <button id="reset-button" type="button" class="viz-button">Reset</button>
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

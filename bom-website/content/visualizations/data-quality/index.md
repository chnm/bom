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
summary: "This visualization shows the data quality patterns for Bills of Mortality records by parish and week. You can examine either illegible records (difficult to read or transcribe) or missing records (incomplete data) to understand temporal and geographic patterns in data quality issues."
---

This visualization shows the data quality patterns for Bills of Mortality records by parish and week. You can examine either illegible records (difficult to read or transcribe) or missing records (incomplete data) to understand temporal and geographic patterns in data quality issues.

<div id="row">
    <h3 id="chart-title">Data Quality by Week</h3>
    <div class="viz-controls">
        <div class="viz-field is-narrow">
            <label for="year" class="viz-label">Year:</label>
            <select id="year" class="viz-select">
                <option value="">Loading years...</option>
            </select>
        </div>
        <div class="viz-field">
            <label for="quality-type" class="viz-label">Quality Issue:</label>
            <select id="quality-type" class="viz-select">
                <option value="">Loading...</option>
            </select>
        </div>
        <div class="viz-actions">
            <button id="update-button" type="button" class="viz-button is-rounded">Update</button>
        </div>
    </div>
    <div id="summary-stats" class="viz-stats"></div>
    <div id="chart" class="chart-frame"></div>
    <div class="viz-note">
        <strong>Color Legend:</strong> 
        <span style="color: #047857;">■ Good</span> (no data quality issues),
        <span style="color: #b45309;">■ Partial Issues</span> (some records have issues),
        <span style="color: #b91c1c;">■ All Issues</span> (all records have issues),
        <span style="color: #6b7280;">■ No Data</span> (no records available).
    </div>
    <figcaption>This visualization helps identify temporal patterns in data quality, which may correspond to different scribes, paper quality issues, or historical events affecting record-keeping. The number of records refers to whether one of the "buried" values or "plague" values or both are missing for a given parish. The data updates regularly as new transcriptions are added to the database.</figcaption>
    <p><a href="#top">Return to top</a></p>
</div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

---
title: "Arithmetic Accuracy Explorer"
date: 2026-09-08
draft: true
abstract: "Explore when printed weekly subtotals agree with parish-summed mortality counts"
summary: "Interactive view of weekly differences between printed subtotals and parish-summed counts."
script: visualizations/arithmetic-accuracy/main.js
styles: visualizations/arithmetic-accuracy/style.css
layout: visualizations
thumbnail: arithmetic-accuracy.png
thumbdesc: "Heatmap of weekly arithmetic differences in the London Bills of Mortality."
author:
  - Jessica Otis
  - Jason Heppler
category: "project-data"
---

Printed weekly bills reported subtotals for groups of London parishes. This explorer compares those printed subtotals with totals calculated from the individual parish entries.

<div id="arithmetic-explorer" aria-busy="true">
  <div class="explorer-controls" aria-label="Visualization controls">
    <label id="count-control">
      <span>Count</span>
      <select id="count-type">
        <option value="buried">Burial counts</option>
        <option value="plague">Plague counts</option>
      </select>
    </label>
    <label id="scope-control">
      <span>Include</span>
      <select id="data-scope">
        <option value="all">All comparable weeks</option>
        <option value="legible">Legible weeks only</option>
      </select>
    </label>
    <label id="year-control">
      <span>Detail year</span>
      <select id="detail-year"></select>
    </label>
  </div>
  <p id="explorer-status" class="explorer-status" role="status" aria-live="polite">Loading the archived article data...</p>
  <section id="weekly-panel" class="explorer-panel">
    <div id="weekly-summary" class="summary-grid" aria-label="Weekly data summary"></div>
    <div class="chart-card">
      <div class="chart-heading">
        <div>
          <p class="eyebrow">Long-run overview</p>
          <h3 id="weekly-overview-title">Arithmetic differences by year and week</h3>
        </div>
        <div class="difference-legend" aria-label="Difference color legend">
          <span><i class="legend-swatch negative"></i> Parish sum larger</span>
          <span><i class="legend-swatch exact"></i> Exact match</span>
          <span><i class="legend-swatch positive"></i> Printed subtotal larger</span>
          <span><i class="legend-swatch missing"></i> Unavailable or excluded</span>
        </div>
      </div>
      <div id="weekly-overview" class="plot-container"></div>
      <p class="chart-note">Color intensity represents the logarithm of the difference, allowing small and unusually large discrepancies to remain visible together. The outlined column is the selected detail year.  Click any column to select it.</p>
    </div>
    <div class="chart-card detail-card">
      <div class="chart-heading">
        <div>
          <p class="eyebrow">Selected-year detail</p>
          <h3 id="weekly-detail-title">Weekly differences</h3>
        </div>
      </div>
      <div id="weekly-detail" class="plot-container"></div>
      <details class="data-table-disclosure">
        <summary>View the selected year as a table</summary>
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Week</th>
                <th scope="col">Printed subtotal</th>
                <th scope="col">Parish sum</th>
                <th scope="col">Difference</th>
                <th scope="col">Legible</th>
              </tr>
            </thead>
            <tbody id="weekly-table-body"></tbody>
          </table>
        </div>
      </details>
    </div>
  </section>
  <div id="explorer-error" class="explorer-error is-hidden" role="alert"></div>
  <footer class="explorer-footer">
    <div>
      <strong>Publication snapshot</strong>
      <span id="snapshot-label">Loading version information…</span>
    </div>
    <nav aria-label="Download explorer data">
      <a href="/data/arithmetic-accuracy/weekly-differences.csv" download>Weekly CSV</a>
    </nav>
  </footer>
  <noscript>This explorer requires JavaScript. The complete derived data remain available from the CSV download link above.</noscript>
</div>

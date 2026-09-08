---
title: "Arithmetic Accuracy Explorer"
date: 2026-09-08
draft: true
abstract: "Explore when printed weekly subtotals agree with parish-summed mortality counts"
summary: "Interactive views of weekly arithmetic differences, the effect of excluding illegible bills, and the relationship between legibility and arithmetic-error rates."
script: visualizations/arithmetic-accuracy/main.js
styles: visualizations/arithmetic-accuracy/style.css
layout: visualizations
thumbnail: arithmetic-accuracy.png
thumbdesc: "Scatterplot comparing the legibility of weekly bills with their arithmetic-error rate."
author:
  - Jessica Otis
  - Jason Heppler
category: "project-data"
---

Printed weekly bills reported subtotals for groups of London parishes. This
explorer compares those printed subtotals with totals calculated from the
individual parish entries. It uses the archived dataset prepared for the
article rather than the changing live database.

<div id="arithmetic-explorer" aria-busy="true">
  <div class="explorer-tabs" role="tablist" aria-label="Arithmetic accuracy views">
    <button type="button" role="tab" data-view="weekly" aria-selected="true">Weekly differences</button>
    <button type="button" role="tab" data-view="comparison" aria-selected="false">All vs. legible</button>
    <button type="button" role="tab" data-view="legibility" aria-selected="false">Legibility &amp; errors</button>
  </div>
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
  <p id="explorer-status" class="explorer-status" role="status" aria-live="polite">Loading the archived article data…</p>
  <section id="weekly-panel" class="explorer-panel" role="tabpanel">
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
      <p class="chart-note">Color intensity represents the signed logarithm of the difference, allowing small and unusually large discrepancies to remain visible together. The outlined column is the selected detail year; click any column to select it.</p>
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
  <section id="comparison-panel" class="explorer-panel is-hidden" role="tabpanel">
    <div id="comparison-summary" class="summary-grid" aria-label="Annual comparison summary"></div>
    <div class="chart-card">
      <div class="chart-heading">
        <div>
          <p class="eyebrow">Annual comparison</p>
          <h3 id="comparison-title">All data compared with legible-only data</h3>
        </div>
        <div class="difference-legend" aria-label="Legibility legend">
          <span><i class="legend-dot ordinary"></i> Some illegible weeks</span>
          <span><i class="legend-dot fully"></i> Every observed week legible</span>
        </div>
      </div>
      <div id="comparison-chart" class="plot-container"></div>
      <p class="chart-note">The dashed diagonal is a 1:1 reference line. Points above it have a larger mean difference when illegible weeks are retained.</p>
    </div>
  </section>
  <section id="legibility-panel" class="explorer-panel is-hidden" role="tabpanel">
    <div id="legibility-summary" class="summary-grid" aria-label="Legibility and arithmetic-error summary"></div>
    <div class="chart-card">
      <div class="chart-heading">
        <div>
          <p class="eyebrow">Annual relationship, 1663–1752</p>
          <h3>Legible weekly bills and arithmetic-error rates</h3>
        </div>
      </div>
      <div id="legibility-chart" class="plot-container"></div>
      <p class="chart-note">The fitted line and shaded 95% confidence interval summarize the annual relationship; they do not imply that legibility causes arithmetic accuracy.</p>
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
      <a href="/data/arithmetic-accuracy/annual-comparison.csv" download>Annual comparison CSV</a>
      <a href="/data/arithmetic-accuracy/legibility-error-rate.csv" download>Legibility CSV</a>
    </nav>
  </footer>
  <noscript>This explorer requires JavaScript. The complete derived data remain available from the CSV download links above.</noscript>
</div>

### How to read the explorer

An arithmetic difference is the printed subtotal minus the sum of the individual
parish counts. Positive values mean that the printed subtotal is larger; negative
values mean that the parish sum is larger. A week is classed as legible only when
neither its parish counts nor its printed subtotal contains a value marked
illegible.

The archived source files are verified by byte size and SHA-256 checksum before
these derived data are produced. Missing observations are never interpolated.


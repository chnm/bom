---
title: "Parish Deaths"
date: 2025-03-24
updated: 2025-04-30
abstract: "Sparklines of plague and non-plague parish deaths"
summary: "Multiple sparkline visualization showing temporal patterns of parish deaths with data normalization options (log10, normalized) and filtering by burial type (burials, plague, both) for improved visibility of smaller count variations."
script: visualizations/sparklines/main.js
styles: visualizations/sparklines/style.css
layout: visualizations
thumbnail: sparklines.png
thumbdesc: "A screenshot of multiple sparklines of parish deaths"
author:
- Savannah Scott
- Jason Heppler
category: "temporal"
---
<p>Because the range of total deaths varies significantly, it can be difficult to see the smaller counts on these graphs. Normalizing the data can improve visibility by removing drastic range differences. The two normalization options are log<sub>10</sub>(x+1) and normalized. <strong>Log<sub>10</sub>(x+1)</strong> transforms the data by adding one before taking the logarithm, which preserves zero values and mitigates right-skewed datasets, making them a more normal distribution. <strong>Normalized</strong> standardizes the data with extent normalization, which maps the minimum to zero and the maximum to one. Both make smaller values more visible, and make comparison easier.</p>
<div id="row">
    <h4>Modify data:</h4>
    <div class="viz-controls is-wrapping">
          <fieldset class="viz-field is-spaced" id="data-format">
            <legend class="viz-label is-large" for="data-format">
              Data Format:
            </legend>
            <div>
                <div>
                   <input type="radio" id ="original" name="data-format" value="original" checked/>
                    <label for="original">original</label>
                </div>
                <div>
                    <input type="radio" id="log10(x+1)" name="data-format" value="log10(x+1)"/>
                    <label for="log10(x+1)">log10(x+1)</label>
                </div>
                <div>
                    <input type="radio" id="normalized" name="data-format" value="normalized"/>
                    <label for="normalized">normalized</label>
                </div>
            </div>
          </fieldset>
          <fieldset class="viz-field is-spaced" id="count-type">
            <legend class="viz-label is-large" for="count-type">
              Count Type:
            </legend>
            <div>
                <input type="radio" id="burials" name="count-type" value="burials" checked/>
                <label for="burials">burials</label>
            </div>
            <div>
                <input type="radio" id="plague" name="count-type" value="plague"/>
                <label for="plague">plague</label>
            </div>
            <div>
                <input type="radio" id="both" name="count-type" value="both"/>
                <label for="both">both</label>
            </div>
          </fieldset>
          <div class="viz-actions is-pair">
            <button id="update-button" type="button" class="viz-button is-large">Update</button>
            <button id="reset-button" type="button" class="viz-button is-large">Reset</button>
          </div>
    </div>
</div><br>
<div id="facets" class="chart-frame"></div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

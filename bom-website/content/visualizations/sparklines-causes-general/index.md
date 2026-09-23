---
title: "Causes of Death (General Bills)"
date: 2024-12-12
updated: 2024-12-12
abstract: "Sparklines of Causes of Deaths from General Bills"
script: visualizations/sparklines-causes-general/main.js
styles: visualizations/sparklines-causes-general/style.css
layout: visualizations
thumbnail: sparklines-causes.png
thumbdesc: "A screenshot of multiple sparklines of causes of deaths"
author:
- Savannah Scott
category: "temporal"
summary: "Because the range of total deaths varies significantly, it can be difficult to see the smaller counts on these graphs. Normalizing the data can improve visibility by removing drastic range differences. The two normalization options are log<sub>10</sub>(x+1) and normalized. <strong>Log<sub>10</sub>(x+1)</strong> transforms the data by adding one before taking the logarithm, which preserves zero values and mitigates right-skewed datasets, making them a more normal distribution. <strong>Normalized</strong> standardizes the data with mean normalization, which subtracts the average from each value. Both make smaller values more visible, and make comparison easier.."
---
<p>This visualization shows causes of death from the <strong>annual general bills of mortality</strong>. For causes of death from the weekly bills, see the [Weekly Bills sparklines visualization](/visualizations/sparklines-causes/).</p>

<p>Because the range of total deaths varies significantly, it can be difficult to see the smaller counts on these graphs. Normalizing the data can improve visibility by removing drastic range differences. The two normalization options are log<sub>10</sub>(x+1) and normalized. <strong>Log<sub>10</sub>(x+1)</strong> transforms the data by adding one before taking the logarithm, which preserves zero values and mitigates right-skewed datasets, making them a more normal distribution. <strong>Normalized</strong> standardizes the data with mean normalization, which subtracts the average from each value. Both make smaller values more visible, and make comparison easier.</p>
<p>The <strong>remove plague deaths</strong> option graphs all causes of death except plague. Plague deaths are the primary outlier due to the outbreak in 1665. Removing the plague deaths allows greater visibility for smaller values with the original dataset.</p>
<div id="row">
    <h4>Choose your preferences</h4>
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
                    <label for="log10(x+1)">log<sub>10</sub>(x+1)</label>
                </div>
                <div>
                    <input type="radio" id="normalized" name="data-format" value="normalized"/>
                    <label for="normalized">normalized</label>
                </div>
            </div>
          </fieldset>
          <fieldset id="plague-format">
            <legend class="sr-only">Plague filtering</legend>
            <div>
                <input type="checkbox" id="plague" name="plague-format"/>
                <label for="plague">Remove Plague Deaths</label>
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

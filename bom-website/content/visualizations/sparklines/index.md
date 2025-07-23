---
title: "Parish Deaths"
date: 2025-03-24
updated: 2025-04-30
abstract: "Sparklines of plague and non-plague parish deaths"
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
    <div class="flex flex-wrap items-center space-x-4 mb-6">
          <fieldset class="flex flex-col space-y-2" id="data-format">
            <legend class="block text-gray-700 text-base font-bold" for="data-format">
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
                    <input type="radio" id="normailzed" name="data-format" value="normalized"/>
                    <label for="normalized">normalized</label>
                </div>
            </div>
          </fieldset>
          <fieldset class="flex flex-col space-y-2" id="count-type">
            <legend class="block text-gray-700 text-base font-bold" for="count-type">
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
          <div class="flex space-x-2 ml-auto mt-5">
            <button id="update-button" type="button" class="rounded-l-lg border border-gray-200 bg-white text-base font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-black focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Update</button>
            <button id="reset-button" type="button" class="rounded-r-md border border-gray-200 bg-white text-base font-medium px-4 py-2 text-gray-900 hover:bg-dbn-blue hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700">Reset</button>
          </div>
    </div>
</div><br>
<div id="facets"></div>

### Suggested citation

Please use the following as a suggested citation:

{{< citation >}}

---
title: "Parish Deaths"
created: 2025-03-24
updated: 2025-03-24
abstract: "Sparklines of plague and non-plague parish deaths"
script: visualizations/sparklines/main.js
styles: visualizations/sparklines/style.css
layout: visualizations
thumbnail: sparklines.png
thumbdesc: "A screenshot of multiple sparklines of parish deaths"
author:
---
<div id="row">
    <h4>Choose your preferences</h4>
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
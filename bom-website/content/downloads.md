---
title: Data Downloads
slug: /downloads/
---

We provide multiple ways to use and interact with the data generated through this project. If you prefer to access the data from our online database directly through the data API, please consult the [data API's documentation](/api/). The data has been rearranged into a long format and returns JSON objects across weekly and general bills, christenings, causes of death, and foodstuffs. 

Data can be downloaded as comma-separated value (CSV) documents, which are available [on our Github repository](https://github.com/chnm/bom/tree/main/bom-data/).

The primary downloadable datasets are as follows
- data transcribed from the [bills of mortality](https://github.com/chnm/bom/tree/main/bom-data/data-csvs), whose filenames can be generally translated as follows:
    - YYYY-MM-DD: date last updated
    - Bodleian/BL/HEH/Laxton/Millar/QC/Wellcome: document source
    - weeklybills: weekly data
    - generalbills: annual data
    - parishes: parish-by-parish counts of plague mortality and total mortality
    - causes: city-wide (including local suburbs) counts for various causes of death
    - gender: city-wide (including local suburbs) christenings and burials broken down into male and female
    - foodstuffs: city-wide data on the prices of various foodstuffs, primarily bread
- [death dictionary](https://github.com/chnm/bom/blob/main/bom-data/2025-01-31-deathdictionary.csv)
- [geoJSON files](https://github.com/chnm/bom/tree/main/bom-data/geoJSON-files) for the parishes over time
- [node and edge lists](https://github.com/chnm/bom/tree/main/bom-data/parish-networks) for the parish network over time
- [shapefiles](https://github.com/chnm/bom/tree/main/bom-data/parish-shapefiles) for the parishes over time, including a [parish name authority file](https://github.com/chnm/bom/blob/main/bom-data/parish-shapefiles/2023-02-08-London-parishes-authority-file.csv)

The READMEs in the repostitories further describe the contents of the datasets. The weekly and annual bills of mortality CSVs are arranged as wide tables and are exports from [DataScribe](https://datascribe.tech).

The supporting data for our article publications can be found below:

<table class="data-table">
    <thead>
        <tr class="table-header">
            <th class="table-cell">Citation</th>
            <th class="table-cell">Data</th>
        </tr>
    </thead>
    <tbody>
        <tr class="table-row">
            <td class="table-cell description-cell">Jessica M. Otis and Katherine Kania, "<a href="https://www.tandfonline.com/eprint/CEY8KQIIISAAYRQNEP9T/full?target=10.1080/03058034.2025.2572138">The Monarchs' Bills of Mortality: A Geographical Analysis of Death in Seventeenth-Century London</a>," <i>The London Journal</i> (forthcoming).</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/monarchical-bills" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell description-cell">Jason A. Heppler and Jessica M. Otis, "‘To Number the Days of a Man’: Arithmetic and the London Bills of Mortality, 1636–1752" (under review)</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-processing/scripts/bompy/data/2025-11-ArchivalCopyofArticleData" class="download-link">Download</a></td>
        </tr>
    </tbody>
</table>

Please feel free to contact us if you have questions about downloading or using these datasets.

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

<!-- 


<table class="data-table">
    <thead>
        <tr class="table-header">
            <th class="table-cell" style="width: 200px;">Files</th>
            <th class="table-cell">Description</th>
            <th class="table-cell">Download</th>
        </tr>
    </thead>
    <tbody>
        <tr class="table-row">
            <td class="table-cell file-name">Bodleian V1, V2, V3, and V4 Weekly Bills Parishes</td>
            <td class="table-cell description-cell">Bodleian Weekly Bills Parishes contains mortality information from weekly bills published in the 1630s through 1670s. It contains parish-by-parish counts of plague mortality and total mortality for the parish, along with subtotals and totals of christenings (births registered within the Church of England) and burials (deaths registered within the Church of England).</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Bodleian V1, V2, V3, and V4 Weekly Bills Causes</td>
            <td class="table-cell description-cell">Bodleian Weekly Bills Causes contains mortality information from weekly bills published in the 1630s through 1670s. It contains city-wide (including local suburbs) death counts for various causes of death, along with information about christenings (births registered within the Church of England), burials (deaths registered within the Church of England), plague deaths, and bread prices.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Wellcome Weekly Bills 1669-1670 Parishes</td>
            <td class="table-cell description-cell">Wellcome Weekly Bills 1669-1670 Parishes contains mortality information from weekly bills published in the late 17th century. It contains parish-by-parish counts of plague mortality and total mortality for the parish, along with subtotals and totals of christenings (births registered within the Church of England) and burials (deaths registered within the Church of England).</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Wellcome Weekly Bills 1669-1670 Causes</td>
            <td class="table-cell description-cell">Wellcome Weekly Bills Causes contains mortality information from weekly bills published in the late 17th century. It contains city-wide (including local suburbs) death counts for various causes of death, along with information about christenings (births registered within the Church of England), burials (deaths registered within the Church of England), plague deaths, and bread prices.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Laxton 1700 Weekly Bills Causes</td>
            <td class="table-cell description-cell">Laxton 1700 Weekly Bills Causes contains mortality information from weekly bills published in the year 1700. It contains city-wide (including local suburbs) death counts for various causes of death.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Laxton 1700 Weekly Bills Gender</td>
            <td class="table-cell description-cell">Laxton 1700 Weekly Bills Gender contains demographic statistics by gender from weekly bills published in the year 1700.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Laxton 1700 Weekly Bills Foodstuffs</td>
            <td class="table-cell description-cell">Laxton 1700 Weekly Bills Foodstuffs contains food prices from weekly bills published in the year 1700. There are various types of bread and also salt.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Laxton Weekly Bills Parishes</td>
            <td class="table-cell description-cell">Laxton Old Weekly Bills Parishes contains mortality information from weekly bills published in the early 18th century. It contains parish-by-parish counts of total mortality for the parish along with subtotals and totals of christenings (births registered within the Church of England) and burials (deaths registered within the Church of England). It uses the old transcription conventions, as compared to Laxton New Weekly Bills Parishes (forthcoming), which will use the new conventions.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Laxton Weekly Bills Causes</td>
            <td class="table-cell description-cell">Laxton Old Weekly Bills Causes contains mortality information from weekly bills published in the early eighteenth century. It contains city-wide (including local suburbs) death counts for various causes of death. It uses the old transcription conventions, as compared to Laxton New Weekly Bills Causes (forthcoming), which will use the new conventions.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Millar General Bills Pre-Plague Parishes</td>
            <td class="table-cell description-cell">Millar General Bills PrePlague Parishes contains mortality information from "general" or annual summary bills published in the early 18th century. It contains parish-by-parish counts of plague mortality and total mortality for the parish along with subtotals and totals of christenings (births registered within the Church of England) and burials (deaths registered within the Church of England).</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">Millar General Bills Post-Plague Parishes</td>
            <td class="table-cell description-cell">Contains parish-by-parish counts of total mortality for the parish along with subtotals and totals of christenings in the early 18th century.</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">BL Weekly Bills Parishes</td>
            <td class="table-cell description-cell">BL Weekly Bills Parishes contains mortality information from weekly bills published from the 1660s onwards. It contains parish-by-parish counts of plague mortality and total mortality for the parish, along with subtotals and totals of christenings (births registered within the Church of England) and burials (deaths registered within the Church of England).</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
        <tr class="table-row">
            <td class="table-cell file-name">HEH1635 Weekly Bills Parishes</td>
            <td class="table-cell description-cell">HEH1635 Weekly Bills Parishes contains mortality information from a single weekly bill from 1635. It contains parish-by-parish counts of plague mortality and total mortality for the parish, along with subtotals and totals of christenings (births registered within the Church of England) and burials (deaths registered within the Church of England).</td>
            <td class="table-cell download-cell"><a href="https://github.com/chnm/bom/tree/main/bom-data/data-csvs" class="download-link">Download</a></td>
        </tr>
    </tbody>
</table>
 -->

Please feel free to contact us if you have questions about downloading or using these datasets.
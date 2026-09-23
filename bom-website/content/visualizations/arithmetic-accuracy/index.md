---
title: "Arithmetic Accuracy"
date: 2026-09-22
draft: true
abstract: "Compare printed weekly subtotals with parish-summed mortality counts"
summary: "Interactive view of weekly differences between printed subtotals and parish-summed counts, drawn live from the Death by Numbers API."
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

Printed weekly bills reported subtotals for groups of London parishes. This explorer compares those printed subtotals with totals calculated from the individual parish entries, using the current Death by Numbers database rather than a fixed snapshot, so it reflects corrections and new transcriptions as they are added.

{{< arithmetic-explorer api="https://data.chnm.org/bom/arithmetic" >}}

### How these figures are calculated

An arithmetic difference is the printed subtotal minus the sum of the individual parish counts. Positive values mean the printed subtotal is larger; negative values mean the parish sum is larger. Only weekly bills are included, and the Westminster pesthouse is left out of the parish sums because the printed subtotals do not include it. A week counts as legible only when none of its parish counts or subtotals is marked illegible.

Some weeks survive in more than one copy, and the copies do not always agree. Where that happens the database keeps the largest readable value for each parish and each subtotal, so a week's figures can come from different copies. Those weeks are marked as mixed copies: a difference there may reflect disagreement between copies rather than an error on a single printed bill. A few different bills also share the same week number; the table and detail chart list each one with its dates.

Because of these choices, and because the data continue to change, figures here can differ from the archived analysis published with our article on arithmetic accuracy.

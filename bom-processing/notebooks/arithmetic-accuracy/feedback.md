I have several comments on the presentation of the data in the tables and graphs accompanying the text.
1. In Tables 2,3, and 4, "math error" is better described as "arithmetic error."
2. The graphs in Figures 4, 5 and 9 are every hard to read. I had to use a magnifying glass to read the axis titles and labels, and, even then it was not particularly easy. In Figures 3 and 4, "Exact match" is colour-coded purple. However an exact match corresponds to 0 numerically and so no purple spikes or dots appear on the graph,
3. Figure 4 presents at time series. A time series analysis could be carried out to see if the series is merely random noise or follows a model such as an autoregressive-moving average model or something else.
4. I have problems understanding Figures 4 and 5 together. The only difference between two appears to be that Figure 4 includes all bills and Figure 5 includes only legible bills. Are there some years where the fills are all legible so that the error for the year would be the same in both graphs? This not obvious from the two graphs. A graph to examine this issue would be a scatterplot showing the differences in the legible bills on the x-axis and the differences in all bills on the y-axis.
5. Figures 4 and 5 could be rotated by 90 degrees. The would allow for a larger, more readable graph,
6. Figure 9 should be deleted and replaced. The y-axis presents two different types of measurements on the same axis and so can be confusing. It is also difficult to discern the relationship between the two variables with this graph. Figure 9 should be replaced by a scatterplot. If you want to ask the question, "Does the error rate change with the percentage legible bills?", then the error rate should be displayed on the y-axis and the percentage on the x-axis. Depending on what this graph looks like there may be a model that explains the relationships between the two variables.

## Revision work plan

### 1. Terminology in Tables 2–4

- [ ] Replace "math error" with "arithmetic error" in the manuscript/table source.
- Manuscript source: `Manuscript_anonymous.docx`, Tables 2–4 (rendered pages 2–4) and their entries in the captions list (page 12).
- The exact phrase does not occur in the notebooks. The notebook headings currently use "Mathematical Accuracy Analysis"; these can also be changed to "Arithmetic Accuracy Analysis" for consistency.

### 2 and 5. Readability of Figures 4 and 5

- Likely notebook sources:
  - Figure 4: `02a_mathematical_accuracy_original_data.ipynb`, cell 28 (all data).
  - Figure 5: `02c_mathematical_accuracy_illegible_weeks_removed.ipynb`, cell 39 (weeks containing illegible data removed).
- Manuscript locations: Figure 4 on rendered page 6 and Figure 5 on rendered page 7.
- The feedback refers to the "Exact match" legend in Figures 3 and 4, but Figure 3 in the supplied manuscript is the DataScribe screenshot. The legend appears in Figures 4 and 5, so the revision will treat that reference as a numbering slip.
- [ ] Remove "Perfect Match" from the categorical legend. Exact matches have a difference of zero and are already represented by the horizontal zero reference line.
- [ ] Increase label, tick, and legend sizes and simplify the titles.
- [ ] Produce publication-ready landscape versions, including vector PDF/SVG output and a high-resolution PNG preview.
- [ ] Repair the clipped layout in the legible-only figure.

### 3. Time-series analysis for Figure 4

- [ ] Construct a properly ordered weekly series with explicit missing weeks rather than treating observed rows as an uninterrupted sequence.
- [ ] Examine the signed arithmetic difference and an absolute-error series separately; the signed series can hide errors through cancellation.
- [ ] Report descriptive trend/seasonality checks, autocorrelation diagnostics, and a white-noise test.
- [ ] Fit an ARMA/ARIMA-family model only if the diagnostics and data coverage support one; otherwise report evidence that the series is indistinguishable from noise or too discontinuous for that model.

### 4. Direct comparison of all-data and legible-only results

- [ ] Create a paired scatterplot by year rather than asking readers to compare two dense weekly plots visually.
- Proposed x-axis: annual mean absolute arithmetic difference after excluding weeks containing illegible data.
- Proposed y-axis: annual mean absolute arithmetic difference using all data.
- [ ] Add a 1:1 reference line and distinguish years in which every observed week is legible. Those years should fall on the 1:1 line.
- [ ] Report the number of paired years and a correlation or robust regression summary as appropriate.

### 6. Replace Figure 9

- Current source: `04_general_bills_subtotals.ipynb`, cell 36.
- Manuscript location: rendered page 11.
- [ ] Delete the dual-axis line chart from the revised figure set.
- [ ] Define annual arithmetic error rate as the percentage of comparable weekly observations for which the printed subtotal differs from the parish-summed count.
- [ ] Define percentage legible as 100 minus the percentage of weekly bills containing any illegible value.
- [ ] Plot percentage legible on the x-axis and arithmetic error rate on the y-axis, with one point per year.
- [ ] Add a fitted relationship and uncertainty interval only if supported, and report the model specification and diagnostics in the text or supplement.

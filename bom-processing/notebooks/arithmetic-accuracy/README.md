# Arithmetic accuracy revision analysis

This directory preserves the seven original analysis notebooks and adds a focused,
reproducible workflow for the revise-and-resubmit changes to Tables 2–4 and Figures
4, 5, and 9. `Manuscript_anonymous.docx` is reference material only and is not
modified by this workflow.

The revised analysis uses the repository's
`2025-11-ArchivalCopyofArticleData` snapshot. The loader prefers complete local
Git LFS files. If the checkout contains only LFS pointer files, it downloads the
same objects from the immutable repository commit recorded in `analysis.py`,
stores them in `data-cache/`, and verifies both byte size and SHA-256.

## Local setup with uv

From this directory:

```bash
uv sync
uv run pytest
uv run python analysis.py
uv run jupyter lab
```

`uv run python analysis.py` downloads any missing data and creates publication
figures in `figures/`, analysis tables in `tables/`, and a concise statistical
summary in `tables/revision_results.md`. When the full repository checkout is
available, the same command also refreshes the versioned data files and thumbnail
for the standalone website explorer at `/visualizations/arithmetic-accuracy/`.

To execute the notebook non-interactively:

```bash
uv run jupyter nbconvert \
  --to notebook \
  --execute 05_reviewer_revisions.ipynb \
  --output 05_reviewer_revisions.executed.ipynb \
  --ExecutePreprocessor.timeout=1200
```

Set `BOM_DATA_DIR` to use an existing directory containing the five required CSV
files. Set `BOM_DATA_REF` only when intentionally testing a different repository
revision; the default is the archived-data commit recorded in `analysis.py`.

## Google Colab

After the working branch has been published, open a Colab notebook, clone the
repository with a sparse checkout, and install the analysis dependencies:

```python
!git clone --filter=blob:none --no-checkout https://github.com/chnm/bom.git
!git -C bom sparse-checkout init --cone
!git -C bom sparse-checkout set bom-processing/notebooks/arithmetic-accuracy bom-processing/scripts/bompy/data/2025-11-ArchivalCopyofArticleData
!git -C bom fetch origin writing/mathematical-accuracy
!git -C bom checkout -B writing/mathematical-accuracy FETCH_HEAD
%cd bom/bom-processing/notebooks/arithmetic-accuracy
%pip install -q pandas numpy matplotlib scipy statsmodels
```

Then run `05_reviewer_revisions.ipynb`. Git LFS is not required in Colab: the
loader detects pointer files, downloads the pinned objects into `data-cache/`,
and verifies them before reading.

## Outputs

- `figures/figure_4_all_bills.*`: larger landscape weekly arithmetic differences.
- `figures/figure_5_legible_bills.*`: the same view after removing every week
  containing an illegible parish count or printed subtotal.
- `figures/figure_4_5_annual_comparison.*`: paired annual mean absolute
  differences with a 1:1 reference line and fully legible years distinguished.
- `figures/figure_9_legibility_error_rate.*`: replacement scatterplot with
  percentage legible weeks on the x-axis and arithmetic-error rate on the y-axis.
- `tables/tables_2_4_terminology.md`: exact terminology changes to apply later to
  the manuscript and caption list.
- `tables/time_series_diagnostics.csv`: coverage, trend, autocorrelation,
  white-noise, and conditional ARMA-family results for Figure 4.
- `bom-website/static/data/arithmetic-accuracy/`: compact JSON used by the
  interactive explorer plus downloadable weekly and annual CSVs.

The original notebooks remain historical records. New revision code belongs in
`analysis.py` and `05_reviewer_revisions.ipynb` so the source analysis is not
silently rewritten.

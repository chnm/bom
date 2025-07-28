# London Bills of Mortality

Main project repo for Death by Numbers, a project on the London Bills of Mortality. This is our "monorepo" of all content related to the project. These are broken down into a few different areas (please consult these directory's individual READMEs for more information.)

- **bom-data**: Data files (CSVs, Excel files, and shapefiles) and exports from the transcribed bills of mortality.
- **bom-processing**: R and Python Scripts, database migrations, and scripts for making maps.
- **bom-website**: The website for deathbynumbers.org, built with the static-site generator Hugo and custom dbn theme.

## Updating the website

For project members wishing to update the website, but not have to clone the entire repository, here are the steps to follow.

1. Open Terminal. From here, navigate to where you'd like the directory to
   live (e.g., `cd ~/Dropbox/work`).
2. From here, you'll do a sparse checkout.

```
git clone --depth 1 --filter=blob:none --sparse https://github.com/chnm/bom
```

3. Change into the cloned directory (`cd bom`). The folder should be empty. 
4. Now, you can grab the website files: `git sparse-checkout set bom-website`

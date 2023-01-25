# London Bills of Mortality

Main project repo for Death by Numbers, a project on the London Bills of Mortality. 

- **api-docs** contains documentation for the API
- **data-csvs** contains data exports from the Bills of Mortality 
- **DataScribe installation**; these data exports will form the basis for the csvs shared through deathbynumbers.org and are what researchers interested in an early look at our data should consult

db contains
- **parish-shapefiles** contains shapefiles for the parishes contained within the Bills of Mortality, as they changed over time

mapping contains
- **monarchical-bills** contains a catalog of extant reports to the monarch, in-progress transcriptions, and a parish name crosswalk

scripts contains
- The BOM Catalog Excel file is in progress and does not contain all bills known to the project; it currently focuses on bills from the 1630s-1690s
0 For the Bills of Mortality database code, see `/bom-db`
- Files associated with the early stage of this project are also available at https://github.com/jmotis/billsofmortality

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

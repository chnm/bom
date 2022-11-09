#! /usr/bin/env python3 

import pandas as pd

# Read in the DataScribe exports as Pandas dataframes.
# -----------------------------------------------------
raw_laxton_1700_foodstuffs = pd.read_csv('Laxton 1700-1799 Foodstuffs.csv')
raw_laxton_foodstuffs = pd.read_csv('Laxton Foodstuffs.csv')
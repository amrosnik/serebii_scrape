import pandas as pd
#import pokescrape as scrape
import numpy as np

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 16)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 

df = pd.read_pickle("./joined_table_pickle.pkl")

## best and worst in each category
## TODO: figure out a way to print this out better
stat_categories = df.columns.values.tolist()[-8:]
"""
for stat in stat_categories:
    print("********** POKEMON WITH HIGHEST ",stat," **********")
    print(df.iloc[df[stat].idxmax()])
    print("********** POKEMON WITH LOWEST ",stat," **********")
    print(df.iloc[df[stat].idxmin()])
"""

## let's double-check that the Total and Average columns are correct
df['amr_total'] = df.iloc[:, -8:-2].sum(axis=1)
df['Average'] = round(df['Average'],1)
df['amr_mean'] = df.iloc[:, -9:-3].mean(axis=1) 
df['amr_mean'] = round(df['amr_mean'],1)
diff_total = np.where(df['amr_total'] != df['Total'])
diff_mean = np.where(df['amr_mean'] != df['Average'])
## these are expected to be (array([], dtype=int64),), so len=1
if len(diff_total) > 1:
    print("uh oh, totals were calculated incorrectly.")
if len(diff_mean) > 1:
    print("uh oh, means were calculated incorrectly.")
if len(diff_total) == 1 and len(diff_mean) == 1:
    df = df.drop(['amr_mean','amr_total'], axis=1)

## most even keel (lowest stdev)
df['stdev'] = df.iloc[:, -8:-2].std(axis=1) 
df['stdev'] = round(df['stdev'],1)
print(df.iloc[df['stdev'].idxmax()])
print(df.iloc[df['stdev'].idxmin()])

## REALLY FUN TIME: let's look at best/worst by type.
## AND THEN average + stdev by type. and see which pokemon is closest to the average picture for its type.
## (try grouping pokemon with same primary + secondary types) 
## (also do the first approximation with only using the primary type) 
## (also do "pure" vs. "mixed" types for each type. "pure" meaning, pokemon with only one type. "mixed" otherwise.)

## look for patterns in stat distributions for each type. 

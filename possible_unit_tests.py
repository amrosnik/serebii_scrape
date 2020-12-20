import pandas as pd
import pokescrape as scrape
import numpy as np
import re 
import matplotlib.pyplot as plt
from itertools import chain 
import os 

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 16)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 

df = pd.read_pickle("./joined_table_pickle.pkl")

# TODO: possible unit tests here...originally done in base_stats_crunch.py ######


## paranoid check to make sure the new data structure is consistent with the old one
## good news, everyone: they are consistent! and I actually found an error in the old one.

old_df = pd.read_pickle("../../Downloads/early_joined_table_pickle.pkl")
for i in range(len(df)):
   #print(old_df.loc[i,'number'],old_df.loc[i,'type'],df.loc[i,'primary_type'],df.loc[i,'secondary_type'])
   stripped_old = old_df.loc[i,'type'].replace('[,\[\]]','')
   stripped_1 = df.loc[i,'primary_type'].replace('[,\[\]]','')
   stripped_2 = df.loc[i,'secondary_type'].replace('[,\[\]]','')
   if stripped_2 == "NONE":
       stripped_2 = " " 
   stripped_new = stripped_1 + " " + stripped_2
   if stripped_1 in str(old_df.loc[i,'type']):
       yay = 1 
   else:
       print("missing primary type")
       print(old_df.loc[i,'number'],old_df.loc[i,'type'],stripped_1,stripped_2)
   if stripped_2 != " ":
      if stripped_2 in str(old_df.loc[i,'type']):
          yay = 1 
      else:
          print("missing secondary type")
          print(old_df.loc[i,'number'],old_df.loc[i,'type'],stripped_1,stripped_2)

# TODO: transform this into a unit test of some kind
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

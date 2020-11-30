import pandas as pd
import pokescrape as scrape
import numpy as np
import re 

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 16)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 

df = pd.read_pickle("./joined_table_pickle.pkl")

## paranoid check to make sure the new data structure is consistent with the old one
## will delete eventually
## good news, everyone: they are consistent! and I actually found an error in the old one.
"""
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
exit(0)
"""
def form_or_type(df):
    formStandard = typeStandard = False
    regexp = re.compile(r'standard|normal|average|50|midday')
    if regexp.search(df['form_name']):
        formStandard = True 
    if regexp.search(df['type_name']):
        typeStandard = True
    if formStandard and typeStandard:
        variant = 'standard'
    elif formStandard and not typeStandard:
        variant = df['type_name']
    elif not formStandard and typeStandard:
        variant = df['form_name']
    else:
        variant = df['type_name']
    return(variant)
#TODO: test this code's logic on something other than use cases from best_and_worst()

def best_and_worst(df):
    ## best and worst in each category
    stat_categories = ['HP','Attack','Defense','Sp. Attack','Sp. Defense', 'Speed', 'Total','Average']
    best_worst_stats = pd.DataFrame()
    for stat in stat_categories:
        best = df.iloc[df[stat].idxmax()]
        worst = df.iloc[df[stat].idxmin()]
        best_variant = form_or_type(best)
        worst_variant = form_or_type(worst)
        new_row = {'stat': stat, 'best_variant': best_variant, 'best': best['name'], 'best_value': best[stat], 'worst_variant': worst_variant, 'worst': worst['name'], 'worst_value': worst[stat] }
        best_worst_stats = best_worst_stats.append(new_row,ignore_index=True)
    best_worst_stats = best_worst_stats[['stat','best_variant','best','best_value','worst_variant','worst','worst_value']]
    best_worst_stats['best_value'] = best_worst_stats['best_value'].astype('int32')
    best_worst_stats['worst_value'] = best_worst_stats['worst_value'].astype('int32')
    return(best_worst_stats)

best_worst = best_and_worst(df)
print("********* BEST AND WORST PER STAT ACROSS ALL POKEMON **********")
print(best_worst)
#exit(0)

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

## stdev perspective
df['stdev'] = df.iloc[:, -8:-2].std(axis=1) 
df['stdev'] = round(df['stdev'],1)
print("********* MOST AND LEAST WELL-ROUNDED ACROSS ALL POKEMON **********")
print(df.iloc[df['stdev'].idxmin()])
print(df.iloc[df['stdev'].idxmax()])

## let's look at best/worst by type.
simple_stats = pd.DataFrame()
for x in scrape.possible_types:
    print("********* NOW GROUPING FOR TYPE ",x," **********")
    primary_type_grouping = df[df['primary_type'].str.contains(x,regex=True,na=False)]
    primary_type_grouping = primary_type_grouping.reset_index()
    secondary_type_grouping = df[df['secondary_type'].str.contains(x,regex=True,na=False)]
    secondary_type_grouping = secondary_type_grouping.reset_index()
    ## get the type totals per each generation
    for j in range(1,9):
       generation_grp_1 = primary_type_grouping[(primary_type_grouping['generation']==j) & (primary_type_grouping['primary_type'] == x)]
       generation_grp_2 = secondary_type_grouping[(secondary_type_grouping['generation']==j) & (secondary_type_grouping['secondary_type'] == x)]
       new_row = {'type': x, 'primary': len(generation_grp_1), 'secondary': len(generation_grp_2), 'generation':j }
       simple_stats = simple_stats.append(new_row,ignore_index=True)

    ## append new row for total of each type across all generations
    new_row = {'type': x, 'primary': len(primary_type_grouping), 'secondary': len(secondary_type_grouping), 'generation': 999 }
    simple_stats = simple_stats.append(new_row,ignore_index=True)

    best_worst_1 = best_and_worst(primary_type_grouping)
    print(best_worst_1)
    print("********* NOW GROUPING FOR SECONDARY TYPE ",x," **********")
    best_worst_2 = best_and_worst(secondary_type_grouping)
    print(best_worst_2)

    #TODO: calculate the "average" Pokemon per type (+ calc stdev for stats, too!) 
    #TODO:see which pokemon is closest to the average picture for its type.
    ## first, do to  first approximation with only using the primary type, so only primary_type_grouping
    ## THEN group primary+secondary groupings together and repeat the calc  

    #TODO: look for patterns in stat distributions for each type.
    #TODO: make bar graphs to visualize the base stats for best/worst, avg, closest-to-avg by type.

simple_stats['primary'] = simple_stats['primary'].astype('int32')
simple_stats['secondary'] = simple_stats['secondary'].astype('int32')
simple_stats['generation'] = simple_stats['generation'].astype('int32')
simple_stats = simple_stats[['type','primary','secondary','generation']]
#print(simple_stats)
#TODO: plot the numbers of each primary and secondary type (bar graph) and how many of each type per generation




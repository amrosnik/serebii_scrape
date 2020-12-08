import pandas as pd
import pokescrape as scrape
import numpy as np
import re 
import matplotlib.pyplot as plt

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 16)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 

df = pd.read_pickle("./joined_table_pickle.pkl")

"""
## paranoid check to make sure the new data structure is consistent with the old one
## will delete eventually
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
exit(0)
"""

# ********** ********** # 
# ********** FUNCTION DEFINITIONS ********** # 
# ********** ********** # 

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

def avg_stdev_per_type(grp):
    ## calculate the average and stdev of each base stat for a given type 
    stat_categories = ['HP','Attack','Defense','Sp. Attack','Sp. Defense', 'Speed', 'Total','Average']
  
    # copy the structure of a Pokemon in the group, so that the average profile
    # can be outputted in the same format 
    avg_poke = grp.iloc[0].copy()
    avg_poke['name'] = 'AVERAGE_PROFILE_'+avg_poke['primary_type']
    avg_poke['number'] = 999 
    avg_poke['type_name'] = 'standard'
    avg_poke['secondary_type'] = 'NONE'
    avg_poke['generation'] = 999 
    avg_poke['form_name'] = 'standard'
    for stat in stat_categories:
       std_name = stat +"_stdev"
       avg_poke[stat] = grp[stat].mean()
       avg_poke[stat] = round(avg_poke[stat],1)
       avg_poke[std_name] = grp[stat].std()
       avg_poke[std_name] = round(avg_poke[std_name],1)
    avg_poke['stdev'] = avg_poke[stat_categories[:-2]].std() 
    avg_poke['stdev'] = round(avg_poke['stdev'],1)
    return(avg_poke)
  
def find_most_avg(grp, avg_poke):
    ## find the Pokemon in a particular type grouping that 
    ## most resembles the average profile
    
    # calculate diffs between any given stat and the stat from avg_poke 
    stat_categories = ['HP','Attack','Defense','Sp. Attack','Sp. Defense', 'Speed', 'Total','Average']
    grp['diff_sum'] = 0 
    for stat in stat_categories:
       diff_name = stat +"_diff"
       std_name = stat +"_stdev"
       grp[diff_name] = abs(grp[stat] - avg_poke[stat]) 
       grp['diff_sum'] = grp['diff_sum'] + grp[diff_name]

    most_avg = grp.iloc[grp['diff_sum'].idxmin()]
    return(most_avg)

def base_stat_plot(df,descriptor,avg_profile=False):
    ## make a scatter or line plot of the base stats for a dataFrame row
    base_stats = ['HP','Attack','Defense','Sp. Attack','Sp. Defense', 'Speed']
    y_vals = df.loc[base_stats].values
    x_pos = np.arange(len(base_stats)) 
    if avg_profile:
      base_std = ['HP_stdev','Attack_stdev','Defense_stdev','Sp. Attack_stdev','Sp. Defense_stdev', 'Speed_stdev']
      y_std = df.loc[base_std].values
      plt.bar(x_pos,y_vals,yerr=y_std)
    else:
      plt.bar(x_pos,y_vals)
    plt.xlabel("Base Stats")
    plt.ylabel("Value")
    plt.title("Base stat values for "+ descriptor,wrap=True)
    plt.xticks(x_pos, base_stats)
    plt.show()
    # TODO: prettify plots, save them to files 

def double_plot(df1,df2,descriptor,avg_profile=[False,False],labels=['df1','df2']):
    ## make a scatter or line plot of the base stats for a dataFrame row
    base_stats = ['HP','Attack','Defense','Sp. Attack','Sp. Defense', 'Speed']
    y1_vals = df1.loc[base_stats].values
    y2_vals = df2.loc[base_stats].values
    x_pos = np.arange(len(base_stats)) 
    width = 0.3
    base_std = ['HP_stdev','Attack_stdev','Defense_stdev','Sp. Attack_stdev','Sp. Defense_stdev', 'Speed_stdev']
    if avg_profile[0]:
        y1_std = df1.loc[base_std].values
        plt.bar(x_pos, y1_vals, yerr= y1_std, width=width,color='b',label=labels[0])
    else:
        plt.bar(x_pos, y1_vals, width=width,color='b',label=labels[0])

    if avg_profile[1]:
        y2_std = df2.loc[base_std].values
        plt.bar(x_pos+ width, y2_vals, yerr= y2_std, width=width,color='g',label=labels[1])
    else:
        plt.bar(x_pos+ width, y2_vals, width=width,color='g',label=labels[1])
    plt.xlabel("Base Stats")
    plt.ylabel("Value")
    plt.title("Base stat values for "+ descriptor,wrap=True)
    plt.xticks(x_pos, base_stats)
    plt.legend(loc='best')
    plt.show()
    # TODO: prettify plots, save them to files 


# ********** ********** # 
# ********** MESSING AROUND WITH MAIN DATASET ********** # 
# ********** ********** # 
best_worst = best_and_worst(df)
#print("********* BEST AND WORST PER STAT ACROSS ALL POKEMON **********")
#print(best_worst)
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
#TODO: transform this into a unit test of some kind

## stdev perspective
df['stdev'] = df.iloc[:, -8:-2].std(axis=1) 
df['stdev'] = round(df['stdev'],1)
#print("********* MOST AND LEAST WELL-ROUNDED ACROSS ALL POKEMON **********")
#print(df.iloc[df['stdev'].idxmin()])
#print(df.iloc[df['stdev'].idxmax()])


# ********** ********** # 
# ********** TYPE BY TYPE ********** # 
# ********** ********** # 
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

    ## best and worst by grouping
    best_worst_1 = best_and_worst(primary_type_grouping)
    best_worst_2 = best_and_worst(secondary_type_grouping)
    #print(best_worst_1)
    #print(best_worst_2)

    ## see which pokemon is closest to the average picture for its type.
    avg_poke = avg_stdev_per_type(primary_type_grouping)
    most_avg = find_most_avg(primary_type_grouping,avg_poke)
    #base_stat_plot(avg_poke,"Average profile of primary type "+x,avg_profile=True)
    
    ## group primary+secondary groupings together: avg, closest to avg Pokemon  
    primary_and_secondary = pd.concat([primary_type_grouping, secondary_type_grouping], ignore_index=True)
    avg_poke12 = avg_stdev_per_type(primary_and_secondary)
    most_avg12 = find_most_avg(primary_and_secondary,avg_poke)
    #print(avg_poke12)
    #print(most_avg12)

    #double_plot(avg_poke,avg_poke12,"Average profiles of "+x+" type",avg_profile=[True,True],labels=['primary type','primary+secondary type'])
    #base_stat_plot(avg_poke12,"Average profile of mixed type "+x,avg_profile=True)

    #TODO: PLOTSSSS 
    # (bar graph) base stats for best/worst for each type (primary, primary+secondary)
    # (line/scatter plot) closest-to-avg for each type (primary, primary+secondary)
    # (scatterplot) all pts for each base stat for each type (primary, primary+secondary)
    # (scatterplot) distributions of each base stat for every type (primary, primary+secondary)
    # TODO: calculate VARIANCES when creating distributions.

simple_stats['primary'] = simple_stats['primary'].astype('int32')
simple_stats['secondary'] = simple_stats['secondary'].astype('int32')
simple_stats['generation'] = simple_stats['generation'].astype('int32')
simple_stats = simple_stats[['type','primary','secondary','generation']]
#print(simple_stats)

#plot the numbers of each primary and secondary type per generation
for gen in simple_stats['generation'].unique():
     gen_data = simple_stats[simple_stats['generation'] == gen]

     ## plot all types for a given generation
     primary_vals = gen_data[['primary']].values
     primary_vals = [y for x in primary_vals for y in x]
     secondary_vals = gen_data[['secondary']].values
     secondary_vals = [y for x in secondary_vals for y in x]
     if gen == 1:
        gen_size = max(scrape.generations[gen-1]) - min(scrape.generations[gen-1])
     elif gen > 1 and gen < 999: 
        gen_size = max(scrape.generations[gen-1]) - min(scrape.generations[gen-1]) + 1
     else:
         gen_size = scrape.total_num
     x_pos = np.arange(len(scrape.possible_types))
     fig, ax1 = plt.subplots()
     ax1.set_xlabel("Type")
     ax1.set_ylabel("Count")
     plt.xticks(x_pos, scrape.possible_types)
     plt.xticks(rotation=90)
     mn,mx = ax1.set_ylim(0,max(primary_vals)+6)
     if gen != 999:
        ax1.set_yticks(np.arange(0,max(primary_vals)+6,2))
        plt.title("Type totals for generation "+str(gen),wrap=True)
     else: 
        ax1.set_yticks(np.arange(0,max(primary_vals)+6,10))
        plt.title("Type totals for all generations",wrap=True)
     ax1.bar(x_pos,primary_vals,color='b',label='primary type')
     ax1.bar(x_pos + 0.1,secondary_vals,color='g',label='secondary type')
     ax1.legend(loc='best')
     ax2 = ax1.twinx()
     ax2.set_ylim(mn/gen_size*100, mx/gen_size*100)
     ax2.set_yticks(np.arange(mn/gen_size*100,mx/gen_size*100,2))
     ax2.set_ylabel("Percentage of Generation Total Count")
     fig.tight_layout()
     plt.show()

# TODO: miscellaneous questions to ask 
# which primary + secondary (non-NONE) combo is most common?
# which type was the most common in each generation? the least common? 
# do Pokemon of a given type follow a pattern for relative magnitudes of base stats? 
# does including Pokemon w/ secondary type significantly shift a base stat distribution? hypothesis: it does for types that are usually present as secondary types / that have low primary:secondary ratios. 
# for Pokemon with multiple variants/forms, how does that change the base stats? same total, different individual stats? are there trends for how stats change among Alolan or Galarian variants? 

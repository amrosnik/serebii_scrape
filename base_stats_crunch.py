import pandas as pd
import pokescrape as scrape
import numpy as np
import re 
import matplotlib.pyplot as plt
from itertools import chain 
import os 
import basestats as bs

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 16)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 

df = pd.read_pickle("./joined_table_pickle.pkl")

# ********** ********** # 
# ********** MESSING AROUND WITH MAIN DATASET ********** # 
# ********** ********** # 
#print("********* BEST AND WORST PER STAT ACROSS ALL POKEMON **********")
#best_worst = best_and_worst(df)
#best_worst.to_csv('table_outputs/best_worst_overall.csv',index=False)

## stdev perspective
df['stdev'] = df.iloc[:, -8:-2].std(axis=1) 
df['stdev'] = round(df['stdev'],1)
#print("********* MOST AND LEAST WELL-ROUNDED ACROSS ALL POKEMON **********")
#print(pd.DataFrame(df.iloc[df['stdev'].idxmin()]))
#print(pd.DataFrame(df.iloc[df['stdev'].idxmax()]))
#pd.DataFrame(df.iloc[df['stdev'].idxmin()]).to_csv('table_outputs/lowest_stdev_overall.csv',index=True)
#pd.DataFrame(df.iloc[df['stdev'].idxmax()]).to_csv('table_outputs/highest_stdev_overall.csv',index=True)

# which primary + secondary (non-NONE) combo is most common?
df['primary+secondary'] = df['primary_type'] + " " + df['secondary_type']
df['primary+secondary'] = df['primary+secondary'].str.replace(" NONE","")
print("Most common primary+secondary type combo: ",df['primary+secondary'].mode())

# ********** ********** # 
# ********** TYPE BY TYPE ********** # 
# ********** ********** # 
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

    # TODO: create a simple_stats equivalent for dual-types? i.e., by looking at the primary+secondary column in df. 
    ## akin to the study in http://rstudio-pubs-static.s3.amazonaws.com/67019_5d0a712031c34eea9f7d4095740da8d8.html 

    ## append new row for total of each type across all generations
    new_row = {'type': x, 'primary': len(primary_type_grouping), 'secondary': len(secondary_type_grouping), 'generation': 999 }
    simple_stats = simple_stats.append(new_row,ignore_index=True)

    ## best and worst by grouping
    best_worst_1 = bs.best_and_worst(primary_type_grouping)
    best_worst_2 = bs.best_and_worst(secondary_type_grouping)
    #print(best_worst_1)
    #print(best_worst_2)
    #best_worst_1.to_csv('table_outputs/best_worst_primary_type_'+x+'.csv',index=False)
    #best_worst_2.to_csv('table_outputs/best_worst_secondary_type_'+x+'.csv',index=False)

    ## see which pokemon is closest to the average picture for its type.
    avg_poke = bs.avg_stdev_per_type(primary_type_grouping)
    most_avg = bs.find_most_avg(primary_type_grouping,avg_poke)
    bs.base_stat_plot(avg_poke,"Average profile of primary type "+x,avg_profile=True,save_plots=True,path=os.getcwd()+"/base_stat_plots/")
    #print("Most average primary "+x+" type Pokemon:",most_avg)
    #pd.DataFrame(most_avg).to_csv('table_outputs/most_avg_primary_type_'+x+'.csv',index=True)
    
    ## group primary+secondary groupings together: avg, closest to avg Pokemon  
    primary_and_secondary = pd.concat([primary_type_grouping, secondary_type_grouping], ignore_index=True)
    avg_poke12 = bs.avg_stdev_per_type(primary_and_secondary)
    most_avg12 = bs.find_most_avg(primary_and_secondary,avg_poke)
    #print(avg_poke12)
    #print("Most average primary OR secondary "+x+" type Pokemon:",most_avg12)
    #pd.DataFrame(most_avg12).to_csv('table_outputs/most_avg_primary-secondary_type_'+x+'.csv',index=True)

    bs.double_plot(avg_poke,avg_poke12,"Average profiles of "+x+" type",avg_profile=[True,True],labels=['primary type','primary + secondary type'],save_plots=True,path=os.getcwd()+"/base_stat_plots/")
    #bs.base_stat_plot(avg_poke12,"Average profile of mixed type "+x,avg_profile=True)

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
exit(0)

#plot the numbers of each primary and secondary type per generation
for gen in simple_stats['generation'].unique():
     gen_data = simple_stats[simple_stats['generation'] == gen]
     gen_data = gen_data.reset_index()
   
     # most common types per generation
     max_primary = gen_data.iloc[gen_data['primary'].idxmax()]
     max_secondary = gen_data.iloc[gen_data['secondary'].idxmax()]
     print("Most common primary and secondary types in gen "+str(gen)+": ",max_primary['type'],max_secondary['type'])
     min_primary = gen_data.iloc[gen_data['primary'].idxmin()]
     min_secondary = gen_data.iloc[gen_data['secondary'].idxmin()]
     print("Least common primary and secondary types in gen "+str(gen)+": ",min_primary['type'],min_secondary['type'])
  
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
     #plt.show()
     plt.close()

#plot the numbers of each type as its count changes over generations
for t in scrape.possible_types:
     primary_data = simple_stats[simple_stats['type'] == t]
     ## plot all types for a given generation
     primary_vals = primary_data[['primary']].values
     primary_vals = [y for x in primary_vals for y in x]
     secondary_vals = primary_data[['secondary']].values
     secondary_vals = [y for x in secondary_vals for y in x]

     # TODO: normalize these values by gen total 
     generations = np.arange(1,len(primary_vals),1)
     fig, ax1 = plt.subplots()
     ax1.set_xlabel("Generation")
     ax1.set_ylabel("Count")
     mn,mx = ax1.set_ylim(0,max(chain(primary_vals[:-1],secondary_vals[:-1])))
     ax1.set_yticks(np.arange(0,max(chain(primary_vals[:-1],secondary_vals[:-1])),2))
     plt.title("Totals for type "+t+" per generation",wrap=True)
     ax1.plot(generations,primary_vals[:-1],color='b',label='primary type',marker='.')
     ax1.plot(generations,secondary_vals[:-1],color='g',label='secondary type',marker='.')
     ax1.legend(loc='best')
     fig.tight_layout()
     #plt.show()
     plt.close()

# TODO: miscellaneous questions to ask 
# do Pokemon of a given type follow a pattern for relative magnitudes of base stats? 
# does including Pokemon w/ secondary type significantly shift a base stat distribution? hypothesis: it does for types that are usually present as secondary types / that have low primary:secondary ratios. 
# for Pokemon with multiple variants/forms, how does that change the base stats? same total, different individual stats? are there trends for how stats change among Alolan or Galarian variants? 

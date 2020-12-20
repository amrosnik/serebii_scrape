import pandas as pd
import pokescrape as scrape
import numpy as np
import re 
import matplotlib.pyplot as plt
from itertools import chain 
import os 

######## ######## ######## ########
######## BASESTATS MODULE ########
######## ######## ######## ######## 
######## Defined here are functions for analyzing and visualizing Pokemon base stats. ########

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

def base_stat_plot(df,descriptor,avg_profile=False,save_plots=False,path=os.getcwd()):
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
    if save_plots:
        save_name = descriptor.lower().replace(" ","_").replace("+","and")
        if avg_profile:
            save_name = "avg_"+save_name
        plt.savefig(path+"/base_stats_"+save_name+".ps")
    else:
        plt.show()
    plt.close()

def double_plot(df1,df2,descriptor,avg_profile=[False,False],labels=['df1','df2'],save_plots=False,path=os.getcwd()):
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
    if save_plots:
        save_name = descriptor.lower().replace(" ","_").replace("+","and")
        if labels[0] != 'df1' and labels[1] != 'df2':
            print_labels = [l.lower().replace(" ","_").replace("+","and") for l in labels]
            save_name = save_name+"_for_"+print_labels[0]+"_AND_"+print_labels[1]
        if avg_profile[0] or avg_profile[1]:
            save_name = "avg_"+save_name
        plt.savefig(path+"/base_stats_"+save_name+".ps")
    else:
        plt.show() 
    plt.close()


import pandas as pd
import pokescrape as scrape

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 10)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 

### Process:
# 1. split out simple_table such that each row has ONE type entry on it.
## e.g., if a species has a standard form and a Galarian form, 
## it will have TWO rows for it in the expanded table. 
# 2. import Bulbapedia table. For now, remove rows with "(Mega" 
## because for now we're discounting Mega Evolution. 
# 3. Join the two tables based on: name, number, and type name. 
## Will somehow need to specify that "Standard Type" in expanded_table 
## should map onto NO parentheses for a given species. 
## Will need to add an exception for FUCKING DARMANITAN so can properly 
## join on its Galarian Zen form.

### notes: 
## having done some poking around (haha) on the Bulbapedia table, 
## for some reason I can't account for FIVE forms. 
## The two tables have the same numbers of Galarian and Alolan forms. 
## Excluding the Mega forms, and counting out all the special forms 
## that don't have a type difference but a base stat difference, 
## for whatever reason there are FIVE things I can't account for.

## I'll probably just do the join and see what happens.   


#### read in data
simple_table = pd.read_csv('table_outputs/simple_table.csv',header=0)
simple_table = simple_table[['name', 'number','type_name','type','generation']]
#simple_table = simple_table.set_index(['name','type_name'])
#print(simple_table)

bulba_table = pd.read_csv('external_inputs/bulbapedia_baseStatsList_no-word-form.csv',header=0)
# making the names lowercase will make life easier
bulba_table['Pokémon'] = bulba_table['Pokémon'].str.lower()
# let's make a new column out of anything in parentheses. 
# This will be the bulba_table equivalent of the type_name column 
names_and_types = bulba_table['Pokémon'].str.split(pat="(",expand=True)
bulba_table['Pokémon'] = names_and_types[0]
bulba_table['Pokémon'] = bulba_table['Pokémon'].str.strip()
bulba_table['form_name'] = names_and_types[1].str.replace(")","").fillna("standard")
bulba_table = bulba_table[['Pokémon', '#','form_name','HP','Attack','Defense','Sp. Attack', 
        'Sp. Defense', 'Speed','Total','Average']]
#bulba_table = bulba_table.set_index(['Pokémon','form_name'])
#print(bulba_table)
#exit(0)

#### expand simple_table such that we have a row for every type entry
# TODO: play around with exception cases, like pikachu or pumpkaboo
#simple_subset = simple_table[simple_table['name']=='eevee']
#print(simple_subset)

#bulba_subset = bulba_table[bulba_table['Pokémon']=='eevee']
#print(bulba_subset)

#both_subset = pd.merge(simple_subset,bulba_subset,how='outer',left_on=['name','type_name'],right_on=['Pokémon','form_name'])
#print(both_subset[0:10])

def join_simple_bulba(pokename):
    simple_subset = simple_table[simple_table['name']==pokename]
    bulba_subset = bulba_table[bulba_table['Pokémon']==pokename]
    both_subset = pd.merge(simple_subset,bulba_subset,how='outer',left_on=['name','type_name'],right_on=['Pokémon','form_name'])
    return(both_subset)

#print(join_simple_bulba('eevee'))
#exit(0)

## Now let's get to joins! 
poke_names = simple_table.name.unique()
bulba_names = bulba_table.Pokémon.unique()
if len(poke_names) != len(bulba_names):
    print("WARNING! simple_table AND bulba_table HAVE DIFFERENT TOTAL NUMBERS OF UNIQUE POKEMON SPECIES. Please look at the data and see if one of them is out-of-date or erroneous.")

## iterate over all the unique names of Pokemon within simple_table and join the two data sources
big_joined_table = pd.DataFrame()
simples = simple_table.columns
bulbas = bulba_table.columns


for name in poke_names[0:151]:
    joined_table = join_simple_bulba(name)
    ## if we have Mega Evolution data, let's drop it for now.
    ## maybe I'll include it at some point, but my assumption 
    ## that Mega Evolutions have the same type as the standard forms
    ## is not true for several species, and...Mega Evolution is a temporary state anyway.
    joined_table = joined_table[~joined_table['form_name'].str.contains('mega',na=False)]

    ## if all simple_table columns are NaN, then check if there is a standard type row.
    ## if there is, copy its simple_table data into it 
    standard_type_row = joined_table[joined_table['type_name'] == 'standard']
    if len(joined_table[joined_table[simples].isna().any(axis=1)]) > 0:
        print("simple_table columns are NaN")
        if len(standard_type_row) > 1:
            print("WARNING! we have multiple standard type rows for whatever reason.")
        elif len(standard_type_row) == 1:
            print("there exists a standard type row! Now let's copy standard type data for our missing type data for this special form.")
            joined_table['name'].fillna(value=standard_type_row['name'].values[0],inplace=True)
            joined_table['number'].fillna(value=standard_type_row['number'].values[0],inplace=True)
            joined_table['type_name'].fillna(value=standard_type_row['type_name'].values[0],inplace=True)
            joined_table['type'].fillna(value=standard_type_row['type'].values[0],inplace=True)
            joined_table['generation'].fillna(value=standard_type_row['generation'].values[0],inplace=True)          
        elif len(standard_type_row) == 0:
            print("WARNING: We don't have a standard type row. Will need to look to some other row for filling in these data.")
    #print(joined_table)
    big_joined_table = big_joined_table.append(joined_table,ignore_index=True)

print(big_joined_table)

## TODO: figure out a way to do NaN handling for cases when there is a form_name but no corresponding type_name
## ...there should be about 50 Mega + 32 rando = 82 cases.
## ...in all cases, the type info should be copied from the 'standard' entry for that species


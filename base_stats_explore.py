import pandas as pd
import pokescrape as scrape

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
names_and_types = bulba_table['Pokémon'].str.split(pat="(",expand=True)
bulba_table['Pokémon'] = names_and_types[0]
bulba_table['Pokémon'] = bulba_table['Pokémon'].str.strip()
bulba_table['form_name'] = names_and_types[1].str.replace(")","").fillna("standard")
bulba_table = bulba_table[['Pokémon', '#','form_name','HP','Attack','Defense','Sp. Attack', 
        'Sp. Defense', 'Speed','Total','Average']]
#bulba_table = bulba_table.set_index(['Pokémon','form_name'])
# let's make a new column out of anything in parentheses. 
# This will be the bulba_table equivalent of the type_name column 
#print(bulba_table)

#exit(0)
#### expand simple_table such that we have a row for every type entry
simple_subset = simple_table[simple_table['name']=='meowth']
#print(simple_subset['type_name'].values)

bulba_subset = bulba_table[bulba_table['Pokémon'].str.contains('meowth')]
#print(bulba_subset['form_name'].values)

both_subset = pd.merge(simple_subset,bulba_subset,how='outer',left_on=['name','type_name'],right_on=['Pokémon','form_name'])
print(both_subset[0:10])
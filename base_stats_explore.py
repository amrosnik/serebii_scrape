import pandas as pd
#import pokescrape as scrape
import numpy as np

pd.set_option('display.max_row', 1050)
pd.set_option('display.max_column', 10)
#### This script file will be used to manipulate the * simple_table * saved in table_outputs/
#### for the sake of initial data exploration. 


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


for name in poke_names[700:750]:
    joined_table = join_simple_bulba(name)
    ## if we have Mega Evolution data, let's drop it for now.
    ## maybe I'll include it at some point, but my assumption 
    ## that Mega Evolutions have the same type as the standard forms
    ## is not true for several species, and...Mega Evolution is a temporary state anyway.
    joined_table = joined_table[~joined_table['form_name'].str.contains('mega',na=False)]

    #print(joined_table.iloc[:,np.r_[1:4,5,7:12]])
    ## if all simple_table columns are NaN, then check if there is a standard type row.
    ## if there is, copy its simple_table data into it 
    standard_type_row = joined_table[joined_table['type_name'] == 'standard']
    if len(joined_table[joined_table[simples].isna().any(axis=1)]) > 0:
        print("simple_table columns are NaN for ",name)
        if len(standard_type_row) > 1:
            print("WARNING! we have multiple standard type rows for whatever reason.")
        elif len(standard_type_row) == 1:
            print("there exists a standard type row for ",name,"! Now let's copy standard type data for our missing type data for this special form.")
            for y in simples:
                joined_table[y].fillna(value=standard_type_row[y].values[0],inplace=True)
        elif len(standard_type_row) == 0:
            print("WARNING: We don't have a standard type row. Will need to look to some other row for filling in these data.")
    standard_form_row = joined_table[joined_table['form_name'].str.contains('standard|normal',regex=True,na=False)]
    if len(joined_table[joined_table[bulbas].isna().any(axis=1)]) > 0:
        print("bulba_table columns are NaN for ",name)
        if len(standard_form_row) > 1:
            print("WARNING! we have multiple standard form rows for whatever reason.")
        elif len(standard_form_row) == 1:
            print("there exists a standard form row for ",name,"! Now let's copy standard form data for our missing form data for this special type.")
            for x in bulbas:
                joined_table[x].fillna(value=standard_form_row[x].values[0],inplace=True)
        elif len(standard_form_row) == 0:
            print("WARNING: We don't have a standard form row. Will need to look to some other row for filling in these data.")

    ## EXCEPTION HANDLING
    # Giratina (#487) has no standard form, but rather two forms (Altered and Origin). Counterintuitively, the Altered form is the more common one.
    # so let's delete the "standard type" row with NaNs in the form entries
    if name == "giratina":
        joined_table = joined_table.drop(standard_type_row.index)
    # Rotom (#479) has a LOT of forms with type differences. My two tables labeled the standard form/type differently,
    # but they contain the same data. Dropping one of them. 
    # also, apparently Rotom Dex can't be used as a Pokemon in battle and breeding, so let's drop that, too.
    if name == "rotom":
        joined_table['type_name'].replace(to_replace='^rotom',value='standard',regex=True,inplace=True)
        joined_table = joined_table.drop(standard_form_row.index)
        joined_table = joined_table.drop(joined_table[joined_table['type_name']=='rotom dex'].index)
    # Darmanitan (#555): easily my least favorite Pokemon because of all the exception handling for it. What a diva.
    # Need to copy the Galarian type data to the Galarian Zen form.
    if name == "darmanitan":
        joined_table.loc[joined_table['form_name']=='galarian form, zen mode', ['type_name']] = joined_table.loc[joined_table['form_name']=='galarian form, zen mode', ['type_name']].replace("standard","galarian form, zen mode")
        joined_table.loc[joined_table['form_name']=='galarian form, zen mode', ['type']] = joined_table.loc[joined_table['form_name']=='galarian form, zen mode', ['type']].replace("['fire']","['ice', 'fire']")
    # The Gen V legendaries have two forms, Incarnate or Therian. There is no "standard" form, 
    # so let's drop the sad attempt to make a standard form. Note the type is the same for both forms. 
    if name == "tornadus" or name == "thundurus" or name == "landorus":
        joined_table = joined_table.drop(standard_type_row.index)
    # Aegislash (#681) has two forms, neither of which is "standard"
    if name == "aegislash":
        joined_table = joined_table.drop(standard_type_row.index)    
    # Pumpkaboo and Gourgeist (#710 and 711) have multiple sizes, and "average size" is the standard form.
    if name == "pumpkaboo" or name == "gourgeist":
        joined_table = joined_table.drop(standard_type_row.index)    
    # Zygarde (#718) is the coolest. Let's consider its 50% forme the "average".
    if name == "zygarde":
        joined_table = joined_table.drop(standard_type_row.index)    
    # Lycanroc (#745)'s midday form is the closest to an average 
    if name == "lycanroc":
        joined_table = joined_table.drop(standard_type_row.index)    
    # Wishiwashi (#746) changes form based on battle stats, so let's consider its Solo Form the standard
    if name == "wishiwashi":
        solo_row = joined_table[joined_table['form_name'].str.contains('solo',regex=True,na=False)]
        for x in bulbas:
            if x != 'form_name':
                joined_table[x].fillna(value=solo_row[x].values[0],inplace=True)
            else:
                joined_table[x].fillna(value='standard',inplace=True)
        #print(standard_type_row)
        #print(standard_form_row)

    ## Drop any duplicate standard/normal rows 
        # Deoxys
        # Darmanitan
        # Kyurem

    #print(joined_table)
    big_joined_table = big_joined_table.append(joined_table,ignore_index=True)

print(big_joined_table.iloc[:,np.r_[1:3,5,7:9]])
#big_joined_table.to_pickle("./joined_table_pickle.pkl")

## TODO: figure out a way to do NaN handling for cases when there is a type_name but no corresponding form_name
## ...there should be about 32 cases, excluding the 50 Mega Evolutions.
## ...in all cases, the type info should be copied from the 'standard' entry for that species.
## if there is no standard type row, I'll need to update that manually

### notes: 
## having done some poking around (haha) on the Bulbapedia table, 
## for some reason I can't account for FIVE forms. 
## The two tables have the same numbers of Galarian and Alolan forms. 
## Excluding the Mega forms, and counting out all the special forms 
## that don't have a type difference but a base stat difference, 
## for whatever reason there are FIVE things I can't account for.

#idx = pd.IndexSlice
#df = pd.read_pickle("./adventure_pickle_CLEAN.pkl")

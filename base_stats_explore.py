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
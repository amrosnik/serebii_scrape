import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re

######## ######## ######## ########
######## POKESCRAPE MODULE ########
######## ######## ######## ######## 
######## This module stores all the global, immutable variables used throughout this project. ########
######## The most important of these is hrefs, a master list of links to all Pokemon pages. ########
######## Defined here are functions for all scraping needs to retrieve data from serebii.net. ########

######## ######## ########
######## GLOBAL VARIABLES ########

## At time of writing, the newest generation is Gen VIII, so we expect 893 Pokemon
## we also expect the following for other attributes: 
total_num = 898

possible_types = ["normal", "fire", "grass", "water", "fighting", "flying", 
"poison", "ground", "rock", "bug", "ghost", "electric",
"psychic", "ice", "dragon", "dark", "steel", "fairy"]

possible_genders = ["genderless", "female", "male"]

possible_egg_groups = ["monster", "human-like", "water 1", "water 2", "water 3", "bug", 
"mineral", "flying", "amorphous", "field", "fairy", "ditto", "grass", "dragon", 
"no eggs discovered", "gender unknown"]

gen_i = (0,151)
gen_ii = (152,251)
gen_iii = (252,386)
gen_iv = (387,493)
gen_v = (494,649)
gen_vi = (650,721)
gen_vii = (722,809)
gen_viii = (810,total_num) ## TODO: whenever gen_ix is released, add that tuple to this section and modify gen_viii end number accordingly 
generations = [gen_i,gen_ii,gen_iii,gen_iv,gen_v,gen_vi,gen_vii,gen_viii]

######## ######## ########

######## ######## ########
######## FUNCTION DEFINITIONS ########

def get_master_list(): 
   ########  GET THE MASTER LIST OF LINKS, HREFS ########
   ## Link to the best Pokedex around: 
   url = 'https://www.serebii.net/pokemon/all.shtml'
   time.sleep(2)
   response = requests.get(url)

   soup = BeautifulSoup(response.text, "html.parser")

   ## let's grab the links to all Pokemon. 
   # the form of each entry in hrefs is: 
   # /pokemon/NAME_OF_POKEMON
   ## the data are given in a tabular format, and for each row of the table, 
   ## it looks like this: 
   # <table class="pkmn"><tr><td><a href="/pokemon/NAME_OF_POKEMON"><img border="0" src="/pokedex-swsh/icon/POKEDEX_NUMBER.png"/></a></td></tr></table> 
   # we just want the href part, since that's the extra part of the link we need to get to the Pokedex entries!
   # here's how to get it: 
   hrefs = [a.attrs['href'] for a in (table.find('a') for table in soup.findAll('table',{"class": "pkmn"})) if a]

   return(hrefs)

def which_generation(num):
    gen = 999
    for (lower,upper) in generations:
        if (lower <= num <= upper): 
            gen = generations.index((lower,upper))+1
    if gen != 999:
        return(gen)
    else:
        print("WARNING: THIS POKEDEX NUMBER,",num, " DOES NOT EXIST. RETURNING 999 AS GENERATION NUMBER")
        return(999)

def check_type(types_found,regional_check=True):
    reference = set(possible_types)
    newb = set(types_found)
    if len(newb) == 0 and not regional_check:
        print("Empty set of types")
    elif (not reference & newb and len(newb) > 0): 
        print("No identifiable type found!")

def split_by_dex(type_array):
    intermed_type = [x.split('/')[1] for x in type_array]
    for x in range(len(type_array)): 
        if "dex" in intermed_type[x]:
        # some Pokemon have special forms that are unique to them. The types for these 
        # unique variants that result in a change in type are given via /pokedex-SOMETHING links, 
        # so they need to be parsed differently. 
            type_array[x] = type_array[x].split('/')[2]
            type_array[x] = type_array[x].split('.')[0]
        elif intermed_type[x] == "pokemon":
            type_array[x] = type_array[x].split('/')[3]
    return(type_array)

def get_soup(hrefs,i):
    orig_link = 'https://www.serebii.net'+hrefs[i]
    name = hrefs[i].split('/')[2] #split up entry to get NAME_OF_POKEMON      
    if i == 554 or i > 892:
        orig_link = 'https://www.serebii.net'+'/pokedex-swsh/'+name
    orig_response = requests.get(orig_link)
    orig_soup = BeautifulSoup(orig_response.text, "html.parser")
    #print("my name is",name,"# is ",i+1)
    return(orig_soup,orig_response,name)

def get_types_and_variants(hrefs,i):  
    indiv_types = dict()  
    orig_soup,orig_response,name = get_soup(hrefs,i)
    ## determine Type 
    cens = orig_soup.find('td',{"class":"cen"}).findAll('tr') # the first class="cen" is always the Type section. 
    if len(cens) == 0: 
        # the 'tr' tags only appear if there is at least one regional variant
        cens = orig_soup.find('td',{"class":"cen"})
        standard_type = [a.attrs['href'] for a in cens.findAll('a')]
        standard_type = split_by_dex(standard_type)
        check_type(standard_type,regional_check=False)
        indiv_types.update({"standard" : standard_type})
    else:
        intermed = cens[0].findAll('a')
        standard_type = [a.attrs['href'] for a in intermed]

        # first, check if we have a "Normal Type". If present, this will serve as the default type
        # then, search for regional variations or unique variations 
        normal_find = [ cen.find(text='Normal') for cen in cens ]
        unique_variations = []
        if not all(normal_find): 
            for j in range(len(cens)):
                if normal_find[j]:
                    if "standard" in indiv_types:
                        print("WARNING: For ,*",name,"* There is more than one standard type?!")
                    else: 
                        intermed = cens[j].findAll('a')
                        standard_type = [a.attrs['href'] for a in intermed]
                        standard_type = split_by_dex(standard_type)
                        indiv_types.update({"standard" : standard_type})
                else:
                    tds = cens[j].find(['td'])
                    new_type_name = tds.contents[0]
                    if new_type_name in indiv_types:
                        print("WARNING: For ,*",name,"* Same non-standard type appears twice?!")
                        new_type_name = new_type_name+" #2"
                    #unique_variations.append(new_type_name)
                    new_type = cens[j].findAll('a')
                    new_type = [a.attrs['href'] for a in new_type]
                    new_type = split_by_dex(new_type)
                    indiv_types.update({new_type_name.lower() : new_type})
    if "Alolan" in indiv_types:
        alolan_form = True
    else: 
        alolan_form = False
                    
    if "Galarian" in indiv_types:
        galarian_form = True
    else:
        galarian_form = False
    for k in indiv_types:
        check_type(indiv_types[k])
    return(indiv_types,name)


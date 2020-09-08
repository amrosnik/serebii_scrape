import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re

## At time of writing, the newest generation is Gen VIII, so we expect 893 Pokemon
## we also expect the following for other attributes: 
total_num = 893

possible_types = ["normal", "fire", "grass", "water", "fighting", "flying", 
"poison", "ground", "rock", "bug", "ghost", "electric",
"psychic", "ice", "dragon", "dark", "steel", "fairy"]

possible_genders = ["genderless", "female", "male"]

possible_egg_groups = ["monster", "human-like", "water 1", "water 2", "water 3", "bug", 
"mineral", "flying", "amorphous", "field", "fairy", "ditto", "grass", "dragon", 
"no eggs discovered", "gender unknown"]

## Link to the best Pokedex around: 
url = 'https://www.serebii.net/pokemon/all.shtml'
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

## let's grab the links to all Pokemon. 
## the data are given in a tabular format, and for each row of the table, 
## it looks like this: 
# <table class="pkmn"><tr><td><a href="/pokemon/NAME_OF_POKEMON"><img border="0" src="/pokedex-swsh/icon/POKEDEX_NUMBER.png"/></a></td></tr></table> 
# we just want the href part, since that's the extra part of the link we need to get to the Pokedex entries!
# here's how to get it: 
hrefs = [a.attrs['href'] for a in (table.find('a') for table in soup.findAll('table',{"class": "pkmn"})) if a]

# so, the form of each entry in hrefs is: 
# /pokemon/NAME_OF_POKEMON

## TEST: ensure we have all 893 Pokemon
if len(hrefs) < total_num: 
    print("Uh oh, we didn't catch 'em all!")
    exit()
elif len(hrefs) > total_num: 
    print("Either there's more than "+str(total_num)+" Pokemon now, or we're actually scraping Digimon data...")
    exit()

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


## we need to loop through *all* Pokemon listed on this page. 
#for i in range(0,len(hrefs)):
misfits = [350, 412, 478, 491, 554, 647, 719, 740, 799, 887, 888]
    ## EXCEPTIONS THAT MUST BE HANDLED: 
    # Hoopa, 720
    # Oricorio, 741
    # Necrozma, 800 
    # Zacian, 888
    # Zamazenta, 889
    # Meloetta, 648
    # Darmanitan, 555 
    # Shaymin, 492
    # Rotom, 479
    # Wormadam, 413
    # Castform, 351

gen_i = range(0,150)
gen_ii = range(150,250)
gen_iii = range(250,385)
gen_iv = range(385,492)
gen_v = range(492,648)
gen_vi = range(648,720)
gen_vii = range(720,808)
gen_viii = range(808,892)

for i in range(1,3):  
    indiv_types = dict()  
    orig_link = 'https://www.serebii.net'+hrefs[i]
    name = hrefs[i].split('/')[2] #split up entry to get NAME_OF_POKEMON      
    if i == 554:
        orig_link = 'https://www.serebii.net'+'/pokedex-swsh/'+name
    orig_response = requests.get(orig_link)
    orig_soup = BeautifulSoup(orig_response.text, "html.parser")
    print("my name is",name,"# is ",i+1)
    ## determine Type 
    cens = orig_soup.find('td',{"class":"cen"}).findAll('tr') # the first class="cen" is always the Type section. 
    if len(cens) == 0: 
        # the 'tr' tags only appear if there is at least one regional variant
        cens = orig_soup.find('td',{"class":"cen"})
        standard_type = [a.attrs['href'] for a in cens.findAll('a')]
        standard_type = split_by_dex(standard_type)
        check_type(standard_type,regional_check=False)
        indiv_types.update({"Standard Type" : standard_type})
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
                    if "Standard Type" in indiv_types:
                        print("WARNING: There is more than one standard type?!")
                    else:
                        intermed = cens[j].findAll('a')
                        standard_type = [a.attrs['href'] for a in intermed]
                        standard_type = split_by_dex(standard_type)
                        indiv_types.update({"Standard Type" : standard_type})
                else:
                    tds = cens[j].find(['td'])
                    new_type_name = tds.contents[0]
                    if new_type_name in indiv_types:
                        print("WARNING: Same non-standard type appears twice?!")
                        new_type_name = new_type_name+" #2"
                    #unique_variations.append(new_type_name)
                    new_type = cens[j].findAll('a')
                    new_type = [a.attrs['href'] for a in new_type]
                    new_type = split_by_dex(new_type)
                    indiv_types.update({new_type_name : new_type})
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
    print(indiv_types)

    ## get Pokedex number 
    ## remember, Python indexes start at ONE, so the actual pokedex index is...i+1
    if i < 10: 
        index = '00'+str(i+1)
    elif i >= 10 and i < 100: 
        index = '0'+str(i+1)
    else: 
        index = str(i+1)

    ## make sure we have the correct Pokedex version.
    ## for Pokemon in Gen I-VII, we'll take data from the Gen VII Pokedex
    if i < 809: 
        pokedex_link = 'https://www.serebii.net/pokedex-sm/'+index+".shtml"
    ## for Pokemon in Gen VIII, we'll take data from the Gen VIII Pokedex  
    else: 
        pokedex_link = 'https://www.serebii.net/pokedex-swsh/'+name+'/' 

    dex_response = requests.get(pokedex_link)
    dex_soup = BeautifulSoup(dex_response.text, "html.parser")

    ## use dextable to look for: Egg Group, Evolutionary Chain 
    dextables = dex_soup.findAll('table',{"class":"dextable"})
    #print(len(dextables))
    evoln_table = [dextable.find(text="Evolutionary Chain") for dextable in dextables]
    evoln_index = evoln_table.index("Evolutionary Chain")
    evoln_chain = dextables[evoln_index]
    evoln_trs = evoln_chain.findAll('tr')
    # the second tr is the one we want. the first one denotes we are looking for an Evolutionary Chain
    evoln_chain_forreal = evoln_trs[1] #.contents
    find_evolns = evoln_chain_forreal.findAll('td',{"class":"pkmn"})
    evolns_as = [z.find('a').attrs['href'] for z in find_evolns]
    self_finder = [re.search(index,z) for z in evolns_as]
    self_index = [ z for z in self_finder if z is not None]
    self_index = self_finder.index(self_index[0]) # we hopefully should only have one element here...test this
    print(self_index)
    if len(evolns_as) > 1: 
        is_it_in_an_evoln_chain = True 
        if len(evolns_as) > self_index: # this breaks for the final stage of an evoln chain 
            does_it_evolve = True
        else:
            does_it_evolve = False
    else:
        is_it_in_an_evoln_chain = False 
    #find_evolns = [ evoln.findAll('td') for evoln in evoln_chain_forreal ] 
    # TODO: probs will need to write this finding + find index + subsequent finding of correct tr tag 
    # into a function... 
    # TODO: ensure that we don't catch Mega Evoln in this process... 
    print(is_it_in_an_evoln_chain, does_it_evolve)



    # use the "Alternate forms" section to look for non-regional other Alternate Forms? 

    ## Mega evolution
        # search page for alt="Mega Evolution Artwork"
    ## Gigantamax 
        # search page for alt="Gigantamax"
     
    """
    
    ## now that we have the Pokedex entry data, let's get some more attributes!
    # Gender Ratio 
    # Gender differences: search to see if this section exists once in correct Pokedex 
    # Egg Groups 
    # Shiny (look for "Shiny Sprite"; not all may have this)
    # [ miscellaneous variations that may involve variations without type changes ]  

    time.sleep(1)
    """
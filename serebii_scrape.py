import requests
import urllib.request
import time
from bs4 import BeautifulSoup

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

for i in range(24,27):  
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
    for i in indiv_types:
        check_type(indiv_types[i])
    print(indiv_types)

    # use the "Alternate forms" section to look for non-regional other Alternate Forms? 

    ## Mega evolution
        # search page for alt="Mega Evolution Artwork"
    ## Gigantamax 
        # search page for alt="Gigantamax"
     
    """
    ## get Pokedex number 
    if i < 10: 
        index = '00'+str(i)
    elif i >= 10 and i < 100: 
        index = '0'+str(i)
    else: 
        index = str(i)

    ## make sure we have the correct Pokedex version.
    ## for Pokemon in Gen I-VII, we'll take data from the Gen VII Pokedex
    if i < 809: 
        pokedex_link = 'https://www.serebii.net/pokedex-sm'+index+".shtml"
    ## for Pokemon in Gen VIII, we'll take data from the Gen VIII Pokedex  
    else: 
        pokedex_link = 'https://www.serebii.net/pokedex-swsh/'+name+'/' 

    dex_response = requests.get(pokedex_link)
    dex_soup = BeautifulSoup(dex_response.text, "html.parser")

    ## now that we have the Pokedex entry data, let's get some more attributes!
    # Gender Ratio 
    # Gender differences: search to see if this section exists once in correct Pokedex 
    # Egg Groups 
    # Shiny (look for "Shiny Sprite"; not all may have this)
    # [ miscellaneous variations that may involve variations without type changes ]  

    time.sleep(1)
    """
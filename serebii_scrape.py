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

## we need to loop through *all* Pokemon listed on this page. 
#for i in range(0,len(hrefs)):
misfits = [350, 412, 478, 491, 554, 647, 719, 740, 799, 887, 888]
misfits_abridged = [887,888]
for i in misfits:  
    indiv_types = dict()  
    orig_link = 'https://www.serebii.net'+hrefs[i]
    orig_response = requests.get(orig_link)
    orig_soup = BeautifulSoup(orig_response.text, "html.parser")
    name = hrefs[i].split('/')[2] #split up entry to get NAME_OF_POKEMON 
     
    print("my name is",name,"# is ",i+1)
    ## determine Type 
    cens = orig_soup.find('td',{"class":"cen"}).findAll('tr') # the first class="cen" is always the Type section. 
    if len(cens) == 0: 
        # the 'tr' tags only appear if there is at least one regional variant
        trs = False
        cens = orig_soup.find('td',{"class":"cen"})
        standard_type = [a.attrs['href'] for a in cens.findAll('a')]
    else:
        trs = True
        intermed = cens[0].findAll('a')
        standard_type = [a.attrs['href'] for a in intermed]

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

    intermed_type = [x.split('/')[1] for x in standard_type]
    for x in range(len(standard_type)): 
        if "dex" in intermed_type[x]:
            # some Pokemon have special forms that are unique to them. The types for these 
            # unique variants that result in a change in type are given via /pokedex-SOMETHING links, 
            # so they need to be parsed differently. 
            standard_type[x] = standard_type[x].split('/')[2]
            standard_type[x] = standard_type[x].split('.')[0]
        elif intermed_type[x] == "pokemon":
            standard_type[x] = standard_type[x].split('/')[3]
    check_type(standard_type,regional_check=False)
    indiv_types.update({"Standard Type" : standard_type})

    print("you're my type, "+name+"! got ",standard_type)
    alolan_form = galarian_form = False
    alolan_type = galarian_type = []
    if trs: 
        for i in range(1,len(cens)):
            alolan = cens[i].find(text='Alolan')
            galarian = cens[i].find(text='Galarian')
            if alolan:
                alolan_form = True 
                alolan_type = cens[i].findAll('a')
                alolan_type = [a.attrs['href'] for a in alolan_type]
                alolan_type = [x.split('/')[3] for x in alolan_type]
                print("Alolan type(s): ",alolan_type)
                # TODO: functionalize this bit of code? I use it 3 times...
                galarian_form = False
            if galarian:
                galarian_form = True 
                galarian_type = cens[i].findAll('a')
                galarian_type = [a.attrs['href'] for a in galarian_type]
                galarian_type = [x.split('/')[3] for x in galarian_type]
                print("Galarian type(s): ",galarian_type)
                alolan_form = False
            else:
                alolan_form = False
                galarian_form = False
    
        normal_find = [ cen.find(text='Normal') for cen in cens ]
        unique_variations = []
        if not all(normal_find): # if we have NO mention of a "Standard/Normal type", 
        # then we check for the names of these exclusively unique variations
            for j in range(len(cens)):
                #if normal_find[j]:
                    # TODO: refactor so that here we find the Standard Type 
                    # TODO: refactor to check for Alola, Galar flags here 
                if not normal_find[j]:
                    tds = cens[j].find(['td'])
                    new_type_name = tds.contents[0]
                    unique_variations.append(new_type_name)
                    new_type = cens[j].findAll('a')
                    new_type = [a.attrs['href'] for a in new_type]
                    new_type = [x.split('/')[2] for x in new_type ] 
                    new_type = [x.split('.')[0] for x in new_type ] 
                    indiv_types.update({new_type_name : new_type})
            # TODO: check if there are non-standard types for some Pokemon! (the misfits)
    check_type(alolan_type)
    check_type(galarian_type)
    print(indiv_types)

    # TODO: make a dictionary with all the types!! 

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
    # should I even bother with the Shadow thing? hard to figure out where to scrape the data... 
    # [ miscellaneous variations] : unclear where these will show up. More research needed. 

    time.sleep(1)
    """
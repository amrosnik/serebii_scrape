import requests
import urllib.request
import time
from bs4 import BeautifulSoup

## At time of writing, the newest generation is Gen VIII, so we expect 893 Pokemon 
total_num = 893

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

possible_types = ["normal", "fire", "grass", "water", "fighting", "flying", 
"poison", "ground", "rock", "bug", "ghost", "electric",
"psychic", "ice", "dragon", "dark", "steel", "fairy"]

possible_genders = ["genderless", "female", "male"]

possible_egg_groups = ["monster", "human-like", "water 1", "water 2", "water 3", "bug", 
"mineral", "flying", "amorphous", "field", "fairy", "ditto", "grass", "dragon", 
"no eggs discovered", "gender unknown"]

## we need to loop through *all* Pokemon listed on this page. 
for i in range(0,len(hrefs)):
    orig_link = 'https://www.serebii.net'+hrefs[i]
    orig_response = requests.get(orig_link)
    orig_soup = BeautifulSoup(orig_response.text, "html.parser")
     
    ## determine Type 
    cens = orig_soup.find('td',{"class":"cen"}).findAll('tr') # the first class="cen" is always the Type section. 
    # but there may be multiple Types, and if there are Alola and Galarian versions, the Types may differ. 
    # these different versions are separated by 'tr' tags. 
    standard_type = cens[0].findAll('a')['href']
    standard_type = standard_type.split('/')[3] #split up entry to get TYPE_OF_POKEMON 
    # TODO: double-check this works if the standard type actually has two types! test w/ Bulbasaur
    if len(cens) > 1: 
        for i in (1,len(cens)):
            alolan = cens.find(text='Alolan')
            galarian = cens.find(text='Galarian Type')
            if alolan:
                alolan_form = True 
                alolan_type = cens[i].findAll('a')['href']
                alolan_type = alolan_type.split('/')[3]
                # TODO: double-check this works if the Alolan type actually has two types! test w/ Raichu 
                # TODO: functionalize this bit of code? I use it 3 times...
                galarian_form = False
            elif galarian:
                galarian_form = True 
                galarian_type = cens[i].findAll('a')['href']
                galarian_type = alolan_type.split('/')[3]
                # TODO: double-check this works if the Galarian type actually has two types! test w/ Meowth
                alolan_form = False
            else:
                alolan_form = False
                galarian_form = False
    # TODO TEST: make sure that the types found 
    
    # use the "Alternate forms" section to look for Alola, Galar, and other Alternate Forms? 

    ## Mega evolution
        # search page for alt="Mega Evolution Artwork"
    ## Gigantamax 
        # search page for alt="Gigantamax"
     
    ## get Pokedex number 
    name = hrefs[i].split('/')[2] #split up entry to get NAME_OF_POKEMON 
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

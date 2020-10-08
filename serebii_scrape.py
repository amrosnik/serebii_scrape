import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import pokescrape as scrape 

## TEST: ensure we have all 893 Pokemon
if len(scrape.hrefs) < scrape.total_num: 
    print("Uh oh, we didn't catch 'em all!")
    exit()
elif len(scrape.hrefs) > scrape.total_num: 
    print("Either there's more than "+str(scrape.total_num)+" Pokemon now, or we're actually scraping Digimon data...")
    exit()

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

for i in range(24,26):

    indiv_types = scrape.get_types_and_variants(i)
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
    self_index = [ self_finder.index(i) for i in self_index ]
    num_evolns = len(evolns_as)
    if num_evolns > 1: 
        is_it_in_an_evoln_chain = True 
        if len(self_index) > 1: 
            if num_evolns > len(self_index): 
                # if we are in this scenario, we have a Pokemon that can Gigantamax and/or Mega Evolve
                if max(self_index) == (num_evolns - 1):
                    does_it_evolve = False
                    if (max(self_index)-1 in self_index): 
                    # if the two largest numbers in the self_index are indices for this Pokemon, 
                    # it is at the end of its evolutionary chain AND it has multiple possible forms.
                    # those additional forms may be: regional variations, unique variations, 
                    # Mega Evolutions, or Gigantamax evolutions.
                        mega = True # TODO: NOT NECESSARILY TRUE! need to work on this logic
                        gigantamax = False # TODO: NOT NECESSARILY TRUE! need to work on this logic
                    else:
                        mega = False 
                        gigantamax = False
            else:
                does_it_evolve = False
        elif len(self_index) == 1:
            mega = False
            gigantamax = False
            if self_index[0] == (num_evolns -1):
                does_it_evolve = False
            elif self_index[0] < (num_evolns -1):
                does_it_evolve = True   
    else:
        is_it_in_an_evoln_chain = False 
        does_it_evolve = False
        mega = False
        gigantamax = False
    #find_evolns = [ evoln.findAll('td') for evoln in evoln_chain_forreal ] 
    # TODO: probs will need to write this finding + find index + subsequent finding of correct tr tag 
    # into a function... 
    print(is_it_in_an_evoln_chain, does_it_evolve, mega, gigantamax)

    # use the "Alternate forms" section to look for non-regional other Alternate Forms
    ## Mega evolution
        # search page for alt="Mega Evolution Artwork"
    ## Gigantamax 
        # search page for alt="Gigantamax"
        # since Gigantamax is a Gen VIII thing only, will need to use this page for ALL Pokemon to check this. -_- 
     
    """
    
    ## now that we have the Pokedex entry data, let's get some more attributes!
    # Gender Ratio 
    # Gender differences: search to see if this section exists once in correct Pokedex 
    # Egg Groups 
    # Shiny (look for "Shiny Sprite"; not all may have this)
    # [ miscellaneous variations that may involve variations without type changes ]  

    time.sleep(1)
    """
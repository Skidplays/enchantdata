from os import name, write
import requests
import requests
from collections import Counter
from tqdm import trange, tqdm
import concurrent.futures
import time

ALL_CHARACTERS_LIST = "https://poe.ninja/api/data/d1a91d2df1f6b52a1f5888f1d593abe4/getbuildoverview"
# overview(league), type(exp,depthsolo)(optional), language(en,pt,ru,th,ge,fr,es,ko)(optional)
SPECIFIC_CHARACTER = "https://poe.ninja/api/data/7ced296e802fa437db07d9827a75b7f7/GetCharacter"
# account, name, overview(league), language(en,pt,ru,th,ge,fr,es,ko)(optional), type(exp,depthsolo)(optional)
CHARACTER_LINKS = []
HELMS_LIST = []
MAX_THREAD = 100
                        

def get_all_accounts(filename: str, json):
    with open(filename, 'w+', encoding='utf-8') as file:
        accounts = json.get('accounts')
        names = json.get('names')
        account_zip = zip(accounts, names)
        for i in account_zip:
           file.write(f'{i[0]}, {i[1]}\n')
    return list(zip(accounts, names))

def write_to_file(filename, helm_list):
    cnt = Counter(helm_list)
    with open(filename, 'w') as file:
        for k, v in cnt.most_common():
            try:
                file.write("{}, {}: {}\n".format(k[0], k[1], v))
            except IndexError:
                file.write("{}, {}: {}\n".format(k[0], "", v))

def get_helmet(link: str):
    r = requests.get(link)
    character_data = r.json()

    for i in range(len(character_data['items'])):
        if(character_data['items'][i]['itemData']['inventoryId']) == "Helm":
            # Get helmet rarity and name
            if(character_data['items'][i]['itemClass']) == 3:   # Is unique
                helmet_name = character_data['items'][i]['itemData']['name']
            else:
                helmet_name = character_data['items'][i]['itemData']['baseType']
            if 'enchantMods' in character_data['items'][i]['itemData']:
                helmet_enchant = character_data['items'][i]['itemData']['enchantMods'][0]
            else: 
                helmet_enchant = ""
            helm_tuple = (helmet_name, helmet_enchant)
            HELMS_LIST.append(helm_tuple)
    time.sleep(0.25)


def concurrent_run(links):
    threads = min(MAX_THREAD, len(CHARACTER_LINKS))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        list(tqdm(executor.map(get_helmet, CHARACTER_LINKS), total=len(CHARACTER_LINKS)))

# Getting all characters
payload = {'overview': 'expedition','type': 'exp', 'language': 'en'}
r = requests.get(ALL_CHARACTERS_LIST, params=payload)
all_data = r.json()

# Save accounts
zipped_accounts = get_all_accounts("accounts.txt", all_data)

# Create links for concurrent run
for account, name in zipped_accounts:
    link = f'{SPECIFIC_CHARACTER}?account={account}&name={name}&overview=expedition&type=exp&language=en'
    CHARACTER_LINKS.append(link)

# Execute all url fetching
concurrent_run(CHARACTER_LINKS)

write_to_file('data.txt', HELMS_LIST)

# Getting individual characters
# with open('helmets.txt', 'w+', encoding='utf-8') as file:
#     for i in trange(len(zipped_accounts)):
#         helmet = get_individual_character(tuple(zipped_accounts)[i][0], tuple(zipped_accounts)[i][1], 'expedition')
#         file.write(str(helmet))
print('Done')
    
#print(character_data['items'][0]['itemSlot']) #Loop and check 1 for helmet slot check itemClass 3 for unique 2 for rare
#print(character_data['items'][8]['itemData']['enchantMods'])
#print(type(character_data['items'][0]))
#mylist = [1,1,1,2,2,3,3,3,3,3]
#c = Counter
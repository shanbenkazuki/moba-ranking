import undetected_chromedriver as uc 
import time 
from bs4 import BeautifulSoup
import urllib.parse

def get_pokemon_info(pokemon_rate):
  td_tags = pokemon_rate.find_all('td')
  rate = td_tags[1].find('div').find('div').get('value')
  img_tags = pokemon_rate.find_all('img')
  second_img_tag = img_tags[1]
  src = second_img_tag['src']
  parsed_url = urllib.parse.urlparse(src)
  params = urllib.parse.parse_qs(parsed_url.query)
  url_param = params.get('url')[0] if 'url' in params else None
  pokemon_name = ''
  if url_param:
    split_url_param = url_param.split('/')
    last_element = split_url_param[-1]
    split_last_element = last_element.replace('.png', '').split('_')
    pokemon_name = split_last_element[-1]
  
  return pokemon_name, float(rate)

options = uc.ChromeOptions() 
options.add_argument('--headless') 
driver = uc.Chrome(use_subprocess=True, options=options) 
driver.get("https://uniteapi.dev/meta") 
time.sleep(20) 

html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

pokemon_info_dict = {}

win_rate_list = soup.select('#content-container > div > div.sc-eaff77bf-0.fJbBUh > div:nth-child(2) > div > div > table > tbody > tr')
for pokemon_rate in win_rate_list:
  pokemon_name, win_rate = get_pokemon_info(pokemon_rate)
  pokemon_info_dict[pokemon_name] = {'winrate': win_rate}

pick_rate_list = soup.select('#content-container > div > div.sc-eaff77bf-0.fJbBUh > div:nth-child(1) > div > div > table > tbody > tr')
for pokemon_rate in pick_rate_list:
  pokemon_name, pick_rate = get_pokemon_info(pokemon_rate)
  if pokemon_name in pokemon_info_dict:
    pokemon_info_dict[pokemon_name].update({'pickrate': pick_rate})

min_winrate = min([pokemon_info['winrate'] for pokemon_info in pokemon_info_dict.values()])
max_winrate = max([pokemon_info['winrate'] for pokemon_info in pokemon_info_dict.values()])
min_pickrate = min([pokemon_info['pickrate'] for pokemon_info in pokemon_info_dict.values()])
max_pickrate = max([pokemon_info['pickrate'] for pokemon_info in pokemon_info_dict.values()])

# データの正規化とスコアの計算
for pokemon_name, pokemon_info in pokemon_info_dict.items():
    normalized_winrate = (pokemon_info['winrate'] - min_winrate) / (max_winrate - min_winrate)
    normalized_pickrate = (pokemon_info['pickrate'] - min_pickrate) / (max_pickrate - min_pickrate)

    # スコアを計算
    score = (normalized_winrate + normalized_pickrate) / 2

    # スコアをデータに追加
    pokemon_info_dict[pokemon_name]['score'] = score

# Define the rank thresholds
ranks = {
    'S+': 0.7,
    'S': 0.6,
    'A+': 0.5,
    'A': 0.4,
    'B': 0.3
}

# Add ranks to the data
for pokemon_name, pokemon_info in pokemon_info_dict.items():
    score = pokemon_info['score']
    for rank, threshold in ranks.items():
        if score >= threshold:
            pokemon_info_dict[pokemon_name]['rank'] = rank
            break
    else:
        pokemon_info_dict[pokemon_name]['rank'] = 'C'

driver.close()
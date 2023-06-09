import undetected_chromedriver as uc 
import time 
import urllib.parse
import conv.pokemon_unite.convPokemon as convPokemon

from bs4 import BeautifulSoup
from common import tagComponent as tag

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
  if pokemon_name == 'Single':
    pokemon_name = 'Urshifu'
  
  return pokemon_name, float(rate)

options = uc.ChromeOptions() 
options.add_argument('--headless') 
driver = uc.Chrome(use_subprocess=True, options=options) 
driver.get("https://uniteapi.dev/meta") 
time.sleep(10) 

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
    'S': 0.55,
    'A+': 0.4,
    'A': 0.25,
    'B': 0.1
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

# ポケモン名のリストを格納する辞書
ranked_pokemon = {
    'S+': [],
    'S': [],
    'A+': [],
    'A': [],
    'B': [],
    'C': []
}

# バランス
splus_balance=""
s_balance=""
a_plus_balance=""
a_balance=""
b_balance=""
c_balance=""

# アタック
splus_attack=""
s_attack=""
a_plus_attack=""
a_attack=""
b_attack=""
c_attack=""

# スピード
splus_speed=""
s_speed=""
a_plus_speed=""
a_speed=""
b_speed=""
c_speed=""

# ディフェンス
splus_defense=""
s_defense=""
a_plus_defense=""
a_defense=""
b_defense=""
c_defense=""

# サポート
splus_support=""
s_support=""
a_plus_support=""
a_support=""
b_support=""
c_support=""

# データをループして各ランクのポケモン名を取得
for pokemon, info in pokemon_info_dict.items():
    rank = info['rank']
    ranked_pokemon[rank].append(pokemon)

for pokemon in ranked_pokemon['S+']:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon)
    if style == "balance":
        splus_balance += pokemon_a_tag
    elif style == "attack":
        splus_attack += pokemon_a_tag
    elif style == "defense":
        splus_defense += pokemon_a_tag
    elif style == "speed":
        splus_speed += pokemon_a_tag
    elif style == "support":
        splus_support += pokemon_a_tag


# stier作成
for pokemon in ranked_pokemon['S']:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon)
    if style == "balance":
        s_balance += pokemon_a_tag
    elif style == "attack":
        s_attack += pokemon_a_tag
    elif style == "defense":
        s_defense += pokemon_a_tag
    elif style == "speed":
        s_speed += pokemon_a_tag
    elif style == "support":
        s_support += pokemon_a_tag

# A+ier作成
for pokemon in ranked_pokemon['A+']:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon)
    if style == "balance":
        a_plus_balance += pokemon_a_tag
    elif style == "attack":
        a_plus_attack += pokemon_a_tag
    elif style == "defense":
        a_plus_defense += pokemon_a_tag
    elif style == "speed":
        a_plus_speed += pokemon_a_tag
    elif style == "support":
        a_plus_support += pokemon_a_tag

# Atier作成
for pokemon in ranked_pokemon['A']:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon)
    if style == "balance":
        a_balance += pokemon_a_tag
    elif style == "attack":
        a_attack += pokemon_a_tag
    elif style == "defense":
        a_defense += pokemon_a_tag
    elif style == "speed":
        a_speed += pokemon_a_tag
    elif style == "support":
        a_support += pokemon_a_tag

# Btier作成
for pokemon in ranked_pokemon['B']:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon)
    if style == "balance":
        b_balance += pokemon_a_tag
    elif style == "attack":
        b_attack += pokemon_a_tag
    elif style == "defense":
        b_defense += pokemon_a_tag
    elif style == "speed":
        b_speed += pokemon_a_tag
    elif style == "support":
        b_support += pokemon_a_tag

# Ctier作成
for pokemon in ranked_pokemon['C']:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon)
    if style == "balance":
        c_balance += pokemon_a_tag
    elif style == "attack":
        c_attack += pokemon_a_tag
    elif style == "defense":
        c_defense += pokemon_a_tag
    elif style == "speed":
        c_speed += pokemon_a_tag
    elif style == "support":
        c_support += pokemon_a_tag


# タブ始まり
print('<!-- wp:loos/tab {"tabId":"479b3ce7","tabWidthPC":"flex-50","tabWidthSP":"flex-50","tabHeaders":["バランス","アタック","スピード","ディフェンス","サポート"],"className":"is-style-balloon"} -->')
print('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="flex-50"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="true" aria-controls="tab-479b3ce7-0" data-onclick="tabControl">バランス</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-1" data-onclick="tabControl">アタック</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-2" data-onclick="tabControl">スピード</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-3" data-onclick="tabControl">ディフェンス</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-4" data-onclick="tabControl">サポート</button></li></ul><div class="c-tabBody">')

# バランス
print('<!-- wp:loos/tab-body {"tabId":"479b3ce7"} --><div id="tab-479b3ce7-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_balance + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_balance + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + a_plus_balance + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_balance + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_balance + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_balance + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# アタック
print('<!-- wp:loos/tab-body {"id":1,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_attack + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_attack + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + a_plus_attack + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_attack + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_attack + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_attack + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# スピード
print('<!-- wp:loos/tab-body {"id":2,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_speed + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_speed + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + a_plus_speed + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_speed + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_speed + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_speed + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ディフェンス
print('<!-- wp:loos/tab-body {"id":3,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_defense + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_defense + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + a_plus_defense + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_defense + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_defense + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_defense + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# サポート
print('<!-- wp:loos/tab-body {"id":4,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_support + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_support + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + a_plus_support + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_support + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_support + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_support + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

#タブ終わり
print('</div></div><!-- /wp:loos/tab -->')

driver.close()
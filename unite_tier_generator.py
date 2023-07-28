import undetected_chromedriver as uc 
import time 
import urllib.parse
import tagComponent as tag
import pandas as pd

from fetch_moba_database import save_to_pokemon_meta_data
from fetch_moba_database import get_pokemon_data
from moba_version_generator import get_unite_version
from bs4 import BeautifulSoup
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

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
options.add_argument("--auto-open-devtools-for-tabs")
options.add_argument('--headless') 
driver = uc.Chrome(use_subprocess=True, options=options) 
# driver.get("https://uniteapi.dev/meta") 
# time.sleep(10) 

driver.execute_script('''window.open("http://nowsecure.nl","_blank");''') # open page in new tab
time.sleep(5) # wait until page has loaded
driver.switch_to.window(window_name=driver.window_handles[0])   # switch to first tab
driver.close() # close first tab
driver.switch_to.window(window_name=driver.window_handles[0] )  # switch back to new tab
time.sleep(2)
driver.get("https://google.com")
time.sleep(2)
driver.get("https://uniteapi.dev/meta") # this should pass cloudflare captchas now
time.sleep(10) 

html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, 'html.parser')

print(soup)

# 参照日を出力　
element = soup.select_one('h3.sc-1198f0c0-2.EhlYE')
text = element.get_text(strip=True)
prefix = "Last Updated:"
if text.startswith(prefix):
  text = text[len(prefix):].strip()
date_obj = datetime.strptime(text, "%d %B %Y")
reference_date = date_obj.strftime("%Y-%m-%d")

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

df = pd.DataFrame(pokemon_info_dict).T.astype(float)
scaler = MinMaxScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)
df_scaled['score'] = df_scaled.mean(axis=1)

for hero, score in df_scaled['score'].items():
    pokemon_info_dict[hero]['score'] = score

# Define the rank thresholds
ranks = {
    'S+': 0.5,
    'S': 0.4,
    'A+': 0.3,
    'A': 0.2,
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

# バージョン情報を取得
version = get_unite_version()

# データベースに保存する
save_to_pokemon_meta_data(pokemon_info_dict, reference_date, version)

# ポケモンの情報を取得
pokemon_data = get_pokemon_data()

# ポケモンをスタイルとランクに基づいてグループ化する辞書を作成
style_rank_dict = {
  'all-rounder': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'attacker': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'defender': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'speedster': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'supporter': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []}
}

# ポケモンをスタイルとランクごとにグループ化
for pokemon, info in pokemon_info_dict.items():
  rank = info['rank']
  style = pokemon_data[pokemon]['style']
  style_rank_dict[style][rank].append(pokemon)

# 各スタイルとランクのポケモンをタグとして追加
tier_tags = {}
for style, rank_dict in style_rank_dict.items():
  tier_tags[style] = {}
  for rank, pokemon_list in rank_dict.items():
    tier_tags[style][rank] = ''
    for pokemon in pokemon_list:
      pokemon_image_url = pokemon_data[pokemon]['image_url']
      pokemon_article_url = pokemon_data[pokemon]['article_url']
      pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
      tier_tags[style][rank] += pokemon_a_tag

# 各変数を設定
splus_balance = tier_tags['all-rounder']['S+']
splus_attack = tier_tags['attacker']['S+']
splus_defense = tier_tags['defender']['S+']
splus_speed = tier_tags['speedster']['S+']
splus_support = tier_tags['supporter']['S+']

s_balance = tier_tags['all-rounder']['S']
s_attack = tier_tags['attacker']['S']
s_defense = tier_tags['defender']['S']
s_speed = tier_tags['speedster']['S']
s_support = tier_tags['supporter']['S']

a_plus_balance = tier_tags['all-rounder']['A+']
a_plus_attack = tier_tags['attacker']['A+']
a_plus_defense = tier_tags['defender']['A+']
a_plus_speed = tier_tags['speedster']['A+']
a_plus_support = tier_tags['supporter']['A+']

a_balance = tier_tags['all-rounder']['A']
a_attack = tier_tags['attacker']['A']
a_defense = tier_tags['defender']['A']
a_speed = tier_tags['speedster']['A']
a_support = tier_tags['supporter']['A']

b_balance = tier_tags['all-rounder']['B']
b_attack = tier_tags['attacker']['B']
b_defense = tier_tags['defender']['B']
b_speed = tier_tags['speedster']['B']
b_support = tier_tags['supporter']['B']

c_balance = tier_tags['all-rounder']['C']
c_attack = tier_tags['attacker']['C']
c_defense = tier_tags['defender']['C']
c_speed = tier_tags['speedster']['C']
c_support = tier_tags['supporter']['C']

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

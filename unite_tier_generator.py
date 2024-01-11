import time
import components.swell_tag_component as tag
import pandas as pd

from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
import os
import pandas as pd
import sqlite3
from fetch_moba_database import get_pokemon_data
from datetime import datetime

def get_pokemon_info(pokemon_rate):
  rate = pokemon_rate.select_one('td div div')['value']
  src = pokemon_rate.select_one('img')['src']

  name_without_prefix = os.path.splitext(os.path.basename(src))[0].replace('t_Square_', '')
  parts = name_without_prefix.split('_')

  pokemon_name = name_without_prefix if len(parts) == 1 else '_'.join(parts[:-1])

  return pokemon_name, float(rate)

def get_rank_from_score(score):
  if score >= 1.5:
    return 'S+'
  elif score >= 1.0:
    return 'S'
  elif score >= 0.5:
    return 'A+'
  elif score >= -1.0:
    return 'A'
  elif score >= -1.5:
    return 'B'
  else:
    return 'C'

# Tierのデータを取得
page = ChromiumPage()
page.get('https://uniteapi.dev/meta')
time.sleep(5)
html = page.html
soup = BeautifulSoup(html, 'html.parser')

# データをスクレイピングして整形する
pokemon_tier_data = {}
for key, value in get_pokemon_data().items():
  # 各ポケモンのstyleを取得
  pokemon_style = value['style']

  # 新しい辞書にポケモン名とそのstyleを追加
  pokemon_tier_data[key] = {'style': pokemon_style}
  pokemon_tier_data[key]['image_url'] = value['image_url']

# 勝率を取得
win_rate_list = soup.select('#content-container > div > div.sc-eaff77bf-0.fJbBUh > div:nth-child(3) > div > div > table > tbody > tr')
for pokemon_rate in win_rate_list:
  pokemon_name, win_rate = get_pokemon_info(pokemon_rate)
  if pokemon_name == 'Meowscara':
    pokemon_name = 'Meowscarada'
  if pokemon_name in pokemon_tier_data:
    pokemon_tier_data[pokemon_name]['win_rate'] = win_rate

# 選択率を取得
pick_rate_list = soup.select('#content-container > div > div.sc-eaff77bf-0.fJbBUh > div:nth-child(1) > div > div > table > tbody > tr')
for pokemon_rate in pick_rate_list:
  pokemon_name, pick_rate = get_pokemon_info(pokemon_rate)
  # もしpokemon_nameがMeowscaraならMeowscaradaに変更
  if pokemon_name == 'Meowscara':
    pokemon_name = 'Meowscarada'
  if pokemon_name in pokemon_tier_data:
    # print(pokemon_name)
    pokemon_tier_data[pokemon_name]['pick_rate'] = pick_rate

# データベースに保存
# 参照日を取得
text = soup.select_one('#content-container > div > h3').get_text(strip=True)
date_str = text.replace("Last Updated:", "").strip()
reference_date = datetime.strptime(date_str, "%d %B %Y").strftime("%Y-%m-%d")

conn = sqlite3.connect('moba_database.sqlite3')
c = conn.cursor()

insert_query = '''
INSERT INTO pokemon_meta_data (name, win_rate, pick_rate, reference_date)
VALUES (?, ?, ?, ?)
'''

for hero, data_dict in pokemon_tier_data.items():
  try:
    c.execute(insert_query, (hero, data_dict['win_rate'], data_dict['pick_rate'], reference_date))
  except sqlite3.IntegrityError:
    error_message = f"Duplicate entry found for {hero} on {reference_date}"
    print(error_message)

conn.commit()
conn.close()

# スクレイピングしたデータからz-scoreを計算
df = pd.DataFrame(pokemon_tier_data).T

df = df.astype({'win_rate': 'float', 'pick_rate': 'float'})

# Z-score を計算
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()

df['interaction'] = df['win_rate_z'] * df['pick_rate_z']


# 総合スコアを計算（win_rate の Z-score に 60% の重み、pick_rate の Z-score に 40% の重み）
df['tier_score'] = 0.6 * df['win_rate_z'] + 0.4 * df['pick_rate_z'] - 0.1 * df['interaction']

for pokemon in pokemon_tier_data:
  pokemon_tier_data[pokemon]['tier_score'] = df.at[pokemon, 'tier_score']


# styleごとにdictを分ける
balance_dict = {}
attack_dict = {}
defense_dict = {}
speed_dict = {}
support_dict = {}

for pokemon, info in pokemon_tier_data.items():
  style = info['style']
  if style == 'all-rounder':
    balance_dict[pokemon] = info
  elif style == 'attacker':
    attack_dict[pokemon] = info
  elif style == 'defender':
    defense_dict[pokemon] = info
  elif style == 'speedster':
    speed_dict[pokemon] = info
  elif style == 'supporter':
    support_dict[pokemon] = info

splus_balance = ''
s_balance = ''
a_plus_balance = ''
a_balance = ''
b_balance = ''
c_balance = ''

splus_attack = ''
s_attack = ''
a_plus_attack = ''
a_attack = ''
b_attack = ''
c_attack = ''

splus_defense = ''
s_defense = ''
a_plus_defense = ''
a_defense = ''
b_defense = ''
c_defense = ''

splus_speed = ''
s_speed = ''
a_plus_speed = ''
a_speed = ''
b_speed = ''
c_speed = ''

splus_support = ''
s_support = ''
a_plus_support = ''
a_support = ''
b_support = ''
c_support = ''

# styleごとにランクを分ける
for pokemon, data in balance_dict.items():
  pokemon_tier_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['tier_score']) == 'S+':
    splus_balance += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'S':
    s_balance += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A+':
    a_plus_balance += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A':
    a_balance += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'B':
    b_balance += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'C':
    c_balance += pokemon_tier_img_tag

for pokemon, data in attack_dict.items():
  pokemon_tier_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['tier_score']) == 'S+':
    splus_attack += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'S':
    s_attack += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A+':
    a_plus_attack += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A':
    a_attack += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'B':
    b_attack += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'C':
    c_attack += pokemon_tier_img_tag

for pokemon, data in defense_dict.items():
  pokemon_tier_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['tier_score']) == 'S+':
    splus_defense += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'S':
    s_defense += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A+':
    a_plus_defense += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A':
    a_defense += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'B':
    b_defense += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'C':
    c_defense += pokemon_tier_img_tag

for pokemon, data in speed_dict.items():
  pokemon_tier_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['tier_score']) == 'S+':
    splus_speed += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'S':
    s_speed += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A+':
    a_plus_speed += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A':
    a_speed += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'B':
    b_speed += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'C':
    c_speed += pokemon_tier_img_tag

for pokemon, data in support_dict.items():
  pokemon_tier_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['tier_score']) == 'S+':
    splus_support += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'S':
    s_support += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A+':
    a_plus_support += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'A':
    a_support += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'B':
    b_support += pokemon_tier_img_tag
  elif get_rank_from_score(data['tier_score']) == 'C':
    c_support += pokemon_tier_img_tag

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


page.quit()

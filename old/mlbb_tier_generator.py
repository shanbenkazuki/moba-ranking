import time
import pandas as pd
import components.swell_tag_component as tag
import json

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from components.fetch_moba_database import get_hero_data
from sklearn.preprocessing import MinMaxScaler
from components.fetch_moba_database import save_to_hero_meta_data
from moba_version_generator import get_mlbb_version
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"



def switch_to_mystic(driver):
  time.sleep(2)
  #driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()
  # レジェンド表示に切り替え（ミシックがまだ集計されてない場合）
  driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()
  time.sleep(3)

def assign_rank(score):
  if score >= 0.65:
    return 'S+'
  elif score >= 0.45:
    return 'S'
  elif score >= 0.35:
    return 'A+'
  elif score >= 0.20:
    return 'A'
  elif score >= 0.10:
    return 'B'
  else:
    return 'C'

def get_hero_meta_data(rateList):
  hero_meta_data = {}
  for heroRate in rateList:
    heroEn = heroRate.span.string
    winRatePoint = heroRate.contents[2].string.split("%")[0]
    popRatePoint = heroRate.contents[4].string.split("%")[0]
    banRatePoint = heroRate.contents[6].string.split("%")[0]
    hero_meta_data[heroEn] = {
      'win_rate': winRatePoint,
      'pick_rate': popRatePoint,
      'ban_rate': banRatePoint
    }
  return hero_meta_data

def normalize_data(hero_meta_data):
  df = pd.DataFrame(hero_meta_data).T.astype(float)
  scaler = MinMaxScaler()
  df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)
  df_scaled['Ranking'] = df_scaled.mean(axis=1)
  return df_scaled

def add_ranking_to_hero_data(hero_meta_data, df_scaled):
  for character in hero_meta_data:
    score = df_scaled.loc[character, 'Ranking']
    rank = assign_rank(score)
    hero_meta_data[character]['Score'] = score
    hero_meta_data[character]['Rank'] = rank
  return hero_meta_data

def group_heroes_by_lane_and_rank(hero_meta_data, hero_data):
  role_rank_dict = {
    'Fighter': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Mage': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Tank': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Assassin': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Marksman': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Support': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []}
  }
  for hero, info in hero_meta_data.items():
    rank = info['Rank']
    role = hero_data[hero]['role']
    role_rank_dict[role][rank].append(hero)
  return role_rank_dict

def generate_tier_tags(lane_rank_dict, hero_data):
  tier_tags = {}
  for role, rank_dict in lane_rank_dict.items():
    tier_tags[role] = {}
    for rank, hero_list in rank_dict.items():
      tier_tags[role][rank] = ''
      for hero in hero_list:
        hero_image_url = hero_data[hero]['image_url']
        hero_article_url = hero_data[hero]['article_url']
        hero_a_tag = tag.createHeroATag(hero_image_url, hero_article_url)
        tier_tags[role][rank] += hero_a_tag
  return tier_tags

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(WAIT_TIME)
driver.get(DISPLAY_URL)

time.sleep(10)

# 画面遷移とデータ取得の処理を関数化
switch_to_mystic(driver)
rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")

# heroデータ取得
hero_data = get_hero_data()

# ヒーローメタデータの生成と正規化
hero_meta_data = get_hero_meta_data(rateList)

# print(hero_meta_data)

# print(json.dumps(hero_meta_data))

df_scaled = normalize_data(hero_meta_data)

print(df_scaled)

# ランキング値の追加
hero_meta_data = add_ranking_to_hero_data(hero_meta_data, df_scaled)

# 参照日を取得
reference_date = BeautifulSoup(driver.page_source, 'html.parser').select_one("#rank > div.header > div:nth-child(1) > ul > li").text

# バージョン情報を取得
version = get_mlbb_version()

# データベースに保存
save_to_hero_meta_data(hero_meta_data, reference_date, version)

# レーンとランクでヒーローをグループ化
lane_rank_dict = group_heroes_by_lane_and_rank(hero_meta_data, hero_data)

# タグ生成
tier_tags = generate_tier_tags(lane_rank_dict, hero_data)

splusFighterHero = tier_tags['Fighter']['S+']
sFighterHero = tier_tags['Fighter']['S']
aplusFighterHero = tier_tags['Fighter']['A+']
aFighterHero = tier_tags['Fighter']['A']
bFighterHero = tier_tags['Fighter']['B']
cFighterHero = tier_tags['Fighter']['C']

splusMageHero = tier_tags['Mage']['S+']
sMageHero = tier_tags['Mage']['S']
aplusMageHero = tier_tags['Mage']['A+']
aMageHero = tier_tags['Mage']['A']
bMageHero = tier_tags['Mage']['B']
cMageHero = tier_tags['Mage']['C']

splusTankHero = tier_tags['Tank']['S+']
sTankHero = tier_tags['Tank']['S']
aplusTankHero = tier_tags['Tank']['A+']
aTankHero = tier_tags['Tank']['A']
bTankHero = tier_tags['Tank']['B']
cTankHero = tier_tags['Tank']['C']

splusAssassinHero = tier_tags['Assassin']['S+']
sAssassinHero = tier_tags['Assassin']['S']
aplusAssassinHero = tier_tags['Assassin']['A+']
aAssassinHero = tier_tags['Assassin']['A']
bAssassinHero = tier_tags['Assassin']['B']
cAssassinHero = tier_tags['Assassin']['C']

splusMarksmanHero = tier_tags['Marksman']['S+']
sMarksmanHero = tier_tags['Marksman']['S']
aplusMarksmanHero = tier_tags['Marksman']['A+']
aMarksmanHero = tier_tags['Marksman']['A']
bMarksmanHero = tier_tags['Marksman']['B']
cMarksmanHero = tier_tags['Marksman']['C']

splusSupportHero = tier_tags['Support']['S+']
sSupportHero = tier_tags['Support']['S']
aplusSupportHero = tier_tags['Support']['A+']
aSupportHero = tier_tags['Support']['A']
bSupportHero = tier_tags['Support']['B']
cSupportHero = tier_tags['Support']['C']

# タブ始まり
print('<!-- wp:loos/tab {"tabId":"55c27d22","tabWidthPC":"flex-50","tabHeaders":["ファイター","メイジ","タンク","アサシン","ハンター","サポート"],"className":"is-style-balloon"} -->')
print('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="auto"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="true" aria-controls="tab-55c27d22-0" data-onclick="tabControl">ファイター</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-1" data-onclick="tabControl">メイジ</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-2" data-onclick="tabControl">タンク</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-3" data-onclick="tabControl">アサシン</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-4" data-onclick="tabControl">ハンター</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-5" data-onclick="tabControl">サポート</button></li></ul><div class="c-tabBody">')

# Fighter
print('<!-- wp:loos/tab-body {"tabId":"55c27d22"} --><div id="tab-55c27d22-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusFighterHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sFighterHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusFighterHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aFighterHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bFighterHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cFighterHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# Mage
print('<!-- wp:loos/tab-body {"id":1,"tabId":"55c27d22"} --><div id="tab-55c27d22-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusMageHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sMageHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusMageHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aMageHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bMageHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cMageHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# Tank
print('<!-- wp:loos/tab-body {"id":2,"tabId":"55c27d22"} --><div id="tab-55c27d22-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusTankHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sTankHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusTankHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aTankHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bTankHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cTankHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# Assassin
print('<!-- wp:loos/tab-body {"id":3,"tabId":"55c27d22"} --><div id="tab-55c27d22-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusAssassinHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sAssassinHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusAssassinHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aAssassinHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bAssassinHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cAssassinHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# Marksman
print('<!-- wp:loos/tab-body {"id":4,"tabId":"55c27d22"} --><div id="tab-55c27d22-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusMarksmanHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sMarksmanHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusMarksmanHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aMarksmanHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bMarksmanHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cMarksmanHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# Support
print('<!-- wp:loos/tab-body {"id":5,"tabId":"55c27d22"} --><div id="tab-55c27d22-5" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusSupportHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sSupportHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusSupportHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aSupportHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bSupportHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cSupportHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

#タブ終わり
print('</div></div><!-- /wp:loos/tab -->')

import time
import tagComponent as tag
import pandas as pd

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from old.fetch_moba_database_4 import get_hero_data
from sklearn.preprocessing import MinMaxScaler

def assign_rank(score):
  if score >= 0.7:
    return 'S+'
  elif score >= 0.6:
    return 'S'
  elif score >= 0.5:
    return 'A+'
  elif score >= 0.4:
    return 'A'
  elif score >= 0.3:
    return 'B'
  else:
    return 'C'


DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

# 画面遷移
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(DISPLAY_URL)
driver.implicitly_wait(WAIT_TIME)

time.sleep(2)

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()
# レジェンド表示に切り替え（ミシックがまだ集計されてない場合）
#driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()

time.sleep(3)

#ランキング抽出
rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")

# #heroデータ取得
hero_data = get_hero_data()

hero_meta_data = {}
for heroRate in rateList:
  heroEn = heroRate.span.string
  heroJa = hero_data[heroEn]['name_jp']
  heroImageURL = hero_data[heroEn]['image_url']
  heroArticleURL = hero_data[heroEn]['article_url']
  heroAtag = tag.createHeroATag(heroImageURL, heroArticleURL)
  winRatePoint = heroRate.contents[2].string.split("%")[0]
  popRatePoint = heroRate.contents[4].string.split("%")[0]
  banRatePoint = heroRate.contents[6].string.split("%")[0]
  hero_meta_data[heroEn] = {
    'win_rate': winRatePoint,
    'pick_rate': popRatePoint,
    'ban_rate': banRatePoint
  }
# DataFrameに変換
df = pd.DataFrame(hero_meta_data).T

# 値をfloatに変換
df = df.astype(float)

# 正規化
scaler = MinMaxScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

# 平均の計算とランキング列の追加
df_scaled['Ranking'] = df_scaled.mean(axis=1)

# 以下が元のデータにランキング値を追加するコードです。
for character in hero_meta_data:
  hero_meta_data[character]['Score'] = df_scaled.loc[character, 'Ranking']

for character in hero_meta_data:
  score = hero_meta_data[character]['Score']
  hero_meta_data[character]['Rank'] = assign_rank(score)

lane_rank_dict = {
  'Jungle': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'Gold': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'EXP': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'Roam': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  'Mid': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []}
}

for hero, info in hero_meta_data.items():
  rank = info['Rank']
  suggested_lane = hero_data[hero]['suggested_lane']
  suggested_lane_list = suggested_lane.split(",")
  for lane in suggested_lane_list:
    lane_rank_dict[lane][rank].append(hero)

# 各スタイルとランクのポケモンをタグとして追加
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

splusJungleHero = tier_tags['Jungle']['S+']
sJungleHero = tier_tags['Jungle']['S']
aplusJungleHero = tier_tags['Jungle']['A+']
aJungleHero = tier_tags['Jungle']['A']
bJungleHero = tier_tags['Jungle']['B']
cJungleHero = tier_tags['Jungle']['C']

splusRoamHero = tier_tags['Roam']['S+']
sRoamHero = tier_tags['Roam']['S']
aplusRoamHero = tier_tags['Roam']['A+']
aRoamHero = tier_tags['Roam']['A']
bRoamHero = tier_tags['Roam']['B']
cRoamHero = tier_tags['Roam']['C']

splusMidHero = tier_tags['Mid']['S+']
sMidHero = tier_tags['Mid']['S']
aplusMidHero = tier_tags['Mid']['A+']
aMidHero = tier_tags['Mid']['A']
bMidHero = tier_tags['Mid']['B']
cMidHero = tier_tags['Mid']['C']

splusGoldHero = tier_tags['Gold']['S+']
sGoldHero = tier_tags['Gold']['S']
aplusGoldHero = tier_tags['Gold']['A+']
aGoldHero = tier_tags['Gold']['A']
bGoldHero = tier_tags['Gold']['B']
cGoldHero = tier_tags['Gold']['C']

splusExpHero = tier_tags['EXP']['S+']
sExpHero = tier_tags['EXP']['S']
aplusExpHero = tier_tags['EXP']['A+']
aExpHero = tier_tags['EXP']['A']
bExpHero = tier_tags['EXP']['B']
cExpHero = tier_tags['EXP']['C']

# タブ始まり
print('<!-- wp:loos/tab {"tabId":"9e24a182","tabWidthPC":"flex-50","tabWidthSP":"flex-50","tabHeaders":["Jg","Gold","Exp","Roam","Mid"],"className":"is-style-balloon"} -->')
print('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="flex-50"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="true" aria-controls="tab-9e24a182-0" data-onclick="tabControl">Jg</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-1" data-onclick="tabControl">Gold</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-2" data-onclick="tabControl">Exp</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-3" data-onclick="tabControl">Roam</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-4" data-onclick="tabControl">Mid</button></li></ul><div class="c-tabBody">')

# Jungle
print('<!-- wp:loos/tab-body {"tabId":"9e24a182"} --><div id="tab-9e24a182-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusJungleHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sJungleHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusJungleHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aJungleHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bJungleHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cJungleHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ゴールド
print('<!-- wp:loos/tab-body {"id":1,"tabId":"9e24a182"} --><div id="tab-9e24a182-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusGoldHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sGoldHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusGoldHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aGoldHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bGoldHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cGoldHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# EXP
print('<!-- wp:loos/tab-body {"id":2,"tabId":"9e24a182"} --> <div id="tab-9e24a182-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusExpHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sExpHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusExpHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aExpHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bExpHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cExpHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ローム
print('<!-- wp:loos/tab-body {"id":3,"tabId":"9e24a182"} --><div id="tab-9e24a182-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusRoamHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sRoamHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusRoamHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aRoamHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bRoamHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cRoamHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ミッド
print('<!-- wp:loos/tab-body {"id":4,"tabId":"9e24a182"} --><div id="tab-9e24a182-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusMidHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sMidHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusMidHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aMidHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bMidHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cMidHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

#タブ終わり
print('</div></div><!-- /wp:loos/tab -->')

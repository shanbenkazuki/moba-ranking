import pandas as pd
import components.swell_tag_component as tag
import sqlite3
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from fetch_moba_database import get_hero_data
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_rank_from_score(score):
  if score >= 1.0:
    return 'S+'
  elif score >= 0.5:
    return 'S'
  elif score >= 0:
    return 'A+'
  elif score >= -0.5:
    return 'A'
  elif score >= -1.0:
    return 'B'
  else:
    return 'C'
  
DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(WAIT_TIME)
driver.get(DISPLAY_URL)

# プライバシーポリシーを閉じる
WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='mt-cb-policy']/div/div[2]"))).click()

# Mythic+のタブに切り替える
# WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[2]"))).click()
# rank_level = 'Mythic+'

# Mythic Glory+のタブに切り替える
WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[3]"))).click()
rank_level = 'Mythic Glory+'

# 画面が表示されるまで待つ
WebDriverWait(driver, WAIT_TIME).until(
  EC.presence_of_element_located((By.CSS_SELECTOR, ".slotwrapper > ul > li > a"))
)

time.sleep(1)

# データをスクレイピングして整形する
rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
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

# データをdbに保存する
reference_date = BeautifulSoup(driver.page_source, 'html.parser').select_one("#rank > div.header > div:nth-child(1) > ul > li").text
conn = sqlite3.connect('moba_database.sqlite3')
c = conn.cursor()

insert_query = '''
INSERT INTO hero_meta_data (name, win_rate, pick_rate, ban_rate, reference_date, rank_level)
VALUES (?, ?, ?, ?, ?, ?)
'''

for hero, data_dict in hero_meta_data.items():
  try:
    c.execute(insert_query, (hero, data_dict['win_rate'], data_dict['pick_rate'], data_dict['ban_rate'], reference_date, rank_level))
  except sqlite3.IntegrityError:
    error_message = f"Duplicate entry found for {hero} on {reference_date}"
    print(error_message)

conn.commit()
conn.close()

# スクレイピングしたデータからz-socreを計算する
pd.set_option('display.max_rows', None)
df = pd.DataFrame(hero_meta_data).T
df = df.astype({'win_rate': 'float', 'pick_rate': 'float', 'ban_rate': 'float'})
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()
df['interaction'] = df['win_rate_z'] * df['pick_rate_z']
df['tier_score_z'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']

df.to_csv('hero_meta_data.csv', index=True)

# hero_dictにzscoreを保存する
hero_dict = {}
for hero, data in get_hero_data().items():
  hero_dict[hero] = {
    'role': data['role'],
    'image_url': data['image_url'],
    'z_score': df.loc[hero, 'tier_score_z'] if hero in df.index else None
  }

## hero_dictをroleごとに分ける
tank_hero_dict = {}
fighter_hero_dict = {}
support_hero_dict = {}
assassin_hero_dict = {}
marksman_hero_dict = {}
mage_hero_dict = {}

for role, data in hero_dict.items():
  if data['role'] == 'Tank':
    tank_hero_dict[role] = data
  elif data['role'] == 'Fighter':
    fighter_hero_dict[role] = data
  elif data['role'] == 'Support':
    support_hero_dict[role] = data
  elif data['role'] == 'Assassin':
    assassin_hero_dict[role] = data
  elif data['role'] == 'Marksman':
    marksman_hero_dict[role] = data
  elif data['role'] == 'Mage':
    mage_hero_dict[role] = data

# zscoreをもとにtierを作成する
splusFighterHero = ''
sFighterHero = ''
aplusFighterHero = ''
aFighterHero = ''
bFighterHero = ''
cFighterHero = ''

splusTankHero = ''
sTankHero = ''
aplusTankHero = ''
aTankHero = ''
bTankHero = ''
cTankHero = ''

splusSupportHero = ''
sSupportHero = ''
aplusSupportHero = ''
aSupportHero = ''
bSupportHero = ''
cSupportHero = ''

splusAssassinHero = ''
sAssassinHero = ''
aplusAssassinHero = ''
aAssassinHero = ''
bAssassinHero = ''
cAssassinHero = ''

splusMarksmanHero = ''
sMarksmanHero = ''
aplusMarksmanHero = ''
aMarksmanHero = ''
bMarksmanHero = ''
cMarksmanHero = ''

splusMageHero = ''
sMageHero = ''
aplusMageHero = ''
aMageHero = ''
bMageHero = ''
cMageHero = ''

for hero, data in tank_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['z_score']) == 'S+':
    splusTankHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'S':
    sTankHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A+':
    aplusTankHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A':
    aTankHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'B':
    bTankHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'C':
    cTankHero += tier_hero_img_tag


for hero,data in fighter_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['z_score']) == 'S+':
    splusFighterHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'S':
    sFighterHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A+':
    aplusFighterHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A':
    aFighterHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'B':
    bFighterHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'C':
    cFighterHero += tier_hero_img_tag

for hero,data in support_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['z_score']) == 'S+':
    splusSupportHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'S':
    sSupportHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A+':
    aplusSupportHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A':
    aSupportHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'B':
    bSupportHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'C':
    cSupportHero += tier_hero_img_tag

for hero,data in assassin_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['z_score']) == 'S+':
    splusAssassinHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'S':
    sAssassinHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A+':
    aplusAssassinHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A':
    aAssassinHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'B':
    bAssassinHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'C':
    cAssassinHero += tier_hero_img_tag

for hero,data in marksman_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['z_score']) == 'S+':
    splusMarksmanHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'S':
    sMarksmanHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A+':
    aplusMarksmanHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A':
    aMarksmanHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'B':
    bMarksmanHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'C':
    cMarksmanHero += tier_hero_img_tag

for hero,data in mage_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if get_rank_from_score(data['z_score']) == 'S+':
    splusMageHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'S':
    sMageHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A+':
    aplusMageHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'A':
    aMageHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'B':
    bMageHero += tier_hero_img_tag
  elif get_rank_from_score(data['z_score']) == 'C':
    cMageHero += tier_hero_img_tag

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

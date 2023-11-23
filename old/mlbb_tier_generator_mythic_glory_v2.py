import time
import pandas as pd
import tagComponent as tag
import json

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from fetch_moba_database import get_hero_data
from sklearn.preprocessing import MinMaxScaler
from fetch_moba_database import save_to_hero_meta_data
from moba_version_generator import get_mlbb_version
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def check_score(score):
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

time.sleep(20)

driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

time.sleep(3)

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

# heroデータ取得
# get_hero_data()のキーをhero_dictにキーにし、その中にroleとimage_urlを追加する
hero_dict = {}
for hero, data in get_hero_data().items():
  hero_dict[hero] = {'role': data['role'], 'image_url': data['image_url']}

# スクレイピングで取得したデータ
# hero_meta_data = {'Minotaur': {'win_rate': '55.43', 'pick_rate': '0.81', 'ban_rate': '1.9'}, 'Diggie': {'win_rate': '55.23', 'pick_rate': '0.58', 'ban_rate': '10.53'}, 'Lolita': {'win_rate': '54.31', 'pick_rate': '0.46', 'ban_rate': '4.82'}, 'Floryn': {'win_rate': '54.19', 'pick_rate': '0.8', 'ban_rate': '51.76'}, 'Popol and Kupa': {'win_rate': '53.97', 'pick_rate': '0.77', 'ban_rate': '1.12'}, 'Rafaela': {'win_rate': '53.84', 'pick_rate': '1.24', 'ban_rate': '19.26'}, 'Guinevere': {'win_rate': '53.82', 'pick_rate': '1.85', 'ban_rate': '34.54'}, 'Argus': {'win_rate': '53.79', 'pick_rate': '0.29', 'ban_rate': '0.1'}, 'Odette': {'win_rate': '53.69', 'pick_rate': '0.82', 'ban_rate': '0.16'}, 'Terizla': {'win_rate': '53.67', 'pick_rate': '1.66', 'ban_rate': '4.89'}, 'Zhask': {'win_rate': '53.67', 'pick_rate': '0.7', 'ban_rate': '0.27'}, 'Wanwan': {'win_rate': '53.6', 'pick_rate': '1.45', 'ban_rate': '19.93'}, 'Khaleed': {'win_rate': '53.38', 'pick_rate': '0.57', 'ban_rate': '2.43'}, 'Phoveus': {'win_rate': '52.98', 'pick_rate': '0.19', 'ban_rate': '0.23'}, 'Luo Yi': {'win_rate': '52.96', 'pick_rate': '0.66', 'ban_rate': '0.27'}, 'Gord': {'win_rate': '52.95', 'pick_rate': '0.88', 'ban_rate': '0.14'}, 'Ixia': {'win_rate': '52.83', 'pick_rate': '0.8', 'ban_rate': '2.99'}, 'Aldous': {'win_rate': '52.77', 'pick_rate': '1.31', 'ban_rate': '1.7'}, 'Belerick': {'win_rate': '52.76', 'pick_rate': '0.72', 'ban_rate': '0.67'}, 'Masha': {'win_rate': '52.72', 'pick_rate': '0.15', 'ban_rate': '0.19'}, 'Cyclops': {'win_rate': '52.47', 'pick_rate': '0.9', 'ban_rate': '0.1'}, 'Yi Sun-shin': {'win_rate': '52.39', 'pick_rate': '0.26', 'ban_rate': '0.04'}, 'Aamon': {'win_rate': '52.29', 'pick_rate': '0.53', 'ban_rate': '0.3'}, 'Aulus': {'win_rate': '52.27', 'pick_rate': '0.18', 'ban_rate': '0.04'}, 'Harley': {'win_rate': '52.25', 'pick_rate': '1.26', 'ban_rate': '14.76'}, 'Hylos': {'win_rate': '52.24', 'pick_rate': '0.3', 'ban_rate': '0.06'}, 'Ruby': {'win_rate': '52.23', 'pick_rate': '0.67', 'ban_rate': '0.14'}, 'Bane': {'win_rate': '52.23', 'pick_rate': '0.4', 'ban_rate': '0.06'}, 'Bruno': {'win_rate': '52.21', 'pick_rate': '1.6', 'ban_rate': '0.66'}, 'Lylia': {'win_rate': '52.12', 'pick_rate': '0.85', 'ban_rate': '0.16'}, 'Benedetta': {'win_rate': '52.08', 'pick_rate': '0.6', 'ban_rate': '0.35'}, 'Carmilla': {'win_rate': '52.02', 'pick_rate': '0.14', 'ban_rate': '0.12'}, 'Hanabi': {'win_rate': '51.81', 'pick_rate': '3.04', 'ban_rate': '3.47'}, "Chang'e": {'win_rate': '51.8', 'pick_rate': '1.74', 'ban_rate': '2.89'}, 'Hanzo': {'win_rate': '51.79', 'pick_rate': '0.31', 'ban_rate': '0.63'}, 'Gloo': {'win_rate': '51.75', 'pick_rate': '0.11', 'ban_rate': '0.11'}, 'Faramis': {'win_rate': '51.71', 'pick_rate': '0.32', 'ban_rate': '1.43'}, 'Baxia': {'win_rate': '51.56', 'pick_rate': '0.25', 'ban_rate': '0.36'}, 'Alice': {'win_rate': '51.54', 'pick_rate': '0.12', 'ban_rate': '0.04'}, 'Joy': {'win_rate': '51.41', 'pick_rate': '0.35', 'ban_rate': '2.88'}, 'Gatotkaca': {'win_rate': '51.38', 'pick_rate': '0.96', 'ban_rate': '0.35'}, 'Roger': {'win_rate': '51.36', 'pick_rate': '1.23', 'ban_rate': '5.05'}, 'Moskov': {'win_rate': '51.34', 'pick_rate': '1.88', 'ban_rate': '2.78'}, 'Melissa': {'win_rate': '51.3', 'pick_rate': '0.77', 'ban_rate': '0.48'}, 'Freya': {'win_rate': '51.29', 'pick_rate': '0.46', 'ban_rate': '0.17'}, 'Angela': {'win_rate': '51.24', 'pick_rate': '1.45', 'ban_rate': '69.64'}, 'Brody': {'win_rate': '51.1', 'pick_rate': '1.56', 'ban_rate': '0.44'}, 'Arlott': {'win_rate': '51.07', 'pick_rate': '0.66', 'ban_rate': '3.72'}, 'Tigreal': {'win_rate': '51.05', 'pick_rate': '1.45', 'ban_rate': '1.04'}, 'Valir': {'win_rate': '50.89', 'pick_rate': '1.93', 'ban_rate': '30.67'}, 'Julian': {'win_rate': '50.85', 'pick_rate': '0.48', 'ban_rate': '0.21'}, 'Harith': {'win_rate': '50.85', 'pick_rate': '0.33', 'ban_rate': '0.31'}, 'X.Borg': {'win_rate': '50.79', 'pick_rate': '0.98', 'ban_rate': '2.41'}, 'Thamuz': {'win_rate': '50.74', 'pick_rate': '0.69', 'ban_rate': '0.16'}, 'Helcurt': {'win_rate': '50.67', 'pick_rate': '0.38', 'ban_rate': '0.43'}, 'Xavier': {'win_rate': '50.62', 'pick_rate': '0.89', 'ban_rate': '0.1'}, 'Alpha': {'win_rate': '50.58', 'pick_rate': '1.64', 'ban_rate': '1.62'}, 'Edith': {'win_rate': '50.43', 'pick_rate': '0.88', 'ban_rate': '0.87'}, 'Natalia': {'win_rate': '50.38', 'pick_rate': '0.27', 'ban_rate': '0.44'}, 'Yu Zhong': {'win_rate': '50.35', 'pick_rate': '1.5', 'ban_rate': '0.38'}, 'Nolan': {'win_rate': '50.32', 'pick_rate': '0.77', 'ban_rate': '75.75'}, 'Alucard': {'win_rate': '50.15', 'pick_rate': '0.46', 'ban_rate': '0.12'}, 'Natan': {'win_rate': '50.14', 'pick_rate': '0.41', 'ban_rate': '0.12'}, 'Yin': {'win_rate': '50', 'pick_rate': '0.87', 'ban_rate': '5.18'}, 'Kadita': {'win_rate': '49.93', 'pick_rate': '0.88', 'ban_rate': '0.6'}, 'Karina': {'win_rate': '49.89', 'pick_rate': '0.96', 'ban_rate': '3.53'}, 'Granger': {'win_rate': '49.77', 'pick_rate': '0.81', 'ban_rate': '0.1'}, 'Irithel': {'win_rate': '49.74', 'pick_rate': '1.3', 'ban_rate': '0.32'}, 'Cecilion': {'win_rate': '49.66', 'pick_rate': '1.22', 'ban_rate': '0.19'}, 'Uranus': {'win_rate': '49.59', 'pick_rate': '0.4', 'ban_rate': '0.2'}, 'Khufra': {'win_rate': '49.56', 'pick_rate': '1.24', 'ban_rate': '2.4'}, 'Eudora': {'win_rate': '49.53', 'pick_rate': '0.8', 'ban_rate': '0.46'}, 'Clint': {'win_rate': '49.5', 'pick_rate': '0.78', 'ban_rate': '0.06'}, 'Estes': {'win_rate': '49.44', 'pick_rate': '0.77', 'ban_rate': '44.65'}, 'Kagura': {'win_rate': '49.39', 'pick_rate': '0.56', 'ban_rate': '0.07'}, 'Atlas': {'win_rate': '49.34', 'pick_rate': '0.74', 'ban_rate': '3.17'}, 'Vale': {'win_rate': '49.32', 'pick_rate': '0.81', 'ban_rate': '0.29'}, 'Kaja': {'win_rate': '49.26', 'pick_rate': '0.21', 'ban_rate': '0.22'}, 'Hilda': {'win_rate': '49.25', 'pick_rate': '0.5', 'ban_rate': '0.27'}, 'Badang': {'win_rate': '49.23', 'pick_rate': '0.4', 'ban_rate': '0.05'}, 'Martis': {'win_rate': '49.18', 'pick_rate': '1.79', 'ban_rate': '12.07'}, 'Saber': {'win_rate': '49.07', 'pick_rate': '0.89', 'ban_rate': '5.59'}, 'Kimmy': {'win_rate': '49.06', 'pick_rate': '0.18', 'ban_rate': '0.05'}, 'Sun': {'win_rate': '49', 'pick_rate': '0.59', 'ban_rate': '0.29'}, 'Leomord': {'win_rate': '48.88', 'pick_rate': '0.21', 'ban_rate': '0.03'}, 'Lunox': {'win_rate': '48.67', 'pick_rate': '0.24', 'ban_rate': '0.03'}, 'Claude': {'win_rate': '48.36', 'pick_rate': '1.33', 'ban_rate': '0.13'}, 'Yve': {'win_rate': '48.34', 'pick_rate': '0.13', 'ban_rate': '0.06'}, 'Akai': {'win_rate': '48.33', 'pick_rate': '0.44', 'ban_rate': '0.13'}, 'Novaria': {'win_rate': '48.25', 'pick_rate': '1.58', 'ban_rate': '14.95'}, 'Miya': {'win_rate': '48.23', 'pick_rate': '0.71', 'ban_rate': '0.22'}, 'Minsitthar': {'win_rate': '48.22', 'pick_rate': '0.47', 'ban_rate': '2.08'}, 'Layla': {'win_rate': '48.2', 'pick_rate': '1.49', 'ban_rate': '0.79'}, 'Barats': {'win_rate': '48.16', 'pick_rate': '0.08', 'ban_rate': '0.04'}, 'Fredrinn': {'win_rate': '48.12', 'pick_rate': '0.62', 'ban_rate': '0.46'}, 'Johnson': {'win_rate': '48.08', 'pick_rate': '0.87', 'ban_rate': '1.88'}, 'Zilong': {'win_rate': '48.04', 'pick_rate': '1.07', 'ban_rate': '0.36'}, 'Ling': {'win_rate': '48.02', 'pick_rate': '0.54', 'ban_rate': '0.23'}, 'Dyrroth': {'win_rate': '47.97', 'pick_rate': '1.53', 'ban_rate': '0.33'}, 'Mathilda': {'win_rate': '47.95', 'pick_rate': '0.71', 'ban_rate': '69.96'}, 'Hayabusa': {'win_rate': '47.93', 'pick_rate': '0.73', 'ban_rate': '0.18'}, 'Lapu-Lapu': {'win_rate': '47.87', 'pick_rate': '0.42', 'ban_rate': '0.03'}, 'Silvanna': {'win_rate': '47.67', 'pick_rate': '0.25', 'ban_rate': '0.04'}, 'Vexana': {'win_rate': '47.66', 'pick_rate': '1.03', 'ban_rate': '0.48'}, 'Gusion': {'win_rate': '47.63', 'pick_rate': '1.29', 'ban_rate': '0.59'}, 'Jawhead': {'win_rate': '47.46', 'pick_rate': '0.53', 'ban_rate': '0.1'}, 'Lancelot': {'win_rate': '46.94', 'pick_rate': '2.41', 'ban_rate': '1.98'}, 'Esmeralda': {'win_rate': '46.91', 'pick_rate': '0.64', 'ban_rate': '0.24'}, 'Selena': {'win_rate': '46.88', 'pick_rate': '0.49', 'ban_rate': '0.1'}, 'Fanny': {'win_rate': '46.71', 'pick_rate': '0.78', 'ban_rate': '16.24'}, 'Aurora': {'win_rate': '46.42', 'pick_rate': '0.1', 'ban_rate': '0.04'}, 'Grock': {'win_rate': '46.4', 'pick_rate': '0.14', 'ban_rate': '0.03'}, 'Franco': {'win_rate': '46.37', 'pick_rate': '2.55', 'ban_rate': '4.67'}, 'Nana': {'win_rate': '46.13', 'pick_rate': '1.33', 'ban_rate': '2.42'}, 'Karrie': {'win_rate': '46.11', 'pick_rate': '0.66', 'ban_rate': '0.05'}, 'Lesley': {'win_rate': '45.86', 'pick_rate': '1.23', 'ban_rate': '0.33'}, 'Pharsa': {'win_rate': '45.16', 'pick_rate': '0.38', 'ban_rate': '0.03'}, 'Valentina': {'win_rate': '44.92', 'pick_rate': '0.48', 'ban_rate': '0.43'}, 'Balmond': {'win_rate': '44.89', 'pick_rate': '0.56', 'ban_rate': '0.09'}, 'Paquito': {'win_rate': '44.72', 'pick_rate': '0.47', 'ban_rate': '0.06'}, 'Beatrix': {'win_rate': '44.71', 'pick_rate': '0.72', 'ban_rate': '0.05'}, 'Chou': {'win_rate': '44.33', 'pick_rate': '1.43', 'ban_rate': '0.65'}}

# データをdbに保存する

# データからzsocreを計算する
# DataFrameに変換
pd.set_option('display.max_rows', None)
df = pd.DataFrame(hero_meta_data).T
df = df.astype({'win_rate': 'float', 'pick_rate': 'float', 'ban_rate': 'float'})

# Zスコアの計算
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()

# 相互作用項の導入
df['interaction'] = df['win_rate_z'] * df['pick_rate_z']

# 指定された重みに基づいてtier_score_zを計算
df['tier_score_z'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']


# hero_dictにzscoreを保存する
# TODO:いない場合の処理を追加する
for hero in df.index:
  hero_dict[hero]['z_score'] = df.loc[hero, 'tier_score_z']

# for hero in df.index:
#     hero_dict[hero] = {'z_score': df.loc[hero, 'tier_score_z']}

# 結果の確認
# print(hero_dict)

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

# 結果の確認
# print(tank_hero_dict)
# print(fighter_hero_dict)
# print(support_hero_dict)
# print(assassin_hero_dict)
# print(marksman_hero_dict)
# print(mage_hero_dict)

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
  if check_score(data['z_score']) == 'S+':
    splusTankHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'S':
    sTankHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A+':
    aplusTankHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A':
    aTankHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'B':
    bTankHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'C':
    cTankHero += tier_hero_img_tag

# print(splusTankHero)
# print(sTankHero)
# print(aplusTankHero)
# print(aTankHero)
# print(bTankHero)
# print(cTankHero)

for hero,data in fighter_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if check_score(data['z_score']) == 'S+':
    splusFighterHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'S':
    sFighterHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A+':
    aplusFighterHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A':
    aFighterHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'B':
    bFighterHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'C':
    cFighterHero += tier_hero_img_tag

for hero,data in support_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if check_score(data['z_score']) == 'S+':
    splusSupportHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'S':
    sSupportHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A+':
    aplusSupportHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A':
    aSupportHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'B':
    bSupportHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'C':
    cSupportHero += tier_hero_img_tag

for hero,data in assassin_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if check_score(data['z_score']) == 'S+':
    splusAssassinHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'S':
    sAssassinHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A+':
    aplusAssassinHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A':
    aAssassinHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'B':
    bAssassinHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'C':
    cAssassinHero += tier_hero_img_tag

for hero,data in marksman_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if check_score(data['z_score']) == 'S+':
    splusMarksmanHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'S':
    sMarksmanHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A+':
    aplusMarksmanHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A':
    aMarksmanHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'B':
    bMarksmanHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'C':
    cMarksmanHero += tier_hero_img_tag

for hero,data in mage_hero_dict.items():
  tier_hero_img_tag = tag.createHeroImgTag(data['image_url'])
  if check_score(data['z_score']) == 'S+':
    splusMageHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'S':
    sMageHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A+':
    aplusMageHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'A':
    aMageHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'B':
    bMageHero += tier_hero_img_tag
  elif check_score(data['z_score']) == 'C':
    cMageHero += tier_hero_img_tag

# hero名の辞書をget_hero_data()で取得
# hero_name_dict = {}
# for hero, data in hero_data.items():
#   hero_name_dict[hero] = hero_data[hero]['name_en']

# print(hero_name_dict)

# print(hero_meta_data)

# hero_meta_dataにroleを追加する
# for hero in hero_meta_data:
#   if hero in hero_data:
#     hero_meta_data[hero]['role'] = hero_data[hero]['role']

# print(hero_meta_data)

# print(json.dumps(hero_meta_data))

# 役割別の辞書を初期化
# tank_hero_meta_data = {}
# fighter_hero_meta_data = {}
# support_hero_meta_data = {}
# assassin_hero_meta_data = {}
# marksman_hero_meta_data = {}
# mage_hero_meta_data = {}

# # hero_meta_dataを役割別に分類
# for hero, meta in hero_meta_data.items():
#   if hero in hero_data:
#     role = hero_data[hero]['role']
#     if role == 'Tank':
#       tank_hero_meta_data[hero] = meta
#     elif role == 'Fighter':
#       fighter_hero_meta_data[hero] = meta
#     elif role == 'Support':
#       support_hero_meta_data[hero] = meta
#     elif role == 'Assassin':
#       assassin_hero_meta_data[hero] = meta
#     elif role == 'Marksman':
#       marksman_hero_meta_data[hero] = meta
#     elif role == 'Mage':
#       mage_hero_meta_data[hero] = meta

# 結果を表示
# print("Tank Heroes:")
# print(tank_hero_meta_data)
# print("\nFighter Heroes:")
# print(fighter_hero_meta_data)
# print("\nSupport Heroes:")
# print(support_hero_meta_data)
# print("\nAssassin Heroes:")
# print(assassin_hero_meta_data)
# print("\nMarksman Heroes:")
# print(marksman_hero_meta_data)
# print("\nMage Heroes:")
# print(mage_hero_meta_data)

# # DataFrameに変換
# pd.set_option('display.max_rows', None)
# df = pd.DataFrame(hero_meta_data).T
# df = df.astype({'win_rate': 'float', 'pick_rate': 'float', 'ban_rate': 'float'})

# # Zスコアの計算
# df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
# df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
# df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()

# # 相互作用項の導入
# df['interaction'] = df['win_rate_z'] * df['pick_rate_z']

# # 指定された重みに基づいてtier_score_zを計算
# df['tier_score_z'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']

# # ランキング順に並べ替え
# ranked_df = df.sort_values('tier_score_z', ascending=False)

# ランキング結果を表示
# print(ranked_df[['tier_score_z']])

# ranked_df.to_csv('hero_tier_ranking.csv')


# # DataFrameに変換
# df = pd.DataFrame(support_hero_meta_data).T
# df = df.astype({'win_rate': 'float', 'pick_rate': 'float', 'ban_rate': 'float'})

# # Zスコアの計算
# df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
# df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
# df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()

# # 指定された重みに基づいてtier_score_zを計算
# df['tier_score_z'] = 0.5 * df['win_rate_z'] + 0.3 * df['pick_rate_z'] + 0.2 * df['ban_rate_z']

# # ランキング順に並べ替え
# ranked_df = df.sort_values('tier_score_z', ascending=False)

# # ランキング結果を表示
# print(ranked_df[['win_rate', 'pick_rate', 'ban_rate', 'tier_score_z']])


# 2. データの準備
# df = pd.DataFrame.from_dict(tank_hero_meta_data, orient='index')
# df['win_rate'] = df['win_rate'].astype(float)  # win_rateをfloat型に変換

# # 3. ロール別の統計計算
# role_grouped = df.groupby('role')['win_rate'].agg(['mean', 'std']).reset_index()

# # データに統計値をマージ
# df = df.merge(role_grouped, on='role', suffixes=('', '_role'))

# # 4. Zスコアの計算
# df['z_score'] = df.apply(lambda row: (row['win_rate'] - row['mean']) / row['std'], axis=1)

# # 5. ランキングの作成
# sorted_df = df.sort_values(by=['role', 'z_score'], ascending=[True, False])
# print(sorted_df)

# 結果の表示（例：上位5件）
# print(sorted_df[['role', 'win_rate', 'z_score']].head())

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

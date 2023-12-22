import pandas as pd
import json
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
WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[2]"))).click()
rank_level = 'Mythic+'

# Mythic Glory+のタブに切り替える
# WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[3]"))).click()
# rank_level = 'Mythic Glory+'

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

# スクレイピングしたデータからz-socreを計算する
pd.set_option('display.max_rows', None)
df = pd.DataFrame(hero_meta_data).T
df = df.astype({'win_rate': 'float', 'pick_rate': 'float', 'ban_rate': 'float'})
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()
df['interaction'] = df['win_rate_z'] * df['pick_rate_z']
df['tier_score_z'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']

# df.to_csv('hero_meta_data.csv', index=True)

# hero_dictにzscoreを保存する
hero_dict = {}
# for hero, data in get_hero_data().items():
#   hero_dict[hero] = {
#     'role': data['role'],
#     'image_url': data['image_url'],
#     'z_score': df.loc[hero, 'tier_score_z'] if hero in df.index else None
#   }
# mlbb_hero.jsonからname_enとimage_urlを取得し、hero_dictに保存する
with open('mlbb_hero.json', 'r') as f:
  mlbb_hero = json.load(f)

# json形式のmlbb_heroからname_enとimage_urlを取得し、hero_dictに保存する
for hero in mlbb_hero:
  # print(hero)
  #{'name_jp': 'ロイン', 'name_en': 'Lolita', 'role': 'Support', 'image_url': 'https://shanbenzzz.com/wp-content/uploads/2023/12/Lolita.webp'}
  hero_dict[hero['name_en']] = {
    'role': hero['role'],
    'image_url': hero['image_url'],
    'z_score': df.loc[hero['name_en'], 'tier_score_z'] if hero['name_en'] in df.index else None
  }

# print(hero_dict)s

# zscoreを元にランクを計算し、hero_dictに保存する
  
for hero, data in hero_dict.items():
  if data['z_score'] is None:
    continue
  data['rank'] = get_rank_from_score(data['z_score'])

# [
#     {"url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Moskov.webp", "rank": "S"},
#     {"url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Bruno.webp", "rank": "A"},
#     {"url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Jhonson.webp", "rank": "A"}
# ]
# 上記のような形式でjsonを作成する
hero_list = []
for hero, data in hero_dict.items():
  if data['z_score'] is None:
    continue
  hero_list.append({
    'url': data['image_url'],
    'rank': data['rank']
  })

# jsonにする
# hero_list = json.dumps(hero_list)

# print(hero_list)

# hero_listを"mlbb_ranking.json"としてインデントを2にして整形して出力する"
with open('mlbb_ranking.json', 'w') as f:
  json.dump(hero_list, f, indent=2)
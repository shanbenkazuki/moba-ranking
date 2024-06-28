import time
import pandas as pd
import components.swell_tag_component as tag
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from components.fetch_moba_database import get_hero_data
from sklearn.preprocessing import MinMaxScaler
from components.fetch_moba_database import save_to_hero_meta_data
from moba_version_generator import get_mlbb_version
from selenium.webdriver.chrome.service import Service

DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

def initialize_driver():
  service = Service(ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service)
  driver.implicitly_wait(WAIT_TIME)
  return driver

def switch_to_mystic_400(driver):
  time.sleep(2)
  #driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()
  # レジェンド表示に切り替え（ミシックがまだ集計されてない場合）
  driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()
  time.sleep(3)

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
  
def extract_ranking_data(driver):
  rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
  return rateList

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
  # lane_rank_dict = {
  #   'Jungle': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  #   'Gold': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  #   'EXP': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  #   'Roam': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
  #   'Mid': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []}
  # }
  role_rank_dict = {
    'Fighter': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Mage': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Tank': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Assassin': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Marksman': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []},
    'Support': {'S+': [], 'S': [], 'A+': [], 'A': [], 'B': [], 'C': []}
}

  # for hero, info in hero_meta_data.items():
  #   rank = info['Rank']
  #   suggested_lane = hero_data[hero]['suggested_lane']
  #   suggested_lane_list = suggested_lane.split(",")
  #   for lane in suggested_lane_list:
  #     lane_rank_dict[lane][rank].append(hero)
  # return lane_rank_dict

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

# 画面遷移とデータ取得の処理を関数化
# driver = initialize_driver()
# driver.get(DISPLAY_URL)
# switch_to_mystic_400(driver)
# rateList = extract_ranking_data(driver)

# # heroデータ取得
# hero_data = get_hero_data()

# # ヒーローメタデータの生成と正規化
# hero_meta_data = get_hero_meta_data(rateList)
# df_scaled = normalize_data(hero_meta_data)

# # ランキング値の追加
# hero_meta_data = add_ranking_to_hero_data(hero_meta_data, df_scaled)
# # print(hero_meta_data)

# # test
# score_and_rank_only = {}
# for character, stats in hero_meta_data.items():
#   score_and_rank_only[character] = {'Score': stats['Score'], 'Rank': stats['Rank']}
  
# hero_meta_data = score_and_rank_only

hero_meta_data = {'Floryn': {'Score': 0.49572111817434356, 'Rank': 'A'}, 'Yve': {'Score': 0.4871158576433725, 'Rank': 'A'}, 'Alice': {'Score': 0.3629989381609278, 'Rank': 'B'}, 'Freya': {'Score': 0.37789524156377624, 'Rank': 'B'}, 'Lolita': {'Score': 0.34000458943262685, 'Rank': 'B'}, 'Gord': {'Score': 0.3289145154265197, 'Rank': 'B'}, 'Edith': {'Score': 0.3650150778647873, 'Rank': 'B'}, 'Ling': {'Score': 0.5065286482556418, 'Rank': 'A+'}, 'Khaleed': {'Score': 0.2728963681401576, 'Rank': 'C'}, 'Arlott': {'Score': 0.6697688349753429, 'Rank': 'S'}, 'Bane': {'Score': 0.34721035934469535, 'Rank': 'B'}, 'Alpha': {'Score': 0.6041064417373337, 'Rank': 'S'}, 'Diggie': {'Score': 0.2807944093581535, 'Rank': 'C'}, 'Uranus': {'Score': 0.49831970588270563, 'Rank': 'A'}, 'Terizla': {'Score': 0.3172496091992834, 'Rank': 'B'}, 'Gloo': {'Score': 0.2686458006956119, 'Rank': 'C'}, 'Argus': {'Score': 0.25504701102216953, 'Rank': 'C'}, 'Yi Sun-shin': {'Score': 0.2994255456064162, 'Rank': 'C'}, 'Carmilla': {'Score': 0.2390370666011812, 'Rank': 'C'}, 'Joy': {'Score': 0.5197147438833852, 'Rank': 'A+'}, 'Natalia': {'Score': 0.251500582802139, 'Rank': 'C'}, 'Kadita': {'Score': 0.3426506614179942, 'Rank': 'B'}, 'Clint': {'Score': 0.32678930353937047, 'Rank': 'B'}, 'Aldous': {'Score': 0.28303840881400116, 'Rank': 'C'}, 'Bruno': {'Score': 0.28190934088798864, 'Rank': 'C'}, 'Harley': {'Score': 0.3026220586377663, 'Rank': 'B'}, 'Valir': {'Score': 0.36350782573853596, 'Rank': 'B'}, 'Minotaur': {'Score': 0.2587884388360419, 'Rank': 'C'}, 'X.Borg': {'Score': 0.2897901895663884, 'Rank': 'C'}, 'Baxia': {'Score': 0.2417559957853903, 'Rank': 'C'}, 'Kaja': {'Score': 0.24958026359165156, 'Rank': 'C'}, 'Moskov': {'Score': 0.30534204770511586, 'Rank': 'B'}, 'Kimmy': {'Score': 0.2135248413368802, 'Rank': 'C'}, 'Brody': {'Score': 0.36605414142191367, 'Rank': 'B'}, 'Phoveus': {'Score': 0.19213485195910204, 'Rank': 'C'}, "Chang'e": {'Score': 0.4334820743842271, 'Rank': 'A'}, 'Angela': {'Score': 0.31749688963996664, 'Rank': 'B'}, 'Claude': {'Score': 0.5065424897497327, 'Rank': 'A+'}, 'Hylos': {'Score': 0.20862180680650746, 'Rank': 'C'}, 'Irithel': {'Score': 0.22340207506013263, 'Rank': 'C'}, 'Cecilion': {'Score': 0.2791981119249299, 'Rank': 'C'}, 'Hanabi': {'Score': 0.3135420913445753, 'Rank': 'B'}, 'Helcurt': {'Score': 0.23893279728905428, 'Rank': 'C'}, 'Fredrinn': {'Score': 0.26434743012693296, 'Rank': 'C'}, 'Granger': {'Score': 0.24655784865368827, 'Rank': 'C'}, 'Eudora': {'Score': 0.21122684833361113, 'Rank': 'C'}, 'Belerick': {'Score': 0.2109439540550413, 'Rank': 'C'}, 'Xavier': {'Score': 0.25744276028635366, 'Rank': 'C'}, 'Lylia': {'Score': 0.21175874079450532, 'Rank': 'C'}, 'Zhask': {'Score': 0.2020855100005935, 'Rank': 'C'}, 'Cyclops': {'Score': 0.21277764262692403, 'Rank': 'C'}, 'Melissa': {'Score': 0.25514331545742747, 'Rank': 'C'}, 'Khufra': {'Score': 0.40333799092110906, 'Rank': 'A'}, 'Hanzo': {'Score': 0.19846266685270184, 'Rank': 'C'}, 'Aamon': {'Score': 0.20071377420499614, 'Rank': 'C'}, 'Beatrix': {'Score': 0.3871778682426476, 'Rank': 'B'}, 'Lesley': {'Score': 0.6152283008952633, 'Rank': 'S'}, 'Novaria': {'Score': 0.6022746826316675, 'Rank': 'S'}, 'Luo Yi': {'Score': 0.1817101476352437, 'Rank': 'C'}, 'Badang': {'Score': 0.1897516574581096, 'Rank': 'C'}, 'Harith': {'Score': 0.19649041588886873, 'Rank': 'C'}, 'Saber': {'Score': 0.21717997500299013, 'Rank': 'C'}, 'Faramis': {'Score': 0.42892643703241057, 'Rank': 'A'}, 'Kagura': {'Score': 0.21074082701010333, 'Rank': 'C'}, 'Rafaela': {'Score': 0.16733918961491367, 'Rank': 'C'}, 'Lunox': {'Score': 0.1863161061213173, 'Rank': 'C'}, 'Natan': {'Score': 0.17103391577654878, 'Rank': 'C'}, 'Karina': {'Score': 0.20673925018628983, 'Rank': 'C'}, 'Julian': {'Score': 0.16666288587068442, 'Rank': 'C'}, 'Aulus': {'Score': 0.14319582170020212, 'Rank': 'C'}, 'Odette': {'Score': 0.14744307716746755, 'Rank': 'C'}, 'Hayabusa': {'Score': 0.2263515458409465, 'Rank': 'C'}, 'Atlas': {'Score': 0.24465105839149026, 'Rank': 'C'}, 'Yu Zhong': {'Score': 0.20081958608188377, 'Rank': 'C'}, 'Aurora': {'Score': 0.1360247317694126, 'Rank': 'C'}, 'Hilda': {'Score': 0.1658376061621046, 'Rank': 'C'}, 'Yin': {'Score': 0.1727913419126752, 'Rank': 'C'}, 'Miya': {'Score': 0.16589586066659787, 'Rank': 'C'}, 'Gatotkaca': {'Score': 0.15035249293538105, 'Rank': 'C'}, 'Ruby': {'Score': 0.16092681217811122, 'Rank': 'C'}, 'Grock': {'Score': 0.16013220102627337, 'Rank': 'C'}, 'Estes': {'Score': 0.2818284179910518, 'Rank': 'C'}, 'Leomord': {'Score': 0.13173835010479296, 'Rank': 'C'}, 'Fanny': {'Score': 0.31168104745349634, 'Rank': 'B'}, 'Lapu-Lapu': {'Score': 0.20355903994721472, 'Rank': 'C'}, 'Selena': {'Score': 0.16455075553763363, 'Rank': 'C'}, 'Benedetta': {'Score': 0.13677986763040068, 'Rank': 'C'}, 'Esmeralda': {'Score': 0.20970468096720996, 'Rank': 'C'}, 'Martis': {'Score': 0.3301700018277879, 'Rank': 'B'}, 'Roger': {'Score': 0.13472953566794366, 'Rank': 'C'}, 'Alucard': {'Score': 0.14130321320373337, 'Rank': 'C'}, 'Wanwan': {'Score': 0.12851909306507944, 'Rank': 'C'}, 'Thamuz': {'Score': 0.12868298174904919, 'Rank': 'C'}, 'Minsitthar': {'Score': 0.40253046583046137, 'Rank': 'A'}, 'Popol and Kupa': {'Score': 0.11713225934127054, 'Rank': 'C'}, 'Vale': {'Score': 0.1266974715337066, 'Rank': 'C'}, 'Franco': {'Score': 0.36729711338848126, 'Rank': 'B'}, 'Gusion': {'Score': 0.1524334342221097, 'Rank': 'C'}, 'Jawhead': {'Score': 0.1277038450685056, 'Rank': 'C'}, 'Dyrroth': {'Score': 0.17914580007556158, 'Rank': 'C'}, 'Zilong': {'Score': 0.12865315630981136, 'Rank': 'C'}, 'Valentina': {'Score': 0.2258234177925852, 'Rank': 'C'}, 'Pharsa': {'Score': 0.144032523193444, 'Rank': 'C'}, 'Sun': {'Score': 0.1105554991964901, 'Rank': 'C'}, 'Layla': {'Score': 0.13194609476189065, 'Rank': 'C'}, 'Johnson': {'Score': 0.11810690443618738, 'Rank': 'C'}, 'Guinevere': {'Score': 0.10019736208722442, 'Rank': 'C'}, 'Barats': {'Score': 0.07988667653847609, 'Rank': 'C'}, 'Silvanna': {'Score': 0.0831947646400562, 'Rank': 'C'}, 'Paquito': {'Score': 0.19828662543018014, 'Rank': 'C'}, 'Karrie': {'Score': 0.13782699436509163, 'Rank': 'C'}, 'Masha': {'Score': 0.05498642729529841, 'Rank': 'C'}, 'Chou': {'Score': 0.17906446507186238, 'Rank': 'C'}, 'Akai': {'Score': 0.06636480337849508, 'Rank': 'C'}, 'Ixia': {'Score': 0.0899734432353259, 'Rank': 'C'}, 'Lancelot': {'Score': 0.22612585248505623, 'Rank': 'C'}, 'Vexana': {'Score': 0.04802724467798278, 'Rank': 'C'}, 'Tigreal': {'Score': 0.04881947140782119, 'Rank': 'C'}, 'Balmond': {'Score': 0.056998970201913475, 'Rank': 'C'}, 'Mathilda': {'Score': 0.006415749906818487, 'Rank': 'C'}, 'Nana': {'Score': 0.04278296936517803, 'Rank': 'C'}}

# df = pd.DataFrame(hero_meta_data).T.astype(float)
# scaler = MinMaxScaler()
# df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)
# df_scaled['score'] = df_scaled.mean(axis=1)

# # ヒストグラム作成
# plt.hist(df_scaled['score'], bins=10, edgecolor='black')

# # x軸の目盛りを0.05刻みに設定
# plt.xticks([i/100 for i in range(0, 101, 5)])

# # y軸の目盛りを1つずつ表示
# plt.yticks(range(0, len(df_scaled)+1, 1))

# # グラフのラベルとタイトル設定
# plt.xlabel('Score')
# plt.ylabel('Frequency')
# plt.title('Distribution of Scores')

# # グラフ表示
# plt.show()

scores = [stats['Score'] for stats in hero_meta_data.values()]

# Create bins
min_score = min(scores)
max_score = max(scores)
bins = np.arange(min_score, max_score + 0.05, 0.05) # add 0.05 to max_score to include the last interval

# Plot
plt.hist(scores, bins=bins, edgecolor='black')
plt.xlabel('Score')
plt.ylabel('Count')
plt.title('Histogram of Scores')

# Set xticks every 0.05 interval
plt.xticks(np.arange(min_score, max_score + 0.05, 0.05), rotation=90) # rotation for better visibility of xticks

plt.show()
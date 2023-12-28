import time
import pandas as pd

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fetch_moba_database import get_hero_data
from bs4 import BeautifulSoup

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

WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)

# カテゴリの個数
category_num = 6

# ランクの個数
rank_num = 6

# fighterのXPATH
s_plus_fighter_path = "//*[@id='tier-container']/div[2]/div[2]"
s_fighter_path = "//*[@id='tier-container']/div[3]/div[2]"
a_plus_fighter_path = "//*[@id='tier-container']/div[4]/div[2]"
a_fighter_path = "//*[@id='tier-container']/div[5]/div[2]"
b_fighter_path = "//*[@id='tier-container']/div[6]/div[2]"
c_fighter_path = "//*[@id='tier-container']/div[7]/div[2]"

# mageのXPATH
s_plus_mage_path = "//*[@id='tier-container']/div[2]/div[3]"
s_mage_path = "//*[@id='tier-container']/div[3]/div[3]"
a_plus_mage_path = "//*[@id='tier-container']/div[4]/div[3]"
a_mage_path = "//*[@id='tier-container']/div[5]/div[3]"
b_mage_path = "//*[@id='tier-container']/div[6]/div[3]"
c_mage_path = "//*[@id='tier-container']/div[7]/div[3]"

# tankのXPATH
s_plus_tank_path = "//*[@id='tier-container']/div[2]/div[4]"
s_tank_path = "//*[@id='tier-container']/div[3]/div[4]"
a_plus_tank_path = "//*[@id='tier-container']/div[4]/div[4]"
a_tank_path = "//*[@id='tier-container']/div[5]/div[4]"
b_tank_path = "//*[@id='tier-container']/div[6]/div[4]"
c_tank_path = "//*[@id='tier-container']/div[7]/div[4]"

# assassinのXPATH
s_plus_assassin_path = "//*[@id='tier-container']/div[2]/div[5]"
s_assassin_path = "//*[@id='tier-container']/div[3]/div[5]"
a_plus_assassin_path = "//*[@id='tier-container']/div[4]/div[5]"
a_assassin_path = "//*[@id='tier-container']/div[5]/div[5]"
b_assassin_path = "//*[@id='tier-container']/div[6]/div[5]"
c_assassin_path = "//*[@id='tier-container']/div[7]/div[5]"

# marksmanのXPATH
s_plus_marksman_path = "//*[@id='tier-container']/div[2]/div[6]"
s_marksman_path = "//*[@id='tier-container']/div[3]/div[6]"
a_plus_marksman_path = "//*[@id='tier-container']/div[4]/div[6]"
a_marksman_path = "//*[@id='tier-container']/div[5]/div[6]"
b_marksman_path = "//*[@id='tier-container']/div[6]/div[6]"
c_marksman_path = "//*[@id='tier-container']/div[7]/div[6]"

# supportのXPATH
s_plus_support_path = "//*[@id='tier-container']/div[2]/div[7]"
s_support_path = "//*[@id='tier-container']/div[3]/div[7]"
a_plus_support_path = "//*[@id='tier-container']/div[4]/div[7]"
a_support_path = "//*[@id='tier-container']/div[5]/div[7]"
b_support_path = "//*[@id='tier-container']/div[6]/div[7]"
c_support_path = "//*[@id='tier-container']/div[7]/div[7]"

# モバイル・レジェンドの名前、ロールをsqliteのから取得する
hero_data = get_hero_data()

# print(hero_data)



# モバイル・レジェンドのランキングページを開く
# driver.get("https://m.mobilelegends.com/en/rank")

# # プライバシーポリシーを閉じる
# WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='mt-cb-policy']/div/div[2]"))).click()

# # Mythic+のタブに切り替える
# WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[2]"))).click()
# rank_level = 'Mythic+'

# # Mythic Glory+のタブに切り替える
# # WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[3]"))).click()
# # rank_level = 'Mythic Glory+'

# # 画面が表示されるまで待つ
# WebDriverWait(driver, WAIT_TIME).until(
#   EC.presence_of_element_located((By.CSS_SELECTOR, ".slotwrapper > ul > li > a"))
# )


# # データをスクレイピングして整形する
# rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
# hero_meta_data = {}
# for heroRate in rateList:
#   heroEn = heroRate.span.string
#   winRatePoint = heroRate.contents[2].string.split("%")[0]
#   popRatePoint = heroRate.contents[4].string.split("%")[0]
#   banRatePoint = heroRate.contents[6].string.split("%")[0]
#   hero_meta_data[heroEn] = {
#     'win_rate': winRatePoint,
#     'pick_rate': popRatePoint,
#     'ban_rate': banRatePoint
#   }

# print(hero_meta_data)
hero_meta_data = {'Nolan': {'win_rate': '64.24', 'pick_rate': '1.53', 'ban_rate': '80'}, 'Mathilda': {'win_rate': '64.16', 'pick_rate': '3.19', 'ban_rate': '30.78'}, 'Wanwan': {'win_rate': '63.54', 'pick_rate': '2.13', 'ban_rate': '72.34'}, 'Diggie': {'win_rate': '63.12', 'pick_rate': '1.15', 'ban_rate': '65.3'}, 'Grock': {'win_rate': '62.54', 'pick_rate': '0.32', 'ban_rate': '0'}, 'Freya': {'win_rate': '62.45', 'pick_rate': '1.72', 'ban_rate': '6.13'}, 'Edith': {'win_rate': '62.37', 'pick_rate': '0.29', 'ban_rate': '0.03'}, 'Nana': {'win_rate': '60.6', 'pick_rate': '1.87', 'ban_rate': '2.12'}, 'Fanny': {'win_rate': '60.5', 'pick_rate': '1.6', 'ban_rate': '27.99'}, 'Vale': {'win_rate': '60.32', 'pick_rate': '0.32', 'ban_rate': '0.06'}, 'Thamuz': {'win_rate': '60.31', 'pick_rate': '0.85', 'ban_rate': '0.03'}, 'Pharsa': {'win_rate': '60.23', 'pick_rate': '0.09', 'ban_rate': '0.01'}, 'Johnson': {'win_rate': '60', 'pick_rate': '0.18', 'ban_rate': '0.52'}, 'Natalia': {'win_rate': '60', 'pick_rate': '0.05', 'ban_rate': '0.04'}, 'Paquito': {'win_rate': '59.95', 'pick_rate': '0.43', 'ban_rate': '0.01'}, 'Alice': {'win_rate': '59.84', 'pick_rate': '2.77', 'ban_rate': '27.24'}, 'Uranus': {'win_rate': '59.74', 'pick_rate': '0.16', 'ban_rate': '0.03'}, 'Argus': {'win_rate': '59.26', 'pick_rate': '0.03', 'ban_rate': '0.01'}, 'Gord': {'win_rate': '59.22', 'pick_rate': '0.53', 'ban_rate': '0.04'}, 'Ixia': {'win_rate': '59.19', 'pick_rate': '0.86', 'ban_rate': '0.17'}, 'Arlott': {'win_rate': '59.15', 'pick_rate': '2.97', 'ban_rate': '8.71'}, 'Faramis': {'win_rate': '59.13', 'pick_rate': '2.81', 'ban_rate': '11.34'}, 'Gloo': {'win_rate': '59.09', 'pick_rate': '0.05', 'ban_rate': '0.02'}, 'Harith': {'win_rate': '59.01', 'pick_rate': '0.6', 'ban_rate': '0.96'}, 'Luo Yi': {'win_rate': '58.99', 'pick_rate': '0.39', 'ban_rate': '0.16'}, 'Floryn': {'win_rate': '58.79', 'pick_rate': '0.39', 'ban_rate': '0.68'}, 'Odette': {'win_rate': '58.69', 'pick_rate': '0.53', 'ban_rate': '0.1'}, 'Joy': {'win_rate': '58.53', 'pick_rate': '2.33', 'ban_rate': '56.41'}, 'Julian': {'win_rate': '58.45', 'pick_rate': '0.44', 'ban_rate': '0.13'}, 'Ruby': {'win_rate': '58.19', 'pick_rate': '1.42', 'ban_rate': '0.88'}, 'Leomord': {'win_rate': '58.1', 'pick_rate': '0.26', 'ban_rate': '0.03'}, 'Terizla': {'win_rate': '58.08', 'pick_rate': '1.72', 'ban_rate': '0.18'}, 'Kadita': {'win_rate': '58.04', 'pick_rate': '0.83', 'ban_rate': '0.1'}, 'Minotaur': {'win_rate': '57.97', 'pick_rate': '2.52', 'ban_rate': '7.7'}, 'Selena': {'win_rate': '57.81', 'pick_rate': '0.33', 'ban_rate': '0.13'}, 'Alucard': {'win_rate': '57.41', 'pick_rate': '0.11', 'ban_rate': '0.03'}, 'Khaleed': {'win_rate': '57.39', 'pick_rate': '0.78', 'ban_rate': '0.13'}, 'Brody': {'win_rate': '57.32', 'pick_rate': '4.45', 'ban_rate': '0.96'}, 'Rafaela': {'win_rate': '57.31', 'pick_rate': '0.27', 'ban_rate': '0.07'}, 'Dyrroth': {'win_rate': '57.2', 'pick_rate': '2.1', 'ban_rate': '1.31'}, 'Aldous': {'win_rate': '57.06', 'pick_rate': '0.33', 'ban_rate': '0.08'}, 'Guinevere': {'win_rate': '56.95', 'pick_rate': '2.72', 'ban_rate': '41.35'}, 'Claude': {'win_rate': '56.73', 'pick_rate': '4.58', 'ban_rate': '0.53'}, 'Benedetta': {'win_rate': '56.53', 'pick_rate': '0.67', 'ban_rate': '0.21'}, 'Yu Zhong': {'win_rate': '56.31', 'pick_rate': '2.15', 'ban_rate': '0.34'}, 'Gatotkaca': {'win_rate': '56.25', 'pick_rate': '0.02', 'ban_rate': '0'}, 'Natan': {'win_rate': '55.94', 'pick_rate': '0.65', 'ban_rate': '1.72'}, 'X-Borg': {'win_rate': '55.91', 'pick_rate': '0.89', 'ban_rate': '0.6'}, 'Lylia': {'win_rate': '55.86', 'pick_rate': '1.78', 'ban_rate': '0.79'}, 'Saber': {'win_rate': '55.81', 'pick_rate': '0.04', 'ban_rate': '0.06'}, 'Fredrinn': {'win_rate': '55.61', 'pick_rate': '0.84', 'ban_rate': '0.33'}, 'Hanzo': {'win_rate': '55.56', 'pick_rate': '0.25', 'ban_rate': '0.34'}, 'Novaria': {'win_rate': '55.32', 'pick_rate': '1.51', 'ban_rate': '0.4'}, 'Layla': {'win_rate': '55.32', 'pick_rate': '0.19', 'ban_rate': '0.28'}, 'Zhask': {'win_rate': '55.28', 'pick_rate': '0.13', 'ban_rate': '0'}, 'Minsitthar': {'win_rate': '55.17', 'pick_rate': '0.09', 'ban_rate': '0.06'}, 'Lapu-Lapu': {'win_rate': '55.14', 'pick_rate': '0.88', 'ban_rate': '0.03'}, 'Baxia': {'win_rate': '55.12', 'pick_rate': '0.26', 'ban_rate': '0.23'}, 'Bruno': {'win_rate': '55.09', 'pick_rate': '2.63', 'ban_rate': '0.55'}, 'Lunox': {'win_rate': '54.99', 'pick_rate': '3.68', 'ban_rate': '36.39'}, 'Beatrix': {'win_rate': '54.95', 'pick_rate': '0.95', 'ban_rate': '0.01'}, 'Granger': {'win_rate': '54.88', 'pick_rate': '0.39', 'ban_rate': '0.07'}, 'Melissa': {'win_rate': '54.87', 'pick_rate': '0.23', 'ban_rate': '0.05'}, "Chang'e": {'win_rate': '54.76', 'pick_rate': '0.21', 'ban_rate': '0.01'}, 'Tigreal': {'win_rate': '54.07', 'pick_rate': '1.63', 'ban_rate': '3.79'}, 'Valentina': {'win_rate': '53.99', 'pick_rate': '1.63', 'ban_rate': '1.03'}, 'Masha': {'win_rate': '53.97', 'pick_rate': '0.31', 'ban_rate': '0.34'}, 'Vexana': {'win_rate': '53.89', 'pick_rate': '0.49', 'ban_rate': '0.04'}, 'Yve': {'win_rate': '53.75', 'pick_rate': '0.08', 'ban_rate': '0'}, 'Valir': {'win_rate': '53.73', 'pick_rate': '0.21', 'ban_rate': '0.31'}, 'Phoveus': {'win_rate': '53.53', 'pick_rate': '0.52', 'ban_rate': '0.61'}, 'Estes': {'win_rate': '53.49', 'pick_rate': '0.31', 'ban_rate': '0.72'}, 'Yi Sun-shin': {'win_rate': '53.41', 'pick_rate': '0.36', 'ban_rate': '0.1'}, 'Barats': {'win_rate': '53.21', 'pick_rate': '1.46', 'ban_rate': '15.78'}, 'Eudora': {'win_rate': '52.38', 'pick_rate': '0.09', 'ban_rate': '0.01'}, 'Xavier': {'win_rate': '52.37', 'pick_rate': '0.67', 'ban_rate': '0.06'}, 'Aamon': {'win_rate': '52.26', 'pick_rate': '0.16', 'ban_rate': '0.05'}, 'Chou': {'win_rate': '52.22', 'pick_rate': '0.46', 'ban_rate': '0.06'}, 'Clint': {'win_rate': '52.03', 'pick_rate': '0.73', 'ban_rate': '0.03'}, 'Angela': {'win_rate': '52.01', 'pick_rate': '2.09', 'ban_rate': '17.59'}, 'Kagura': {'win_rate': '51.46', 'pick_rate': '0.28', 'ban_rate': '0.03'}, 'Hayabusa': {'win_rate': '51.38', 'pick_rate': '0.41', 'ban_rate': '0.17'}, 'Karrie': {'win_rate': '51.21', 'pick_rate': '1.9', 'ban_rate': '1.06'}, 'Alpha': {'win_rate': '51.19', 'pick_rate': '0.34', 'ban_rate': '0.01'}, 'Roger': {'win_rate': '50.97', 'pick_rate': '0.53', 'ban_rate': '0.07'}, 'Martis': {'win_rate': '50.95', 'pick_rate': '1.4', 'ban_rate': '1.71'}, 'Yin': {'win_rate': '50.57', 'pick_rate': '0.27', 'ban_rate': '0.17'}, 'Kaja': {'win_rate': '50.57', 'pick_rate': '0.63', 'ban_rate': '1.04'}, 'Balmond': {'win_rate': '50.48', 'pick_rate': '2.65', 'ban_rate': '45.89'}, 'Irithel': {'win_rate': '50.24', 'pick_rate': '0.63', 'ban_rate': '0.01'}, 'Hanabi': {'win_rate': '50', 'pick_rate': '0.29', 'ban_rate': '0.07'}, 'Harley': {'win_rate': '50', 'pick_rate': '0.19', 'ban_rate': '0.13'}, 'Khufra': {'win_rate': '49.89', 'pick_rate': '0.89', 'ban_rate': '0.38'}, 'Lancelot': {'win_rate': '49.82', 'pick_rate': '1.43', 'ban_rate': '0.21'}, 'Popol and Kupa': {'win_rate': '49.77', 'pick_rate': '0.44', 'ban_rate': '0.27'}, 'Cecilion': {'win_rate': '49.6', 'pick_rate': '0.26', 'ban_rate': '0.04'}, 'Jawhead': {'win_rate': '49.46', 'pick_rate': '0.1', 'ban_rate': '0.05'}, 'Cyclops': {'win_rate': '49.39', 'pick_rate': '0.25', 'ban_rate': '0.05'}, 'Karina': {'win_rate': '49.22', 'pick_rate': '0.26', 'ban_rate': '0.07'}, 'Sun': {'win_rate': '49.12', 'pick_rate': '0.06', 'ban_rate': '0.01'}, 'Lesley': {'win_rate': '48.96', 'pick_rate': '0.44', 'ban_rate': '0'}, 'Hilda': {'win_rate': '48.94', 'pick_rate': '0.1', 'ban_rate': '0.03'}, 'Ling': {'win_rate': '48.84', 'pick_rate': '0.31', 'ban_rate': '0.02'}, 'Helcurt': {'win_rate': '48.41', 'pick_rate': '0.16', 'ban_rate': '0.02'}, 'Bane': {'win_rate': '48.21', 'pick_rate': '0.26', 'ban_rate': '0.07'}, 'Akai': {'win_rate': '48.21', 'pick_rate': '0.37', 'ban_rate': '0.08'}, 'Carmilla': {'win_rate': '47.83', 'pick_rate': '0.05', 'ban_rate': '0.04'}, 'Badang': {'win_rate': '47.76', 'pick_rate': '0.07', 'ban_rate': '0.02'}, 'Silvanna': {'win_rate': '47.62', 'pick_rate': '0.02', 'ban_rate': '0'}, 'Gusion': {'win_rate': '47.46', 'pick_rate': '0.34', 'ban_rate': '0.05'}, 'Lolita': {'win_rate': '47.33', 'pick_rate': '0.13', 'ban_rate': '0.08'}, 'Franco': {'win_rate': '47.33', 'pick_rate': '0.88', 'ban_rate': '0.8'}, 'Hylos': {'win_rate': '47.27', 'pick_rate': '0.06', 'ban_rate': '0'}, 'Zilong': {'win_rate': '46.36', 'pick_rate': '0.11', 'ban_rate': '0.06'}, 'Moskov': {'win_rate': '43.68', 'pick_rate': '0.27', 'ban_rate': '0.04'}, 'Kimmy': {'win_rate': '43.06', 'pick_rate': '0.15', 'ban_rate': '0.02'}, 'Esmeralda': {'win_rate': '42.15', 'pick_rate': '0.23', 'ban_rate': '0.07'}, 'Atlas': {'win_rate': '41.89', 'pick_rate': '0.08', 'ban_rate': '0.16'}, 'Aulus': {'win_rate': '36.84', 'pick_rate': '0.04', 'ban_rate': '0.01'}, 'Miya': {'win_rate': '36.25', 'pick_rate': '0.08', 'ban_rate': '0.2'}, 'Belerick': {'win_rate': '22.22', 'pick_rate': '0.04', 'ban_rate': '0.01'}, 'Aurora': {'win_rate': '20', 'pick_rate': '0.02', 'ban_rate': '0'}}

# スクレイピングしたデータからz-socreを計算する
pd.set_option('display.max_rows', None)
df = pd.DataFrame(hero_meta_data).T
df = df.astype({'win_rate': 'float', 'pick_rate': 'float', 'ban_rate': 'float'})
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()
df['interaction'] = df['win_rate_z'] * df['pick_rate_z']
df['tier_score_z'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']


hero_dict = {}

#  hero_dataからキーとroleを取得し、hero_dictにnameとroleとして保存する
for hero, data in hero_data.items():
  hero_dict[hero] = {
    'role': data['role'],
    'z_score': df.loc[hero, 'tier_score_z'] if hero in df.index else None
  }

for hero, data in hero_dict.items():
  if data['z_score'] is None:
    continue
  data['rank'] = get_rank_from_score(data['z_score'])

# print(hero_dict)

# 対象のページを開く
driver.get("http://localhost:3000/tiers/28/arrange")

#  ページを全画面にする
driver.maximize_window()

# ページを10%縮小する
driver.execute_script("document.body.style.zoom='80%'")

time.sleep(5)

# hero_dictのキーを取得し、hero_dictのキーの数だけ繰り返す
for hero, data in hero_dict.items():
  print(hero)
  print(f'//img[@alt="{hero}"]')
  # 画像要素を待つ
  image = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f'//img[@alt="{hero}"]'))
  )
  driver.execute_script("arguments[0].scrollIntoView();", image)
  # time.sleep(2)
  print(data)
  print(data['role'])
  print(data['rank'])
  # ドロップ先の要素を待つ
  # roleごとに分岐する
  if data['role'] == 'Support':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_support_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_support_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_support_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_support_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_support_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_support_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Fighter':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_fighter_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_fighter_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_fighter_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_fighter_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_fighter_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_fighter_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    else:
      print('error')
  elif data['role'] == 'Mage':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_mage_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_mage_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_mage_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_mage_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_mage_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_mage_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Tank':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_tank_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_tank_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_tank_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_tank_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_tank_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_tank_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Assassin':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_assassin_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_assassin_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_assassin_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_assassin_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_assassin_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_assassin_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Marksman':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_marksman_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_marksman_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_marksman_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_marksman_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_marksman_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_marksman_path))
      )
      # driver.execute_script("arguments[0].scrollIntoView();", target)
      # time.sleep(2)
      ActionChains(driver).drag_and_drop(image, target).perform()
  else:
    print('error')

time.sleep(5)




# # 画像要素を待つ
# image = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//img[@alt="Aamon"]'))
# )

# # ドロップ先の要素を待つ
# target = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@id="tier-container"]/div[2]/div[2]'))
# )

# # ドラッグアンドドロップ操作を実行

# time.sleep(5)
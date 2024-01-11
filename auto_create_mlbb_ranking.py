import time
import pandas as pd
import sqlite3

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
from fetch_moba_database import get_hero_data

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

# chrome_options = Options()
# chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service('/usr/local/bin/chromedriver')

driver = webdriver.Chrome(service=service)

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

# sqliteのデータベースに接続する
conn = sqlite3.connect('moba_database.sqlite3')

c = conn.cursor()

reference_date = '2024-01-09'

query = f"SELECT name, pick_rate, win_rate, ban_rate FROM hero_meta_data WHERE reference_date ={reference_date}"

# Execute the query
c.execute(query)

rows = c.fetchall()

conn.close()

hero_meta_data = {}
for row in rows:
  hero_name, pick_rate, win_rate, ban_rate = row
  hero_meta_data[hero_name] = {
    'pick_rate': f'{pick_rate:.2f}',
    'win_rate': f'{win_rate:.2f}',
    'ban_rate': f'{ban_rate:.2f}'
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

driver.get("http://localhost:3000/login")

# メールアドレス入力欄を特定し、メールアドレスを入力
email_input = driver.find_element(By.ID, 'email')  # 実際のIDに置き換える
email_input.send_keys("aaa@aaa.com")

# パスワード入力欄を特定し、パスワードを入力
password_input = driver.find_element(By.ID, 'password')  # 実際のIDに置き換える
password_input.send_keys("aaaa")

# "ログイン"と書かれたボタンをクリック
login_button = driver.find_element(By.ID, 'login_button')
login_button.click()

time.sleep(5)

# 対象のページを開く
driver.get("http://localhost:3000/tiers/29/arrange")

time.sleep(3)

# hero_dictのキーを取得し、hero_dictのキーの数だけ繰り返す
for hero, data in hero_dict.items():
  if "X.Borg" == hero:
    hero = "X-Borg"
  # 画像要素を待つ
  image = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f'//img[@alt="{hero}"]'))
  )
  driver.execute_script("arguments[0].scrollIntoView();", image)
  time.sleep(1)
  # roleごとに分岐する
  if data['role'] == 'Support':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      # S+と表示されている箇所までスクロールする
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_support_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_support_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_support_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_support_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_support_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_support_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Fighter':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_fighter_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_fighter_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_fighter_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_fighter_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_fighter_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_fighter_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    else:
      print('error')
  elif data['role'] == 'Mage':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_mage_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_mage_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_mage_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_mage_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_mage_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_mage_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Tank':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_tank_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_tank_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_tank_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_tank_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_tank_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_tank_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Assassin':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_assassin_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_assassin_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_assassin_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_assassin_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_assassin_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_assassin_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
  elif data['role'] == 'Marksman':
    # rankごとに分岐してドラッグアンドドロップする
    if data['rank'] == 'S+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_plus_marksman_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'S':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, s_marksman_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A+':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_plus_marksman_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'A':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, a_marksman_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'B':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, b_marksman_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
    elif data['rank'] == 'C':
      target = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, c_marksman_path))
      )
      driver.execute_script("arguments[0].scrollIntoView();", target)
      ActionChains(driver).drag_and_drop(image, target).perform()
  else:
    print('error')

time.sleep(3)

# 保存ボタンを押下する
save_button = WebDriverWait(driver, 10).until(
  EC.presence_of_element_located((By.XPATH, '//*[@id="display-modal"]'))
)

save_button.click()

time.sleep(2)

# 保存ボタンを押下する
tier_save_button = WebDriverWait(driver, 10).until(
  EC.presence_of_element_located((By.XPATH, '//*[@id="save-tier-image"]'))
)

tier_save_button.click()

time.sleep(3)

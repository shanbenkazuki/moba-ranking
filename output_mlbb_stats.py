import pandas as pd
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service)
driver.implicitly_wait(WAIT_TIME)
driver.get(DISPLAY_URL)

# プライバシーポリシーを閉じる
WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='mt-cb-policy']/div/div[2]"))).click()

time.sleep(2)

# Mythic+のタブに切り替える
WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[2]"))).click()
rank_level = 'Mythic+'

# 画面が表示されるまで待つ
WebDriverWait(driver, WAIT_TIME).until(
  EC.presence_of_element_located((By.CSS_SELECTOR, ".slotwrapper > ul > li > a"))
)

# Mythic+のタブに切り替える
WebDriverWait(driver, WAIT_TIME).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='rank']/div[1]/div[2]/ul/li[2]"))).click()
rank_level = 'Mythic+'

time.sleep(2)

# データをスクレイピングして整形する
rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
hero_meta_data = []
for heroRate in rateList:
  heroEn = heroRate.span.string
  winRatePoint = float(heroRate.contents[2].string.split("%")[0])
  popRatePoint = float(heroRate.contents[4].string.split("%")[0])
  banRatePoint = float(heroRate.contents[6].string.split("%")[0])
  hero_meta_data.append({
    'hero': heroEn,
    'win_rate': winRatePoint,
    'pick_rate': popRatePoint,
    'ban_rate': banRatePoint
  })

# DataFrameを作成
df = pd.DataFrame(hero_meta_data)

# z-scoreを計算
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std()
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std()
df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std()
df['interaction'] = df['win_rate_z'] * df['pick_rate_z']
df['z_score'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']

# 必要な列のみ選択
df = df[['hero', 'win_rate', 'pick_rate', 'ban_rate', 'z_score']]

reference_date = BeautifulSoup(driver.page_source, 'html.parser').select_one("#rank > div.header > div:nth-child(1) > ul > li").text

output_folder = "stats/mlbb"

try:
    # CSVファイルに出力
    csv_filename = f"{output_folder}/hero_meta_data_{reference_date}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"CSVファイル '{csv_filename}' の出力に成功しました。")
except Exception as e:
    print(f"CSVファイルの出力に失敗しました: {str(e)}")

driver.quit()
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
from datetime import datetime

DISPLAY_URL = "https://m.mobilelegends.com/rank"
WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# service = Service()

driver = webdriver.Chrome()
driver.implicitly_wait(WAIT_TIME)

# ブラウザを最大化して表示
driver.maximize_window()
driver.get(DISPLAY_URL)
time.sleep(5)

# 過去7日間のデータを表示するように設定
xpath = '//*[@id="root"]/div/div[3]/div/div[1]/div[1]/div[1]/div[2]/div[2]'
element = driver.find_element(By.XPATH, xpath)
element.click()
time.sleep(5)
new_xpath = '//*[@id="root"]/div/div[3]/div/div[1]/div[1]/div[1]/div[1]/div/div[3]'
new_element = driver.find_element(By.XPATH, new_xpath)
new_element.click()
time.sleep(5)

# 対象の要素が表示されるまで待機
target_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > div.mt-2673591.mt-empty > div > div.mt-2729690.mt-empty > div > div.mt-2684827.mt-empty > div'))
)

# 対象の要素までスクロール
driver.execute_script("arguments[0].scrollIntoView();", target_element)

# スクロールを繰り返して、最下段までデータを読み込む
last_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
while True:
    driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", target_element)
    time.sleep(2)  # データの読み込みを待機
    new_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
    if new_height == last_height:
        break
    last_height = new_height


time.sleep(5)

rateList = BeautifulSoup(driver.page_source, 'html.parser').select("#root > div > div.mt-2673591.mt-empty > div > div.mt-2729690.mt-empty > div > div.mt-2684827.mt-empty > div > div")


hero_meta_data = []
for heroRate in rateList:
   hero_name = heroRate.select_one("div.mt-2693555 > div.mt-2693412 > span").text
   pick_rate = float(heroRate.select_one("div.mt-2684925 > span").text.replace("%", ""))
   win_rate = float(heroRate.select_one("div.mt-2684926 > span").text.replace("%", ""))
   ban_rate = float(heroRate.select_one("div.mt-2687632 > span").text.replace("%", ""))
   hero_meta_data.append({
       'hero': hero_name,
       'win_rate': win_rate,
       'pick_rate': pick_rate,
       'ban_rate': ban_rate
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

reference_date_str = BeautifulSoup(driver.page_source, 'html.parser').select_one("#root > div > div.mt-2673591.mt-empty > div > div.mt-2693420.mt-empty > div.mt-2693423.mt-empty > div.mt-2693419.mt-text > span").text

reference_date = datetime.strptime(reference_date_str, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d')

output_folder = "/Users/yamamotokazuki/develop/moba-ranking-rails/db/csv/hero_rates"

try:
    # CSVファイルに出力
    csv_filename = f"{output_folder}/hero_rates_{reference_date}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"CSVファイル '{csv_filename}' の出力に成功しました。")
except Exception as e:
    print(f"CSVファイルの出力に失敗しました: {str(e)}")

driver.quit()
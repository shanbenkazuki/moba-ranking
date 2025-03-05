from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# WebDriverWait用のインポート
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import sqlite3
from datetime import date

from datetime import datetime

# ----- Seleniumによるスクレイピング処理 -----

# ChromeOptionsの設定
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")

# Chromeドライバーのセットアップ（ChromeOptionsを指定）
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 指定のURLを開く
driver.get("https://m.mobilelegends.com/rank")
wait = WebDriverWait(driver, 10)

# プライバリーポリシーのクローズボタンが表示されるまで待機しクリックする
close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mt-cb-policy > div > div.mt-cb-policy-close")))
close_button.click()

time.sleep(5)

# 1. 期間範囲タブクリック
try:
    # 最初のセレクタを使って要素を取得
    period_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684829.mt-uid-99966.mt-dropdown > div.mt-2684835.mt-uid-99964.mt-empty > div.mt-2684838.mt-uid-99962.mt-empty"
    )))
except Exception as e:
    # 最初のセレクタが見つからなかった場合、代替のセレクタを試す
    period_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-2684885.mt-uid-99957.mt-empty > div.mt-2684887.mt-uid-99955.mt-empty"
    )))
period_tab.click()

time.sleep(2)

# 2. Past 7 days選択
past7_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684829.mt-uid-99966.mt-dropdown > div.mt-dropdown-list.visible > div > div.mt-2684831.mt-uid-99880.mt-empty.mt-list-item"
past7_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, past7_selector)))
past7_option.click()

time.sleep(2)

# 3. ランク選択タブクリック
rank_tab_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-2684885.mt-uid-99957.mt-empty > div.mt-2684887.mt-uid-99955.mt-empty"
rank_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, rank_tab_selector)))
rank_tab.click()

time.sleep(2)

# 4. Mythic選択
mythic_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-dropdown-list.visible > div > div.mt-2684882.mt-uid-99849.mt-empty.mt-list-item"
mythic_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, mythic_selector)))
mythic_option.click()

time.sleep(5)

# 5. データ読み込み対象の要素を取得（スクロール対象）
target_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2729690.mt-uid-99949.mt-empty > div > div.mt-2684827.mt-uid-99942.mt-empty > div"
target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_selector)))

# ページの最下部までスクロールしてデータを読み込みます
last_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
while True:
    driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", target_element)
    time.sleep(2)  # データの読み込みを待機
    new_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(5)

# ページソースをBeautifulSoupで解析してヒーローデータを抽出
soup = BeautifulSoup(driver.page_source, 'html.parser')
rateList = soup.select("#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2729690.mt-uid-99949.mt-empty > div > div.mt-2684827.mt-uid-99942.mt-empty > div > div")

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

time.sleep(5)
driver.quit()

# ----- SQLiteへのデータ保存処理 -----

# データベースのパス
db_path = "/Users/yamamotokazuki/develop/moba-ranking/mlbb.db"

# SQLiteデータベースに接続
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

# patchesテーブルからrelease_dateが最新のpatch_numberを取得
cursor.execute("SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1")
result = cursor.fetchone()
if result:
    latest_patch_number = result[0]
else:
    print("patchesテーブルにデータがありません。")
    latest_patch_number = None

# CSS セレクタを使って対象の要素を取得
selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2693423.mt-uid-99952.mt-empty > div.mt-2693419.mt-uid-99950.mt-text > span"
element = soup.select_one(selector)

if element:
    reference_date_str = element.get_text()
    print(reference_date_str)
else:
    print("指定したセレクタに該当する要素が見つかりませんでした")

reference_date = datetime.strptime(reference_date_str, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d')

# hero_meta_dataの各ヒーローデータをhero_statsテーブルに挿入
for hero in hero_meta_data:
    cursor.execute("""
        INSERT INTO hero_stats 
        (hero_name, win_rate, pick_rate, ban_rate, reference_date, rank, patch_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        hero['hero'],
        hero['win_rate'],
        hero['pick_rate'],
        hero['ban_rate'],
        reference_date,
        "Mythic",  # 固定値
        latest_patch_number
    ))

# 変更をコミットして接続を閉じる
conn.commit()
conn.close()

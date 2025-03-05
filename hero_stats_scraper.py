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

# 少し待機
time.sleep(5)

# 1. 期間範囲タブクリック
period_tab_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684829.mt-uid-99966.mt-dropdown > div.mt-2684835.mt-uid-99964.mt-empty"
period_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, period_tab_selector)))
period_tab.click()

# 少し待機
time.sleep(2)

# 2. Past 7 days選択
past7_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684829.mt-uid-99966.mt-dropdown > div.mt-dropdown-list.visible > div > div.mt-2684831.mt-uid-99880.mt-empty.mt-list-item"
past7_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, past7_selector)))
past7_option.click()

# 少し待機
time.sleep(2)

# 3. ランク選択タブクリック
rank_tab_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-2684885.mt-uid-99957.mt-empty > div.mt-2684887.mt-uid-99955.mt-empty"
rank_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, rank_tab_selector)))
rank_tab.click()

# 少し待機
time.sleep(2)

# 4. Mythic選択
mythic_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-dropdown-list.visible > div > div.mt-2684882.mt-uid-99849.mt-empty.mt-list-item"
mythic_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, mythic_selector)))
mythic_option.click()

# 結果確認のため少し待機
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

# 結果確認のため少し待機
time.sleep(5)

rateList = BeautifulSoup(driver.page_source, 'html.parser').select("#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2729690.mt-uid-99949.mt-empty > div > div.mt-2684827.mt-uid-99942.mt-empty > div")

# 各ヒーローのデータを収集します
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

# ブラウザを閉じる
driver.quit()

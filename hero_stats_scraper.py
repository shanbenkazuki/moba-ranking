import os
import time
import logging
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- ログ設定 ---
log_dir = "/Users/yamamotokazuki/develop/moba-ranking/logs"
os.makedirs(log_dir, exist_ok=True)
today = datetime.now().strftime('%Y-%m-%d')
log_file = os.path.join(log_dir, f"mlbb_scraping_{today}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Mobile Legends ランクスクレイピング処理を開始")
    
    # ----- Seleniumによるスクレイピング処理 -----
    try:
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 10)
        logging.info("Chromeドライバーの起動に成功")
    except Exception:
        logging.exception("Chromeドライバーの起動に失敗")
        return

    try:
        driver.get("https://m.mobilelegends.com/rank")
        logging.info("指定URLをオープン")
        
        # プライバシーポリシーのクローズボタンを待機・クリック
        close_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#mt-cb-policy > div > div.mt-cb-policy-close")
        ))
        close_button.click()
        logging.info("プライバシーポリシーのポップアップをクローズ")
        time.sleep(5)
    except Exception:
        logging.exception("ページオープンまたはプライバシーポリシーのクローズでエラー発生")
        driver.quit()
        return

    # 1. 期間範囲タブクリック
    try:
        period_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684829.mt-uid-99966.mt-dropdown > div.mt-2684835.mt-uid-99964.mt-empty > div.mt-2684838.mt-uid-99962.mt-empty"
        )))
        logging.info("期間範囲タブを取得（第一セレクタ）")
    except Exception:
        logging.warning("第一セレクタで期間範囲タブが取得できなかったため、代替セレクタを試行")
        try:
            period_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-2684885.mt-uid-99957.mt-empty > div.mt-2684887.mt-uid-99955.mt-empty"
            )))
            logging.info("期間範囲タブを取得（代替セレクタ）")
        except Exception:
            logging.exception("期間範囲タブの取得に失敗")
            driver.quit()
            return
    period_tab.click()
    logging.info("期間範囲タブをクリック")
    time.sleep(2)

    # 2. Past 7 days選択
    try:
        past7_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684829.mt-uid-99966.mt-dropdown > div.mt-dropdown-list.visible > div > div.mt-2684831.mt-uid-99880.mt-empty.mt-list-item"
        past7_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, past7_selector)))
        past7_option.click()
        logging.info("『Past 7 days』オプションを選択")
    except Exception:
        logging.exception("『Past 7 days』オプションの選択に失敗")
        driver.quit()
        return
    time.sleep(2)

    # 3. ランク選択タブクリック
    try:
        rank_tab_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-2684885.mt-uid-99957.mt-empty > div.mt-2684887.mt-uid-99955.mt-empty"
        rank_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, rank_tab_selector)))
        rank_tab.click()
        logging.info("ランク選択タブをクリック")
    except Exception:
        logging.exception("ランク選択タブのクリックに失敗")
        driver.quit()
        return
    time.sleep(2)

    # 4. Mythic選択
    try:
        mythic_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2684825.mt-uid-99967.mt-empty > div.mt-2684880.mt-uid-99959.mt-dropdown > div.mt-dropdown-list.visible > div > div.mt-2684882.mt-uid-99849.mt-empty.mt-list-item"
        mythic_option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, mythic_selector)))
        mythic_option.click()
        logging.info("『Mythic』ランクを選択")
    except Exception:
        logging.exception("『Mythic』ランクの選択に失敗")
        driver.quit()
        return
    time.sleep(5)

    # 5. データ読み込み対象要素のスクロール
    try:
        target_selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2729690.mt-uid-99949.mt-empty > div > div.mt-2684827.mt-uid-99942.mt-empty > div"
        target_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_selector)))
        logging.info("スクロール対象の要素を取得")
        
        last_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
        while True:
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", target_element)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
            if new_height == last_height:
                break
            last_height = new_height
        logging.info("データの読み込み完了（スクロール処理終了）")
    except Exception:
        logging.exception("スクロール処理中にエラー発生")
        driver.quit()
        return

    time.sleep(5)
    
    # BeautifulSoupでページ解析
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        logging.info("BeautifulSoupでページ解析成功")
        
        rateList = soup.select("#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2729690.mt-uid-99949.mt-empty > div > div.mt-2684827.mt-uid-99942.mt-empty > div > div")
        logging.info(f"抽出対象のヒーローデータ件数: {len(rateList)}")
        
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
        logging.info("ヒーローデータの抽出に成功")
    except Exception:
        logging.exception("BeautifulSoupでのデータ解析に失敗")
        driver.quit()
        return

    time.sleep(5)
    driver.quit()
    logging.info("Chromeドライバーを正常に終了")

    # ----- SQLiteへのデータ保存処理 -----
    try:
        db_path = "/Users/yamamotokazuki/develop/moba-ranking/mlbb.db"
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        logging.info("SQLiteデータベースに接続成功")
    except Exception:
        logging.exception("SQLiteデータベースへの接続に失敗")
        return

    try:
        cursor.execute("SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            latest_patch_number = result[0]
            logging.info(f"最新のpatch_number: {latest_patch_number}")
        else:
            logging.warning("patchesテーブルにデータがありません")
            latest_patch_number = None
    except Exception:
        logging.exception("patchesテーブルからのデータ取得に失敗")
        conn.close()
        return

    try:
        selector = "#root > div.mt-2669608.mt-uid-99999.mt-full-container > div.mt-2673591.mt-uid-99970.mt-empty > div > div.mt-2693420.mt-uid-99968.mt-empty > div.mt-2693423.mt-uid-99952.mt-empty > div.mt-2693419.mt-uid-99950.mt-text > span"
        element = soup.select_one(selector)
        if element:
            reference_date_str = element.get_text()
            logging.info(f"参照日時文字列を取得: {reference_date_str}")
        else:
            logging.error("参照日時の要素が見つかりません")
            conn.close()
            return
        
        reference_date = datetime.strptime(reference_date_str, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d')
        logging.info(f"整形済み参照日時: {reference_date}")
    except Exception:
        logging.exception("参照日時の処理に失敗")
        conn.close()
        return

    try:
        for hero in hero_meta_data:
            # heroesテーブルにヒーローが存在するかチェック
            cursor.execute("SELECT english_name FROM heroes WHERE english_name = ?", (hero['hero'],))
            result = cursor.fetchone()
            if result is None:
                cursor.execute("INSERT INTO heroes (english_name) VALUES (?)", (hero['hero'],))
                logging.info(f"新規ヒーロー '{hero['hero']}' を heroes テーブルに挿入")
            
            # hero_statsテーブルへデータ挿入
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
                "Mythic",
                latest_patch_number
            ))
            logging.info(f"hero_stats テーブルに '{hero['hero']}' のデータを挿入")
        conn.commit()
        logging.info("SQLiteデータベースへのコミットに成功")
    except Exception:
        logging.exception("SQLiteデータの挿入に失敗。ロールバックを実施")
        conn.rollback()
        conn.close()
        return

    conn.close()
    logging.info("SQLite接続を正常にクローズ")
    logging.info("スクレイピングおよびデータ保存処理を正常に完了")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("メイン処理で未捕捉の例外が発生")

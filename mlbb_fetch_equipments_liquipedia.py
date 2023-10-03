import time
import sqlite3
import json

from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

DISPLAY_URL = "https://liquipedia.net/mobilelegends/Portal:Equipment"
WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(WAIT_TIME)
driver.get(DISPLAY_URL)
time.sleep(5)

data = {}

def fetch_equipment_data(selector, tab_xpath=None, damege_type=""):
    """
    Fetch equipment data using the provided selector.
    If tab_xpath is provided, click the tab before fetching the data.
    """
    if tab_xpath:
        driver.find_element(By.XPATH, tab_xpath).click()
        time.sleep(2)  # wait for the tab to load
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    lis = soup.select(selector)
    for li in lis:
        name_en = li.select_one('.gallerytext > p > a').get_text(strip=True)
        print(name_en)

        # Placeholder values
        name_ja = ""
        type = damege_type
        image_url = ""
        
        # Add data to JSON object
        data[name_en] = {
            "name": name_ja,
            "type": type,
            "image_url": image_url
        }

def insert_data_into_db(data):
    conn = sqlite3.connect('moba_database.sqlite3')
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for name_en, item in data.items():
        name_ja = item['name']
        type = item['type']
        image_url = item['image_url']
        created_at = now
        updated_at = now
        
        try:
            cursor.execute('''
                INSERT INTO mlbb_equipments (name_ja, name_en, equipment_type, image_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name_ja, name_en, type, image_url, created_at, updated_at))
            print(f"Inserted: {name_en} ({name_ja})")
        except sqlite3.IntegrityError:
            print(f"Duplicated entry: {name_en} ({name_ja})")

    conn.commit()
    conn.close()

# Fetch physical equipment data
attack_selector = '#mw-content-text > div > div.tabs-dynamic.navigation-not-searchable > div > div.content1.active > ul > li'
attack_tab_xpath = '//*[@id="mw-content-text"]/div/div[1]/ul/li[1]/a'
fetch_equipment_data(attack_selector, attack_tab_xpath, "Attack")

# Fetch magic equipment data
magic_selector = '#mw-content-text > div > div.tabs-dynamic.navigation-not-searchable > div > div.content2.active > ul > li'
magic_tab_xpath = '//*[@id="mw-content-text"]/div/div[1]/ul/li[2]/a'
fetch_equipment_data(magic_selector, magic_tab_xpath, "Magic")

# Fetch defense equipment data
defense_selector = '#mw-content-text > div > div.tabs-dynamic.navigation-not-searchable > div > div.content3.active > ul > li'
defense_tab_xpath = '//*[@id="mw-content-text"]/div/div[1]/ul/li[3]/a'
fetch_equipment_data(defense_selector, defense_tab_xpath, "Defense")

# Fetch movement equipment data
movement_selector = '#mw-content-text > div > div.tabs-dynamic.navigation-not-searchable > div > div.content4.active > ul > li'
movement_tab_xpath = '//*[@id="mw-content-text"]/div/div[1]/ul/li[4]/a'
fetch_equipment_data(movement_selector, movement_tab_xpath, "Move")

# 全てのデータ取得が完了した後でデータベースに挿入
print(json.dumps(data, indent=2, ensure_ascii=False))

# Don't forget to close the browser window
driver.quit()

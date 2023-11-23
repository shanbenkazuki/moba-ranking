import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import NavigableString
from deepl_english_to_japanese import conv_mlbb_en_to_ja_translation

DISPLAY_URL = "https://www.reddit.com/r/MobileLegendsGame/comments/16mnofj/patch_notes_1820_org_server/"
WAIT_TIME = 10

chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(WAIT_TIME)

driver.get(DISPLAY_URL)
time.sleep(10)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# セレクタに基づいて要素を探す
target_element = soup.select_one('#t3_16mnofj-post-rtjson-content')

def translate_text_nodes(element):
    for child in element.children:
        if isinstance(child, NavigableString):
            translated_text = conv_mlbb_en_to_ja_translation(str(child))
            child.replace_with(translated_text)
        else:
            translate_text_nodes(child)


# 要素が見つかった場合、そのHTMLを取得
if target_element:
    translate_text_nodes(target_element)  # この関数でテキストノードだけを翻訳

    translated_html = target_element.prettify()

    # 翻訳されたHTMLをテキストファイルに保存
    with open('translated_output.html', 'w', encoding='utf-8') as f:
        f.write(translated_html)
        
    print("Translated HTML content has been saved to translated_output.html")
else:
    print("Element not found.")
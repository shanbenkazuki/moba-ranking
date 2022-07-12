import time
import sys
import conv.mobile_legends.convJaMlbbHero as convJaMlbbHero
import conv.mobile_legends.convImgMlbbHero as convImgMlbbHero
import conv.mobile_legends.convJaEnTerm as convJaEnTerm

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from googletrans import Translator


PATCH_URL = "https://mobile-legends.fandom.com/wiki/Patch_Notes_1.6.66"
WAIT_TIME = 20
FETCH_TABLE_SELECTOR = "#mw-content-text > div.mw-parser-output > table:nth-child(14)"

# 画面遷移
driver = webdriver.Chrome()
driver.get(PATCH_URL)
driver.implicitly_wait(WAIT_TIME)

# 見出しタグの生成
def createHeading(heroName):
    return '<!-- wp:heading {"level":3} --><h3>' + heroName + '</h3><!-- /wp:heading -->'

# 初期テーブルスタートタグの生成
def createStartTag():
    return '<!-- wp:table {"className":"is-style-regular"} --><figure class="wp-block-table is-style-regular"><table><tbody>'

# 初期テーブルエンドタグの生成
def createEndTag():
    return '</tbody></table></figure><!-- /wp:table -->'

# ヒーロー画像タグの生成
def createImgTag(heroImage):
    return '<tr><td><span class="swl-cell-text-centered"><img class="wp-image-1050" style="width: 150px;" src="' + heroImage + '" alt=""></span></td></tr>'

def createStrongTag(str):
    # 用語があれば日本語に変換
    attributeJa = convJaEnTerm.convJaEnTerm(str)
    #強調タグにして返す
    return '<tr><td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black" aria-hidden="true">&nbsp;</span><strong><span class="swl-cell-text-centered">' + attributeJa  + '</span></strong></td></tr>'

def createContentTag(tr):
    content = translator.translate(tr.find('td').text, src="en", dest="ja").text
    return '<tr><td>' + content + '</td></tr>'

# 新ヒーロー抽出
heroAdjustments = BeautifulSoup(driver.page_source, 'html.parser').select(FETCH_TABLE_SELECTOR)

# 試行する
tryNum = 0
while len(heroAdjustments) == 0:
    # ページ情報抽出
    driver.get(PATCH_URL)
    time.sleep(3)
    heroAdjustments = BeautifulSoup(driver.page_source, 'html.parser').select(FETCH_TABLE_SELECTOR)
    print("試行")
    tryNum += 1
    if tryNum == 5:
        break

# 5回試行して正常に取れない場合、終了
if len(heroAdjustments) == 0:
    print("失敗")
    driver.close()
    driver.quit()
    sys.exit()

#見出し
heroNameEn = "Xavier"
heroNameJa = convJaMlbbHero.convJaHeroName(heroNameEn)
print(createHeading(heroNameJa))

#初期テーブルスタートタグ作成
print(createStartTag())
heroImage = convImgMlbbHero.convImgHeroName(heroNameEn)
print(createImgTag(heroImage))

# 調整ヒーローテーブルのtrタグをすべて取得
trs = heroAdjustments[0].find_all('tr')
translator = Translator()

for tr in trs:
    strongStr = tr.find('th').contents[0] + tr.find('span').text
    print(createStrongTag(strongStr))
    print(createContentTag(tr))

#初期テーブルエンドタグ作成
print(createEndTag())

driver.close()
driver.quit()

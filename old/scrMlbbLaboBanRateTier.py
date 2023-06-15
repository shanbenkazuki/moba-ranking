import time
import tagComponent as tag
import locale
import datetime
import old.convImgMlbbHero as convImgMlbbHero
import old.convArticleMlbbHero as convArticleMlbbHero

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

# 画面遷移
driver = webdriver.Chrome()
driver.get(DISPLAY_URL)
driver.implicitly_wait(WAIT_TIME)

time.sleep(2)

#すべてのヒーローに辞書を作成
allHeroList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a > div:nth-of-type(1) > span")
heroDic={}
for hero in allHeroList:
    hero = hero.string
    heroDic[''+ hero +''] ={}

#Legend+に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()

#変換されるまで待機
time.sleep(2)

#Legendでのヒーロー勝率取得
allHeroLegendsWinRateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroLegendsWinRateList):
    hero = allHeroLegendsWinRateList[i].span.string
    banRate = allHeroLegendsWinRateList[i].contents[6].string.split("%")[0]
    heroDic[hero]['Legend'] = float(banRate)

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

#変換されるまで待機
time.sleep(2)

#Mythicでのヒーローバン率取得
allHeroMythicWinRateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroMythicWinRateList):
    hero = allHeroMythicWinRateList[i].span.string
    banRate = allHeroMythicWinRateList[i].contents[6].string.split("%")[0]
    heroDic[hero]['Mythic'] = float(banRate)

#参照日を当日で出力
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
dt_now = datetime.datetime.now()
nowDate = dt_now.strftime('%Y年%m月%d日')

splusTierHero=""
sTierHero=""
aplusTierHero=""
aTierHero=""
bTierHero=""
cTierHero=""

#ターミナルに表示
for hero in heroDic:
    heroImageURL = convImgMlbbHero.convImgHeroName(hero)
    heroArticleURL = convArticleMlbbHero.convArticleHero(hero)
    heroAtag = tag.createHeroATag(heroImageURL, heroArticleURL)
    legendBanRate = heroDic[hero]['Legend']
    mythicBanRate = heroDic[hero]['Mythic']
    banRate = (legendBanRate + mythicBanRate) / 2
    #print(banRate)
    if banRate >= 80:
        splusTierHero += heroAtag
    elif banRate >= 60:
        sTierHero += heroAtag
    elif banRate >= 40:
        aplusTierHero += heroAtag
    elif banRate >= 20:
        aTierHero += heroAtag
    elif banRate >= 10:
        bTierHero += heroAtag
    else :
        cTierHero += heroAtag

# テーブルスタートタグ
print('<!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} -->')
print('<figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')

# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusTierHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sTierHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusTierHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aTierHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bTierHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cTierHero + tag.createTrEndTag())

# テーブルエンドタグ
print('</tbody></table></figure><!-- /wp:table -->')
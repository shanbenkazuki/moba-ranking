import time
import convMlbbHero as convMlbbHero
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

import locale
import datetime

loginUrl = "https://m.mobilelegends.com/en/rank"

#ランキング画面遷移
profilePath = '/Users/kazuki/Library/Application Support/Google/Chrome/Profile 5'
profilefolder = '--user-data-dir=' + profilePath
 
profileOptions = Options()
profileOptions.add_argument(profilefolder)
 
driver = webdriver.Chrome(options = profileOptions)
driver.get(loginUrl)

#BAN率の昇順表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/ul/li[7]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#すべてのヒーローに辞書を作成
allHeroList = soup.select(".slotwrapper > ul > li > a > div:nth-of-type(1) > span")
heroDic={}
for hero in allHeroList:
    hero = hero.string
    heroDic[''+ hero +''] ={}

#Allページでのヒーロー勝率取得
allHeroAllWinRateList = soup.select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroAllWinRateList):
    hero = allHeroAllWinRateList[i].span.string
    winRate = allHeroAllWinRateList[i].contents[2].string
    heroDic[hero]['All'] = winRate

#Legend+に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#Legendでのヒーロー勝率取得
allHeroLegendsWinRateList = soup.select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroLegendsWinRateList):
    hero = allHeroLegendsWinRateList[i].span.string
    winRate = allHeroLegendsWinRateList[i].contents[2].string
    heroDic[hero]['Legend'] = winRate

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#Mythicでのヒーローバン率取得
allHeroMythicWinRateList = soup.select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroMythicWinRateList):
    hero = allHeroMythicWinRateList[i].span.string
    winRate = allHeroMythicWinRateList[i].contents[2].string
    heroDic[hero]['Mythic'] = winRate

#参照日を当日で出力
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
dt_now = datetime.datetime.now()
nowDate = dt_now.strftime('%Y年%m月%d日')

#ターミナルに表示
print("* 参照日：''" + nowDate + "''")
print("[-]")
print("|CENTER|CENTER|CENTER|CENTER|c")
print("|ヒーロー|COLSORT:All勝率|COLSORT:Legend勝率|COLSORT:Mythic勝率|h")
for hero in heroDic:
    convhero = convMlbbHero.convertHeroName(hero)
    #整数部分を0埋めする
    allWinRateList = heroDic[hero]['All'].split(".")
    if(len(allWinRateList)==1):
        #整数1〜9の場合、小数点が発生しないため
        allWinRateList[0].zfill(3)
    else:
        allWinRateList[0] = allWinRateList[0].zfill(2)
    allWinRate = ".".join(allWinRateList)

    #整数部分を0埋めする
    legendWinRateList = heroDic[hero]['Legend'].split(".")
    if(len(legendWinRateList)==1):
        #整数1〜9の場合、小数点が発生しないため
        legendWinRateList[0] = legendWinRateList[0].zfill(3)
    else:
        legendWinRateList[0] = legendWinRateList[0].zfill(2)
    legendWinRate = ".".join(legendWinRateList)

    if('Mythic' in heroDic[hero]):
        mythicWinRate = heroDic[hero]['Mythic']
        print("|" + convhero +"|"+ allWinRate + "|"+ legendWinRate + "|" + mythicWinRate + "|")
    else:
        print("|" + convhero +"|"+ allWinRate + "|"+ legendWinRate + "|"+ "No Data" +"|")
print("[END]")

driver.close()
driver.quit()
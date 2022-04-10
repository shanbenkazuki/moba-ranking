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

#Allページでのヒーローバン率取得
allHeroAllBanRateList = soup.select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroAllBanRateList):
    hero = allHeroAllBanRateList[i].span.string
    banRate = allHeroAllBanRateList[i].contents[6].string
    heroDic[hero]['All'] = banRate

#Legend+に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#Legendでのヒーローバン率取得
allHeroLegendsBanRateList = soup.select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroLegendsBanRateList):
    hero = allHeroLegendsBanRateList[i].span.string
    banRate = allHeroLegendsBanRateList[i].contents[6].string
    heroDic[hero]['Legend'] = banRate

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#Mythicでのヒーローバン率取得
allHeroMythicBanRateList = soup.select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroMythicBanRateList):
    hero = allHeroMythicBanRateList[i].span.string
    banRate = allHeroMythicBanRateList[i].contents[6].string
    heroDic[hero]['Mythic'] = banRate

#参照日を当日で出力
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
dt_now = datetime.datetime.now()
nowDate = dt_now.strftime('%Y年%m月%d日')

#ターミナルに表示
print("* 参照日：''" + nowDate + "''")
print("[-]")
print("|CENTER|CENTER|CENTER|CENTER|c")
print("|ヒーロー|COLSORT:AllBAN率|COLSORT:LegendBAN率|COLSORT:MythicBAN率|h")
for hero in heroDic:
    convhero = convMlbbHero.convertHeroName(hero)
    #整数部分を0埋めする
    allBanRateList = heroDic[hero]['All'].split(".")
    if(len(allBanRateList)==1):
        #整数1〜9の場合、小数点が発生しないため
        allBanRateList[0].zfill(3)
    else:
        allBanRateList[0] = allBanRateList[0].zfill(2)
    allBanRate = ".".join(allBanRateList)

    #整数部分を0埋めする
    legendBanRateList = heroDic[hero]['Legend'].split(".")
    if(len(legendBanRateList)==1):
        #整数1〜9の場合、小数点が発生しないため
        legendBanRateList[0] = legendBanRateList[0].zfill(3)
    else:
        legendBanRateList[0] = legendBanRateList[0].zfill(2)
    legendBanRate = ".".join(legendBanRateList)

    if('Mythic' in heroDic[hero]):
        mythicBanRate = heroDic[hero]['Mythic']
        print("|" + convhero +"|"+ allBanRate + "|"+ legendBanRate + "|" + mythicBanRate + "|")
    else:
        print("|" + convhero +"|"+ allBanRate + "|"+ legendBanRate + "|"+ "No Data" +"|")
print("[END]")

driver.close()
driver.quit()
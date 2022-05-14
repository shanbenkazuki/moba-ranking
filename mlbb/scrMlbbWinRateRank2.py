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
    winRate = allHeroLegendsWinRateList[i].contents[2].string.split("%")[0]
    heroDic[hero]['Legend'] = float(winRate)

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
    winRate = allHeroMythicWinRateList[i].contents[2].string.split("%")[0]
    heroDic[hero]['Mythic'] = float(winRate)

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
    convhero = convMlbbHero.convertHeroName(hero) + " "
    legendWinRate = heroDic[hero]['Legend']
    mythicWinRate = heroDic[hero]['Mythic']
    winRate = (legendWinRate + mythicWinRate) / 2
    if winRate >= 58:
        splusTierHero += convhero
    elif winRate >= 55:
        sTierHero += convhero
    elif winRate >= 52:
        aplusTierHero += convhero
    elif winRate >= 49:
        aTierHero += convhero
    elif winRate >= 46:
        bTierHero += convhero
    else :
        cTierHero += convhero

print("#description")
print("#contents()")
print("参照日：''" + nowDate + "''")

print("[+]◀各ランクの評価基準")
print("|CENTER:20%|CENTER:|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|勝率58%以上|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|勝率55%以上|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|勝率52%以上|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|勝率49%以上|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|勝率46%以上|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|勝率46%未満|")
print("[END]")

print("*AllHero")
print("|!12%|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusTierHero + "|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sTierHero + "|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusTierHero + "|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aTierHero + "|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bTierHero + "|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cTierHero + "|")

driver.close()
driver.quit()
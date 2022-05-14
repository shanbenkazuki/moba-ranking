import time
import convMlbbHero as convMlbbHero
import convRoleMlbbHero as convRoleMlbbHero
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

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#ヒーロー率取得
rateList = soup.select(".slotwrapper > ul > li > a")
#Jungle
splusJungleHero=""
sJungleHero=""
aplusJungleHero=""
aJungleHero=""
bJungleHero=""
cJungleHero=""
#Roam
splusRoamHero=""
sRoamHero=""
aplusRoamHero=""
aRoamHero=""
bRoamHero=""
cRoamHero=""
#Mid
splusMidHero=""
sMidHero=""
aplusMidHero=""
aMidHero=""
bMidHero=""
cMidHero=""
#Gold
splusGoldHero=""
sGoldHero=""
aplusGoldHero=""
aGoldHero=""
bGoldHero=""
cGoldHero=""
#EXP
splusExpHero=""
sExpHero=""
aplusExpHero=""
aExpHero=""
bExpHero=""
cExpHero=""
for heroRate in rateList:
    hero = heroRate.span.string
    gamerchHero = convMlbbHero.convertHeroName(hero) + " "
    convRoleHero = convRoleMlbbHero.convertRoleHeroName(hero)
    winRatePoint = heroRate.contents[2].string.split("%")[0]
    popRatePoint = heroRate.contents[4].string.split("%")[0]
    banRatePoint = heroRate.contents[6].string.split("%")[0]
    tierPoint = float(winRatePoint)*2 + float(popRatePoint)*10 + float(banRatePoint)
    for role in convRoleHero:
        if role=="Jungle":
            if tierPoint > 180:
                splusJungleHero += gamerchHero
            elif tierPoint > 150:
                sJungleHero += gamerchHero
            elif tierPoint > 120:
                aplusJungleHero += gamerchHero
            elif tierPoint > 110:
                aJungleHero += gamerchHero
            elif tierPoint > 100:
                bJungleHero += gamerchHero
            else :
                cJungleHero += gamerchHero
        elif role=="Roam":
            if tierPoint > 180:
                splusRoamHero += gamerchHero
            elif tierPoint > 150:
                sRoamHero += gamerchHero
            elif tierPoint > 120:
                aplusRoamHero += gamerchHero
            elif tierPoint > 110:
                aRoamHero += gamerchHero
            elif tierPoint > 100:
                bRoamHero += gamerchHero
            else :
                cRoamHero += gamerchHero
        elif role=="Mid":
            if tierPoint > 180:
                splusMidHero += gamerchHero
            elif tierPoint > 150:
                sMidHero += gamerchHero
            elif tierPoint > 120:
                aplusMidHero += gamerchHero
            elif tierPoint > 110:
                aMidHero += gamerchHero
            elif tierPoint > 100:
                bMidHero += gamerchHero
            else :
                cMidHero += gamerchHero
        elif role=="Gold":
            if tierPoint > 180:
                splusGoldHero += gamerchHero
            elif tierPoint > 150:
                sGoldHero += gamerchHero
            elif tierPoint > 120:
                aplusGoldHero += gamerchHero
            elif tierPoint > 110:
                aGoldHero += gamerchHero
            elif tierPoint > 100:
                bGoldHero += gamerchHero
            else :
                cGoldHero += gamerchHero
        elif role=="EXP":
            if tierPoint > 180:
                splusExpHero += gamerchHero
            elif tierPoint > 150:
                sExpHero += gamerchHero
            elif tierPoint > 120:
                aplusExpHero += gamerchHero
            elif tierPoint > 110:
                aExpHero += gamerchHero
            elif tierPoint > 100:
                bExpHero += gamerchHero
            else :
                cExpHero += gamerchHero

print("#description")
print("#contents()")
print("参考バージョン情報：''1.6.66''")

#JungleTier
print("*ジャングル")
print("|!12%|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusJungleHero + "|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sJungleHero + "|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusJungleHero + "|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aJungleHero + "|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bJungleHero + "|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cJungleHero + "|")

#GoldTier
print("*ゴールド")
print("|!12%|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusGoldHero + "|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sGoldHero + "|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusGoldHero + "|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aGoldHero + "|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bGoldHero + "|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cGoldHero + "|")

#EXPTier
print("*EXP")
print("|!12%|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusExpHero + "|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sExpHero + "|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusExpHero + "|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aExpHero + "|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bExpHero + "|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cExpHero + "|")

#RoamTier
print("*ローム")
print("|!12%|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusRoamHero + "|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sRoamHero + "|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusRoamHero + "|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aRoamHero + "|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bRoamHero + "|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cRoamHero + "|")

#MidTier
print("*ミッド")
print("|!12%|c")
print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusMidHero + "|")
print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sMidHero + "|")
print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusMidHero + "|")
print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aMidHero + "|")
print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bMidHero + "|")
print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cMidHero + "|")

driver.close()
driver.quit()
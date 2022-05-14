import time
import convMlbbHero as convMlbbHero
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def fetchTierList(role):
    #S+Tier取得
    scrSplusTierHero = soup.select("body > div.page > div > div:nth-child(9) > div.tierlist-bottom-row > div[data-role="+ role +"] > a > span")
    splusTierHero=""
    for i, hero in enumerate(scrSplusTierHero):
        hero = convMlbbHero.convertHeroName(hero.string)
        splusTierHero += hero
    print("|bgcolor(#ff9900):&color(#ffffff){&size(18){S+}}|bgcolor(#ffeecc):" + splusTierHero + "|")

    #STier取得
    scrSTierHero = soup.select("body > div.page > div > div:nth-child(10) > div.tierlist-bottom-row > div[data-role="+ role +"] > a > span")
    sTierHero=""
    for i, hero in enumerate(scrSTierHero):
        hero = convMlbbHero.convertHeroName(hero.string)
        sTierHero += hero
    print("|bgcolor(#ff6666):&color(#ffffff){&size(18){S}}|bgcolor(#ffeeee):" + sTierHero + "|")

    #A+Tier取得
    scrAplusTierHero = soup.select("body > div.page > div > div:nth-child(11) > div.tierlist-bottom-row > div[data-role="+ role +"] > a > span")
    aplusTierHero=""
    for i, hero in enumerate(scrAplusTierHero):
        hero = convMlbbHero.convertHeroName(hero.string)
        aplusTierHero += hero
    print("|bgcolor(#ff00cc):&color(#ffffff){&size(18){A+}}|bgcolor(#ffe7fa):" + aplusTierHero + "|")

    #ATier取得
    scrATierHero = soup.select("body > div.page > div > div:nth-child(13) > div.tierlist-bottom-row > div[data-role="+ role +"] > a > span")
    aTierHero=""
    for i, hero in enumerate(scrATierHero):
        hero = convMlbbHero.convertHeroName(hero.string)
        aTierHero += hero
    print("|bgcolor(#6666ff):&color(#ffffff){&size(18){A}}|bgcolor(#eeeeff):" + aTierHero + "|")

    #BTier取得
    scrBTierHero = soup.select("body > div.page > div > div:nth-child(14) > div.tierlist-bottom-row > div[data-role="+ role +"] > a > span")
    bTierHero=""
    for i, hero in enumerate(scrBTierHero):
        hero = convMlbbHero.convertHeroName(hero.string)
        bTierHero += hero
    print("|bgcolor(#53abff):&color(#ffffff){&size(18){B}}|bgcolor(#f0f8ff):" + bTierHero + "|")

    #CTier取得
    scrCTierHero = soup.select("body > div.page > div > div:nth-child(15) > div.tierlist-bottom-row > div[data-role="+ role +"] > a > span")
    cTierHero=""
    for i, hero in enumerate(scrCTierHero):
        hero = convMlbbHero.convertHeroName(hero.string)
        cTierHero += hero
    print("|bgcolor(#0dbc0d):&color(#ffffff){&size(18){C}}|bgcolor(#eeffee):" + cTierHero + "|")
    return

loginUrl = "https://www.expertwm.com/tierlist/"

#Tier画面遷移
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

fetchRole=""

print("#description")
print("最終更新日：2022年3月3日")

#ジャングル
print("*ジャングル")
print("|!12%|c")
fetchRole="jungle"
fetchTierList(fetchRole)

#ゴールド
print("*ゴールド")
print("|!12%|c")
fetchRole="gold"
fetchTierList(fetchRole)

#exp
print("*EXP")
print("|!12%|c")
fetchRole="exp"
fetchTierList(fetchRole)

#roam
print("*ローム")
print("|!12%|c")
fetchRole="roam"
fetchTierList(fetchRole)

#mid
print("*ミッド")
print("|!12%|c")
fetchRole="mid"
fetchTierList(fetchRole)


driver.close()
driver.quit()

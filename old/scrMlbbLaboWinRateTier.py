import time
import tagComponent as tag
import locale
import datetime
import old.convImgMlbbHero as convImgMlbbHero
import old.convArticleMlbbHero as convArticleMlbbHero
import old.convRoleMlbbHero as convRoleMlbbHero

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
    winRate = allHeroLegendsWinRateList[i].contents[2].string.split("%")[0]
    heroDic[hero]['Legend'] = float(winRate)

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

#変換されるまで待機
time.sleep(2)

#Mythicでのヒーロー勝率取得
allHeroMythicWinRateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")
for i, hero in enumerate(allHeroMythicWinRateList):
    hero = allHeroMythicWinRateList[i].span.string
    winRate = allHeroMythicWinRateList[i].contents[2].string.split("%")[0]
    heroDic[hero]['Mythic'] = float(winRate)

# #参照日を当日で出力
# locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
# dt_now = datetime.datetime.now()
# nowDate = dt_now.strftime('%Y年%m月%d日')


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
    legendWinRate = heroDic[hero]['Legend']
    mythicWinRate = heroDic[hero]['Mythic']
    winRate = (legendWinRate + mythicWinRate) / 2
    for role in convRoleMlbbHero.convertRoleHeroName(hero):
        if role=="Jungle":
            if winRate >= 58:
                splusJungleHero += heroAtag
            elif winRate >= 56:
                sJungleHero += heroAtag
            elif winRate >= 54:
                aplusJungleHero += heroAtag
            elif winRate >= 52:
                aJungleHero += heroAtag
            elif winRate >= 50:
                bJungleHero += heroAtag
            else :
                cJungleHero += heroAtag
        elif role=="Roam":
            if winRate >= 58:
                splusRoamHero += heroAtag
            elif winRate >= 56:
                sRoamHero += heroAtag
            elif winRate >= 54:
                aplusRoamHero += heroAtag
            elif winRate >= 52:
                aRoamHero += heroAtag
            elif winRate >= 50:
                bRoamHero += heroAtag
            else :
                cRoamHero += heroAtag
        elif role=="Mid":
            if winRate >= 58:
                splusMidHero += heroAtag
            elif winRate >= 56:
                sMidHero += heroAtag
            elif winRate >= 54:
                aplusMidHero += heroAtag
            elif winRate >= 52:
                aMidHero += heroAtag
            elif winRate >= 50:
                bMidHero += heroAtag
            else :
                cMidHero += heroAtag
        elif role=="Gold":
            if winRate >= 58:
                splusGoldHero += heroAtag
            elif winRate >= 56:
                sGoldHero += heroAtag
            elif winRate >= 54:
                aplusGoldHero += heroAtag
            elif winRate >= 52:
                aGoldHero += heroAtag
            elif winRate >= 50:
                bGoldHero += heroAtag
            else :
                cGoldHero += heroAtag
        elif role=="EXP":
            if winRate >= 58:
                splusExpHero += heroAtag
            elif winRate >= 56:
                sExpHero += heroAtag
            elif winRate >= 54:
                aplusExpHero += heroAtag
            elif winRate >= 52:
                aExpHero += heroAtag
            elif winRate >= 50:
                bExpHero += heroAtag
            else :
                cExpHero += heroAtag

# タブ始まり
print('<!-- wp:loos/tab {"tabId":"e10f2805","tabHeaders":["ジャングル","ゴールド","EXP","ローム","ミッド"],"className":"is-style-default"} -->')
print('<div class="swell-block-tab is-style-default" data-width-pc="auto" data-width-sp="auto"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="true" aria-controls="tab-e10f2805-0" data-onclick="tabControl">ジャングル</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-e10f2805-1" data-onclick="tabControl">ゴールド</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-e10f2805-2" data-onclick="tabControl">EXP</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-e10f2805-3" data-onclick="tabControl">ローム</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-e10f2805-4" data-onclick="tabControl">ミッド</button></li></ul><div class="c-tabBody">')

# Jungle
print('<!-- wp:loos/tab-body {"tabId":"e10f2805"} --><div id="tab-e10f2805-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusJungleHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sJungleHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusJungleHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aJungleHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bJungleHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cJungleHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ゴールド
print('<!-- wp:loos/tab-body {"id":1,"tabId":"e10f2805"} --><div id="tab-e10f2805-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusGoldHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sGoldHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusGoldHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aGoldHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bGoldHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cGoldHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# EXP
print('<!-- wp:loos/tab-body {"id":2,"tabId":"e10f2805"} --><div id="tab-e10f2805-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusExpHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sExpHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusExpHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aExpHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bExpHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cExpHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ローム
print('<!-- wp:loos/tab-body {"id":3,"tabId":"e10f2805"} --><div id="tab-e10f2805-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusRoamHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sRoamHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusRoamHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aRoamHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bRoamHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cRoamHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ミッド
print('<!-- wp:loos/tab-body {"id":4,"tabId":"e10f2805"} --><div id="tab-e10f2805-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splusMidHero + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + sMidHero + tag.createTrEndTag())
# A+
print(tag.createTrAPlusStartTag() + aplusMidHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aMidHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bMidHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cMidHero + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

#タブ終わり
print('</div></div><!-- /wp:loos/tab -->')

driver.close()
driver.quit()
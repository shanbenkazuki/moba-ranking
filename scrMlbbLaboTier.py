import time
import common.tagComponent as tag
import conv.mobile_legends.convImgMlbbHero as convImgMlbbHero
import conv.mobile_legends.convArticleMlbbHero as convArticleMlbbHero
import conv.mobile_legends.convRoleMlbbHero as convRoleMlbbHero

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

DISPLAY_URL = "https://m.mobilelegends.com/en/rank"
WAIT_TIME = 10

#ここで、バージョンなどのチェックをします。
#chrome = webdriver.Chrome(ChromeDriverManager().install())

# 画面遷移
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(DISPLAY_URL)
driver.implicitly_wait(WAIT_TIME)

time.sleep(2)

#ミシック400ポイント表示に切り替え
#driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()
# レジェンド表示に切り替え（ミシックがまだ集計されてない場合）
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[2]").click()

time.sleep(3)

#ランキング抽出
rateList = BeautifulSoup(driver.page_source, 'html.parser').select(".slotwrapper > ul > li > a")

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
    heroEn = heroRate.span.string
    heroImageURL = convImgMlbbHero.convImgHeroName(heroEn)
    heroArticleURL = convArticleMlbbHero.convArticleHero(heroEn)
    heroAtag = tag.createHeroATag(heroImageURL, heroArticleURL)
    winRatePoint = heroRate.contents[2].string.split("%")[0]
    popRatePoint = heroRate.contents[4].string.split("%")[0]
    banRatePoint = heroRate.contents[6].string.split("%")[0]
    tierPoint = float(winRatePoint)*2 + float(popRatePoint)*10 + float(banRatePoint)
    for role in convRoleMlbbHero.convertRoleHeroName(heroEn):
        if role=="Jungle":
            if tierPoint > 180:
                splusJungleHero += heroAtag
            elif tierPoint > 150:
                sJungleHero += heroAtag
            elif tierPoint > 120:
                aplusJungleHero += heroAtag
            elif tierPoint > 110:
                aJungleHero += heroAtag
            elif tierPoint > 100:
                bJungleHero += heroAtag
            else :
                cJungleHero += heroAtag
        elif role=="Roam":
            if tierPoint > 180:
                splusRoamHero += heroAtag
            elif tierPoint > 150:
                sRoamHero += heroAtag
            elif tierPoint > 120:
                aplusRoamHero += heroAtag
            elif tierPoint > 110:
                aRoamHero += heroAtag
            elif tierPoint > 100:
                bRoamHero += heroAtag
            else :
                cRoamHero += heroAtag
        elif role=="Mid":
            if tierPoint > 180:
                splusMidHero += heroAtag
            elif tierPoint > 150:
                sMidHero += heroAtag
            elif tierPoint > 120:
                aplusMidHero += heroAtag
            elif tierPoint > 110:
                aMidHero += heroAtag
            elif tierPoint > 100:
                bMidHero += heroAtag
            else :
                cMidHero += heroAtag
        elif role=="Gold":
            if tierPoint > 180:
                splusGoldHero += heroAtag
            elif tierPoint > 150:
                sGoldHero += heroAtag
            elif tierPoint > 120:
                aplusGoldHero += heroAtag
            elif tierPoint > 110:
                aGoldHero += heroAtag
            elif tierPoint > 100:
                bGoldHero += heroAtag
            else :
                cGoldHero += heroAtag
        elif role=="EXP":
            if tierPoint > 180:
                splusExpHero += heroAtag
            elif tierPoint > 150:
                sExpHero += heroAtag
            elif tierPoint > 120:
                aplusExpHero += heroAtag
            elif tierPoint > 110:
                aExpHero += heroAtag
            elif tierPoint > 100:
                bExpHero += heroAtag
            else :
                cExpHero += heroAtag

# タブ始まり
print('<!-- wp:loos/tab {"tabId":"9e24a182","tabWidthPC":"flex-50","tabWidthSP":"flex-50","tabHeaders":["Jg","Gold","Exp","Roam","Mid"],"className":"is-style-balloon"} -->')
print('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="flex-50"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="true" aria-controls="tab-9e24a182-0" data-onclick="tabControl">Jg</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-1" data-onclick="tabControl">Gold</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-2" data-onclick="tabControl">Exp</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-3" data-onclick="tabControl">Roam</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-9e24a182-4" data-onclick="tabControl">Mid</button></li></ul><div class="c-tabBody">')

# Jungle
print('<!-- wp:loos/tab-body {"tabId":"9e24a182"} --><div id="tab-9e24a182-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
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
print('<!-- wp:loos/tab-body {"id":1,"tabId":"9e24a182"} --><div id="tab-9e24a182-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
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
print('<!-- wp:loos/tab-body {"id":2,"tabId":"9e24a182"} --> <div id="tab-9e24a182-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
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
print('<!-- wp:loos/tab-body {"id":3,"tabId":"9e24a182"} --><div id="tab-9e24a182-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
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
print('<!-- wp:loos/tab-body {"id":4,"tabId":"9e24a182"} --><div id="tab-9e24a182-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
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
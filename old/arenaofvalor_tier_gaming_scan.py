import time
import tagComponent as tag
import conv.arena_of_valor.conv_arenaofvalor as conv_arena_of_valor

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

DISPLAY_URL = "https://faindx.com/games/arena-of-valor-tier-list/"

# ジャングル
splus_jungle=""
s_jungle=""
a_jungle=""
b_jungle=""
c_jungle=""

# スレイヤー
splus_slayer=""
s_slayer=""
a_slayer=""
b_slayer=""
c_slayer=""

# ドラゴン
splus_dragon=""
s_dragon=""
a_dragon=""
b_dragon=""
c_dragon=""

# ミッド
splus_mid=""
s_mid=""
a_mid=""
b_mid=""
c_mid=""

# サポート
splus_support=""
s_support=""
a_support=""
b_support=""
c_support=""

# 画面遷移
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(DISPLAY_URL)

time.sleep(2)

splus_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-150766 > div > div.entry-content > figure:nth-child(10) > table > tbody > tr > td:nth-child(1)")
s_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-150766 > div > div.entry-content > figure:nth-child(15) > table > tbody > tr > td:nth-child(1)")
a_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-150766 > div > div.entry-content > figure:nth-child(21) > table > tbody > tr > td:nth-child(1)")
b_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-150766 > div > div.entry-content > figure:nth-child(26) > table > tbody > tr > td:nth-child(1)")
c_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-150766 > div > div.entry-content > figure:nth-child(32) > table > tbody > tr > td:nth-child(1)")
d_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-150766 > div > div.entry-content > figure:nth-child(37) > table > tbody > tr > td:nth-child(1)")

splus_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-12093 > div.single-body.entry > div.single-content > div > figure:nth-child(20) > table > tbody > tr > td:nth-child(1)")
s_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-12093 > div.single-body.entry > div.single-content > div > figure:nth-child(25) > table > tbody > tr > td:nth-child(1)")
a_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-12093 > div.single-body.entry > div.single-content > div > figure:nth-child(28) > table > tbody > tr > td:nth-child(1)")
b_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-12093 > div.single-body.entry > div.single-content > div > figure:nth-child(31) > table > tbody > tr > td:nth-child(1)")
c_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-12093 > div.single-body.entry > div.single-content > div > figure:nth-child(36) > table > tbody > tr > td:nth-child(1)")
d_list = BeautifulSoup(driver.page_source, 'html.parser').select("#post-12093 > div.single-body.entry > div.single-content > div > figure:nth-child(39) > table > tbody > tr > td:nth-child(1)")

# S+Tier
for hero in splus_list:
    hero = hero.string
    heroImageUrl = conv_arena_of_valor.conv_image_hero(hero)
    hero_a_tag = tag.createHeroImgTag(heroImageUrl)
    heroStyle = conv_arena_of_valor.conv_style_name(hero)
    if heroStyle == "Jungler":
        splus_jungle += hero_a_tag
    elif heroStyle == "Dark Slayer":
        splus_slayer += hero_a_tag
    elif heroStyle == "Abyssal Dragon":
        splus_dragon += hero_a_tag
    elif heroStyle == "Mid":
        splus_mid += hero_a_tag
    elif heroStyle == "Roamer":
        splus_support += hero_a_tag

# STier
for hero in s_list:
    hero = hero.string
    heroImageUrl = conv_arena_of_valor.conv_image_hero(hero)
    hero_a_tag = tag.createHeroImgTag(heroImageUrl)
    heroStyle = conv_arena_of_valor.conv_style_name(hero)
    if heroStyle == "Jungler":
        s_jungle += hero_a_tag
    elif heroStyle == "Dark Slayer":
        s_slayer += hero_a_tag
    elif heroStyle == "Abyssal Dragon":
        s_dragon += hero_a_tag
    elif heroStyle == "Mid":
        s_mid += hero_a_tag
    elif heroStyle == "Roamer":
        s_support += hero_a_tag


# ATier
for hero in a_list:
    hero = hero.string
    heroImageUrl = conv_arena_of_valor.conv_image_hero(hero)
    hero_a_tag = tag.createHeroImgTag(heroImageUrl)
    heroStyle = conv_arena_of_valor.conv_style_name(hero)
    if heroStyle == "Jungler":
        a_jungle += hero_a_tag
    elif heroStyle == "Dark Slayer":
        a_slayer += hero_a_tag
    elif heroStyle == "Abyssal Dragon":
        a_dragon += hero_a_tag
    elif heroStyle == "Mid":
        a_mid += hero_a_tag
    elif heroStyle == "Roamer":
        a_support += hero_a_tag

# BTier
for hero in b_list:
    hero = hero.string
    heroImageUrl = conv_arena_of_valor.conv_image_hero(hero)
    hero_a_tag = tag.createHeroImgTag(heroImageUrl)
    heroStyle = conv_arena_of_valor.conv_style_name(hero)
    if heroStyle == "Jungler":
        b_jungle += hero_a_tag
    elif heroStyle == "Dark Slayer":
        b_slayer += hero_a_tag
    elif heroStyle == "Abyssal Dragon":
        b_dragon += hero_a_tag
    elif heroStyle == "Mid":
        b_mid += hero_a_tag
    elif heroStyle == "Roamer":
        b_support += hero_a_tag

# CTier1
for hero in c_list:
    hero = hero.string
    heroImageUrl = conv_arena_of_valor.conv_image_hero(hero)
    hero_a_tag = tag.createHeroImgTag(heroImageUrl)
    heroStyle = conv_arena_of_valor.conv_style_name(hero)
    if heroStyle == "Jungler":
        c_jungle += hero_a_tag
    elif heroStyle == "Dark Slayer":
        c_slayer += hero_a_tag
    elif heroStyle == "Abyssal Dragon":
        c_dragon += hero_a_tag
    elif heroStyle == "Mid":
        c_mid += hero_a_tag
    elif heroStyle == "Roamer":
        c_support += hero_a_tag

# CTier2
for hero in d_list:
    hero = hero.string
    heroImageUrl = conv_arena_of_valor.conv_image_hero(hero)
    hero_a_tag = tag.createHeroImgTag(heroImageUrl)
    heroStyle = conv_arena_of_valor.conv_style_name(hero)
    if heroStyle == "Jungler":
        c_jungle += hero_a_tag
    elif heroStyle == "Dark Slayer":
        c_slayer += hero_a_tag
    elif heroStyle == "Abyssal Dragon":
        c_dragon += hero_a_tag
    elif heroStyle == "Mid":
        c_mid += hero_a_tag
    elif heroStyle == "Roamer":
        c_support += hero_a_tag

# タブ始まり
print('<!-- wp:loos/tab {"tabId":"ff4c939b","tabWidthPC":"flex-50","tabWidthSP":"flex-50","tabHeaders":["ジャングル","スレイヤー","ドラゴン","ミッド","サポート"],"className":"is-style-balloon"} -->')
print('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="flex-50"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="true" aria-controls="tab-ff4c939b-0" data-onclick="tabControl">ジャングル</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-ff4c939b-1" data-onclick="tabControl">スレイヤー</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-ff4c939b-2" data-onclick="tabControl">ドラゴン</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-ff4c939b-3" data-onclick="tabControl">ミッド</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-ff4c939b-4" data-onclick="tabControl">サポート</button></li></ul><div class="c-tabBody">')

# ジャングル
print('<!-- wp:loos/tab-body {"tabId":"ff4c939b"} --><div id="tab-ff4c939b-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_jungle + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_jungle + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_jungle + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_jungle + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_jungle + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# スレイヤー
print('<!-- wp:loos/tab-body {"id":1,"tabId":"ff4c939b"} --><div id="tab-ff4c939b-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_slayer + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_slayer + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_slayer + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_slayer + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_slayer + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ドラゴン
print('<!-- wp:loos/tab-body {"id":2,"tabId":"ff4c939b"} --><div id="tab-ff4c939b-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_dragon + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_dragon + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_dragon + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_dragon + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_dragon + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ミッド
print('<!-- wp:loos/tab-body {"id":3,"tabId":"ff4c939b"} --><div id="tab-ff4c939b-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_mid + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_mid + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_mid + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_mid + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_mid + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# サポート
print('<!-- wp:loos/tab-body {"id":4,"tabId":"ff4c939b"} --><div id="tab-ff4c939b-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_support + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_support + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_support + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_support + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_support + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

#タブ終わり
print('</div></div><!-- /wp:loos/tab -->')

driver.close()
driver.quit()
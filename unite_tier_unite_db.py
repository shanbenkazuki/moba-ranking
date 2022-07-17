import time
import conv.pokemon_unite.convPokemon as convPokemon

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from common import tagComponent as tag

DISPLAY_URL = "https://unite-db.com/tier-list/pokemon"

# バランス
splus_balance=""
s_balance=""
a_balance=""
b_balance=""
c_balance=""

# アタック
splus_attack=""
s_attack=""
a_attack=""
b_attack=""
c_attack=""

# スピード
splus_speed=""
s_speed=""
a_speed=""
b_speed=""
c_speed=""

# ディフェンス
splus_defense=""
s_defense=""
a_defense=""
b_defense=""
c_defense=""

# サポート
splus_support=""
s_support=""
a_support=""
b_support=""
c_support=""

# 画面遷移
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(DISPLAY_URL)

time.sleep(2)

# UNITE-DBでの各ランクのポケモンを取得
pokemon_splus_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-s > div > div > a > p")
pokemon_s_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-a > div > div > a > p")
pokemon_a_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-b > div > div > a > p")
pokemon_b_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-c > div > div > a > p")
pokemon_c_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-d > div > div > a > p")
#pokemon_t_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-t > div > div > a > p")

# Splustier作成
for pokemon in pokemon_splus_list:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon.string)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon.string)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon.string)
    if style == "balance":
        splus_balance += pokemon_a_tag
    elif style == "attack":
        splus_attack += pokemon_a_tag
    elif style == "defense":
        splus_defense += pokemon_a_tag
    elif style == "speed":
        splus_speed += pokemon_a_tag
    elif style == "support":
        splus_support += pokemon_a_tag

# stier作成
for pokemon in pokemon_s_list:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon.string)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon.string)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon.string)
    if style == "balance":
        s_balance += pokemon_a_tag
    elif style == "attack":
        s_attack += pokemon_a_tag
    elif style == "defense":
        s_defense += pokemon_a_tag
    elif style == "speed":
        s_speed += pokemon_a_tag
    elif style == "support":
        s_support += pokemon_a_tag

# Atier作成
for pokemon in pokemon_a_list:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon.string)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon.string)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon.string)
    if style == "balance":
        a_balance += pokemon_a_tag
    elif style == "attack":
        a_attack += pokemon_a_tag
    elif style == "defense":
        a_defense += pokemon_a_tag
    elif style == "speed":
        a_speed += pokemon_a_tag
    elif style == "support":
        a_support += pokemon_a_tag

# Btier作成
for pokemon in pokemon_b_list:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon.string)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon.string)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon.string)
    if style == "balance":
        b_balance += pokemon_a_tag
    elif style == "attack":
        b_attack += pokemon_a_tag
    elif style == "defense":
        b_defense += pokemon_a_tag
    elif style == "speed":
        b_speed += pokemon_a_tag
    elif style == "support":
        b_support += pokemon_a_tag

# Ctier作成
for pokemon in pokemon_c_list:
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon.string)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon.string)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    style = convPokemon.conv_style_name(pokemon.string)
    if style == "balance":
        c_balance += pokemon_a_tag
    elif style == "attack":
        c_attack += pokemon_a_tag
    elif style == "defense":
        c_defense += pokemon_a_tag
    elif style == "speed":
        c_speed += pokemon_a_tag
    elif style == "support":
        c_support += pokemon_a_tag

# タブ始まり
print('<!-- wp:loos/tab {"tabId":"479b3ce7","tabWidthPC":"flex-50","tabWidthSP":"flex-50","tabHeaders":["バランス","アタック","スピード","ディフェンス","サポート"],"className":"is-style-balloon"} -->')
print('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="flex-50"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="true" aria-controls="tab-479b3ce7-0" data-onclick="tabControl">バランス</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-1" data-onclick="tabControl">アタック</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-2" data-onclick="tabControl">スピード</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-3" data-onclick="tabControl">ディフェンス</button></li><li class="c-tabList__item" role="presentation"><button class="c-tabList__button" aria-selected="false" aria-controls="tab-479b3ce7-4" data-onclick="tabControl">サポート</button></li></ul><div class="c-tabBody">')

# バランス
print('<!-- wp:loos/tab-body {"tabId":"479b3ce7"} --><div id="tab-479b3ce7-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_balance + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_balance + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_balance + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_balance + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_balance + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# アタック
print('<!-- wp:loos/tab-body {"id":1,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_attack + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_attack + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_attack + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_attack + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_attack + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# スピード
print('<!-- wp:loos/tab-body {"id":2,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_speed + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_speed + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_speed + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_speed + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_speed + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# ディフェンス
print('<!-- wp:loos/tab-body {"id":3,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
# tr追加場所
# S+
print(tag.createTrSPlusStartTag() + splus_defense + tag.createTrEndTag())
# S
print(tag.createTrSStartTag() + s_defense + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + a_defense + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + b_defense + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + c_defense + tag.createTrEndTag())
print('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->')

# サポート
print('<!-- wp:loos/tab-body {"id":4,"tabId":"479b3ce7"} --><div id="tab-479b3ce7-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-all-centered\u002d\u002dva td_to_th_ is-style-simple"} --><figure class="wp-block-table is-all-centered--va td_to_th_ is-style-simple"><table><tbody>')
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
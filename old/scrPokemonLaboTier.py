from cmath import pi
import time
import old.convPokemon as convPokemon

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from . import tagComponent as tag

DISPLAY_URL_UNITE_DB = "https://unite-db.com/tier-list/pokemon"
DISPLAY_URL_GAME_8 = "https://game8.co/games/Pokemon-UNITE/archives/335997"
DISPLAY_URL_GAME_WITH_JA = "https://gamewith.jp/pokemon-unite/article/show/314847"
WAIT_TIME = 10

#ブログで分けるための変数
sTierHero=""
aTierHero=""
bTierHero=""
cTierHero=""

driver = webdriver.Chrome()

#UNITE-DB
driver.get(DISPLAY_URL_UNITE_DB)
driver.implicitly_wait(WAIT_TIME)

time.sleep(1)

# ポケモンの辞書を作成
pokemon_dict = {}
for pokemon in BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper > div > div > a > p"):
    pokemon_dict[''+ pokemon.string +''] ={}

#UNITE-DBでの各ランクのポケモンを取得
pokemon_s_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-s > div > div > a > p")
pokemon_a_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-a > div > div > a > p")
pokemon_b_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-b > div > div > a > p")
pokemon_c_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-c > div > div > a > p")
pokemon_t_list = BeautifulSoup(driver.page_source, 'html.parser').select("#app > div.container > section > div.content > div.tier-wrapper.tier-t > div > div > a > p")


# 点数追加
for pokemon in pokemon_s_list:
    pokemon_dict[''+ pokemon.string +''] = 5
for pokemon in pokemon_a_list:
    pokemon_dict[''+ pokemon.string +''] = 4

for pokemon in pokemon_b_list:
    pokemon_dict[''+ pokemon.string +''] = 3

for pokemon in pokemon_c_list:
    pokemon_dict[''+ pokemon.string +''] = 2

for pokemon in pokemon_t_list:
    pokemon_dict[''+ pokemon.string +''] = 3

# GAME8
driver.get(DISPLAY_URL_GAME_8)
driver.implicitly_wait(WAIT_TIME)

time.sleep(2)

game_8_ss_list = BeautifulSoup(driver.page_source, 'html.parser').select("body > div.l-content > div.l-3col > div.l-3colMain > div.l-3colMain__center.l-3colMain__center--shadow > div.archive-style-wrapper > table:nth-child(8) > tbody > tr:nth-child(1) > td > div > a > img")
game_8_s_list = BeautifulSoup(driver.page_source, 'html.parser').select("body > div.l-content > div.l-3col > div.l-3colMain > div.l-3colMain__center.l-3colMain__center--shadow > div.archive-style-wrapper > table:nth-child(8) > tbody > tr:nth-child(2) > td > div > a > img")
game_8_a_list = BeautifulSoup(driver.page_source, 'html.parser').select("body > div.l-content > div.l-3col > div.l-3colMain > div.l-3colMain__center.l-3colMain__center--shadow > div.archive-style-wrapper > table:nth-child(8) > tbody > tr:nth-child(3) > td > div > a > img")
game_8_b_list = BeautifulSoup(driver.page_source, 'html.parser').select("body > div.l-content > div.l-3col > div.l-3colMain > div.l-3colMain__center.l-3colMain__center--shadow > div.archive-style-wrapper > table:nth-child(8) > tbody > tr:nth-child(4) > td > div > a > img")
game_8_c_list = BeautifulSoup(driver.page_source, 'html.parser').select("body > div.l-content > div.l-3col > div.l-3colMain > div.l-3colMain__center.l-3colMain__center--shadow > div.archive-style-wrapper > table:nth-child(8) > tbody > tr:nth-child(5) > td > div > a > img")

for game_8_ss_pokemon in game_8_ss_list:
    pokemon_name = convPokemon.conv_pokemon_name(game_8_ss_pokemon.get('alt'))
    pokemon_dict[''+ pokemon_name +''] += 5
for game_8_s_pokemon in game_8_s_list:
    pokemon_name = convPokemon.conv_pokemon_name(game_8_s_pokemon.get('alt'))
    pokemon_dict[''+ pokemon_name +''] += 4
for game_8_a_pokemon in game_8_a_list:
    pokemon_name = convPokemon.conv_pokemon_name(game_8_a_pokemon.get('alt'))
    pokemon_dict[''+ pokemon_name +''] += 3
for game_8_b_pokemon in game_8_b_list:
    pokemon_name = convPokemon.conv_pokemon_name(game_8_b_pokemon.get('alt'))
    pokemon_dict[''+ pokemon_name +''] += 2
for game_8_c_pokemon in game_8_c_list:
    pokemon_name = convPokemon.conv_pokemon_name(game_8_c_pokemon.get('alt'))
    pokemon_dict[''+ pokemon_name +''] += 1

#GAMEWITH
driver.get(DISPLAY_URL_GAME_WITH_JA)
driver.implicitly_wait(WAIT_TIME)

time.sleep(1)

game_with_sss_list_top_bot = BeautifulSoup(driver.page_source, 'html.parser').select("#article-body > div:nth-child(7) > table > tbody > tr:nth-child(2)")[0].find_all('a')
game_with_ss_list_top_bot = BeautifulSoup(driver.page_source, 'html.parser').select("#article-body > div:nth-child(7) > table > tbody > tr:nth-child(4)")[0].find_all('a')
game_with_s_list_top_bot = BeautifulSoup(driver.page_source, 'html.parser').select("#article-body > div:nth-child(7) > table > tbody > tr:nth-child(6)")[0].find_all('a')
game_with_s_list_mid = BeautifulSoup(driver.page_source, 'html.parser').select("#article-body > table > tbody > tr:nth-child(4)")[0].find_all('a')
game_with_a_list_top_bot = BeautifulSoup(driver.page_source, 'html.parser').select("#article-body > div:nth-child(7) > table > tbody > tr:nth-child(8)")[0].find_all('a')
game_with_a_list_mid = BeautifulSoup(driver.page_source, 'html.parser').select("#article-body > table > tbody > tr:nth-child(6)")[0].find_all('a')
game_with_b_list = BeautifulSoup(driver.page_source, 'html.parser').select("#tabledata")[12].find_all('a')

for pokemon_ja in game_with_sss_list_top_bot:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 6

for pokemon_ja in game_with_ss_list_top_bot:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 5

for pokemon_ja in game_with_s_list_top_bot:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 4

for pokemon_ja in game_with_s_list_mid:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 4

for pokemon_ja in game_with_a_list_top_bot:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 3

for pokemon_ja in game_with_a_list_mid:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 3

for pokemon_ja in game_with_b_list:
    pokemon_name_en = convPokemon.conv_en_for_ja(pokemon_ja.contents[2])
    pokemon_dict[''+ pokemon_name_en +''] += 2

#振り分け
for pokemon in pokemon_dict:
    point = pokemon_dict[''+ pokemon +'']
    pokemon_image_url = convPokemon.conv_image_pokemon(pokemon)
    pokemon_article_url = convPokemon.conv_article_pokemon_unite(pokemon)
    pokemon_a_tag = tag.createHeroATag(pokemon_image_url, pokemon_article_url)
    if point >= 13:
        sTierHero += pokemon_a_tag
    elif point >= 10:
        aTierHero += pokemon_a_tag
    elif point >= 7:
        bTierHero += pokemon_a_tag
    else:
        cTierHero += pokemon_a_tag

# テーブルスタートタグ
print('<!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} -->')
print('<figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>')

# tr追加場所
# S
print(tag.createTrSStartTag() + sTierHero + tag.createTrEndTag())
# A
print(tag.createTrAStartTag() + aTierHero + tag.createTrEndTag())
# B
print(tag.createTrBStartTag() + bTierHero + tag.createTrEndTag())
# C
print(tag.createTrCStartTag() + cTierHero + tag.createTrEndTag())

# テーブルエンドタグ
print('</tbody></table></figure><!-- /wp:table -->')

driver.close()
driver.quit()
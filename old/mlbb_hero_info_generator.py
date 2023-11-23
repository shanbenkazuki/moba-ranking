import sqlite3

from bs4 import BeautifulSoup

from copy_text import get_aside_hero_html_fandom
from datetime import datetime

html = get_aside_hero_html_fandom()

soup = BeautifulSoup(html, 'html.parser')

# Arlottを取得するための要素を探す
hero_name_en_element = soup.find('h2', class_='pi-item pi-item-spacing pi-title pi-secondary-background')
print(hero_name_en_element)

# Arlottのテキストを取得する
hero_name_en = hero_name_en_element.br.previous_sibling.strip()
print(hero_name_en)

conn = sqlite3.connect('moba_database.sqlite3')
c = conn.cursor()
c.execute('SELECT name_jp FROM mlbb_hero_info WHERE name_en = ?', (hero_name_en,))
result = c.fetchone()
if result:
    hero_name_ja = result[0]
else:
    print(f"No name_ja found for name_en: {hero_name_en}")
    hero_name_en = ''
conn.close()

print(hero_name_ja)

# 全てのdiv要素を取得
div_elements = soup.find_all('div', class_='pi-data-value pi-font')

# ２つ目のdiv要素を取得 (インデックスは0から始まるため、2つ目の要素はインデックス1となります)
second_div_element = div_elements[1]

# そのdiv要素内のaタグのテキストを取得
role_texts = [a.text for a in second_div_element.find_all('a')]
print(role_texts)

roles_text_ja = []
roles_image = []
role_text_ja = ''

# role_textsの要素を１つずつ取り出し、日本語にする
for role_text in role_texts:
    if role_text == "Fighter":
        roles_text_ja.append("ファイター")
    elif role_text == "Assassin":
        roles_text_ja.append("アサシン")
    elif role_text == "Mage":
        roles_text_ja.append("メイジ")
    elif role_text == "Marksman":
        roles_text_ja.append("ハンター")
    elif role_text == "Support":
        roles_text_ja.append("サポート")
    elif role_text == "Tank":
        roles_text_ja.append("タンク")

for role_text in role_texts:
    if role_text == "Fighter":
        roles_image.append('<img class="wp-image-1222" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/fighter.png" alt="">')
    elif role_text == "Assassin":
        roles_image.append('<img class="wp-image-1509" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/assassin.png" alt="">')
    elif role_text == "Mage":
        roles_image.append('<img class="wp-image-1542" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/mage.png" alt="">')
    elif role_text == "Marksman":
        roles_image.append('<img class="wp-image-1608" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/marksman.png" alt="">')
    elif role_text == "Support":
        roles_image.append('<img class="wp-image-1534" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/support.png" alt="">')
    elif role_text == "Tank":
        roles_image.append('<img class="wp-image-1563" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/tank.png" alt="">')

# roles_text_jaリストの要素を"/"で結合
role_text_ja = "/".join(roles_text_ja)

print(role_text_ja)

role_image_url = "".join(roles_image)

print(role_image_url)

# tableの中の2番目のtd要素内のaタグを探す
# physical_element = soup.select_one('aside:nth-child(4) > div:nth-child(9) > div > a')
# print(physical_element)

# # aタグのテキストを取得する
# damage_type = physical_element.text if physical_element else None
damage_type = soup.select_one('div[data-source="dmg_type"]').select_one('div.pi-data-value').get_text().strip()

print(damage_type)

damage_type_ja = ''

# damage_typeを日本語にする
if damage_type == "Physical":
    damage_type_ja = "物理"
elif damage_type == "Magic":
    damage_type_ja = "魔法"

print(damage_type_ja)

# "Lane Recc."に対応するdiv要素の次のdiv要素内のaタグを探す
lane_element = soup.select_one('h3.pi-data-label:-soup-contains("Lane Recc.") + div a')

print(lane_element)

if lane_element:
    lane_text = lane_element.text.strip()
else:
    # aタグが見つからなかった場合、"Lane Recc."に対応するdiv要素の次のdiv要素のテキストを取得する
    lane_element_div = soup.select_one('h3.pi-data-label:-soup-contains("Lane Recc.") + div.pi-data-value')
    lane_text = lane_element_div.text.strip() if lane_element_div else None

if lane_text:
    lane_text = lane_text.split()[0]  # "EXP Lane"をスペースで分割し、最初の要素"EXP"を取得する

print(lane_text)

lane_image = ''

if lane_text == "EXP":
    lane_image = '<img class="wp-image-1477" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/EXP.jpeg" alt="">'
elif lane_text == "GOLD":
    lane_image = '<img class="wp-image-1483" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/GOLD.jpeg" alt="">'
elif lane_text == "Roam":
    lane_image = '<img class="wp-image-1484" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/Roam.jpeg" alt="">'
elif lane_text == "Mid":
    lane_image = '<img class="wp-image-1485" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/Mid.jpeg" alt="">'
elif lane_text == "Jungle":
    lane_image = '<img class="wp-image-1482" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/jungle.jpeg" alt="">'
elif lane_text == "Jungling":
    lane_image = '<img class="wp-image-1482" style="width: 50px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/jungle.jpeg" alt="">'

print(lane_image)

# "Price"セクションの最初のspan要素の隣のテキストを取得する
price_element = soup.select_one('h3.pi-data-label:-soup-contains("Price") + div span span + span')

# span要素のテキストを取得する
price_text = price_element.text.strip() if price_element else None
print(price_text)

# "Price"セクション内の`or`の後にあるspan要素を取得する
diamond_element = soup.select_one('h3.pi-data-label:-soup-contains("Price") + div span.inline-image.label-after:nth-of-type(2) span + span')

# span要素のテキストを取得する
diamond_text = diamond_element.text.strip() if diamond_element else None
print(diamond_text)

# "Release date"セクションのテキストを取得する
release_date_element = soup.select_one('h3.pi-data-label:-soup-contains("Release date") + div.pi-data-value')

# div要素のテキストを取得する
release_date_text = release_date_element.text.strip() if release_date_element else None

# 日付の形式を確認して変更する
try:
    # %d %B %Y の形式の場合
    release_date = datetime.strptime(release_date_text, '%d %B %Y').strftime('%Y-%m-%d')
except ValueError:
    try:
        # %Y の形式の場合
        release_date = datetime.strptime(release_date_text, '%Y').strftime('%Y')
    except ValueError:
        release_date = None

print(release_date)

# "Specialty"セクションのaタグのテキストを全て取得する
specialty_elements = soup.select('h3.pi-data-label:-soup-contains("Specialty") + div.pi-data-value a')

# aタグのテキストをリストに格納する
specialty_texts = [element.text.strip() for element in specialty_elements]
specialty_texts_ja = []

for specialty_text in specialty_texts:
    if specialty_text == "Charge":
        specialty_texts_ja.append("アサルト")
    elif specialty_text == "Burst":
        specialty_texts_ja.append("爆発力")
    elif specialty_text == "Push":
        specialty_texts_ja.append("前進")
    elif specialty_text == "Damage":
        specialty_texts_ja.append("ダメージ")
    elif specialty_text == "Initiator":
        specialty_texts_ja.append("先手")
    elif specialty_text == "Crowd Control":
        specialty_texts_ja.append("妨害")
    elif specialty_text == "Chase":
        specialty_texts_ja.append("チェイス")
    elif specialty_text == "Control":
        specialty_texts_ja.append("コントロール")
    elif specialty_text == "Regen":
        specialty_texts_ja.append("回復")
    elif specialty_text == "Reap":
        specialty_texts_ja.append("追撃")
    elif specialty_text == "Guard":
        specialty_texts_ja.append("ガード")
    elif specialty_text == "Magic Damage":
        specialty_texts_ja.append("魔法ダメージ")
    elif specialty_text == "Poak":
        specialty_texts_ja.append("ポーク")

# 日本語に変換する

# テキストを指定した形式に変更する
specialty_hero = "/".join(specialty_texts_ja)
print(specialty_hero)

hero_info_html = f"""
<!-- wp:table {{"className":"is-style-regular is-all-centered"}} -->
<figure class="wp-block-table is-style-regular is-all-centered">
  <table>
    <tbody>
      <tr>
        <td colspan="2"><strong><span class="swl-cell-bg has-swl-main-thin-background-color" data-text-color="black"
              aria-hidden="true">&nbsp;</span>{hero_name_ja}（{hero_name_en}）</strong></td>
      </tr>
      <tr>
        <td colspan="2">image</td>
      </tr>
      <tr>
        <td><strong><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
              aria-hidden="true">&nbsp;</span>ロール</strong></td>
        <td>{role_image_url}<br>{role_text_ja}</td>
      </tr>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>リリース日</strong></td>
        <td>{release_date}</td>
      </tr>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>役割</strong></td>
        <td>{specialty_hero}</td>
      </tr>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>ダメージタイプ</strong></td>
        <td>{damage_type_ja}</td>
      </tr>
      <tr>
        <td><strong><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
              aria-hidden="true">&nbsp;</span>価格</strong></td>
        <td>{price_text}<img class="wp-image-4064" style="width: 20px;"
            src="https://shanbenzzz.com/wp-content/uploads/2023/10/Battle_Points.webp" alt="">or {diamond_text}<img
            class="wp-image-4065" style="width: 20px;"
            src="https://shanbenzzz.com/wp-content/uploads/2023/10/Ticket.webp" alt=""><img class="wp-image-4246"
            style="width: 20px;" src="https://shanbenzzz.com/wp-content/uploads/2022/05/Diamond.webp" alt=""></td>
      </tr>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>おすすめポジション</strong></td>
        <td>{lane_image}<br>{lane_text}レーン</td>
      </tr>
      <tr>
        <td><strong><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
              aria-hidden="true">&nbsp;</span>おすすめバトルスキル</strong></td>
        <td>image<br>XXXX</td>
      </tr>
    </tbody>
  </table>
</figure>
<!-- /wp:table -->
"""

# ファイルに書き出す
with open("hero_info.html", "w", encoding="utf-8") as f:
    f.write(hero_info_html)
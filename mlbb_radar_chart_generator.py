import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib

from bs4 import BeautifulSoup
from copy_text import get_hero_performance_txt

hero_performance_html = get_hero_performance_txt()

soup = BeautifulSoup(hero_performance_html, 'html.parser')

def get_width_from_label(label_text):
    label = soup.find('label', string=label_text)
    div_value = label.find_next_sibling('div').find('div', class_='value')
    style = div_value['style']
    width_value = [s.split(':')[1].strip() for s in style.split(';') if 'width' in s][0].replace('%', '')
    return width_value

def convert_width_to_score(percentage):
    percentage = int(percentage)
    if percentage <= 10:
        return 0.5
    elif percentage <= 20:
        return 1.0
    elif percentage <= 30:
        return 1.5
    elif percentage <= 40:
        return 2.0
    elif percentage <= 50:
        return 2.5
    elif percentage <= 60:
        return 3.0
    elif percentage <= 70:
        return 3.5
    elif percentage <= 80:
        return 4.0
    elif percentage <= 90:
        return 4.5
    else:  # percentage <= 100
        return 5.0


durability = convert_width_to_score(get_width_from_label('Durability'))
offense = convert_width_to_score(get_width_from_label('Offense'))
ability_effects = convert_width_to_score(get_width_from_label('Ability Effects'))
difficulty = convert_width_to_score(get_width_from_label('Difficulty'))

print(ability_effects, offense, durability, difficulty)

# データの例
labels = np.array(['攻撃', '生存', '難易度', 'コントロール'])
values = np.array([offense, ability_effects, difficulty, durability])

# レーダーチャートを作るための角度を計算
angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
values = np.concatenate((values, [values[0]]))
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, color='blue', linewidth=2)
ax.fill(angles, values, color='blue', alpha=0.25)

# x軸のティックを設定
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)  # 特別なフォント設定は不要

# y軸のレンジを0から5に設定
ax.set_ylim(0, 5)

# y軸の目盛りを設定
ax.set_yticks(np.arange(0, 5.1, 0.5)) 

# 画像として保存
# plt.savefig('radar_chart.png', bbox_inches='tight', pad_inches=0.1)

# 表示
plt.show()

image = "https://shanbenzzz.com/wp-content/uploads/2023/10/Martis.png"


kaiseki_html = f"""
<!-- wp:table {{"className":"is-style-regular is-all-centered"}} -->
<figure class="wp-block-table is-style-regular is-all-centered">
  <table>
    <tbody>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>生存能力</strong></td>
        <td>[review_stars {ability_effects}/5]</td>
      </tr>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>攻撃能力</strong></td>
        <td>[review_stars {offense}/5]</td>
      </tr>
      <tr>
        <td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
            aria-hidden="true">&nbsp;</span><strong>コントロール効果</strong></td>
        <td>[review_stars {durability}/5]</td>
      </tr>
      <tr>
        <td><strong><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"
              aria-hidden="true">&nbsp;</span><strong>難易度</strong></strong></td>
        <td>[review_stars {difficulty}/5]</td>
      </tr>
      <tr>
        <td colspan="2"><img class="wp-image-4629" style="width: 500px;"
            src="{image}" alt=""></td>
      </tr>
    </tbody>
  </table>
</figure>
<!-- /wp:table -->
"""

# print(kaiseki_html)

# ファイルに書き出す
with open("hero_rader_chart.html", "w", encoding="utf-8") as f:
    f.write(kaiseki_html)
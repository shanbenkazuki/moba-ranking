import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib

from bs4 import BeautifulSoup
from copy_text import get_hero_performance_txt

hero_performance_html = get_hero_performance_txt()

soup = BeautifulSoup(hero_performance_html, 'html.parser')

def get_width_from_label(label_text):
    label = soup.find('label', text=label_text)
    div_value = label.find_next_sibling('div').find('div', class_='value')
    style = div_value['style']
    width_value = [s.split(':')[1].strip() for s in style.split(';') if 'width' in s][0].replace('%', '')
    return width_value

def convert_width_to_score(percentage):
    percentage = int(percentage)
    if percentage <= 10:
        return 1
    elif percentage <= 20:
        return 2
    elif percentage <= 30:
        return 3
    elif percentage <= 40:
        return 4
    elif percentage <= 50:
        return 5
    elif percentage <= 60:
        return 6
    elif percentage <= 70:
        return 7
    elif percentage <= 80:
        return 8
    elif percentage <= 90:
        return 9
    else:  # percentage <= 100
        return 10

durability = convert_width_to_score(get_width_from_label('Durability'))
offense = convert_width_to_score(get_width_from_label('Offense'))
ability_effects = convert_width_to_score(get_width_from_label('Ability Effects'))
difficulty = convert_width_to_score(get_width_from_label('Difficulty'))

# データの例
labels = np.array(['生存', '攻撃', 'コントロール', '難易度'])
values = np.array([durability, offense, ability_effects, difficulty])

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

# y軸のレンジを0から10に設定
ax.set_ylim(0, 10)

# y軸の目盛りを設定
ax.set_yticks(np.arange(0, 11, 1))  # 0, 1, 2, ..., 10 の目盛りを設定

# 画像として保存
# plt.savefig('radar_chart.png', bbox_inches='tight', pad_inches=0.1)

# 表示
plt.show()

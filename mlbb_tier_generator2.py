import sqlite3
import pandas as pd
from scipy.stats import zscore

# ============================
# 1. SQLiteから最新データを取得
# ============================
db_path = '/Users/yamamotokazuki/develop/moba-ranking/mlbb.db'  # DBパス

# SQLiteに接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 最新の reference_date を取得
cursor.execute("SELECT MAX(reference_date) FROM hero_stats")
latest_date = cursor.fetchone()[0]

# 最新の reference_date の行を抽出
cursor.execute("SELECT * FROM hero_stats WHERE reference_date = ?", (latest_date,))
rows = cursor.fetchall()

# カラム名を取得し、DataFrameに変換
column_names = [description[0] for description in cursor.description]
df = pd.DataFrame(rows, columns=column_names)
print(f"最新の reference_date: {latest_date} のデータ件数: {len(rows)}")

# ============================
# 2. heroesテーブルから英名→日本語名のマッピングを取得
# ============================
cursor.execute("SELECT english_name, japanese_name FROM heroes")
hero_map_rows = cursor.fetchall()
hero_name_map = {r[0]: r[1] for r in hero_map_rows}

conn.close()

# ============================
# 3. Zスコア・5段階評価の付与
# ============================
df['win_rate_z'] = zscore(df['win_rate'])
df['pick_rate_z'] = zscore(df['pick_rate'])
df['ban_rate_z'] = zscore(df['ban_rate'])

# 重み設定（例：勝率0.5、BAN率0.3、ピック率0.2）
w_win = 0.5
w_ban = 0.3
w_pick = 0.2

# 合成強さスコアの算出
df['strength_score'] = (
    w_win * df['win_rate_z'] +
    w_ban * df['ban_rate_z'] +
    w_pick * df['pick_rate_z']
)

# スコアに基づき S/A/B/C/D の5段階評価を割り当てる関数
def assign_grade(z):
    if z > 1.0:
        return 'S'
    elif z > 0.5:
        return 'A'
    elif z >= -0.5:
        return 'B'
    elif z >= -1.0:
        return 'C'
    else:
        return 'D'

df['grade'] = df['strength_score'].apply(assign_grade)

# スコアの高い順にソート
df_sorted = df.sort_values(by='strength_score', ascending=False)

# ============================
# 4. HTML生成と出力
# ============================
grades_info = {
    'S': {
        'title': 'S Tier',
        'description': 'Top-tier picks that dominate the meta'
    },
    'A': {
        'title': 'A Tier',
        'description': 'Strong heroes that consistently perform well'
    },
    'B': {
        'title': 'B Tier',
        'description': 'Balanced heroes with situational strengths'
    },
    'C': {
        'title': 'C Tier',
        'description': 'Viable picks that may need team coordination'
    },
    'D': {
        'title': 'D Tier',
        'description': 'Underperforming or niche picks'
    }
}

# HTMLのひな型（簡易的なCSS付き）
html_head = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Hero Tier List</title>
<style>
body {
  background-color: #2b2b2b;
  color: #ffffff;
  font-family: Arial, sans-serif;
  margin: 20px;
}
h1 {
  color: #ffd700;
}
.tier-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #444;
  border-radius: 8px;
  background-color: #333;
}
.tier-title {
  font-size: 1.5em;
  margin-bottom: 5px;
  color: #ffd700;
}
.tier-description {
  font-size: 0.9em;
  margin-bottom: 15px;
  color: #ccc;
}
.hero-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.hero {
  width: 80px;
  text-align: center;
}
.hero img {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  border: 1px solid #555;
  object-fit: cover;
  margin-bottom: 5px;
}
.hero-name {
  font-size: 0.8em;
  color: #fff;
  white-space: nowrap;
}
</style>
</head>
<body>
<h1>MLBB Hero Tier List</h1>
"""

html_tail = """
</body>
</html>
"""

html_body = ""
for grade in ['S', 'A', 'B', 'C', 'D']:
    # そのグレードのヒーローだけ抽出
    subset = df_sorted[df_sorted['grade'] == grade]
    if len(subset) == 0:
        continue

    info = grades_info[grade]
    html_body += f'<div class="tier-section">\n'
    html_body += f'  <div class="tier-title">{info["title"]}</div>\n'
    html_body += f'  <div class="tier-description">{info["description"]}</div>\n'
    html_body += f'  <div class="hero-list">\n'

    # ヒーローごとに表示用HTMLを作成
    for _, row in subset.iterrows():
        english_name = row['hero_name']  # 英名
        japanese_name = hero_name_map.get(english_name, english_name)
        # 例として "hero_images/英名.webp" のパスを使用
        hero_img_path = f"hero_images/{english_name}.webp"

        html_body += f'    <div class="hero">\n'
        html_body += f'      <img src="{hero_img_path}" alt="{japanese_name}">\n'
        html_body += f'      <div class="hero-name">{japanese_name}</div>\n'
        html_body += f'    </div>\n'

    html_body += f'  </div>\n</div>\n'

final_html = html_head + html_body + html_tail

# HTMLファイルに出力
with open('hero_tier_list.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("HTMLファイル 'hero_tier_list.html' を出力しました。")

import sqlite3
import pandas as pd
from scipy.stats import zscore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# ============================
# 1. SQLiteから最新データを取得
# ============================
db_path = '/Users/yamamotokazuki/develop/moba-ranking/mlbb.db'  # DBパス

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT MAX(reference_date) FROM hero_stats")
latest_date = cursor.fetchone()[0]

cursor.execute("SELECT * FROM hero_stats WHERE reference_date = ?", (latest_date,))
rows = cursor.fetchall()

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

w_win = 0.5
w_ban = 0.3
w_pick = 0.2

df['strength_score'] = (
    w_win * df['win_rate_z'] +
    w_ban * df['ban_rate_z'] +
    w_pick * df['pick_rate_z']
)

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
df_sorted = df.sort_values(by='strength_score', ascending=False)

# ============================
# 4. HTML生成と出力
# ============================
grades_info = {
    'S': {'title': 'S Tier', 'description': 'Top-tier picks that dominate the meta'},
    'A': {'title': 'A Tier', 'description': 'Strong heroes that consistently perform well'},
    'B': {'title': 'B Tier', 'description': 'Balanced heroes with situational strengths'},
    'C': {'title': 'C Tier', 'description': 'Viable picks that may need team coordination'},
    'D': {'title': 'D Tier', 'description': 'Underperforming or niche picks'}
}

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
    subset = df_sorted[df_sorted['grade'] == grade]
    if len(subset) == 0:
        continue

    info = grades_info[grade]
    html_body += f'<div class="tier-section">\n'
    html_body += f'  <div class="tier-title">{info["title"]}</div>\n'
    html_body += f'  <div class="tier-description">{info["description"]}</div>\n'
    html_body += f'  <div class="hero-list">\n'

    for _, row in subset.iterrows():
        english_name = row['hero_name']
        japanese_name = hero_name_map.get(english_name, english_name)
        hero_img_path = f"hero_images/{english_name}.webp"

        html_body += f'    <div class="hero">\n'
        html_body += f'      <img src="{hero_img_path}" alt="{japanese_name}">\n'
        html_body += f'      <div class="hero-name">{japanese_name}</div>\n'
        html_body += f'    </div>\n'

    html_body += f'  </div>\n</div>\n'

final_html = html_head + html_body + html_tail

html_file = 'hero_tier_list.html'
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"HTMLファイル '{html_file}' を出力しました。")

# ============================
# 5. SeleniumでHTMLを開いてスクリーンショットを撮る (ChromeDriverManager利用)
# ============================
chrome_options = Options()
chrome_options.add_argument("--window-size=1080,2420")
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ローカルHTMLファイルを開く (file:// URL形式)
html_file_url = "file:///Users/yamamotokazuki/develop/moba-ranking/hero_tier_list.html"
driver.get(html_file_url)

# ページの読み込み待ち（必要に応じて調整）
time.sleep(2)

screenshot_path = "hero_tier_list_screenshot.png"
driver.save_screenshot(screenshot_path)
print(f"スクリーンショット '{screenshot_path}' を保存しました。")

driver.quit()

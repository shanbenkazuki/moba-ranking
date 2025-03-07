import os
import logging
import sqlite3
import pandas as pd
from scipy.stats import zscore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import tweepy

# ----------------------------
# 基本ディレクトリの設定
# ----------------------------
base_dir = "/Users/yamamotokazuki/develop/moba-ranking"

# ----------------------------
# ログ設定（絶対パス）
# ----------------------------
log_dir = os.path.join(base_dir, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8")]
)
logger = logging.getLogger(__name__)

# ----------------------------
# 1. SQLiteから最新データを取得
# ----------------------------
db_path = os.path.join(base_dir, "mlbb.db")  # 絶対パスに変更
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT MAX(reference_date) FROM hero_stats")
latest_date = cursor.fetchone()[0]

cursor.execute("SELECT * FROM hero_stats WHERE reference_date = ?", (latest_date,))
rows = cursor.fetchall()

column_names = [description[0] for description in cursor.description]
df = pd.DataFrame(rows, columns=column_names)
logger.info(f"最新の reference_date: {latest_date} のデータ件数: {len(rows)}")

# ----------------------------
# 2. heroesテーブルから英名→日本語名のマッピングを取得
# ----------------------------
cursor.execute("SELECT english_name, japanese_name FROM heroes")
hero_map_rows = cursor.fetchall()
hero_name_map = {r[0]: r[1] for r in hero_map_rows}

conn.close()

# ----------------------------
# 3. Zスコア・5段階評価の付与
# ----------------------------
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

# ----------------------------
# 4. HTML生成と出力 (description省略)
# ----------------------------
grades_info = {
    'S': {'title': 'S Tier'},
    'A': {'title': 'A Tier'},
    'B': {'title': 'B Tier'},
    'C': {'title': 'C Tier'},
    'D': {'title': 'D Tier'}
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
# hero_imagesの絶対パス
hero_images_dir = os.path.join(base_dir, "hero_images")
for grade in ['S', 'A', 'B', 'C', 'D']:
    subset = df_sorted[df_sorted['grade'] == grade]
    if len(subset) == 0:
        continue

    info = grades_info[grade]
    html_body += f'<div class="tier-section">\n'
    html_body += f'  <div class="tier-title">{info["title"]}</div>\n'
    html_body += f'  <div class="hero-list">\n'

    for _, row in subset.iterrows():
        english_name = row['hero_name']
        japanese_name = hero_name_map.get(english_name, english_name)
        # 絶対パスにして file:// プレフィックスを追加
        hero_img_abs = os.path.join(hero_images_dir, f"{english_name}.webp")
        hero_img_path = "file://" + hero_img_abs

        html_body += f'    <div class="hero">\n'
        html_body += f'      <img src="{hero_img_path}" alt="{japanese_name}">\n'
        html_body += f'      <div class="hero-name">{japanese_name}</div>\n'
        html_body += f'    </div>\n'

    html_body += f'  </div>\n</div>\n'

final_html = html_head + html_body + html_tail

# HTML出力先の絶対パス
output_dir = os.path.join(base_dir, "output")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
html_file = os.path.join(output_dir, "hero_tier_list.html")
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(final_html)

logger.info(f"HTMLファイル '{html_file}' を出力しました。")

# ----------------------------
# 5. SeleniumでHTMLを開いてスクリーンショットを撮る
# ----------------------------
chrome_options = Options()
chrome_options.add_argument("--window-size=1080,2220")
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# HTMLファイルの絶対パスを file:// プレフィックス付きで指定
html_file_url = "file://" + html_file
driver.get(html_file_url)

time.sleep(2)

screenshot_path = os.path.join(output_dir, "hero_tier_list_screenshot.png")
driver.save_screenshot(screenshot_path)
logger.info(f"スクリーンショット '{screenshot_path}' を保存しました。")

driver.quit()

# ----------------------------
# 6. Tweepyでスクリーンショットを添付してXに投稿
# ----------------------------
# Twitter APIの認証情報を環境変数から取得
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')  # v2用のトークン

# OAuth1認証を設定（v1.1用のAPIでメディアアップロードを実施）
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# Tweepy v2クライアントの作成
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

tweet_text = "MLBB Hero Tier List - 最新のヒーローデータをチェック！"

# 画像をアップロードして、media_idを取得（v1.1のAPIを使用）
media = api_v1.media_upload(screenshot_path)

# ツイートを投稿（v2のAPIを使用）
client.create_tweet(text=tweet_text, media_ids=[media.media_id_string])

logger.info("ツイートが投稿されました。")

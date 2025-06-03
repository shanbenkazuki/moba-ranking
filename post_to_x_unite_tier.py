import asyncio
import sqlite3
import os
import math
from pathlib import Path
from datetime import datetime
import tweepy
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# ヘルパー関数
def mean(arr):
    if not arr:
        return 0
    return sum(arr) / len(arr)

def std_dev(arr, arr_mean):
    if not arr or len(arr) <= 1:
        return 1  # 標準偏差が0になることを避ける
    variance = sum((val - arr_mean) ** 2 for val in arr) / len(arr)
    return math.sqrt(variance) if variance > 0 else 1

def assign_grade(score):
    if score > 1.0:
        return 'S'
    elif score > 0.5:
        return 'A'
    elif score >= -0.5:
        return 'B'
    elif score >= -1.0:
        return 'C'
    else:
        return 'D'

def run_query(db, sql, params=None):
    if params is None:
        params = []
    cursor = db.cursor()
    cursor.execute(sql, params)
    return cursor.fetchall(), cursor.description

def run_execute(db, sql, params=None):
    if params is None:
        params = []
    cursor = db.cursor()
    cursor.execute(sql, params)
    db.commit()

async def main():
    try:
        # 基本ディレクトリ設定
        base_dir = "/Users/yamamotokazuki/develop/moba-ranking"
        output_dir = Path(base_dir) / "output"
        output_dir.mkdir(exist_ok=True)
        pokemon_images_dir = Path(base_dir) / "pokemon_images"

        # SQLiteからデータ取得 (moba_log.db)
        db_path = Path(base_dir) / "data" / "moba_log.db"
        db = sqlite3.connect(db_path)

        # Uniteのgame_idを取得
        unite_game_rows, _ = run_query(db, "SELECT id FROM games WHERE game_code = 'unite'")
        if not unite_game_rows:
            print("エラー: Uniteのゲーム情報が見つかりません")
            return
        unite_game_id = unite_game_rows[0][0]
        print(f"Unite game_id: {unite_game_id}")

        # 最新の reference_date を取得
        latest_date_rows, _ = run_query(db, "SELECT MAX(reference_date) as latest_date FROM unite_stats")
        latest_date = latest_date_rows[0][0]

        # 最新日付のunite_statsを取得（charactersテーブルとJOIN）
        pokemon_stats, columns_info = run_query(db, """
            SELECT 
                us.id,
                us.character_id,
                c.english_name as pokemon_name,
                c.japanese_name,
                us.win_rate,
                us.pick_rate,
                us.ban_rate,
                us.reference_date,
                us.patch_id
            FROM unite_stats us
            JOIN characters c ON us.character_id = c.id
            WHERE us.reference_date = ? AND c.game_id = ?
        """, [latest_date, unite_game_id])
        print(f"最新の reference_date ({latest_date}) のデータ件数: {len(pokemon_stats)}")

        # カラム名を取得してディクショナリ形式に変換
        columns = [desc[0] for desc in columns_info]
        pokemon_stats_dict = []
        for row in pokemon_stats:
            row_dict = dict(zip(columns, row))
            pokemon_stats_dict.append(row_dict)

        # デバッグ: NULL値チェック
        print("デバッグ: 最初の数件のデータをチェック")
        for i, row in enumerate(pokemon_stats_dict[:5]):
            print(f"  {i+1}: {row['pokemon_name']} - win_rate: {row['win_rate']}, pick_rate: {row['pick_rate']}, ban_rate: {row['ban_rate']}")
        
        # NULL値を含む行をチェック
        null_rows = []
        for row in pokemon_stats_dict:
            if row['win_rate'] is None or row['pick_rate'] is None or row['ban_rate'] is None:
                null_rows.append(row['pokemon_name'])
        
        if null_rows:
            print(f"警告: NULL値を含むポケモン: {null_rows}")
            # NULL値を0で置換またはスキップする処理を追加
            pokemon_stats_dict = [row for row in pokemon_stats_dict 
                                 if row['win_rate'] is not None and row['pick_rate'] is not None and row['ban_rate'] is not None]
            print(f"NULL値除去後のデータ件数: {len(pokemon_stats_dict)}")

        # 英名→日本語名のマッピング（既にJOINで取得済みなので簡素化）
        pokemon_name_map = {}
        for row in pokemon_stats_dict:
            pokemon_name_map[row['pokemon_name']] = row['japanese_name']

        # 最新パッチ情報（バージョン）の取得
        patch_rows, _ = run_query(db, "SELECT patch_number FROM patches WHERE game_id = ? ORDER BY release_date DESC LIMIT 1", [unite_game_id])
        patch_number = patch_rows[0][0] if patch_rows else "N/A"

        db.close()

        # Zスコア・強さスコア算出
        if not pokemon_stats_dict:
            print("エラー: 有効なデータが存在しません")
            return
            
        win_rates = [row['win_rate'] for row in pokemon_stats_dict]
        pick_rates = [row['pick_rate'] for row in pokemon_stats_dict]
        ban_rates = [row['ban_rate'] for row in pokemon_stats_dict]

        print(f"デバッグ: win_rates サンプル: {win_rates[:5]}")
        print(f"デバッグ: pick_rates サンプル: {pick_rates[:5]}")
        print(f"デバッグ: ban_rates サンプル: {ban_rates[:5]}")

        win_mean = mean(win_rates)
        win_std = std_dev(win_rates, win_mean)
        pick_mean = mean(pick_rates)
        pick_std = std_dev(pick_rates, pick_mean)
        ban_mean = mean(ban_rates)
        ban_std = std_dev(ban_rates, ban_mean)

        print(f"デバッグ: 平均値 - win: {win_mean}, pick: {pick_mean}, ban: {ban_mean}")
        print(f"デバッグ: 標準偏差 - win: {win_std}, pick: {pick_std}, ban: {ban_std}")

        for row in pokemon_stats_dict:
            row['win_rate_z'] = (row['win_rate'] - win_mean) / win_std
            row['pick_rate_z'] = (row['pick_rate'] - pick_mean) / pick_std
            row['ban_rate_z'] = (row['ban_rate'] - ban_mean) / ban_std
            w_win, w_ban, w_pick = 0.5, 0.3, 0.2
            row['strength_score'] = w_win * row['win_rate_z'] + w_ban * row['ban_rate_z'] + w_pick * row['pick_rate_z']
            row['grade'] = assign_grade(row['strength_score'])

        # strength_score の降順にソート
        pokemon_stats_dict.sort(key=lambda x: x['strength_score'], reverse=True)

        # デバッグ: Tier分布を確認
        tier_counts = {}
        for row in pokemon_stats_dict:
            grade = row['grade']
            tier_counts[grade] = tier_counts.get(grade, 0) + 1
        print(f"デバッグ: Tier分布 - {tier_counts}")

        # デバッグ: 最初の数件のenglish_nameを確認
        print("デバッグ: english_nameと画像ファイル名の確認")
        for i, row in enumerate(pokemon_stats_dict[:5]):
            english_name = row['pokemon_name']
            japanese_name = row['japanese_name']
            image_file_path = pokemon_images_dir / f'{english_name}.png'
            exists = image_file_path.exists()
            print(f"  {i+1}: english_name='{english_name}' -> '{english_name}.png' (存在: {exists}) -> 表示名: '{japanese_name}'")

        # HTML出力用文字列生成
        tier_descriptions = {
            'S': 'チャンピオンクラス',
            'A': 'エースクラス',
            'B': 'バランスクラス',
            'C': '状況限定クラス',
            'D': '強化必要クラス'
        }

        html_head = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ポケモンユナイト ティアリスト</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
  <style>
    /* アニメーション削除 */
    
    :root {{
      /* カラフルでポップなカラーパレット */
      --primary-color: #FF5F6D;
      --secondary-color: #3e4edd;
      --bg-color: #FAFAFA;
      --accent-color: #FFD700;
      --text-color: #333;
      --text-light: #666;
      --s-tier: linear-gradient(135deg, #FF9100, #F9455D);
      --a-tier: linear-gradient(135deg, #FDA7DF, #9C27B0);
      --b-tier: linear-gradient(135deg, #5EFCE8, #736EFE);
      --c-tier: linear-gradient(135deg, #A8FF78, #78FFD6);
      --d-tier: linear-gradient(135deg, #BDBBBE, #9D9EA3);
    }}
    
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Noto Sans JP', sans-serif;
    }}
    
    body {{
      background-color: var(--bg-color);
      color: var(--text-color);
      background-image: 
        radial-gradient(circle at 10% 20%, rgba(255, 200, 200, 0.2) 0%, transparent 20%),
        radial-gradient(circle at 90% 30%, rgba(200, 200, 255, 0.2) 0%, transparent 25%),
        radial-gradient(circle at 50% 60%, rgba(255, 255, 200, 0.2) 0%, transparent 30%);
      background-attachment: fixed;
    }}
    
    .container {{
      max-width: 1920px;
      margin: 0 auto;
      padding: 20px;
    }}
    
    .header {{
      text-align: center;
      padding: 40px 20px;
      margin-bottom: 30px;
      position: relative;
      overflow: hidden;
      border-radius: 20px;
      background: white;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }}
    
    .header::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 10px;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }}
    
    .header h1 {{
      font-size: 3.8em;
      font-weight: 900;
      margin-bottom: 15px;
      color: var(--text-color);
      letter-spacing: 2px;
      position: relative;
      display: inline-block;
    }}
    
    .header h1::after {{
      content: '';
      position: absolute;
      bottom: -5px;
      left: 0;
      width: 100%;
      height: 5px;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
      border-radius: 5px;
    }}
    
    .header h1 span {{
      color: var(--primary-color);
      position: relative;
    }}
    
    .header h1 span::before {{
      content: '★';
      position: absolute;
      top: -20px;
      right: -15px;
      font-size: 0.5em;
      color: var(--accent-color);
    }}
    
    .version-info {{
      font-size: 1.2em;
      font-weight: 600;
      color: var(--text-color);
      margin-top: 15px;
      display: flex;
      justify-content: center;
      gap: 30px;
      flex-wrap: wrap;
    }}
    
    .version-info span {{
      display: inline-block;
      background: linear-gradient(90deg, var(--secondary-color), var(--primary-color));
      color: white;
      padding: 8px 20px;
      border-radius: 25px;
      box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
    }}
    
    .tier-section {{
      margin-bottom: 40px;
      padding: 30px;
      border-radius: 20px;
      background-color: white;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      position: relative;
      overflow: hidden;
    }}
    
    /* 装飾要素削除 */
    
    .tier-section.s-tier {{ border-top: 10px solid transparent; border-image: var(--s-tier) 1; }}
    .tier-section.a-tier {{ border-top: 10px solid transparent; border-image: var(--a-tier) 1; }}
    .tier-section.b-tier {{ border-top: 10px solid transparent; border-image: var(--b-tier) 1; }}
    .tier-section.c-tier {{ border-top: 10px solid transparent; border-image: var(--c-tier) 1; }}
    .tier-section.d-tier {{ border-top: 10px solid transparent; border-image: var(--d-tier) 1; }}
    
    .tier-badge {{
      position: absolute;
      top: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.2em;
      font-weight: 900;
      color: white;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
      z-index: 2;
    }}
    
    .tier-badge::after {{
      content: '';
      position: absolute;
      top: -3px;
      left: -3px;
      right: -3px;
      bottom: -3px;
      border-radius: 50%;
      background: white;
      z-index: -1;
    }}
    
    .s-tier .tier-badge {{ background: var(--s-tier); }}
    .a-tier .tier-badge {{ background: var(--a-tier); }}
    .b-tier .tier-badge {{ background: var(--b-tier); }}
    .c-tier .tier-badge {{ background: var(--c-tier); }}
    .d-tier .tier-badge {{ background: var(--d-tier); }}
    
    .tier-title {{
      font-size: 2.2em;
      margin-bottom: 25px;
      color: var(--text-color);
      font-weight: 900;
      display: flex;
      align-items: center;
      position: relative;
      padding-left: 20px;
      padding-bottom: 10px;
    }}
    
    .tier-title::before {{
      content: '';
      position: absolute;
      left: 0;
      bottom: 0;
      width: 100%;
      height: 2px;
      background: rgba(0, 0, 0, 0.1);
    }}
    
    .s-tier .tier-title::before {{ background: var(--s-tier); opacity: 0.3; }}
    .a-tier .tier-title::before {{ background: var(--a-tier); opacity: 0.3; }}
    .b-tier .tier-title::before {{ background: var(--b-tier); opacity: 0.3; }}
    .c-tier .tier-title::before {{ background: var(--c-tier); opacity: 0.3; }}
    .d-tier .tier-title::before {{ background: var(--d-tier); opacity: 0.3; }}
    
    .hero-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 25px;
      justify-content: flex-start;
    }}
    
    .hero {{
      width: 120px;
      text-align: center;
      position: relative;
    }}
    
    .hero-card {{
      background: white;
      border-radius: 18px;
      padding: 10px;
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
    }}
    
    .hero-img-container {{
      position: relative;
      width: 90px;
      height: 90px;
      margin: 0 auto;
      border-radius: 50%;
      overflow: hidden;
      border: 4px solid rgba(255, 255, 255, 0.7);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
      background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    }}
    
    .s-tier .hero-img-container {{ border-color: rgba(255, 145, 0, 0.7); box-shadow: 0 5px 15px rgba(255, 145, 0, 0.3); }}
    .a-tier .hero-img-container {{ border-color: rgba(253, 167, 223, 0.7); box-shadow: 0 5px 15px rgba(253, 167, 223, 0.3); }}
    .b-tier .hero-img-container {{ border-color: rgba(94, 252, 232, 0.7); box-shadow: 0 5px 15px rgba(94, 252, 232, 0.3); }}
    .c-tier .hero-img-container {{ border-color: rgba(168, 255, 120, 0.7); box-shadow: 0 5px 15px rgba(168, 255, 120, 0.3); }}
    .d-tier .hero-img-container {{ border-color: rgba(189, 187, 190, 0.7); box-shadow: 0 5px 15px rgba(189, 187, 190, 0.3); }}
    
    .hero img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    
    @media (max-width: 768px) {{
      .header h1 {{ font-size: 2.5em; }}
      .hero-list {{ justify-content: center; }}
      .tier-section {{ padding: 20px 15px; }}
      .tier-badge {{ width: 50px; height: 50px; font-size: 1.8em; }}
      .tier-title {{ font-size: 1.8em; }}
      .version-info {{ flex-direction: column; gap: 10px; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>ポケモンユナイト <span>ティアリスト</span></h1>
      <div class="version-info">
        <span>バージョン {patch_number}</span>
        <span>更新日 {latest_date}</span>
      </div>
    </div>
"""

        html_tail = f"""  </div>
</body>
</html>
"""

        html_body = ""
        grades = ['S', 'A', 'B', 'C', 'D']
        for grade in grades:
            filtered = [row for row in pokemon_stats_dict if row['grade'] == grade]
            if not filtered:
                continue
            description = tier_descriptions.get(grade, "")
            html_body += f"    <!-- {grade} Tier -->\n"
            html_body += f"    <div class=\"tier-section {grade.lower()}-tier\">\n"
            html_body += f"      <div class=\"tier-badge\">{grade}</div>\n"
            html_body += f"      <div class=\"tier-title\">{grade} Tier</div>\n"
            html_body += f"      <div class=\"hero-list\">\n"
            for row in filtered:
                english_name = row['pokemon_name']
                japanese_name = row['japanese_name'] if row['japanese_name'] else english_name
                win_rate = row['win_rate']
                
                # 画像ファイル名の変換（スペースをハイフンに、特殊文字を処理）
                image_file_name = english_name
                image_file_path = pokemon_images_dir / f'{image_file_name}.png'
                pokemon_img_path = f"file://{image_file_path}"
                
                # 画像ファイルの存在確認
                if not image_file_path.exists():
                    print(f"警告: 画像ファイルが見つかりません: {image_file_path}")
                
                html_body += f"        <div class=\"hero\">\n"
                html_body += f"          <div class=\"hero-card\">\n"
                html_body += f"            <div class=\"hero-img-container\">\n"
                html_body += f"              <img src=\"{pokemon_img_path}\" alt=\"{japanese_name}\">\n"
                html_body += f"              <div class=\"stats-overlay\">勝率: {win_rate:.1f}%</div>\n"
                html_body += f"            </div>\n"
                html_body += f"          </div>\n"
                html_body += f"        </div>\n"
            html_body += f"      </div>\n"
            html_body += f"    </div>\n"

        final_html = html_head + html_body + html_tail
        html_file_path = output_dir / "pokemon_tier_list.html"
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        print(f"HTMLファイルが {html_file_path} に出力されました。")

        # Playwrightでスクリーンショット撮影
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            file_url = f"file://{html_file_path}"
            await page.goto(file_url, wait_until='networkidle')
            await page.wait_for_selector('.header')
            await page.wait_for_selector('.container')

            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            screenshot_path = output_dir / f"pokemon_tier_list_{timestamp}.png"

            # ページ全体のスクリーンショットを撮影
            await page.screenshot(
                path=screenshot_path,
                full_page=True
            )
            print(f"スクリーンショットが {screenshot_path} に保存されました。")

            await browser.close()

        # tweepyでスクリーンショットを添付してXに投稿
        api_key = os.getenv("API_KEY")
        api_secret_key = os.getenv("API_SECRET_KEY")
        access_token = os.getenv("ACCESS_TOKEN")
        access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
        bearer_token = os.getenv("BEARER_TOKEN")

        # Tweepy v2 API client
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret_key,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

        # Tweepy v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret_key, access_token, access_token_secret
        )
        api = tweepy.API(auth)

        tweet_text = f"""今週のポケモンユナイトのTier表を公開します。

バージョン：{patch_number}

#ポケモンユナイト #PokemonUnite #ユナイト"""

        tweet_success = False
        tweet_error = ""
        try:
            # メディアをアップロード
            media = api.media_upload(str(screenshot_path))
            media_id = media.media_id

            # ツイートを投稿
            # client.create_tweet(text=tweet_text, media_ids=[media_id])
            print("ツイートが投稿されました。")
            tweet_success = True
        except Exception as error:
            print(f"ツイート投稿中にエラーが発生しました: {error}")
            tweet_error = str(error)

        # ツイート投稿の結果を moba_log.db の x_post_logs に保存
        log_db_path = Path(base_dir) / "data" / "moba_log.db"
        log_db = sqlite3.connect(log_db_path)
        
        # 日本時間に基づく YYYY-MM-DD 形式のpost_dateを生成
        now = datetime.now()
        post_date = now.strftime("%Y-%m-%d")
        
        run_execute(log_db, 
                   "INSERT INTO x_post_logs (game_id, post_status, error_message, post_date) VALUES (?, ?, ?, ?)",
                   [unite_game_id, 1 if tweet_success else 0, "" if tweet_success else tweet_error, post_date])
        log_db.close()

    except Exception as err:
        print(f"エラー: {err}")

if __name__ == "__main__":
    asyncio.run(main())

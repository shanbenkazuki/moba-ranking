import asyncio
import sqlite3
import os
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.async_api import async_playwright
import tweepy
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# 環境変数の読み込み
load_dotenv()

# ヘルパー関数
def mean(arr):
    return sum(arr) / len(arr) if arr else 0

def std_dev(arr, arr_mean):
    if not arr:
        return 0
    variance = sum((val - arr_mean) ** 2 for val in arr) / len(arr)
    return math.sqrt(variance)

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

def find_champion_image_path(champion_images_dir, english_name):
    """チャンピオン画像ファイルのパスを検索する関数"""
    # 試行する拡張子のリスト
    extensions = ['.webp', '.png', '.jpg', '.jpeg']
    
    for ext in extensions:
        file_path = Path(champion_images_dir) / f"{english_name}{ext}"
        if file_path.exists():
            return f"file://{file_path}"
    
    # ファイルが見つからない場合はwebpのパスを返す（フォールバック）
    return f"file://{champion_images_dir}/{english_name}.webp"

def get_jst_timestamp():
    """JSTのタイムスタンプを生成する関数"""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]

def get_jst_date():
    """JSTの日付（YYYY-MM-DD形式）を生成する関数"""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now.strftime("%Y-%m-%d")

async def main():
    try:
        # 基本ディレクトリ設定
        base_dir = "/Users/yamamotokazuki/develop/moba-ranking"
        output_dir = Path(base_dir) / "output"
        output_dir.mkdir(exist_ok=True)
        champion_images_dir = Path(base_dir) / "champion_images"

        # SQLiteからデータ取得
        db_path = Path(base_dir) / "data" / "moba_log.db"
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Wild Riftのgame_idを取得
            cursor.execute("SELECT id FROM games WHERE game_code = 'wildrift'")
            game_row = cursor.fetchone()
            if not game_row:
                raise Exception("Wild Riftのゲーム情報が見つかりません")
            game_id = game_row['id']
            
            # 対象の5つのlane
            lanes = ['上单', '打野', '中路', '下路', '辅助']
            
            # 最新の reference_date を取得
            cursor.execute("""SELECT MAX(reference_date) as latest_date 
                             FROM wildrift_stats ws 
                             JOIN characters c ON ws.character_id = c.id 
                             WHERE c.game_id = ? AND ws.lane IN (?,?,?,?,?)""", 
                          [game_id] + lanes)
            latest_date_row = cursor.fetchone()
            latest_date = latest_date_row['latest_date']
            
            # 最新日付のwildrift_statsを取得
            cursor.execute("""SELECT ws.*, c.english_name, c.japanese_name, c.chinese_name
                             FROM wildrift_stats ws 
                             JOIN characters c ON ws.character_id = c.id 
                             WHERE c.game_id = ? AND ws.reference_date = ? AND ws.lane IN (?,?,?,?,?)""", 
                          [game_id, latest_date] + lanes)
            champion_stats = [dict(row) for row in cursor.fetchall()]
            
            print(f"最新の reference_date ({latest_date}) のデータ件数: {len(champion_stats)}")
            
            # 最新パッチ情報の取得
            cursor.execute("""SELECT patch_number FROM patches 
                             WHERE game_id = ? ORDER BY release_date DESC LIMIT 1""", [game_id])
            patch_row = cursor.fetchone()
            patch_number = patch_row['patch_number'] if patch_row else "N/A"

        # Zスコア・強さスコア算出
        win_rates = [row['win_rate'] for row in champion_stats if row['win_rate'] is not None]
        pick_rates = [row['pick_rate'] for row in champion_stats if row['pick_rate'] is not None]
        ban_rates = [row['ban_rate'] for row in champion_stats if row['ban_rate'] is not None]

        win_mean = mean(win_rates)
        win_std = std_dev(win_rates, win_mean)
        pick_mean = mean(pick_rates)
        pick_std = std_dev(pick_rates, pick_mean)
        ban_mean = mean(ban_rates)
        ban_std = std_dev(ban_rates, ban_mean)

        for row in champion_stats:
            row['win_rate_z'] = (row['win_rate'] - win_mean) / win_std if win_std > 0 else 0
            row['pick_rate_z'] = (row['pick_rate'] - pick_mean) / pick_std if pick_std > 0 else 0
            row['ban_rate_z'] = (row['ban_rate'] - ban_mean) / ban_std if ban_std > 0 else 0
            
            w_win, w_ban, w_pick = 0.5, 0.3, 0.2
            row['strength_score'] = w_win * row['win_rate_z'] + w_ban * row['ban_rate_z'] + w_pick * row['pick_rate_z']
            row['grade'] = assign_grade(row['strength_score'])

        # strength_score の降順にソート
        champion_stats.sort(key=lambda x: x['strength_score'], reverse=True)

        # 各championのscoreをログ出力
        for row in champion_stats:
            english_name = row['english_name'] or row['chinese_name']
            print(f"{english_name} の score: {row['strength_score']:.3f}")

        # 中国語レーン名を日本語に変換する辞書
        lane_translation = {
            '上单': 'バロン',
            '打野': 'ジャングル',
            '中路': 'ミッド',
            '下路': 'ドラゴン',
            '辅助': 'サポート'
        }

        # テンプレート用のデータ準備
        grades = ['S', 'A', 'B', 'C', 'D']
        champions_by_grade_lane = {}
        
        # grade と lane の組み合わせでデータを整理
        for grade in grades:
            champions_by_grade_lane[grade] = {}
            for lane in lanes:
                filtered = [row for row in champion_stats if row['lane'] == lane and row['grade'] == grade]
                filtered.sort(key=lambda x: x['strength_score'], reverse=True)
                
                champion_list = []
                for row in filtered:
                    japanese_name = row['japanese_name'] or row['chinese_name']
                    english_name = row['english_name'] or row['chinese_name']
                    chinese_name = row['chinese_name']
                    champion_img_path = find_champion_image_path(champion_images_dir, chinese_name)
                    
                    champion_list.append({
                        'japanese_name': japanese_name,
                        'english_name': english_name,
                        'chinese_name': chinese_name,
                        'image_path': champion_img_path
                    })
                
                champions_by_grade_lane[grade][lane] = champion_list
                print(f"デバッグ: {grade}グレード {lane}レーン に {len(champion_list)} 体のチャンピオンを追加")

        # Jinja2テンプレートの設定
        template_dir = Path(base_dir) / "templates"
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('wildrift_tier_list.html')

        # テンプレートレンダリング用の変数
        lanes_translated = [lane_translation[lane] for lane in lanes]
        background_image_path = f"file://{base_dir}/background.jpg"

        # テンプレートレンダリング
        html_content = template.render(
            patch_number=patch_number,
            latest_date=latest_date,
            lanes_keys=lanes,  # 中国語のレーンキー（データアクセス用）
            lanes_translated=lanes_translated,  # 日本語のレーン名（表示用）
            grades=grades,
            champions_by_grade_lane=champions_by_grade_lane,
            background_image_path=background_image_path
        )

        # HTMLファイル出力
        html_file_path = output_dir / "wildrift_tier_list.html"
        html_file_path.write_text(html_content, encoding="utf-8")
        print(f"HTMLファイルが {html_file_path} に出力されました。")

        # Playwrightでスクリーンショット撮影
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1400, "height": 1080})
            file_url = f"file://{html_file_path}"
            await page.goto(file_url, wait_until='networkidle')
            await page.wait_for_selector('.composite-grid')

            timestamp = get_jst_timestamp()
            screenshot_path = output_dir / f"wild_rift_tier_{timestamp}.png"

            # ページ全体のスクリーンショットを撮影
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )
            print(f"スクリーンショットが {screenshot_path} に保存されました。")

            await browser.close()

        # tweepyでXに投稿
        api_key = os.getenv('API_KEY')
        api_secret_key = os.getenv('API_SECRET_KEY')
        access_token = os.getenv('ACCESS_TOKEN')
        access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

        tweet_text = f"""今週のワイルドリフトのTier表を公開します。

バージョン：{patch_number}

#ワイルドリフト #WildRift"""

        # ツイート投稿の結果を記録するための変数
        post_status = 0
        error_message = None
        
        try:
            # tweepy v2 API クライアントの設定
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret_key,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            # API v1.1 クライアント（メディアアップロード用）
            auth = tweepy.OAuth1UserHandler(api_key, api_secret_key, access_token, access_token_secret)
            api = tweepy.API(auth)
            
            # 画像アップロード
            # media = api.media_upload(str(screenshot_path))
            
            # # ツイート投稿
            # client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            print("ツイートが投稿されました。")
            
        except Exception as error:
            print(f"ツイート投稿中にエラーが発生しました: {error}")
            post_status = 1
            error_message = str(error)

        # moba_log.db の x_post_logs テーブルに投稿結果を保存
        post_date = get_jst_date()
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO x_post_logs (game_id, post_status, error_message, post_date) 
                             VALUES (?, ?, ?, ?)""", 
                          [game_id, post_status, error_message, post_date])
            conn.commit()
            print("x_post_logsにツイートの結果が保存されました。")

    except Exception as err:
        print(f"エラー: {err}")

if __name__ == "__main__":
    asyncio.run(main())

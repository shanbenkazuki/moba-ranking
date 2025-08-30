import os
import sqlite3
import math
from datetime import datetime
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
import tweepy
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from src.slack_webhook import send_slack_notification

# .envファイルの読み込み
load_dotenv()

# 基本ディレクトリ設定
BASE_DIR = Path("/Users/yamamotokazuki/develop/moba-ranking")

# ログディレクトリの作成
LOG_DIR = BASE_DIR / "logs" / "mlbb"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日本時間のタイムスタンプ生成
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# ログファイルのパス
LOG_FILE_PATH = LOG_DIR / f"mlbb_tier_x_poster_{get_timestamp()}.log"

# Slack Webhook URL
SLACK_WEBHOOK_URL = os.environ.get('MLBB_SLACK_WEBHOOK_URL')

if not SLACK_WEBHOOK_URL:
    raise ValueError('MLBB_SLACK_WEBHOOK_URL環境変数が設定されていません')

def log_message(message):
    """ログメッセージを出力・保存"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(message)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

def log_error(error_message):
    """エラーログを出力・保存"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ERROR: {error_message}\n"
    print(f"ERROR: {error_message}")
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

def mean(arr):
    """平均値を計算"""
    return sum(arr) / len(arr)

def std_dev(arr, arr_mean):
    """標準偏差を計算"""
    variance = sum((val - arr_mean) ** 2 for val in arr) / len(arr)
    return math.sqrt(variance)

def assign_grade(score):
    """スコアに基づいてグレードを割り当て"""
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

def run_query(db_path, sql, params=None):
    """SQLクエリを実行"""
    if params is None:
        params = []
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

async def main():
    try:
        # 出力ディレクトリの作成
        output_dir = BASE_DIR / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        hero_images_dir = BASE_DIR / "hero_images"

        # SQLiteからデータ取得
        db_path = BASE_DIR / "data" / "moba_log.db"
        
        # 最新のreference_dateを取得
        latest_date_rows = run_query(db_path, "SELECT MAX(reference_date) as latest_date FROM mlbb_stats")
        latest_date = latest_date_rows[0]["latest_date"]
        
        # 最新日付のmlbb_statsを取得（charactersテーブルとJOIN）
        hero_stats = run_query(db_path, """
            SELECT ms.*, c.english_name as hero_name 
            FROM mlbb_stats ms
            JOIN characters c ON ms.character_id = c.id
            WHERE ms.reference_date = ?
        """, [latest_date])
        
        log_message(f"最新のreference_date ({latest_date}) のデータ件数: {len(hero_stats)}")
        
        # 英名→日本語名のマッピング取得
        hero_map_rows = run_query(db_path, """
            SELECT c.english_name, c.japanese_name 
            FROM characters c
            JOIN games g ON c.game_id = g.id
            WHERE g.game_code = 'mlbb'
        """)
        
        hero_name_map = {row["english_name"]: row["japanese_name"] for row in hero_map_rows}
        
        # 最新パッチ情報の取得
        patch_rows = run_query(db_path, """
            SELECT p.patch_number 
            FROM patches p
            JOIN games g ON p.game_id = g.id
            WHERE g.game_code = 'mlbb'
            ORDER BY p.release_date DESC 
            LIMIT 1
        """)
        
        patch_number = patch_rows[0]["patch_number"] if patch_rows else "N/A"
        
        # Zスコア・強さスコア算出
        win_rates = [row["win_rate"] for row in hero_stats]
        pick_rates = [row["pick_rate"] for row in hero_stats]
        ban_rates = [row["ban_rate"] for row in hero_stats]
        
        win_mean = mean(win_rates)
        win_std = std_dev(win_rates, win_mean)
        pick_mean = mean(pick_rates)
        pick_std = std_dev(pick_rates, pick_mean)
        ban_mean = mean(ban_rates)
        ban_std = std_dev(ban_rates, ban_mean)
        
        # 各ヒーローの統計を計算
        hero_data = []
        for row in hero_stats:
            win_rate_z = (row["win_rate"] - win_mean) / win_std
            pick_rate_z = (row["pick_rate"] - pick_mean) / pick_std
            ban_rate_z = (row["ban_rate"] - ban_mean) / ban_std
            
            w_win, w_ban, w_pick = 0.5, 0.3, 0.2
            strength_score = w_win * win_rate_z + w_ban * ban_rate_z + w_pick * pick_rate_z
            grade = assign_grade(strength_score)
            
            hero_data.append({
                **dict(row),
                'win_rate_z': win_rate_z,
                'pick_rate_z': pick_rate_z,
                'ban_rate_z': ban_rate_z,
                'strength_score': strength_score,
                'grade': grade
            })
        
        # strength_scoreの降順にソート
        hero_data.sort(key=lambda x: x['strength_score'], reverse=True)
        
        # HTML生成
        tier_descriptions = {
            'S': 'Meta Definers',
            'A': 'Top Picks',
            'B': 'Balanced Heroes',
            'C': 'Situational Picks',
            'D': 'Needs Buff'
        }
        
        html_content = generate_html(hero_data, hero_name_map, hero_images_dir, patch_number, latest_date, tier_descriptions)
        
        # HTMLファイルの保存
        html_file_path = output_dir / "hero_tier_list.html"
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        log_message(f"HTMLファイルが {html_file_path} に出力されました。")
        
        # Playwrightでスクリーンショット撮影
        timestamp = get_timestamp()
        screenshot_path = output_dir / f"hero_tier_list_{timestamp}.png"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            file_url = f"file://{html_file_path.absolute()}"
            await page.goto(file_url, wait_until='networkidle')
            
            # ページ全体が読み込まれるのを待つ
            await page.wait_for_selector('.header')
            await page.wait_for_selector('.container')
            
            # ページ全体のスクリーンショットを撮影
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )
            
            await browser.close()
        
        log_message(f"スクリーンショットが {screenshot_path} に保存されました。")
        
        # Twitter APIで投稿
        tweet_post_status = 0
        tweet_error_message = None
        
        try:
            # Twitter APIの認証
            api_key = os.getenv("API_KEY")
            api_secret_key = os.getenv("API_SECRET_KEY")
            access_token = os.getenv("ACCESS_TOKEN")
            access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
            
            # Tweepy v2 API
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret_key,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            # v1.1 API（メディアアップロード用）
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret_key, access_token, access_token_secret
            )
            api = tweepy.API(auth)
            
            # ツイートテキスト
            tweet_text = f"""今週のモバイル・レジェンドのTier表を公開します。

バージョン：{patch_number}

#モバイル・レジェンド #モバレ #モバレジェ #MLBB"""
            
            # メディアアップロード
            media = api.media_upload(str(screenshot_path))
            
            # ツイート投稿
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            
            log_message("ツイートが投稿されました。")
            
        except Exception as error:
            tweet_post_status = 1
            tweet_error_message = str(error)
            log_error(f"ツイート投稿中にエラーが発生しました: {tweet_error_message}")
        
        # 投稿結果をDBに保存
        post_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # MLBBのgame_idを取得
            game_id_rows = run_query(db_path, "SELECT id FROM games WHERE game_code = 'mlbb'")
            
            if game_id_rows:
                game_id = game_id_rows[0]["id"]
                
                with sqlite3.connect(db_path) as conn:
                    conn.execute(
                        "INSERT INTO x_post_logs (game_id, post_status, error_message, post_date) VALUES (?, ?, ?, ?)",
                        [game_id, tweet_post_status == 0, tweet_error_message, post_date]
                    )
                    conn.commit()
                
                log_message("ツイート投稿の結果が x_post_logs に保存されました。")
            else:
                log_error("MLBBのgame_idが見つかりませんでした。")
                
        except Exception as error:
            log_error(f"x_post_logs への保存中にエラーが発生しました: {error}")
        
        # Slack通知を送信
        send_slack_notification_for_x_post(tweet_post_status, tweet_error_message, patch_number, latest_date)
    
    except Exception as err:
        log_error(f"エラー: {err}")
        # 予期せぬエラーの場合もSlackに通知
        send_slack_notification_for_x_post(1, str(err), "N/A", "N/A")

def generate_html(hero_data, hero_name_map, hero_images_dir, patch_number, latest_date, tier_descriptions):
    """jinja2テンプレートを使用してHTMLコンテンツを生成"""
    # テンプレート環境の設定
    template_dir = BASE_DIR / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("mlbb_tier_list.html")
    
    # グレード別にヒーローを分類
    heroes_by_grade = {}
    grades = ['S', 'A', 'B', 'C', 'D']
    
    for grade in grades:
        heroes_by_grade[grade] = []
    
    for hero in hero_data:
        grade = hero['grade']
        english_name = hero["hero_name"]
        japanese_name = hero_name_map.get(english_name, english_name)
        hero_img_path = f"file://{hero_images_dir}/{english_name}.webp"
        
        heroes_by_grade[grade].append({
            'english_name': english_name,
            'japanese_name': japanese_name,
            'image_path': hero_img_path,
            'data': hero
        })
    
    # テンプレートにデータを渡してレンダリング
    html_content = template.render(
        patch_number=patch_number,
        latest_date=latest_date,
        grades=grades,
        heroes_by_grade=heroes_by_grade,
        tier_descriptions=tier_descriptions
    )
    
    return html_content

def send_slack_notification_for_x_post(post_status, error_message, patch_number, latest_date):
    """X投稿結果をSlackに通知"""
    try:
        if post_status == 0:  # 成功
            message = f"""✅ MLBB Tierリスト X投稿完了
日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
パッチ: {patch_number}
データ更新日: {latest_date}"""
        else:  # 失敗
            message = f"""🔴 MLBB Tierリスト X投稿失敗
日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
パッチ: {patch_number}
データ更新日: {latest_date}
エラー内容: {error_message}"""
        
        success = send_slack_notification(SLACK_WEBHOOK_URL, message)
        if success:
            log_message('Slack通知の送信に成功')
        else:
            log_error('Slack通知の送信に失敗')
            
    except Exception as e:
        log_error(f'Slack通知送信中にエラー: {e}')

if __name__ == "__main__":
    asyncio.run(main()) 
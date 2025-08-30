import asyncio
import json
import sqlite3
import os
import re
import aiohttp
import aiofiles
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv
from src.slack_webhook import send_slack_notification

# 環境変数の読み込み
load_dotenv()

# 定数
WILDRIFT_GAME_ID = 3

# ログ設定
def setup_logging():
    """ログ設定を行う"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "wildrift_champion_stats_scraper.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# 画像ダウンロード関数
def get_file_extension_from_content_type(content_type):
    """Content-Typeから拡張子を取得"""
    content_type_to_ext = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/webp': '.webp',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
        'image/svg+xml': '.svg'
    }
    return content_type_to_ext.get(content_type.lower(), '.png')

def get_file_extension_from_url(url):
    """URLから拡張子を抽出（フォールバック用）"""
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        return ext if ext else '.png'  # デフォルトは.png
    except Exception:
        return '.png'  # エラー時はデフォルト

async def download_champion_image(image_url, chinese_name, logger):
    """チャンピオン画像をダウンロードして保存"""
    try:
        # champion_imagesディレクトリを作成
        image_dir = "champion_images"
        os.makedirs(image_dir, exist_ok=True)
        
        # タイムアウト設定とコネクター設定でSSL接続エラーを抑制
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(limit=10, force_close=True, enable_cleanup_closed=True)
        
        # 画像をダウンロードしてContent-Typeから拡張子を判定
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    # Content-Typeヘッダーから実際の拡張子を取得
                    content_type = response.headers.get('content-type', '')
                    file_extension = get_file_extension_from_content_type(content_type)
                    
                    # Content-Typeが取得できない場合はURLから判定（フォールバック）
                    if not content_type:
                        file_extension = get_file_extension_from_url(image_url)
                        logger.warning(f"Content-Typeが取得できません。URLから拡張子を推定: {file_extension}")
                    else:
                        logger.info(f"Content-Type: {content_type} -> 拡張子: {file_extension}")
                    
                    # ファイル名を中国語名に設定（実際の拡張子を使用）
                    file_name = f"{chinese_name}{file_extension}"
                    file_path = os.path.join(image_dir, file_name)
                    
                    # 既にファイルが存在する場合はスキップ
                    if os.path.exists(file_path):
                        logger.info(f"画像が既に存在します: {file_path}")
                        return True
                    
                    # ファイルに保存
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    logger.info(f"画像ダウンロード完了: {file_path}")
                    return True
                else:
                    logger.error(f"画像ダウンロード失敗 (HTTP {response.status}): {image_url}")
                    return False
    except Exception as e:
        logger.error(f"画像ダウンロード中にエラー発生: {e}")
        return False

# データベース関連の関数
def get_latest_patch_id():
    """最新のパッチIDを取得"""
    db_path = "data/moba_log.db"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM patches 
            WHERE game_id = ? 
            ORDER BY release_date DESC 
            LIMIT 1
        """, (WILDRIFT_GAME_ID,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_character_id(chinese_name):
    """中国語名からキャラクターIDを取得"""
    db_path = "data/moba_log.db"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM characters 
            WHERE chinese_name = ? AND game_id = ?
        """, (chinese_name, WILDRIFT_GAME_ID))
        result = cursor.fetchone()
        return result[0] if result else None

async def insert_character_if_not_exists(chinese_name, image_url, logger):
    """キャラクターが存在しない場合は挿入（画像ダウンロード付き）"""
    db_path = "data/moba_log.db"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # 既存チェック
        character_id = get_character_id(chinese_name)
        if character_id:
            return character_id
            
        # 新規挿入の場合、画像をダウンロード
        logger.info(f"新規キャラクター '{chinese_name}' の画像をダウンロード中...")
        await download_champion_image(image_url, chinese_name, logger)
        
        # 新規挿入
        cursor.execute("""
            INSERT INTO characters (game_id, chinese_name, english_name, created_at, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (WILDRIFT_GAME_ID, chinese_name, chinese_name))
        conn.commit()
        return cursor.lastrowid

def extract_patch_number(patch_text):
    """パッチテキストからパッチ番号を抽出"""
    try:
        # "ワイルドリフト パッチノート 6.1c" -> "6.1c"
        match = re.search(r'パッチノート\s+([0-9]+\.[0-9]+[a-z]?)', patch_text)
        if match:
            patch_number = match.group(1)
            return patch_number
        else:
            return None
    except Exception:
        return None

def parse_release_date(date_text):
    """リリース日をパース"""
    try:
        # 日付形式を正規化（例: "2025/5/28" -> "2025-05-28"）
        if '/' in date_text:
            parts = date_text.split('/')
            if len(parts) == 3:
                year, month, day = parts
                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                return formatted_date
        return None
    except Exception:
        return None



async def insert_wildrift_stats(champion_stats, patch_id, logger):
    """wildrift_statsテーブルへデータを挿入"""
    db_path = "data/moba_log.db"
    
    # フェーズ1: 全チャンピオンのcharacter_idを事前に取得・作成
    logger.info("チャンピオンのcharacter_id取得フェーズを開始")
    champion_id_map = {}  # {(name, image_url): character_id} のマップ
    
    for chinese_lane, champions in champion_stats.items():
        if chinese_lane == "参照日":
            continue
            
        if not isinstance(champions, list):
            continue
            
        for champion in champions:
            champion_key = (champion["name"], champion["image_url"])
            if champion_key not in champion_id_map:
                # キャラクターIDを取得（存在しない場合は作成）
                character_id = await insert_character_if_not_exists(champion["name"], champion["image_url"], logger)
                champion_id_map[champion_key] = character_id
    
    logger.info(f"character_id取得完了: {len(champion_id_map)}件")
    
    # フェーズ2: 統計データの一括insert
    logger.info("統計データinsertフェーズを開始")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        reference_date = champion_stats["参照日"]
        
        for chinese_lane, champions in champion_stats.items():
            if chinese_lane == "参照日":
                continue
                
            # 中国語のレーン名をそのまま使用
            lane = chinese_lane
            
            if not isinstance(champions, list):
                continue
                
            for champion in champions:
                # 事前に取得したcharacter_idを使用
                champion_key = (champion["name"], champion["image_url"])
                character_id = champion_id_map[champion_key]
                
                try:
                    # INSERT OR IGNORE を使用してユニーク制約違反を回避
                    cursor.execute("""
                        INSERT OR IGNORE INTO wildrift_stats 
                        (character_id, patch_id, win_rate, pick_rate, ban_rate, 
                         reference_date, lane, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        character_id,
                        patch_id,
                        float(champion["胜率"]) if champion["胜率"] else None,
                        float(champion["登场率"]) if champion["登场率"] else None,
                        float(champion["BAN率"]) if champion["BAN率"] else None,
                        reference_date,
                        lane
                    ))
                except Exception as e:
                    logger.error(f"Insert error for lane {lane}, champion {champion['name']}: {e}")
        
        conn.commit()
        logger.info("統計データinsert完了")

def insert_scraper_log(status, error_message):
    """scraper_logsテーブルへスクレイピング結果を保存"""
    db_path = "data/moba_log.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # 日本時間の日付を取得
        jst_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO scraper_logs (game_id, scraper_status, error_message, scraper_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (WILDRIFT_GAME_ID, status, error_message, jst_date))
        conn.commit()



# スクレイピング関数
async def extract_champion_data(page, logger):
    """チャンピオンデータを抽出"""
    data = await page.evaluate("""
        () => {
            const lis = document.querySelectorAll("#data-list > li");
            return Array.from(lis).map(li => {
                const nameEl = li.querySelector('p.hero-name');
                const name = nameEl ? nameEl.innerText.trim() : '';

                const winRateEl = li.querySelector('div:nth-child(4)');
                let winRate = winRateEl ? winRateEl.innerText.trim() : '';
                winRate = winRate.replace('%', '');

                const pickRateEl = li.querySelector('div:nth-child(5)');
                let pickRate = pickRateEl ? pickRateEl.innerText.trim() : '';
                pickRate = pickRate.replace('%', '');

                const banRateEl = li.querySelector('div:nth-child(6)');
                let banRate = banRateEl ? banRateEl.innerText.trim() : '';
                banRate = banRate.replace('%', '');

                // 画像URLを取得
                const imgEl = li.querySelector('div.li-div.hero-msg > div > img');
                const imageUrl = imgEl ? imgEl.src : '';

                return { 
                    name, 
                    胜率: winRate, 
                    登场率: pickRate, 
                    BAN率: banRate,
                    image_url: imageUrl
                };
            }).filter(item => item.name !== '');
        }
    """)
    
    logger.info(f"データ抽出完了: {len(data)}件")
    return data

async def scrape_wildrift_stats(logger):
    """Wild Riftの統計データをスクレイピング"""
    # パッチIDを取得
    patch_id = get_latest_patch_id()
    
    if not patch_id:
        raise Exception("最新のパッチIDが見つかりません")
        
    logger.info(f"ゲームID: {WILDRIFT_GAME_ID}, パッチID: {patch_id}")
    
    async with async_playwright() as p:
        # ブラウザ起動
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://lolm.qq.com/act/a20220818raider/index.html"
        await page.goto(url, wait_until='networkidle')
        logger.info(f"ページをオープン: {url}")
        
        # 参照日を取得
        await page.wait_for_selector("#data-time")
        reference_date = await page.text_content("#data-time")
        reference_date = reference_date.strip()
        logger.info(f"参照日を取得: {reference_date}")
        
        # JSON出力用のオブジェクト
        champion_stats = {"参照日": reference_date}
        
        # ----- 上单（デフォルトタブ） -----
        await page.wait_for_selector("#data-list > li")
        logger.info("上单タブのセレクタ待機完了")
        top_data = await extract_champion_data(page, logger)
        champion_stats["上单"] = top_data
        logger.info("上单データを取得完了")
        
        # ----- 打野 -----
        await page.wait_for_selector("a.btn-place-jungle")
        await page.click("a.btn-place-jungle")
        logger.info("打野ボタンをクリック")
        await page.wait_for_selector("#data-list > li")
        jungle_data = await extract_champion_data(page, logger)
        champion_stats["打野"] = jungle_data
        logger.info("打野データを取得完了")
        
        # ----- 中路 -----
        await page.wait_for_selector("a.btn-place-mid")
        await page.click("a.btn-place-mid")
        logger.info("中路ボタンをクリック")
        await page.wait_for_selector("#data-list > li")
        mid_data = await extract_champion_data(page, logger)
        champion_stats["中路"] = mid_data
        logger.info("中路データを取得完了")
        
        # ----- 下路 -----
        await page.wait_for_selector("a.btn-place-bot")
        await page.click("a.btn-place-bot")
        logger.info("下路ボタンをクリック")
        await page.wait_for_selector("#data-list > li")
        bot_data = await extract_champion_data(page, logger)
        champion_stats["下路"] = bot_data
        logger.info("下路データを取得完了")
        
        # ----- 辅助 -----
        await page.wait_for_selector("a.btn-place-sup")
        await page.click("a.btn-place-sup")
        logger.info("辅助ボタンをクリック")
        await page.wait_for_selector("#data-list > li")
        sup_data = await extract_champion_data(page, logger)
        champion_stats["辅助"] = sup_data
        logger.info("辅助データを取得完了")
        
        # ログファイルへスクレイピング結果を出力
        json_output = json.dumps(champion_stats, ensure_ascii=False, indent=2)
        log_file_path = "logs/wildrift_champion_stats_scraper.log"
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"取得データ:\n{json_output}\n")
        logger.info("全データをログファイルに出力完了")
        
        await browser.close()
        logger.info("ブラウザを閉じました。スクレイピング終了")
        
        # --- SQLiteへの保存処理 ---
        logger.info("wildrift_statsテーブルへデータを保存中")
        await insert_wildrift_stats(champion_stats, patch_id, logger)
        logger.info("wildrift_statsテーブルへデータ保存完了")

async def main():
    """メイン処理"""
    logger = setup_logging()
    
    try:
        logger.info("スクリプト開始")
        
        # --- 統計スクレイピング処理 ---
        await scrape_wildrift_stats(logger)
        
        # --- スクレイピング結果をscraper_logsテーブルへ保存（成功の場合） ---
        logger.info("scraper_logsテーブルへ成功ステータスを保存中")
        insert_scraper_log(True, None)
        logger.info("scraper_logsテーブルへデータ保存完了")
        
        # --- Slack通知（成功） ---
        webhook_url = os.getenv('WILDRIFT_SLACK_WEBHOOK_URL')
        if webhook_url:
            success_message = "✅ Wild Riftスクレイピング処理が正常に完了しました。\n- 統計データ取得完了\n- データベース保存完了"
            send_slack_notification(webhook_url, success_message)
            logger.info("Slack通知（成功）を送信しました")
        else:
            logger.warning("WILDRIFT_SLACK_WEBHOOK_URLが設定されていません")
        
    except Exception as error:
        logger.error(f"エラー発生: {error}")
        # --- エラー発生時、scraper_logsテーブルへ失敗情報を保存 ---
        try:
            insert_scraper_log(False, str(error))
            logger.info("scraper_logsテーブルへエラーステータスを保存完了")
        except Exception as err:
            logger.error(f"scraper_logs保存中に更にエラー発生: {err}")
        
        # --- Slack通知（エラー） ---
        webhook_url = os.getenv('WILDRIFT_SLACK_WEBHOOK_URL')
        if webhook_url:
            error_message = f"❌ Wild Riftスクレイピング処理でエラーが発生しました。\nエラー内容: {error}"
            send_slack_notification(webhook_url, error_message)
            logger.info("Slack通知（エラー）を送信しました")
        else:
            logger.warning("WILDRIFT_SLACK_WEBHOOK_URLが設定されていません")
        
        raise

if __name__ == "__main__":
    asyncio.run(main())

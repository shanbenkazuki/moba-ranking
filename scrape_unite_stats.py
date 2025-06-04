import nodriver as uc
import asyncio
import json
import re
import sqlite3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pathlib import Path
import httpx
import os
from dotenv import load_dotenv

# バージョンチェック機能をインポート
from check_unite_version import extract_latest_update_info, save_patch_to_database

# Slack通知機能をインポート  
from src.slack_webhook import send_slack_notification

# 環境変数を読み込み
load_dotenv()

# データベースファイルパス
DB_PATH = 'data/moba_log.db'

def connect_db():
    """データベースに接続する"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能にする
        return conn
    except sqlite3.Error as e:
        print(f"データベース接続エラー: {e}")
        return None

def check_character_exists(pokemon_name):
    """charactersテーブルでポケモンの存在をチェック"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM characters 
            WHERE game_id = 2 AND english_name = ?
        """, (pokemon_name,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        print(f"キャラクター存在チェックエラー: {e}")
        return False
    finally:
        conn.close()

def get_character_id(pokemon_name):
    """ポケモン名からcharacter_idを取得"""
    conn = connect_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM characters 
            WHERE game_id = 2 AND english_name = ?
        """, (pokemon_name,))
        result = cursor.fetchone()
        return result['id'] if result else None
    except sqlite3.Error as e:
        print(f"キャラクターID取得エラー: {e}")
        return None
    finally:
        conn.close()

def register_new_character(pokemon_name):
    """新規キャラクターをcharactersテーブルに登録"""
    conn = connect_db()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO characters (game_id, english_name, created_at, updated_at)
            VALUES (2, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (pokemon_name,))
        conn.commit()
        character_id = cursor.lastrowid
        print(f"新規キャラクター登録完了: {pokemon_name} (ID: {character_id})")
        return character_id
    except sqlite3.Error as e:
        print(f"キャラクター登録エラー: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

async def download_pokemon_image(pokemon_name, img_url):
    """ポケモンの画像をダウンロードして保存"""
    # pokemon_images/ディレクトリの作成確認
    output_dir = Path("pokemon_images")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # デバッグ用: URLを出力
        print(f"画像ダウンロード中: {pokemon_name}")
        print(f"対象URL: {img_url}")
        
        # URLの妥当性をチェック
        if not img_url or not img_url.startswith(('http://', 'https://')):
            print(f"❌ 無効な画像URL: {img_url}")
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.get(img_url)
            response.raise_for_status()
            
            # ファイル拡張子を取得
            file_extension = img_url.split('.')[-1].split('?')[0]
            if file_extension not in ['png', 'jpg', 'jpeg', 'webp']:
                file_extension = 'png'
            
            # ファイル名を生成
            filename = f"{pokemon_name}.{file_extension}"
            filepath = output_dir / filename
            
            # ファイルに保存
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"画像保存完了: {filepath}")
            return True
            
    except Exception as e:
        print(f"❌ {pokemon_name}の画像ダウンロード中にエラー: {e}")
        print(f"エラー発生時のURL: {img_url}")
        return False

async def get_missing_pokemon_images(missing_pokemon_names):
    """未登録キャラクターの画像URLを取得"""
    if not missing_pokemon_names:
        return {}
    
    try:
        # scrape_unite_image.pyと同様の方法でPlaywrightを使用
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            target_url = "https://unite.pokemon.com/en-us/pokemon/"
            print(f"ポケモン画像取得のため{target_url}にアクセス中...")
            await page.goto(target_url, wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # ポケモンリストのコンテナを取得
            pokemon_list = await page.query_selector("#pokemon-list")
            if not pokemon_list:
                print("ポケモンリストが見つかりませんでした")
                return {}
            
            # すべてのポケモンカードを取得
            pokemon_cards = await pokemon_list.query_selector_all("li")
            
            # 画像URLマッピングを作成
            image_urls = {}
            print(f"🔍 未登録ポケモンリスト: {missing_pokemon_names}")
            
            for card in pokemon_cards:
                try:
                    img_element = await card.query_selector("a > div.pokemon-card__image > div.pokemon-card__character > img")
                    if img_element:
                        src = await img_element.get_attribute("src")
                        srcset = await img_element.get_attribute("srcset")
                        
                        if src:
                            # ポケモン名を抽出
                            pokemon_name = extract_pokemon_name_from_path(src)
                            print(f"🐾 検出されたポケモン: {pokemon_name}")
                            
                            if pokemon_name and pokemon_name in missing_pokemon_names:
                                print(f"✅ マッチ: {pokemon_name}")
                                # 高解像度画像を優先
                                high_res_url = get_high_res_url(src, srcset)
                                image_urls[pokemon_name] = high_res_url
                            elif pokemon_name:
                                print(f"⏭️  スキップ: {pokemon_name} (対象外)")
                                
                except Exception as e:
                    print(f"⚠️  カード処理エラー: {e}")
                    continue
            
            await browser.close()
            print(f"取得した画像URL数: {len(image_urls)}件")
            return image_urls
            
    except Exception as e:
        print(f"画像URL取得中にエラー: {e}")
        return {}

def extract_pokemon_name_from_path(src_path):
    """画像パスからポケモン名を抽出（scrape_unite_image.pyを参考）"""
    print(f"   🔍 パス解析: {src_path}")
    
    pattern = r'/pokemon/([^/]+)/'
    match = re.search(pattern, src_path)
    if match:
        pokemon_name = match.group(1)
        # ハイフン区切りの各単語の先頭を大文字にして返す
        formatted_name = '-'.join(word.capitalize() for word in pokemon_name.split('-'))
        print(f"   ✅ 抽出されたポケモン名: {formatted_name}")
        return formatted_name
    else:
        print(f"   ❌ ポケモン名抽出失敗")
        return None

def get_high_res_url(src, srcset):
    """高解像度画像のURLを取得（scrape_unite_image.pyを参考）"""
    base_url = "https://unite.pokemon.com"
    
    print(f"🔍 URL生成デバッグ:")
    print(f"   src: {src}")
    print(f"   srcset: {srcset}")
    
    def normalize_path(path):
        """相対パスを正規化して絶対パスに変換"""
        # ../ で始まる相対パスを処理
        if path.startswith('../../'):
            # ../../ を削除
            return path[6:]  # '../../' の長さは6文字
        elif path.startswith('../'):
            # ../ を削除
            return path[3:]  # '../' の長さは3文字
        elif path.startswith('./'):
            # ./ を削除
            return path[2:]  # './' の長さは2文字
        else:
            # 絶対パスまたは通常のパス
            return path.lstrip('/')  # 先頭の / を削除
    
    if srcset:
        # srcsetから2x画像を取得
        srcset_parts = srcset.split(',')
        for part in srcset_parts:
            part = part.strip()
            if '2x' in part:
                # 2x画像のパスを抽出
                high_res_path = part.split(' ')[0]
                # パスを正規化
                normalized_path = normalize_path(high_res_path)
                final_url = f"{base_url}/{normalized_path}"
                print(f"   ✅ 高解像度URL: {final_url}")
                return final_url
    
    # srcsetがない場合はsrcを使用
    normalized_path = normalize_path(src)
    final_url = f"{base_url}/{normalized_path}"
    print(f"   ✅ 標準URL: {final_url}")
    return final_url

def extract_pokemon_stats(content):
    """HTMLコンテンツからポケモンの統計データを抽出"""
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(content, 'html.parser')
    
    def extract_meta_information():
        """更新日とトータルゲーム数を抽出してmeta情報を作成"""
        meta = {}
        
        # 更新日を抽出
        last_updated_element = soup.find('p', class_='mantine-focus-auto simpleStat_count__dG_xB m_b6d8b162 mantine-Text-root')
        if last_updated_element:
            last_updated_text = last_updated_element.get_text().strip()
            
            # 英語の月名を数値に変換
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            
            # "June 1" 形式を解析
            match = re.match(r'(\w+)\s+(\d+)', last_updated_text)
            if match:
                month_name, day = match.groups()
                month = month_map.get(month_name)
                day = int(day)
                
                if month:
                    # 年を算出（現在の日付と比較して適切な年を決定）
                    current_date = datetime.now()
                    current_year = current_date.year
                    
                    # 仮の更新日を作成
                    try:
                        update_date = datetime(current_year, month, day)
                        
                        # 更新日が未来すぎる場合（3ヶ月以上先）は前年とみなす
                        if update_date > current_date + timedelta(days=90):
                            update_date = datetime(current_year - 1, month, day)
                        # 更新日が過去すぎる場合（9ヶ月以上前）は翌年とみなす
                        elif update_date < current_date - timedelta(days=270):
                            update_date = datetime(current_year + 1, month, day)
                        
                        meta['last_updated'] = update_date.strftime('%Y-%m-%d')
                    except ValueError:
                        # 日付が無効な場合（例：2月30日など）
                        meta['last_updated'] = f"{current_year}-{month:02d}-{day:02d}"
        
        # トータルゲーム数を抽出
        total_games_elements = soup.find_all('p', class_='mantine-focus-auto simpleStat_count__dG_xB m_b6d8b162 mantine-Text-root')
        for element in total_games_elements:
            # 次の要素がTotal Games Analyzedかチェック
            next_element = element.find_next_sibling('p')
            if next_element and 'Total Games Analyzed' in next_element.get_text():
                total_games_text = element.get_text().strip()
                # 数値のみを抽出（カンマを削除して整数に変換）
                total_games = re.sub(r'[^\d]', '', total_games_text)
                if total_games:
                    meta['total_games_analyzed'] = int(total_games)
                break
        
        return meta
    
    def get_section_by_heading(heading_text):
        """ヘading要素を基準にセクションを取得する（より堅牢な方法）"""
        # ヘadingを探す
        heading = soup.find('h2', string=re.compile(heading_text, re.IGNORECASE))
        if not heading:
            return []
        
        # ヘadingから親コンテナを探す
        section_container = heading.find_parent('div', class_=re.compile(r'sc-d5d8a548-0|iVUifA'))
        if not section_container:
            # フォールバック: より上位の親要素を探す
            section_container = heading.find_parent('div')
            for _ in range(3):  # 最大3レベル上まで探す
                if section_container and section_container.find_all('div', class_=re.compile(r'mantine-Group-root')):
                    break
                section_container = section_container.find_parent('div') if section_container else None
        
        if section_container:
            # セクション内のポケモンデータ要素を取得
            return section_container.find_all('div', class_=re.compile(r'mantine-Group-root'))
        
        return []
    
    def get_section_by_css_fallback(css_selector):
        """フォールバック用のCSSセレクタ"""
        try:
            return soup.select(css_selector)
        except:
            return []
    
    # より堅牢な方法でセクションを取得（ヘading基準 + フォールバック）
    win_rate_elements = get_section_by_heading("Win rate last week")
    if not win_rate_elements:
        win_rate_elements = get_section_by_css_fallback('div.m_6d731127.mantine-Stack-root > div:nth-child(5) > div:nth-child(1) > div > div > div')
    
    pick_rate_elements = get_section_by_heading("Pick rate last week")
    if not pick_rate_elements:
        pick_rate_elements = get_section_by_css_fallback('div.m_6d731127.mantine-Stack-root > div:nth-child(5) > div:nth-child(3) > div > div > div')
    
    ban_rate_elements = get_section_by_heading("Ban rate last week")
    if not ban_rate_elements:
        ban_rate_elements = get_section_by_css_fallback('div.m_6d731127.mantine-Stack-root > div:nth-child(5) > div:nth-child(2) > div > div > div')
    
    def extract_pokemon_data_from_section(section_elements, data_type=""):
        """セクション内からポケモンデータを抽出"""
        pokemon_data = []
        
        for element in section_elements:
            # 各要素内でimg要素を探す（複数の候補パターン）
            img_element = (
                element.find('img', alt=re.compile(r'Avatar of the pokemon')) or
                element.find('img', alt=re.compile(r'pokemon', re.IGNORECASE)) or
                element.find('img', src=re.compile(r'/Sprites/'))
            )
            
            # value属性を持つdiv要素を探す（統計データ）
            value_element = (
                element.find('div', attrs={'value': True}) or
                element.find('div', string=re.compile(r'\d+\.\d+\s*%')) or
                element.find('div', class_=re.compile(r'sc-71f8e1a4-1'))
            )
            
            if img_element and value_element:
                # alt属性からポケモン名を抽出
                alt_text = img_element.get('alt', '')
                pokemon_name = None
                
                if 'Avatar of the pokemon' in alt_text:
                    pokemon_name = alt_text.replace('Avatar of the pokemon ', '')
                    
                    # Mewtwoの場合は、srcsetまたはsrc属性から詳細な形態を取得
                    if pokemon_name == 'Mewtwo':
                        srcset = img_element.get('srcset', '')
                        src = img_element.get('src', '')
                        
                        # srcsetから形態を判定
                        if 'MewtwoX' in srcset:
                            pokemon_name = 'Mewtwo-X'
                        elif 'MewtwoY' in srcset:
                            pokemon_name = 'Mewtwo-Y'
                        # フォールバック: srcから形態を判定
                        elif 'MewtwoX' in src:
                            pokemon_name = 'Mewtwo-X'
                        elif 'MewtwoY' in src:
                            pokemon_name = 'Mewtwo-Y'
                            
                elif alt_text and alt_text != 'Pokemon image':
                    pokemon_name = alt_text
                else:
                    # フォールバック: src属性からポケモン名を抽出
                    src = img_element.get('src', '')
                    if '/Sprites/' in src:
                        pokemon_name = src.split('/')[-1].replace('t_Square_', '').replace('.png', '')
                
                # ポケモン名の空白とピリオドをハイフンに変換
                if pokemon_name:
                    pokemon_name = re.sub(r'[ .]+', '-', pokemon_name)
                
                # value属性から値を抽出
                rate_value = value_element.get('value')
                if not rate_value:
                    # フォールバック: テキストから数値を抽出
                    text_content = value_element.get_text()
                    match = re.search(r'(\d+\.\d+)', text_content)
                    if match:
                        rate_value = match.group(1)
                
                if pokemon_name and rate_value:
                    try:
                        rate_float = float(rate_value)
                        pokemon_data.append({
                            'pokemon_name': pokemon_name,
                            'rate': rate_float
                        })
                    except ValueError:
                        continue
        
        print(f"取得した{data_type}データ: {len(pokemon_data)}件")
        return pokemon_data
    
    # 各セクションからデータを抽出
    win_rate_data = extract_pokemon_data_from_section(win_rate_elements, "勝率")
    pick_rate_data = extract_pokemon_data_from_section(pick_rate_elements, "Pick率")
    ban_rate_data = extract_pokemon_data_from_section(ban_rate_elements, "BAN率")
    
    # データを統合
    all_pokemon_data = {}
    
    # 勝率データを追加
    for data in win_rate_data:
        pokemon_name = data['pokemon_name']
        if pokemon_name not in all_pokemon_data:
            all_pokemon_data[pokemon_name] = {}
        all_pokemon_data[pokemon_name]['win_rate'] = data['rate']
    
    # Pick率データを追加
    for data in pick_rate_data:
        pokemon_name = data['pokemon_name']
        if pokemon_name not in all_pokemon_data:
            all_pokemon_data[pokemon_name] = {}
        all_pokemon_data[pokemon_name]['pick_rate'] = data['rate']
    
    # BAN率データを追加
    for data in ban_rate_data:
        pokemon_name = data['pokemon_name']
        if pokemon_name not in all_pokemon_data:
            all_pokemon_data[pokemon_name] = {}
        all_pokemon_data[pokemon_name]['ban_rate'] = data['rate']
    
    # リスト形式に変換
    result = []
    for pokemon_name, stats in all_pokemon_data.items():
        pokemon_stats = {'pokemon_name': pokemon_name}
        pokemon_stats.update(stats)
        result.append(pokemon_stats)
    
    # 統計情報を出力
    print(f"統合後のポケモンデータ: {len(result)}件")
    
    # メタ情報を抽出
    meta = extract_meta_information()
    
    # メタ情報を統合
    result_with_meta = {
        'meta': meta,
        'pokemon_data': result
    }
    
    # 統計情報を出力
    print(f"メタ情報: 更新日={meta.get('last_updated', 'N/A')}, 総ゲーム数={meta.get('total_games_analyzed', 'N/A')}")
    
    return result_with_meta

def save_unite_stats(character_id, stats_data, reference_date):
    """unite_statsテーブルに統計データを保存"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 既存データをチェック
        cursor.execute("""
            SELECT id FROM unite_stats 
            WHERE character_id = ? AND reference_date = ?
        """, (character_id, reference_date))
        existing = cursor.fetchone()
        
        if existing:
            # 既存データを更新
            cursor.execute("""
                UPDATE unite_stats 
                SET win_rate = ?, pick_rate = ?, ban_rate = ?, updated_at = CURRENT_TIMESTAMP
                WHERE character_id = ? AND reference_date = ?
            """, (
                stats_data.get('win_rate'),
                stats_data.get('pick_rate'), 
                stats_data.get('ban_rate'),
                character_id,
                reference_date
            ))
            print(f"統計データ更新完了: character_id={character_id}")
        else:
            # 新規データを挿入
            cursor.execute("""
                INSERT INTO unite_stats 
                (character_id, win_rate, pick_rate, ban_rate, reference_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                character_id,
                stats_data.get('win_rate'),
                stats_data.get('pick_rate'),
                stats_data.get('ban_rate'),
                reference_date
            ))
            print(f"統計データ挿入完了: character_id={character_id}")
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"統計データ保存エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def save_unite_game_summary(total_games, reference_date):
    """unite_game_summaryテーブルに全体統計を保存"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 既存データをチェック
        cursor.execute("""
            SELECT id FROM unite_game_summary 
            WHERE reference_date = ?
        """, (reference_date,))
        existing = cursor.fetchone()
        
        if existing:
            # 既存データを更新
            cursor.execute("""
                UPDATE unite_game_summary 
                SET total_game_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE reference_date = ?
            """, (total_games, reference_date))
            print(f"ゲーム統計更新完了: 総ゲーム数={total_games}")
        else:
            # 新規データを挿入
            cursor.execute("""
                INSERT INTO unite_game_summary 
                (reference_date, total_game_count, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (reference_date, total_games))
            print(f"ゲーム統計挿入完了: 総ゲーム数={total_games}")
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"ゲーム統計保存エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

async def main():
    # 統計変数を初期化
    existing_count = 0
    new_count = 0
    saved_count = 0
    error_count = 0
    reference_date = None
    total_games = None
    pokemon_data_count = 0
    browser = None
    
    try:
        # スクレイピング前にバージョンチェックを実行
        print("=" * 60)
        print("🔍 Pokémon UNITE バージョンチェックを開始します...")
        print("=" * 60)
        
        try:
            update_info = await extract_latest_update_info()
            
            if update_info:
                print(f"✅ 最新のアップデート情報を取得しました")
                print("-" * 40)
                
                if "date" in update_info:
                    print(f"📅 日付: {update_info['date']}")
                
                if "update_datetime" in update_info:
                    print(f"🕐 アップデート日時: {update_info['update_datetime']}")
                
                if "version" in update_info:
                    print(f"🏷️  バージョン: {update_info['version']}")
                
                if "content" in update_info:
                    print(f"📝 内容: {update_info['content'][:100]}..." if len(update_info['content']) > 100 else f"📝 内容: {update_info['content']}")
                    
                print("-" * 40)
                
                # データベースに保存
                print("💾 データベースに保存中...")
                if save_patch_to_database(update_info):
                    print("✅ データベースへの保存が完了しました")
                else:
                    print("❌ データベースへの保存に失敗しました")
            else:
                print("⚠️  アップデート情報を取得できませんでしたが、スクレイピングを継続します")
            
        except Exception as e:
            print(f"⚠️  バージョンチェック中にエラーが発生しましたが、スクレイピングを継続します: {e}")
        
        print("=" * 60)
        print("📊 統計データのスクレイピングを開始します...")
        print("=" * 60)
        
        # ブラウザを開始（ヘッドレスではない設定で、より人間らしく）
        browser = await uc.start()
        
        try:
            # https://uniteapi.dev/meta にアクセス
            print("https://uniteapi.dev/meta にアクセス中...")
            page = await browser.get('https://uniteapi.dev/meta')
            
            # "Pokémon Unite Meta Tierlist"のテキストが見えるまで待機（サイトに到達したことを確認）
            print("サイトの読み込み確認中...")
            await page.find("Pokémon Unite Meta Tierlist")
            print("サイトに正常にアクセスできました。")
            
            # HTMLコンテンツを取得
            print("HTMLコンテンツを取得中...")
            content = await page.get_content()
            
            # BeautifulSoupでデータを抽出
            print("\nHTMLコンテンツを解析してポケモン統計データを抽出中...")
            pokemon_stats_with_meta = extract_pokemon_stats(content)
            
            # データベース保存処理を開始
            print("\n" + "="*60)
            print("📁 データベース保存処理を開始します...")
            print("="*60)
            
            # メタ情報から参照日付と総ゲーム数を取得
            meta = pokemon_stats_with_meta.get('meta', {})
            reference_date = meta.get('last_updated')
            total_games = meta.get('total_games_analyzed')
            pokemon_data = pokemon_stats_with_meta.get('pokemon_data', [])
            
            if not reference_date:
                print("⚠️  参照日付が取得できませんでした。現在の日付を使用します。")
                reference_date = datetime.now().strftime('%Y-%m-%d')
            
            print(f"📅 参照日付: {reference_date}")
            print(f"🎮 総ゲーム数: {total_games}")
            print(f"🐾 ポケモンデータ数: {len(pokemon_data)}件")
            
            # unite_game_summaryに総ゲーム数を保存
            if total_games:
                save_unite_game_summary(total_games, reference_date)
            
            # キャラクター処理統計
            existing_count = 0
            new_count = 0
            missing_pokemon = []
            
            # 各ポケモンデータを処理
            print("\n🔍 キャラクター存在チェック中...")
            for pokemon in pokemon_data:
                pokemon_name = pokemon.get('pokemon_name')
                if not pokemon_name:
                    continue
                    
                # キャラクター存在チェック
                if check_character_exists(pokemon_name):
                    existing_count += 1
                else:
                    new_count += 1
                    missing_pokemon.append(pokemon_name)
                    print(f"⚠️  未登録キャラクター発見: {pokemon_name}")
            
            print(f"✅ 既存キャラクター: {existing_count}件")
            print(f"🆕 未登録キャラクター: {new_count}件")
            
            # 未登録キャラクターの画像を取得・ダウンロード
            if missing_pokemon:
                print(f"\n🖼️  未登録キャラクターの画像を取得中...")
                image_urls = await get_missing_pokemon_images(missing_pokemon)
                
                # 画像をダウンロードしてキャラクターを登録
                for pokemon_name in missing_pokemon:
                    try:
                        # 画像ダウンロード
                        if pokemon_name in image_urls:
                            await download_pokemon_image(pokemon_name, image_urls[pokemon_name])
                        else:
                            print(f"⚠️  {pokemon_name}の画像URLが見つかりませんでした")
                        
                        # キャラクター登録
                        register_new_character(pokemon_name)
                        
                    except Exception as e:
                        print(f"❌ {pokemon_name}の処理中にエラー: {e}")
            
            # 統計データをデータベースに保存
            print(f"\n💾 統計データをデータベースに保存中...")
            saved_count = 0
            error_count = 0
            
            for pokemon in pokemon_data:
                pokemon_name = pokemon.get('pokemon_name')
                if not pokemon_name:
                    continue
                    
                try:
                    # character_idを取得
                    character_id = get_character_id(pokemon_name)
                    if not character_id:
                        print(f"⚠️  {pokemon_name}のcharacter_idが取得できませんでした")
                        error_count += 1
                        continue
                    
                    # 統計データを保存
                    stats_data = {
                        'win_rate': pokemon.get('win_rate'),
                        'pick_rate': pokemon.get('pick_rate'),
                        'ban_rate': pokemon.get('ban_rate')
                    }
                    
                    if save_unite_stats(character_id, stats_data, reference_date):
                        saved_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"❌ {pokemon_name}の統計データ保存中にエラー: {e}")
                    error_count += 1
            
            # 最終結果を表示
            print("\n" + "="*60)
            print("🎉 処理完了! 結果サマリー:")
            print("="*60)
            print(f"📅 参照日付: {reference_date}")
            print(f"🎮 総ゲーム数: {total_games}")
            print(f"🐾 処理対象ポケモン: {len(pokemon_data)}件")
            print(f"✅ 既存キャラクター: {existing_count}件")
            print(f"🆕 新規登録キャラクター: {new_count}件")
            print(f"💾 統計データ保存成功: {saved_count}件")
            print(f"❌ 統計データ保存失敗: {error_count}件")
            print("="*60)
            
            # Slack通知を送信（成功時）
            slack_webhook_url = os.getenv("UNITE_SLACK_WEBHOOK_URL")
            if slack_webhook_url:
                message = f"""✅ ポケモンユナイト データスクレイピングが完了しました

📅 参照日付: {reference_date}
🎮 総ゲーム数: {total_games:,}件
🐾 処理対象ポケモン: {len(pokemon_data)}件
✅ 既存キャラクター: {existing_count}件
🆕 新規登録キャラクター: {new_count}件
💾 統計データ保存成功: {saved_count}件
❌ 統計データ保存失敗: {error_count}件"""
                
                if send_slack_notification(slack_webhook_url, message):
                    print("Slack通知を送信しました。")
                else:
                    print("Slack通知の送信に失敗しました。")
            else:
                print("UNITE_SLACK_WEBHOOK_URLが設定されていません。")
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            
            # エラー時のSlack通知
            slack_webhook_url = os.getenv("UNITE_SLACK_WEBHOOK_URL")
            if slack_webhook_url:
                error_message = f"""❌ ポケモンユナイト データスクレイピングでエラーが発生しました

⚠️ エラー内容: {str(e)}
📅 発生日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📊 処理状況:
  - 参照日付: {reference_date if reference_date else "未取得"}
  - 既存キャラクター: {existing_count}件
  - 新規キャラクター: {new_count}件
  - 保存成功: {saved_count}件
  - 保存失敗: {error_count}件"""
                
                if send_slack_notification(slack_webhook_url, error_message):
                    print("エラー通知をSlackに送信しました。")
                else:
                    print("Slackエラー通知の送信に失敗しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    finally:
        # ブラウザを終了
        if browser:
            try:
                browser.stop()
            except:
                print("ブラウザの停止中にエラーが発生しましたが、処理は完了しました。")

if __name__ == '__main__':
    # asyncioのイベントループを実行
    uc.loop().run_until_complete(main())

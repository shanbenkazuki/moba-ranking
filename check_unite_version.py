#!/usr/bin/env python3
"""
Pokémon UNITE ニュースページから最新のアップデート記事の詳細情報を取得してデータベースに保存するスクリプト
"""

from playwright.sync_api import sync_playwright
import re
import time
import sqlite3
import os
from typing import Optional, Dict


def save_patch_to_database(update_info: Dict[str, str], db_path: str = "data/moba_log.db") -> bool:
    """
    取得したアップデート情報をデータベースのpatchesテーブルに保存する
    
    Args:
        update_info: アップデート情報の辞書
        db_path: データベースファイルのパス
        
    Returns:
        bool: 保存成功時True、失敗時False
    """
    try:
        # データベースファイルの存在確認
        if not os.path.exists(db_path):
            print(f"❌ データベースファイルが見つかりません: {db_path}")
            return False
        
        # バージョン情報からVer.プレフィックスを除去
        version = update_info.get('version', '')
        if version.startswith('Ver.'):
            patch_number = version[4:]  # 'Ver.'を除去
        else:
            patch_number = version
        
        # 日付情報を取得
        release_date = update_info.get('date')
        
        if not patch_number or not release_date:
            print(f"❌ 必須情報が不足しています: patch_number='{patch_number}', release_date='{release_date}'")
            return False
        
        print(f"データベースに保存します: パッチ={patch_number}, 日付={release_date}")
        
        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Pokémon UNITEのgame_id（2）を使用
        game_id = 2
        
        # 既存のパッチがあるかチェック
        cursor.execute(
            "SELECT id FROM patches WHERE game_id = ? AND patch_number = ?",
            (game_id, patch_number)
        )
        existing_patch = cursor.fetchone()
        
        if existing_patch:
            print(f"⚠️  パッチ {patch_number} は既に存在します（ID: {existing_patch[0]}）")
            
            # 既存パッチの情報を更新
            cursor.execute("""
                UPDATE patches 
                SET release_date = ?, japanese_note = ?, updated_at = CURRENT_TIMESTAMP
                WHERE game_id = ? AND patch_number = ?
            """, (release_date, update_info.get('content', ''), game_id, patch_number))
            
            print(f"✅ パッチ {patch_number} の情報を更新しました")
        else:
            # 新しいパッチを挿入
            cursor.execute("""
                INSERT INTO patches (game_id, patch_number, release_date, japanese_note)
                VALUES (?, ?, ?, ?)
            """, (game_id, patch_number, release_date, update_info.get('content', '')))
            
            print(f"✅ 新しいパッチ {patch_number} を追加しました")
        
        # コミットして接続を閉じる
        conn.commit()
        conn.close()
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


def extract_latest_update_info() -> Optional[Dict[str, str]]:
    """
    Pokémon UNITEのニュースページから最新のアップデート記事の詳細情報を取得する
    
    Returns:
        Dict[str, str]: アップデート情報の辞書、取得できない場合はNone
        - date: YYYY-MM-DD形式の日付
        - update_datetime: アップデート日時
        - version: バージョン情報
        - content: アップデート内容
    """
    
    with sync_playwright() as p:
        # ブラウザを起動（タイムアウトを延長）
        browser = p.chromium.launch(headless=True, timeout=60000)
        page = browser.new_page()
        
        # ページタイムアウトを延長
        page.set_default_timeout(60000)
        
        try:
            print("Pokémon UNITEニュースページにアクセス中...")
            # ページにアクセス（タイムアウト延長）
            page.goto("https://www.pokemonunite.jp/ja/news/", timeout=60000)
            
            print("ページの読み込み待機中...")
            # ページの読み込み待機（タイムアウト延長）
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            # 少し待機
            time.sleep(3)
            
            print("アップデートタブを探しています...")
            # アップデートタブをクリック（より具体的なセレクター）
            try:
                update_button = page.locator('button:has-text("アップデート")')
                if update_button.count() > 0:
                    print("アップデートタブをクリック中...")
                    update_button.click()
                    # フィルタリング完了を待機
                    time.sleep(3)
                else:
                    print("アップデートタブが見つからないため、そのまま継続...")
            except Exception as e:
                print(f"アップデートタブのクリックでエラー: {e}")
                print("そのまま継続します...")
            
            print("最新のアップデート記事のURLを取得中...")
            # 最新のアップデート記事のリンクを取得
            first_update_link = page.locator('a[href*="/ja/news/"]:has(h3:text("アップデート"))').first
            
            if first_update_link.count() > 0:
                # 記事の基本情報を取得
                link_text = first_update_link.text_content()
                article_url = first_update_link.get_attribute('href')
                
                if article_url:
                    # 相対URLを絶対URLに変換
                    if article_url.startswith('/'):
                        article_url = f"https://www.pokemonunite.jp{article_url}"
                    
                    print(f"アップデート記事にアクセス中: {article_url}")
                    # アップデート記事ページに移動
                    page.goto(article_url, timeout=60000)
                    page.wait_for_load_state("domcontentloaded", timeout=30000)
                    time.sleep(2)
                    
                    # 記事ページから詳細情報を取得
                    update_info = _extract_update_details_from_article(page, link_text)
                    
                    if update_info:
                        print(f"取得した情報: {update_info}")
                        return update_info
                    else:
                        print("記事ページから詳細情報を取得できませんでした")
                        return None
                else:
                    print("アップデート記事のURLが取得できませんでした")
                    return None
            else:
                print("アップデート記事が見つかりませんでした")
                # フォールバック: 日付のみ取得
                date_result = _extract_date_with_multiple_strategies(page)
                if date_result:
                    return {"date": date_result}
                return None
                
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            # デバッグ用に現在のページタイトルを取得
            try:
                title = page.title()
                print(f"現在のページタイトル: {title}")
            except:
                print("ページタイトルの取得に失敗")
            return None
        finally:
            browser.close()


def _extract_update_details_from_article(page, link_text: str) -> Optional[Dict[str, str]]:
    """
    アップデート記事ページから詳細情報を取得する
    
    Args:
        page: Playwrightのページオブジェクト
        link_text: リンクテキスト
        
    Returns:
        Dict[str, str]: アップデート情報、取得できない場合はNone
    """
    try:
        print("記事ページから詳細情報を抽出中...")
        
        result = {}
        
        # 1. リンクテキストから日付を抽出
        date_patterns = [
            r'(\d{4})\s+(\d{2})\s*/\s*(\d{2})',  # 2025 05 / 23
            r'(\d{4})\s+(\d{1,2})\s*/\s*(\d{1,2})',  # より柔軟なパターン
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, link_text)
            if match:
                year, month, day = match.groups()
                result["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                break
        
        # 1.5. リンクテキストから取得できない場合、ページ見出しから取得
        if "date" not in result:
            print("リンクテキストから日付が取得できないため、ページ見出しから抽出を試行...")
            # ページ見出しから日付を取得
            page_title = page.title()
            article_heading = page.locator('h1').first
            
            texts_to_check = [page_title]
            if article_heading.count() > 0:
                texts_to_check.append(article_heading.text_content())
            
            # ページの日付表示部分も確認
            date_display = page.locator('generic:has-text("2025")').first
            if date_display.count() > 0:
                texts_to_check.append(date_display.text_content())
            
            for text in texts_to_check:
                if text:
                    for pattern in date_patterns:
                        match = re.search(pattern, text)
                        if match:
                            year, month, day = match.groups()
                            result["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            print(f"ページから日付を抽出: {result['date']}")
                            break
                    if "date" in result:
                        break
            
            # まだ見つからない場合、より柔軟なパターンで検索
            if "date" not in result:
                page_text = page.locator('body').text_content()
                flexible_patterns = [
                    r'(\d{1,2})月(\d{1,2})日',  # MM月DD日
                    r'2025[年\s]*(\d{1,2})[月\s]*(\d{1,2})[日\s]',  # 2025年MM月DD日
                ]
                
                for pattern in flexible_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        if pattern == flexible_patterns[0]:  # MM月DD日の場合
                            month, day = matches[0]
                            result["date"] = f"2025-{month.zfill(2)}-{day.zfill(2)}"
                        else:  # 2025年MM月DD日の場合
                            month, day = matches[0]
                            result["date"] = f"2025-{month.zfill(2)}-{day.zfill(2)}"
                        print(f"柔軟なパターンで日付を抽出: {result['date']}")
                        break
        
        # 2. テーブルから詳細情報を取得
        table = page.locator('table').first
        if table.count() > 0:
            print("アップデート情報テーブルを発見")
            
            # テーブルの各行を処理
            rows = table.locator('tr')
            for i in range(rows.count()):
                row = rows.nth(i)
                cells = row.locator('td')
                
                if cells.count() >= 2:
                    header = cells.nth(0).text_content().strip()
                    value = cells.nth(1).text_content().strip()
                    
                    print(f"テーブル行: {header} = {value}")
                    
                    if "アップデート日時" in header:
                        result["update_datetime"] = value
                    elif "バージョン" in header or "アップデート後のバージョン" in header:
                        result["version"] = value
                    elif "アップデート内容" in header:
                        result["content"] = value
        
        # 3. テーブルが見つからない場合、ページテキストから抽出
        if "update_datetime" not in result or "version" not in result:
            print("テーブルから情報が取得できないため、ページテキストから抽出を試行...")
            page_text = page.locator('body').text_content()
            
            # アップデート日時のパターン
            datetime_patterns = [
                r'(\d{4}年\d{1,2}月\d{1,2}日（[月火水木金土日]）\d{1,2}時)',
                r'(\d{4}年\d{1,2}月\d{1,2}日（[月火水木金土日]）)',
                r'(\d{1,2}月\d{1,2}日（[月火水木金土日]）\d{1,2}時)',
            ]
            
            for pattern in datetime_patterns:
                match = re.search(pattern, page_text)
                if match and "update_datetime" not in result:
                    result["update_datetime"] = match.group(1)
                    print(f"日時を抽出: {result['update_datetime']}")
                    break
            
            # バージョンのパターン
            version_patterns = [
                r'Ver\.[\d.]+',
                r'バージョン[\s:：]*(Ver\.[\d.]+)',
                r'Ver[\s.:：]*([\d.]+)',
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, page_text)
                if match and "version" not in result:
                    result["version"] = match.group(0) if 'Ver.' in match.group(0) else f"Ver.{match.group(1)}"
                    print(f"バージョンを抽出: {result['version']}")
                    break
        
        # 結果の検証
        if result:
            print(f"抽出した情報: {result}")
            return result
        else:
            print("記事から有効な情報を取得できませんでした")
            return None
            
    except Exception as e:
        print(f"記事詳細抽出でエラー: {e}")
        return None


def _extract_date_with_multiple_strategies(page) -> Optional[str]:
    """
    複数の戦略で日付を抽出する（HTML構造の変化に対応）
    
    Args:
        page: Playwrightのページオブジェクト
        
    Returns:
        str: YYYY-MM-DD形式の日付、取得できない場合はNone
    """
    
    strategies = [
        _strategy_2_first_link_structure,
        _strategy_3_text_pattern_search,
        _strategy_4_debug_all_elements
    ]
    
    for i, strategy in enumerate(strategies, 1):
        try:
            print(f"戦略{i}を試行中...")
            result = strategy(page)
            if result:
                print(f"戦略{i}で成功: {result}")
                return result
            print(f"戦略{i}では日付が見つかりませんでした")
        except Exception as e:
            print(f"戦略{i}が失敗: {e}")
            continue
    
    return None


def _strategy_1_section_topics_date(page) -> Optional[str]:
    """戦略1: section内のtopics-dateクラスから取得（削除予定）"""
    return None


def _strategy_2_first_link_structure(page) -> Optional[str]:
    """戦略2: 最初のニュースリンクの構造から取得"""
    try:
        # 最初のニュースリンクを取得
        first_link = page.locator('a[href*="/ja/news/"]').first
        print(f"リンクの数: {page.locator('a[href*=\"/ja/news/\"]').count()}")
        
        if first_link.count() > 0:
            # リンク内のテキストを全て取得
            link_text = first_link.text_content()
            print(f"最初のリンクテキスト: '{link_text}'")
            print(f"リンクテキストの長さ: {len(link_text) if link_text else 0}")
            
            if not link_text:
                print("リンクテキストが空です")
                return None
            
            # より柔軟な日付パターンを正規表現で抽出
            date_patterns = [
                r'(\d{4})\s+(\d{2})\s*/\s*(\d{2})',  # 2025 05 / 23
                r'(\d{4})\s+(\d{1,2})\s*/\s*(\d{1,2})',  # より柔軟なパターン
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, link_text)
                if match:
                    year, month, day = match.groups()
                    formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    print(f"正規表現で抽出: {year}, {month}, {day} -> {formatted_date}")
                    return formatted_date
        else:
            print("ニュースリンクが見つかりません")
    except Exception as e:
        print(f"戦略2でエラー: {e}")
    
    return None


def _strategy_3_text_pattern_search(page) -> Optional[str]:
    """戦略3: ページ全体から日付パターンを検索"""
    try:
        # ページ全体のテキストを取得（修正）
        page_text = page.content()  # page.text_content()ではなくpage.content()を使用
        print(f"ページテキストの長さ: {len(page_text)}")
        
        # 2025年を含む日付パターンを優先的に検索
        date_patterns = [
            r'2025\s+(\d{2})\s*/\s*(\d{2})',  # 2025 MM / DD
            r'2025\s+(\d{1,2})\s*/\s*(\d{1,2})',  # 2025 M / D
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                month, day = matches[0]
                formatted_date = f"2025-{month.zfill(2)}-{day.zfill(2)}"
                print(f"ページテキストから抽出: 2025, {month}, {day} -> {formatted_date}")
                return formatted_date
        
        # 2025が見つからない場合、他の年も検索
        general_pattern = r'(\d{4})\s+(\d{1,2})\s*/\s*(\d{1,2})'
        matches = re.findall(general_pattern, page_text)
        if matches:
            year, month, day = matches[0]  # 最初に見つかったもの
            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            print(f"一般的なパターンから抽出: {year}, {month}, {day} -> {formatted_date}")
            return formatted_date
    except Exception as e:
        print(f"戦略3でエラー: {e}")
    
    return None


def _strategy_4_debug_all_elements(page) -> Optional[str]:
    """戦略4: デバッグ用 - 全ての要素を調査"""
    try:
        print("=== デバッグ: ページの基本情報 ===")
        print(f"ページタイトル: {page.title()}")
        print(f"ページURL: {page.url}")
        
        # 全てのリンクを確認
        all_links = page.locator('a[href*="/ja/news/"]')
        print(f"ニュースリンクの総数: {all_links.count()}")
        
        if all_links.count() > 0:
            print("=== 最初の3つのリンクの詳細 ===")
            for i in range(min(3, all_links.count())):
                link = all_links.nth(i)
                try:
                    href = link.get_attribute('href')
                    text = link.text_content()
                    print(f"リンク{i}: href='{href}', text='{text[:100] if text else 'なし'}...'")
                except Exception as e:
                    print(f"リンク{i}の取得エラー: {e}")
        
        # 8桁の日付パターンを持つ全ての要素を探す
        print("=== 8桁日付パターンを持つ要素の検索 ===")
        date_elements = page.locator('text=/\\d{8}/')
        print(f"8桁日付パターン要素数: {date_elements.count()}")
        
        # 最新の日付を探す（2025年から始まるもの）
        latest_date = None
        for i in range(min(10, date_elements.count())):
            try:
                element = date_elements.nth(i)
                text = element.text_content().strip()
                print(f"8桁日付要素{i}: '{text}'")
                
                # 8桁の日付パターン（YYYYMMDD）を抽出
                match = re.search(r'(\d{8})', text)
                if match:
                    date_str = match.group(1)
                    print(f"抽出した8桁日付: {date_str}")
                    
                    # YYYYMMDD を YYYY-MM-DD に変換
                    if len(date_str) == 8:
                        year = date_str[:4]
                        month = date_str[4:6]
                        day = date_str[6:8]
                        
                        # 日付の妥当性をチェック
                        if (int(year) >= 2024 and 
                            1 <= int(month) <= 12 and 
                            1 <= int(day) <= 31):
                            formatted_date = f"{year}-{month}-{day}"
                            print(f"変換した日付: {formatted_date}")
                            
                            # 最新の日付（2025年を優先、なければ最初に見つかったもの）
                            if latest_date is None or year == "2025":
                                latest_date = formatted_date
                                if year == "2025":
                                    print(f"2025年の日付を発見: {formatted_date}")
                                    return formatted_date
                
            except Exception as e:
                print(f"8桁日付要素{i}の処理エラー: {e}")
        
        if latest_date:
            print(f"最新の日付として選択: {latest_date}")
            return latest_date
                
    except Exception as e:
        print(f"デバッグ戦略でエラー: {e}")
    
    return None


def _format_date_from_texts(texts: list) -> Optional[str]:
    """
    テキストのリストから日付をフォーマットする
    
    Args:
        texts: 日付要素のテキストリスト
        
    Returns:
        str: YYYY-MM-DD形式の日付、失敗時はNone
    """
    year = month = day = None
    
    for text in texts:
        clean_text = re.sub(r'\s*/\s*', '', text).strip()
        
        if re.match(r'^\d{4}$', clean_text):  # 4桁の年
            year = clean_text
        elif re.match(r'^\d{1,2}$', clean_text):
            num = int(clean_text)
            if 1 <= num <= 12 and month is None:  # 月（1-12）
                month = clean_text
            elif 1 <= num <= 31 and day is None:  # 日（1-31）
                day = clean_text
    
    if year and month and day:
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    return None


def extract_date_from_first_update() -> Optional[str]:
    """
    Pokémon UNITEのニュースページから最新のアップデート記事の日付を取得する（下位互換性のため残存）
    
    Returns:
        str: YYYY-MM-DD形式の日付、取得できない場合はNone
    """
    update_info = extract_latest_update_info()
    if update_info and "date" in update_info:
        return update_info["date"]
    return None


def main():
    """メイン関数"""
    print("Pokémon UNITE 最新アップデート記事の詳細情報を取得します...")
    
    update_info = extract_latest_update_info()
    
    if update_info:
        print(f"\n✅ 成功: 最新のアップデート記事の情報を取得しました")
        print("=" * 50)
        
        if "date" in update_info:
            print(f"📅 日付: {update_info['date']}")
        
        if "update_datetime" in update_info:
            print(f"🕐 アップデート日時: {update_info['update_datetime']}")
        
        if "version" in update_info:
            print(f"🏷️  バージョン: {update_info['version']}")
        
        if "content" in update_info:
            print(f"📝 内容: {update_info['content']}")
            
        print("=" * 50)
        
        # データベースに保存
        print("\n💾 データベースに保存中...")
        if save_patch_to_database(update_info):
            print("✅ データベースへの保存が完了しました")
        else:
            print("❌ データベースへの保存に失敗しました")
    else:
        print("\n❌ 失敗: アップデート情報を取得できませんでした")


if __name__ == "__main__":
    main()
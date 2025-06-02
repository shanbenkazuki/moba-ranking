#!/usr/bin/env python3
"""
Pokémon UNITE ニュースページから最新のアップデート記事の日付を取得するスクリプト
"""

from playwright.sync_api import sync_playwright
import re
import time
from typing import Optional


def extract_date_from_first_update() -> Optional[str]:
    """
    Pokémon UNITEのニュースページから最新のアップデート記事の日付を取得する
    
    Returns:
        str: YYYY-MM-DD形式の日付、取得できない場合はNone
    """
    
    with sync_playwright() as p:
        # ブラウザを起動（タイムアウトを延長）
        browser = p.chromium.launch(headless=True, timeout=60000)  # headlessモードに変更、タイムアウト60秒
        page = browser.new_page()
        
        # ページタイムアウトを延長
        page.set_default_timeout(60000)  # 60秒
        
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
            
            print("最新記事の日付を取得中...")
            # 複数の戦略で日付を取得
            date_result = _extract_date_with_multiple_strategies(page)
            
            if date_result:
                print(f"取得した日付: {date_result}")
                return date_result
            else:
                print("日付の取得に失敗しました")
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


def main():
    """メイン関数"""
    print("Pokémon UNITE アップデート記事の最新日付を取得します...")
    
    date = extract_date_from_first_update()
    
    if date:
        print(f"\n✅ 成功: 最新のアップデート記事の日付は {date} です")
    else:
        print("\n❌ 失敗: 日付を取得できませんでした")


if __name__ == "__main__":
    main()
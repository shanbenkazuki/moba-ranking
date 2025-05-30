#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile Legends Bang Bang 最新パッチ情報スクレイピング
Reddit から最新パッチ情報を取得してデータベースに保存
"""

import sqlite3
import re
from datetime import datetime, date
from playwright.sync_api import sync_playwright
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mlbb_patch_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MLBBPatchScraper:
    def __init__(self, db_path='data/moba_log.db'):
        self.db_path = db_path
        self.game_id = 1  # MLBBのgame_id
        
    def get_latest_patch_from_reddit(self):
        """RedditからMLBBの最新パッチ情報を取得"""
        try:
            with sync_playwright() as p:
                # ブラウザを起動（ヘッドレスモード）
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # User-Agentを設定
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # RedditのMLBBページにアクセス
                logger.info("Redditページにアクセス中...")
                page.goto('https://www.reddit.com/r/MobileLegendsGame/', wait_until='networkidle')
                
                # 指定されたXPathでパッチ情報を取得
                xpath = '//*[@id="subreddit-right-rail__partial"]/aside/div/div[5]/div[2]/a[2]/span/span/span'
                
                try:
                    # 要素が表示されるまで待機
                    page.wait_for_selector(f'xpath={xpath}', timeout=10000)
                    
                    # テキストを取得
                    patch_element = page.locator(f'xpath={xpath}')
                    patch_text = patch_element.text_content()
                    
                    logger.info(f"取得したパッチ情報: {patch_text}")
                    
                    # パッチ番号を抽出（例: "Patch Notes 1.9.68 [ORG]" から "1.9.68" を抽出）
                    patch_match = re.search(r'Patch Notes (\d+\.\d+\.\d+)', patch_text)
                    if patch_match:
                        patch_number = patch_match.group(1)
                        logger.info(f"抽出されたパッチ番号: {patch_number}")
                        return patch_number
                    else:
                        logger.error(f"パッチ番号を抽出できませんでした: {patch_text}")
                        return None
                        
                except Exception as e:
                    logger.error(f"XPath要素の取得に失敗: {e}")
                    return None
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            logger.error(f"スクレイピング中にエラーが発生: {e}")
            return None
    
    def check_patch_exists(self, patch_number):
        """指定されたパッチ番号が既にデータベースに存在するかチェック"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM patches 
                WHERE game_id = ? AND patch_number = ?
            """, (self.game_id, patch_number))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"パッチ存在チェック中にエラー: {e}")
            return False
    
    def save_patch_to_db(self, patch_number):
        """パッチ情報をデータベースに保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 現在の日付を文字列形式で取得（ISO形式: YYYY-MM-DD）
            current_date = date.today().isoformat()
            
            # パッチ情報を挿入
            cursor.execute("""
                INSERT INTO patches (game_id, patch_number, release_date, english_note, japanese_note)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.game_id,
                patch_number,
                current_date,
                f"Patch Notes {patch_number} [ORG]",
                f"パッチノート {patch_number}"
            ))
            
            patch_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"パッチ {patch_number} をデータベースに保存しました (ID: {patch_id})")
            return patch_id
            
        except sqlite3.IntegrityError as e:
            logger.warning(f"パッチ {patch_number} は既に存在します: {e}")
            return None
        except Exception as e:
            logger.error(f"データベース保存中にエラー: {e}")
            return None
    
    def log_scraper_status(self, success, error_message=None):
        """スクレイピング結果をログテーブルに記録"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scraper_logs (game_id, scraper_status, error_message, scraper_date)
                VALUES (?, ?, ?, ?)
            """, (
                self.game_id,
                1 if success else 0,
                error_message,
                date.today().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"スクレイピングログを記録しました: {'成功' if success else '失敗'}")
            
        except Exception as e:
            logger.error(f"ログ記録中にエラー: {e}")
    
    def run(self):
        """メイン実行関数"""
        logger.info("MLBB最新パッチ情報スクレイピングを開始")
        
        try:
            # Redditから最新パッチ情報を取得
            patch_number = self.get_latest_patch_from_reddit()
            
            if not patch_number:
                error_msg = "パッチ情報の取得に失敗しました"
                logger.error(error_msg)
                self.log_scraper_status(False, error_msg)
                return False
            
            # 既存パッチかチェック
            if self.check_patch_exists(patch_number):
                logger.info(f"パッチ {patch_number} は既にデータベースに存在します")
                self.log_scraper_status(True, f"パッチ {patch_number} は既存")
                return True
            
            # データベースに保存
            patch_id = self.save_patch_to_db(patch_number)
            
            if patch_id:
                logger.info(f"新しいパッチ {patch_number} を正常に保存しました")
                self.log_scraper_status(True)
                return True
            else:
                error_msg = f"パッチ {patch_number} の保存に失敗しました"
                logger.error(error_msg)
                self.log_scraper_status(False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"予期しないエラーが発生: {e}"
            logger.error(error_msg)
            self.log_scraper_status(False, error_msg)
            return False

def main():
    """メイン関数"""
    scraper = MLBBPatchScraper()
    success = scraper.run()
    
    if success:
        print("✅ MLBB最新パッチ情報の取得・保存が完了しました")
    else:
        print("❌ MLBB最新パッチ情報の取得・保存に失敗しました")
    
    return success

if __name__ == "__main__":
    main()

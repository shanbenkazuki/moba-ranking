"""
Pokemon UNITE アイコン画像スクレイパー
https://unite.pokemon.com/en-us/pokemon/ からすべてのポケモンアイコン画像を取得
"""

import asyncio
import os
import re
from pathlib import Path
from urllib.parse import urljoin
import httpx
from playwright.async_api import async_playwright

class UniteImageScraper:
    def __init__(self):
        self.base_url = "https://unite.pokemon.com"
        self.target_url = "https://unite.pokemon.com/en-us/pokemon/"
        self.output_dir = Path("pokemon_images")
        self.output_dir.mkdir(exist_ok=True)
        
    async def scrape_pokemon_images(self):
        """メインのスクレイピング処理"""
        async with async_playwright() as p:
            # ブラウザを起動
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print(f"アクセス中: {self.target_url}")
                await page.goto(self.target_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)  # 3秒待機
                
                # ポケモンリストのコンテナを取得
                pokemon_list = await page.query_selector("#pokemon-list")
                if not pokemon_list:
                    print("ポケモンリストが見つかりませんでした")
                    return
                
                # すべてのポケモンカードを取得
                pokemon_cards = await pokemon_list.query_selector_all("li")
                print(f"見つかったポケモンカード数: {len(pokemon_cards)}")
                
                # 各ポケモンカードから画像情報を取得
                pokemon_data = []
                for i, card in enumerate(pokemon_cards, 1):
                    try:
                        # 画像要素を取得
                        img_element = await card.query_selector("a > div.pokemon-card__image > div.pokemon-card__character > img")
                        if img_element:
                            src = await img_element.get_attribute("src")
                            srcset = await img_element.get_attribute("srcset")
                            alt = await img_element.get_attribute("alt")
                            
                            if src:
                                # ポケモン名を抽出（パスから）
                                pokemon_name = self.extract_pokemon_name(src)
                                if pokemon_name:
                                    # 高解像度画像を優先（srcsetから2x画像を取得）
                                    high_res_url = self.get_high_res_url(src, srcset)
                                    pokemon_data.append({
                                        'name': pokemon_name,
                                        'url': high_res_url,
                                        'index': i
                                    })
                                    print(f"[{i}] {pokemon_name}: {high_res_url}")
                    except Exception as e:
                        print(f"カード{i}の処理中にエラー: {e}")
                        continue
                
                # 画像をダウンロード
                await self.download_images(pokemon_data)
                
            except Exception as e:
                print(f"スクレイピング中にエラーが発生: {e}")
            finally:
                await browser.close()
    
    def extract_pokemon_name(self, src_path):
        """画像パスからポケモン名を抽出"""
        # ../../images/pokemon/falinks/roster/roster-falinks.png から "falinks" を抽出
        pattern = r'/pokemon/([^/]+)/'
        match = re.search(pattern, src_path)
        if match:
            pokemon_name = match.group(1)
            # ハイフン区切りの各単語の先頭を大文字にして返す
            return '-'.join(word.capitalize() for word in pokemon_name.split('-'))
        return None
    
    def get_high_res_url(self, src, srcset):
        """高解像度画像のURLを取得"""
        if srcset:
            # srcsetから2x画像を取得
            srcset_parts = srcset.split(',')
            for part in srcset_parts:
                part = part.strip()
                if '2x' in part:
                    # 2x画像のパスを抽出
                    high_res_path = part.split(' ')[0]
                    return urljoin(self.base_url, high_res_path)
        
        # srcsetがない場合はsrcを使用
        return urljoin(self.base_url, src)
    
    async def download_images(self, pokemon_data):
        """画像をダウンロード"""
        async with httpx.AsyncClient() as client:
            for pokemon in pokemon_data:
                try:
                    print(f"ダウンロード中: {pokemon['name']}")
                    response = await client.get(pokemon['url'])
                    response.raise_for_status()
                    
                    # ファイル拡張子を取得
                    file_extension = pokemon['url'].split('.')[-1].split('?')[0]
                    if file_extension not in ['png', 'jpg', 'jpeg', 'webp']:
                        file_extension = 'png'
                    
                    # ファイル名を生成（ポケモン名の最初を大文字に）
                    filename = f"{pokemon['name']}.{file_extension}"
                    filepath = self.output_dir / filename
                    
                    # ファイルに保存
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"保存完了: {filepath}")
                    
                except Exception as e:
                    print(f"{pokemon['name']}のダウンロード中にエラー: {e}")
                    continue
    
    async def run(self):
        """スクレイパーを実行"""
        print("Pokemon UNITE アイコン画像スクレイパーを開始...")
        await self.scrape_pokemon_images()
        print("スクレイピング完了!")

async def main():
    """メイン関数"""
    scraper = UniteImageScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())

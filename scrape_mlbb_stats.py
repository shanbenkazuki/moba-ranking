import asyncio
import aiosqlite
import os
import logging
import aiohttp
from datetime import datetime
from playwright.async_api import async_playwright
# 最新パッチ情報取得のためのインポート
from scrape_mlbb_latest_patch import MLBBPatchScraper

# --- ログ設定 ---
def setup_logging():
    """ログ設定を初期化"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'mlbb/mlbb_scraping_{today}.log')
    
    # ログディレクトリを作成
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # ロガーの設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class MLBBScraper:
    """Mobile Legends Bang Bang ランキングスクレイパー"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.browser = None
        self.page = None
        
    async def launch_browser(self):
        """ブラウザを起動"""
        playwright = await async_playwright().__aenter__()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        self.logger.info('Playwrightブラウザの起動に成功')
        
    async def close_browser(self):
        """ブラウザを終了"""
        if self.browser:
            await self.browser.close()
            self.logger.info('Playwrightブラウザを正常に終了')
            
    async def navigate_to_ranking_page(self):
        """ランキングページにアクセス"""
        await self.page.goto('https://m.mobilelegends.com/rank', wait_until='networkidle')
        self.logger.info('指定URLをオープン')
        
    async def close_privacy_policy(self):
        """プライバシーポリシーのポップアップを閉じる"""
        await self.page.wait_for_selector('div.mt-cb-policy-close')
        await self.page.click('#mt-cb-policy > div > div.mt-cb-policy-close')
        self.logger.info('プライバシーポリシーのポップアップをクローズ')
        
    async def select_rank(self):
        """ランクを選択（Mythic）"""
        # 指定されたXPathの要素をクリック
        xpath_selector = '//*[@id="root"]/div[1]/div[5]/div/div[1]/div[1]/div[2]/div[2]'
        await self.page.wait_for_selector(f'xpath={xpath_selector}', timeout=10000)
        self.logger.info('指定されたXPathの要素を確認')
        
        await self.page.click(f'xpath={xpath_selector}')
        self.logger.info('指定されたXPathの要素をクリック')
        
        # Mythic選択
        mythic_xpath = '//*[@id="root"]/div[1]/div[5]/div/div[1]/div[1]/div[2]/div[1]/div/div[4]'
        await self.page.wait_for_selector(f'xpath={mythic_xpath}')
        await self.page.click(f'xpath={mythic_xpath}')
        self.logger.info('『Mythic』ランクを選択')
        
    async def scroll_to_load_all_data(self):
        """スクロールして全データを読み込み"""
        # Seleniumのロジックに合わせてXPathを変更
        scroll_target_xpath = '//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div'
        
        try:
            await self.page.wait_for_selector(f'xpath={scroll_target_xpath}')
            self.logger.info('スクロール対象の要素を取得')
            
            # Seleniumのロジックと同様のスクロール処理
            await self.page.evaluate("""
                async (xpath) => {
                    const target_element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (!target_element) {
                        throw new Error('スクロール対象の要素が見つかりません');
                    }
                    
                    let lastHeight = target_element.scrollHeight;
                    
                    while (true) {
                        target_element.scrollTo(0, target_element.scrollHeight);
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        
                        let newHeight = target_element.scrollHeight;
                        if (newHeight === lastHeight) {
                            break;
                        }
                        lastHeight = newHeight;
                    }
                }
            """, scroll_target_xpath)
            
            self.logger.info('データの読み込み完了（スクロール処理終了）')
            
        except Exception as scroll_error:
            self.logger.error(f'スクロール処理中にエラー発生: {scroll_error}')
            raise scroll_error
        
    async def extract_hero_data(self):
        """ヒーローデータを抽出"""
        hero_meta_data = await self.page.evaluate("""
            () => {
                // 親要素のXPath
                const parentXpath = '//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div';
                const parentElement = document.evaluate(parentXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                
                if (!parentElement) {
                    console.error('親要素が見つかりません');
                    return [];
                }
                
                // 子要素（div）の数を取得
                const childDivs = parentElement.children;
                console.log(`取得対象の子要素数: ${childDivs.length}`);
                
                const data = [];
                
                // 各子要素からデータを抽出
                for (let i = 0; i < childDivs.length; i++) {
                    const index = i + 1; // XPathは1ベースのインデックス
                    
                    // 各要素のXPath（絶対パス）
                    const heroNameXpath = `//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div/div[${index}]/div[2]/div[2]/span`;
                    const pickRateXpath = `//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div/div[${index}]/div[3]/span`;
                    const winRateXpath = `//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div/div[${index}]/div[4]/span`;
                    const banRateXpath = `//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div/div[${index}]/div[5]/span`;
                    const iconImageXpath = `//*[@id="root"]/div[1]/div[5]/div/div[2]/div/div[2]/div/div[${index}]/div[2]/div[1]/img`;
                                                    
                    
                    const heroNameElement = document.evaluate(heroNameXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    const pickRateElement = document.evaluate(pickRateXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    const winRateElement = document.evaluate(winRateXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    const banRateElement = document.evaluate(banRateXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    const iconImageElement = document.evaluate(iconImageXpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    
                    if (heroNameElement && pickRateElement && winRateElement && banRateElement) {
                        const hero_name = heroNameElement.textContent.trim();
                        const pick_rate = parseFloat(pickRateElement.textContent.replace("%", ""));
                        const win_rate = parseFloat(winRateElement.textContent.replace("%", ""));
                        const ban_rate = parseFloat(banRateElement.textContent.replace("%", ""));
                        const icon_src = iconImageElement ? iconImageElement.src : null;
                        
                        data.push({
                            hero: hero_name,
                            win_rate: win_rate,
                            pick_rate: pick_rate,
                            ban_rate: ban_rate,
                            icon_src: icon_src
                        });
                        
                        console.log(`ヒーロー ${index}: ${hero_name} - Pick: ${pick_rate}%, Win: ${win_rate}%, Ban: ${ban_rate}%`);
                    } else {
                        console.warn(`ヒーロー ${index}: 必要な要素が見つかりません`);
                        console.warn(`  - heroName: ${!!heroNameElement}, pickRate: ${!!pickRateElement}, winRate: ${!!winRateElement}, banRate: ${!!banRateElement}`);
                    }
                }
                
                console.log(`合計取得データ数: ${data.length}`);
                return data;
            }
        """)
        
        self.logger.info(f'抽出対象のヒーローデータ件数: {len(hero_meta_data)}')
        
        # データベースに接続してキャラクターの存在確認と画像保存
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, 'moba_log.db')
        
        async with aiosqlite.connect(db_path) as db:
            await db.execute('PRAGMA foreign_keys = ON;')
            
            # MLBBのゲームIDを取得
            game_id = await self.get_mlbb_game_id(db)
            
            for hero in hero_meta_data:
                # キャラクターが存在するかチェック
                async with db.execute(
                    'SELECT id FROM characters WHERE english_name = ? AND game_id = ?',
                    (hero['hero'], game_id)
                ) as cursor:
                    character_result = await cursor.fetchone()
                
                if not character_result and hero['icon_src']:
                    # キャラクターが存在しない場合、アイコン画像を保存
                    await self.save_hero_icon(hero['hero'], hero['icon_src'])
        
        return hero_meta_data
        
    async def extract_reference_date(self):
        """参照日時を抽出"""
        reference_date_str = await self.page.evaluate("""
            () => {
                const xpath = '//*[@id="root"]/div[1]/div[5]/div/div[1]/div[2]/div[2]/span';
                const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return element ? element.textContent : null;
            }
        """)
        
        if not reference_date_str:
            raise Exception('参照日時の要素が見つかりません')
        
        self.logger.info(f'参照日時文字列を取得: {reference_date_str}')
        
        date_part, time_part = reference_date_str.split(' ')
        day, month, year = date_part.split('-')
        reference_date = f'{year}-{month}-{day}'
        
        self.logger.info(f'整形済み参照日時: {reference_date}')
        return reference_date
        
    async def get_mlbb_game_id(self, db):
        """MLBBのゲームIDを取得"""
        async with db.execute('SELECT id FROM games WHERE game_code = ?', ('mlbb',)) as cursor:

            game_result = await cursor.fetchone()
            if not game_result:
                raise Exception('MLBBのゲーム情報が見つかりません')
        
        game_id = game_result[0]
        self.logger.info(f'MLBBのgame_id: {game_id}')
        return game_id
        
    async def get_latest_patch_id(self, db, game_id):
        """最新のパッチIDを取得"""
        async with db.execute(
            'SELECT id FROM patches WHERE game_id = ? ORDER BY release_date DESC LIMIT 1',
            (game_id,)
        ) as cursor:
            patch_result = await cursor.fetchone()
            latest_patch_id = patch_result[0] if patch_result else None
        
        if latest_patch_id:
            self.logger.info(f'最新のpatch_id: {latest_patch_id}')
        else:
            self.logger.warning('patchesテーブルにMLBBのデータがありません')
            
        return latest_patch_id
        
    async def save_hero_data(self, hero_meta_data, reference_date):
        """ヒーローデータをデータベースに保存"""
        # データディレクトリを作成
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, 'moba_log.db')
        async with aiosqlite.connect(db_path) as db:
            await db.execute('PRAGMA foreign_keys = ON;')
            self.logger.info('SQLite (moba_log.db) に接続成功')
            
            game_id = await self.get_mlbb_game_id(db)
            latest_patch_id = await self.get_latest_patch_id(db, game_id)
            
            await db.execute('BEGIN TRANSACTION')
            try:
                for hero in hero_meta_data:
                    await self.process_single_hero(db, hero, reference_date, game_id, latest_patch_id)
                
                await db.commit()
                self.logger.info('SQLite (moba_log.db) へのコミットに成功')
            except Exception as db_insert_error:
                await db.rollback()
                raise db_insert_error

    async def update_japanese_names(self, hero_meta_data):
        """ブラウザが開いている間に日本語名を取得・更新"""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, 'moba_log.db')
        async with aiosqlite.connect(db_path) as db:
            await db.execute('PRAGMA foreign_keys = ON;')
            
            game_id = await self.get_mlbb_game_id(db)
            
            # 日本語名が未設定のキャラクターを特定し、日本語名を取得
            for hero in hero_meta_data:
                async with db.execute(
                    'SELECT id, japanese_name FROM characters WHERE english_name = ? AND game_id = ?',
                    (hero['hero'], game_id)
                ) as cursor:
                    character_result = await cursor.fetchone()
                
                if not character_result:
                    # 新規キャラクターを挿入
                    await db.execute(
                        'INSERT INTO characters (game_id, english_name) VALUES (?, ?)',
                        (game_id, hero['hero'])
                    )
                    # 挿入されたキャラクターのIDを取得
                    async with db.execute(
                        'SELECT id, japanese_name FROM characters WHERE english_name = ? AND game_id = ?',
                        (hero['hero'], game_id)
                    ) as cursor:
                        character_result = await cursor.fetchone()
                    self.logger.info(f"新規キャラクター '{hero['hero']}' を characters テーブルに挿入")
                
                character_id = character_result[0]
                japanese_name = character_result[1]
                
                # japanese_nameがNULLの場合、MLJPwikiから取得
                if japanese_name is None:
                    japanese_name = await self.get_japanese_name_from_wiki(hero['hero'])
                    if japanese_name:
                        await db.execute(
                            'UPDATE characters SET japanese_name = ? WHERE id = ?',
                            (japanese_name, character_id)
                        )
                        await db.commit()
                        self.logger.info(f"キャラクター '{hero['hero']}' の日本語名を更新: {japanese_name}")
                
    async def process_single_hero(self, db, hero, reference_date, game_id, latest_patch_id):
        """単一のヒーローデータを処理（統計データのみ）"""
        # キャラクターIDを取得（この時点で既に存在することが保証されている）
        async with db.execute(
            'SELECT id FROM characters WHERE english_name = ? AND game_id = ?',
            (hero['hero'], game_id)
        ) as cursor:
            character_result = await cursor.fetchone()
        
        if not character_result:
            self.logger.error(f"キャラクター '{hero['hero']}' が見つかりません")
            return
            
        character_id = character_result[0]
        
        # 統計データが既に存在するかチェック
        async with db.execute(
            'SELECT 1 FROM mlbb_stats WHERE character_id = ? AND reference_date = ? AND rank_info = ? AND patch_id = ?',
            (character_id, reference_date, 'Mythic', latest_patch_id)
        ) as cursor:
            stats_exists = await cursor.fetchone()
        
        if stats_exists:
            self.logger.info(f"'{hero['hero']}' のデータはすでに存在するためスキップ")
            return
        
        # 統計データを挿入
        await db.execute("""
            INSERT INTO mlbb_stats 
            (character_id, win_rate, pick_rate, ban_rate, reference_date, rank_info, patch_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id,
            hero['win_rate'],
            hero['pick_rate'],
            hero['ban_rate'],
            reference_date,
            'Mythic',
            latest_patch_id
        ))
        self.logger.info(f"mlbb_stats テーブルに '{hero['hero']}' のデータを挿入")
        
    async def get_japanese_name_from_wiki(self, english_name):
        """MLJPwikiから日本語名を取得"""
        try:
            # 新しいページを作成してwikiにアクセス
            wiki_page = await self.browser.new_page()
            await wiki_page.goto('https://mljpwiki.com/heros', wait_until='networkidle')
            
            # alt属性がenglish_nameと一致するimg要素を探す
            japanese_name = await wiki_page.evaluate("""
                (englishName) => {
                    const imgElements = document.querySelectorAll('#DataTables_Table_0 img');
                    for (const img of imgElements) {
                        if (img.alt === englishName) {
                            // 親要素のテキストを取得
                            const parentText = img.closest('a').textContent.trim();
                            // "{japanese_name} (english_name)" 形式から日本語名を抽出
                            const match = parentText.match(/^(.+?)\\s*\\(/);
                            if (match) {
                                return match[1].trim();
                            }
                        }
                    }
                    return null;
                }
            """, english_name)
            
            await wiki_page.close()
            
            if japanese_name:
                self.logger.info(f"MLJPwikiから日本語名を取得: {english_name} -> {japanese_name}")
            else:
                self.logger.warning(f"MLJPwikiで日本語名が見つかりません: {english_name}")
            
            return japanese_name
            
        except Exception as e:
            self.logger.error(f"MLJPwikiからの日本語名取得に失敗: {english_name} - エラー: {e}")
            return None
        
    async def record_scraping_status(self, scraping_failed, scraping_error_msg):
        """スクレイピング結果をステータステーブルに記録"""
        try:
            # データディレクトリを作成
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            status_db_path = os.path.join(data_dir, 'moba_log.db')
            async with aiosqlite.connect(status_db_path) as status_db:
                # MLBBのゲームIDを取得
                async with status_db.execute('SELECT id FROM games WHERE game_code = ?', ('mlbb',)) as cursor:
                    game_result = await cursor.fetchone()
                    if not game_result:
                        self.logger.error('MLBBのゲーム情報が見つかりません')
                        return
                
                game_id = game_result[0]
                current_date = datetime.now().strftime('%Y-%m-%d')
                
                await status_db.execute(
                    """INSERT INTO scraper_logs (game_id, scraper_status, error_message, scraper_date)
                       VALUES (?, ?, ?, ?)""",
                    (game_id, 1 if scraping_failed else 0, scraping_error_msg if scraping_failed else None, current_date)
                )
                await status_db.commit()
            self.logger.info('scraper_logs テーブルへの記録に成功')
        except Exception as status_error:
            self.logger.error(f'scraper_logs テーブルへの記録に失敗: {status_error}')
            
    async def run_scraping(self):
        """スクレイピング処理を実行"""
        scraping_failed = False
        scraping_error_msg = ''
        
        try:
            self.logger.info('Mobile Legends ランクスクレイピング処理を開始')
            
            # 最新パッチ情報を取得
            self.logger.info('最新パッチ情報を取得中...')
            patch_scraper = MLBBPatchScraper()
            patch_success = await patch_scraper.run()
            
            if not patch_success:
                self.logger.warning('最新パッチ情報の取得に失敗しましたが、処理を続行します')
            else:
                self.logger.info('最新パッチ情報の取得が完了しました')
            
            await self.launch_browser()
            await self.navigate_to_ranking_page()
            await self.close_privacy_policy()
            await self.select_rank()
            await self.scroll_to_load_all_data()
            
            hero_meta_data = await self.extract_hero_data()
            reference_date = await self.extract_reference_date()
            
            # ブラウザが開いている間に日本語名を取得・更新
            self.logger.info('日本語名の取得・更新を開始')
            await self.update_japanese_names(hero_meta_data)
            self.logger.info('日本語名の取得・更新が完了')
            
            await self.close_browser()
            
            await self.save_hero_data(hero_meta_data, reference_date)
            
            self.logger.info('スクレイピングおよびデータ保存処理を正常に完了')
            
        except Exception as error:
            scraping_failed = True
            scraping_error_msg = str(error)
            self.logger.error(f'処理中にエラーが発生: {error}')
            await self.close_browser()
        
        await self.record_scraping_status(scraping_failed, scraping_error_msg)

    async def save_hero_icon(self, hero_name, icon_src):
        """ヒーローのアイコン画像を保存"""
        try:
            # hero_imagesディレクトリを作成
            hero_images_dir = os.path.join(os.path.dirname(__file__), 'hero_images')
            os.makedirs(hero_images_dir, exist_ok=True)
            
            # 画像をダウンロード
            async with aiohttp.ClientSession() as session:
                async with session.get(icon_src) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # ファイル名をhero_nameにして.webp形式で保存
                        file_path = os.path.join(hero_images_dir, f'{hero_name}.webp')
                        with open(file_path, 'wb') as f:
                            f.write(image_data)
                        
                        self.logger.info(f"ヒーローアイコンを保存: {file_path}")
                    else:
                        self.logger.warning(f"画像のダウンロードに失敗: {hero_name} - ステータス: {response.status}")
        except Exception as e:
            self.logger.error(f"ヒーローアイコンの保存に失敗: {hero_name} - エラー: {e}")

async def main():
    """メイン関数"""
    scraper = MLBBScraper()
    await scraper.run_scraping()

# メイン関数の実行
if __name__ == "__main__":
    asyncio.run(main())


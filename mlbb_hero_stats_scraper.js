const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

// --- ログ設定 ---
const logDir = path.join(__dirname, 'logs');
fs.mkdirSync(logDir, { recursive: true });
const today = new Date().toISOString().split('T')[0];
const logFile = path.join(logDir, `mlbb_scraping_${today}.log`);

// ロギング関数
function log(level, message) {
    const timestamp = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });
    const logMessage = `${timestamp} - ${level} - ${message}`;
    console.log(logMessage);
    fs.appendFileSync(logFile, logMessage + '\n', { encoding: 'utf8' });
}

async function main() {
  let scrapingFailed = false;
  let scrapingErrorMsg = '';
  let browser;
  
  try {
    log('INFO', 'Mobile Legends ランクスクレイピング処理を開始');
    
    // Puppeteerの起動
    browser = await puppeteer.launch({
      headless: false,
      defaultViewport: { width: 1920, height: 1080 },
      args: ['--window-size=1920,1080']
    });
    
    const page = await browser.newPage();
    log('INFO', 'Puppeteerブラウザの起動に成功');
    
    // ページにアクセス
    await page.goto('https://m.mobilelegends.com/rank', { waitUntil: 'networkidle2' });
    log('INFO', '指定URLをオープン');
    
    // プライバシーポリシーのクローズボタンをクリック
    await page.waitForSelector('div.mt-cb-policy-close');
    await page.click('#mt-cb-policy > div > div.mt-cb-policy-close');
    log('INFO', 'プライバシーポリシーのポップアップをクローズ');
    
    // 1. 期間範囲タブクリック
    const periodTabSelector = 'div.mt-2684835.mt-uid-99964.mt-empty';
    await page.waitForSelector(periodTabSelector);
    await page.click(periodTabSelector);
    log('INFO', '期間範囲タブをクリック');
    
    // 2. Past 7 days選択
    const pastDaysSelector = 'div.mt-2684831.mt-uid-99880.mt-empty.mt-list-item';
    await page.waitForSelector(pastDaysSelector);
    await page.click(pastDaysSelector);
    log('INFO', '『Past 7 days』オプションを選択');
    
    // 3. ランク選択タブクリック
    const rankTabSelector = 'div.mt-2684885.mt-uid-99957.mt-empty';
    await page.waitForSelector(rankTabSelector);
    await page.click(rankTabSelector);
    log('INFO', 'ランク選択タブをクリック');
    
    // 4. Mythic選択
    const mythicSelector = 'div.mt-2684882.mt-uid-99849.mt-empty.mt-list-item';
    await page.waitForSelector(mythicSelector);
    await page.click(mythicSelector);
    log('INFO', '『Mythic』ランクを選択');
    
    // 5. スクロール処理
    const scrollTargetSelector = 'div.mt-2684827.mt-uid-99942.mt-empty > div';
    await page.waitForSelector(scrollTargetSelector);
    log('INFO', 'スクロール対象の要素を取得');
    
    await page.evaluate(async (selector) => {
      const scrollElement = document.querySelector(selector);
      let lastHeight = scrollElement.scrollHeight;
      
      while (true) {
        scrollElement.scrollTo(0, scrollElement.scrollHeight);
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        let newHeight = scrollElement.scrollHeight;
        if (newHeight === lastHeight) {
          break;
        }
        lastHeight = newHeight;
      }
    }, scrollTargetSelector);
    
    log('INFO', 'データの読み込み完了（スクロール処理終了）');
    
    // HTMLの取得とデータの抽出
    const heroMetaData = await page.evaluate(() => {
      const rateList = document.querySelectorAll("div.mt-2684827.mt-uid-99942.mt-empty > div > div");
      const data = [];
      for (const heroRate of rateList) {
        const hero_name = heroRate.querySelector("div.mt-2693555 > div.mt-2693412 > span").textContent;
        const pick_rate = parseFloat(heroRate.querySelector("div.mt-2684925 > span").textContent.replace("%", ""));
        const win_rate = parseFloat(heroRate.querySelector("div.mt-2684926 > span").textContent.replace("%", ""));
        const ban_rate = parseFloat(heroRate.querySelector("div.mt-2687632 > span").textContent.replace("%", ""));
        
        data.push({
          hero: hero_name,
          win_rate: win_rate,
          pick_rate: pick_rate,
          ban_rate: ban_rate
        });
      }
      return data;
    });
    
    log('INFO', `抽出対象のヒーローデータ件数: ${heroMetaData.length}`);
    
    // 参照日時を取得
    const referenceDateStr = await page.evaluate(() => {
      const element = document.querySelector("div.mt-2693419.mt-uid-99950.mt-text > span");
      return element ? element.textContent : null;
    });
    
    if (!referenceDateStr) {
      throw new Error('参照日時の要素が見つかりません');
    }
    
    log('INFO', `参照日時文字列を取得: ${referenceDateStr}`);
    
    const [datePart, timePart] = referenceDateStr.split(' ');
    const [day, month, year] = datePart.split('-');
    const referenceDate = `${year}-${month}-${day}`;
    
    log('INFO', `整形済み参照日時: ${referenceDate}`);
    
    await browser.close();
    log('INFO', 'Puppeteerブラウザを正常に終了');
    
    // SQLite (mlbb.db)への接続とデータ保存処理
    const dbPath = '/Users/yamamotokazuki/develop/moba-ranking/mlbb.db';
    const db = await open({
      filename: dbPath,
      driver: sqlite3.Database
    });
    await db.run('PRAGMA foreign_keys = ON;');
    log('INFO', 'SQLite (mlbb.db) に接続成功');
    
    const patchResult = await db.get('SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1');
    let latestPatchNumber = patchResult ? patchResult.patch_number : null;
    
    if (latestPatchNumber) {
      log('INFO', `最新のpatch_number: ${latestPatchNumber}`);
    } else {
      log('WARNING', 'patchesテーブルにデータがありません');
    }
    
    await db.run('BEGIN TRANSACTION');
    try {
      for (const hero of heroMetaData) {
        const heroExists = await db.get('SELECT english_name FROM heroes WHERE english_name = ?', hero.hero);
        if (!heroExists) {
          await db.run('INSERT INTO heroes (english_name) VALUES (?)', hero.hero);
          log('INFO', `新規ヒーロー '${hero.hero}' を heroes テーブルに挿入`);
        }
        
        const statsExists = await db.get(
          'SELECT 1 FROM hero_stats WHERE hero_name = ? AND reference_date = ? AND rank = ? AND patch_number = ?',
          [hero.hero, referenceDate, 'Mythic', latestPatchNumber]
        );
        
        if (statsExists) {
          log('INFO', `'${hero.hero}' のデータはすでに存在するためスキップ`);
          continue;
        }
        
        await db.run(`
          INSERT INTO hero_stats 
          (hero_name, win_rate, pick_rate, ban_rate, reference_date, rank, patch_number)
          VALUES (?, ?, ?, ?, ?, ?, ?)
        `, [
          hero.hero,
          hero.win_rate,
          hero.pick_rate,
          hero.ban_rate,
          referenceDate,
          'Mythic',
          latestPatchNumber
        ]);
        log('INFO', `hero_stats テーブルに '${hero.hero}' のデータを挿入`);
      }
      await db.run('COMMIT');
      log('INFO', 'SQLite (mlbb.db) へのコミットに成功');
    } catch (dbInsertError) {
      await db.run('ROLLBACK');
      throw dbInsertError;
    } finally {
      await db.close();
      log('INFO', 'SQLite (mlbb.db) 接続を正常にクローズ');
    }
    
    log('INFO', 'スクレイピングおよびデータ保存処理を正常に完了');
    
  } catch (error) {
    scrapingFailed = true;
    scrapingErrorMsg = error.message;
    log('ERROR', `処理中にエラーが発生: ${error.message}`);
    if (browser) {
      await browser.close();
    }
  }
  
  // ----- スクレイピング結果を moba.db の scraper_status テーブルへ記録 -----
  try {
    const statusDbPath = '/Users/yamamotokazuki/develop/moba-ranking/moba.db';
    const statusDb = await open({
      filename: statusDbPath,
      driver: sqlite3.Database
    });
    // 日付を "YYYY-MM-DD" の形式に整形
    const currentDate = new Date().toISOString().split('T')[0];
    await statusDb.run(
      `INSERT INTO scraper_status (scraper_status, game_title, error_message, scraper_date)
       VALUES (?, ?, ?, ?)`,
      [scrapingFailed ? 1 : 0, 'mlbb', scrapingFailed ? scrapingErrorMsg : null, currentDate]
    );
    await statusDb.close();
    log('INFO', 'scraper_status テーブルへの記録に成功');
  } catch (statusError) {
    log('ERROR', `scraper_status テーブルへの記録に失敗: ${statusError.message}`);
  }
}

// メイン関数の実行
main().catch(error => {
  log('ERROR', `メイン処理で未捕捉の例外が発生: ${error.message}`);
});

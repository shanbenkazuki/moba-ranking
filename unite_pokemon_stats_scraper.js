const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// ログファイルのパス設定
const logDir = '/Users/yamamotokazuki/develop/moba-ranking/logs';
const logFile = path.join(logDir, 'unite_pokemon_stats_scraper.log');

// ログ出力用の簡易関数（コンソール出力とファイルへの追記）
function log(level, message) {
  const logMessage = `[${new Date().toISOString()}] [${level}] ${message}\n`;
  console.log(logMessage);
  fs.appendFileSync(logFile, logMessage);
}

// SQLiteにレコードを挿入する関数（重複チェック付き）
function insertIfNotExists(db, englishName) {
  return new Promise((resolve, reject) => {
    db.get(
      'SELECT english_name FROM pokemons WHERE english_name = ?',
      [englishName],
      (err, row) => {
        if (err) {
          log('ERROR', `SELECTエラー: ${err.message}`);
          return reject(err);
        }
        if (row) {
          log('INFO', `重複のためスキップ: ${englishName}`);
          return resolve(false);
        } else {
          db.run(
            'INSERT INTO pokemons (english_name) VALUES (?)',
            [englishName],
            function (err) {
              if (err) {
                log('ERROR', `INSERTエラー: ${err.message}`);
                return reject(err);
              }
              log('INFO', `INSERT成功: ${englishName}`);
              resolve(true);
            }
          );
        }
      }
    );
  });
}

(async () => {
  let browser;
  let db;
  try {
    // Puppeteerの起動
    browser = await puppeteer.launch({
      headless: false,
      defaultViewport: { width: 1920, height: 1080 },
      args: ['--window-size=1920,1080']
    });
    const page = await browser.newPage();
    log('INFO', 'Puppeteerブラウザの起動に成功');

    // 指定のURLにアクセス（ネットワークアイドル状態を待つ）
    await page.goto('https://uniteapi.dev/meta', { waitUntil: 'networkidle2' });
    log('INFO', '指定URLをオープン');

    // Node.jsのsetTimeoutを使用して10秒待機
    await new Promise(resolve => setTimeout(resolve, 10000));
    log('INFO', '10秒待機完了');

    // =====================
    // ★ pタグからpokemonの英語名を取得してDBへ保存する処理（既存コード例）
    // =====================
    const pTexts = await page.$$eval(
      '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div:nth-child(4) > div > div > div > p',
      elements => elements.map(el => el.innerText.trim())
    );
    log('INFO', `取得したpタグの中身: ${JSON.stringify(pTexts)}`);

    // SQLiteデータベースに接続
    db = new sqlite3.Database('/Users/yamamotokazuki/develop/moba-ranking/unite.db', (err) => {
      if (err) {
        log('ERROR', `DB接続エラー: ${err.message}`);
        throw err;
      }
      log('INFO', 'SQLite DBに接続しました');
    });

    // 取得した各テキストについて、重複チェック後にINSERTする
    for (const englishName of pTexts) {
      try {
        await insertIfNotExists(db, englishName);
      } catch (err) {
        log('ERROR', `レコード処理エラー (${englishName}): ${err.message}`);
      }
    }

    // =====================
    // ★ 勝率・ピック率・バン率の取得処理
    // =====================

    // ① 勝率の取得
    const winRates = await page.$$eval(
      '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(1) > div > div > div',
      elements => {
        const rates = {};
        elements.forEach(element => {
          const img = element.querySelector('img');
          if (!img) return;
          const imgSrc = img.getAttribute('src');
          const filename = imgSrc.split('/').pop();
          let pokemon_name;
          if (filename.includes("Urshifu_Single")) {
            pokemon_name = "Urshifu";
          } else if (filename.includes("Meowscara")) {
            pokemon_name = "Meowscarada";
          } else {
            pokemon_name = filename.split('_').pop().split('.')[0];
          }
          const rateEl = element.querySelector('.sc-71f8e1a4-1');
          const win_rate = rateEl ? rateEl.getAttribute('value') : null;
          rates[pokemon_name] = win_rate;
        });
        return rates;
      }
    );
    log('INFO', `勝率: ${JSON.stringify(winRates)}`);

    // ② ピック率の取得
    const pickRates = await page.$$eval(
      '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(2) > div > div > div',
      elements => {
        const rates = {};
        elements.forEach(element => {
          const img = element.querySelector('img');
          if (!img) return;
          const imgSrc = img.getAttribute('src');
          const filename = imgSrc.split('/').pop();
          let pokemon_name;
          if (filename.includes("Urshifu_Single")) {
            pokemon_name = "Urshifu";
          } else if (filename.includes("Meowscara")) {
            pokemon_name = "Meowscarada";
          } else {
            pokemon_name = filename.split('_').pop().split('.')[0];
          }
          const rateEl = element.querySelector('.sc-71f8e1a4-1');
          const pick_rate = rateEl ? rateEl.getAttribute('value') : null;
          rates[pokemon_name] = pick_rate;
        });
        return rates;
      }
    );
    log('INFO', `ピック率: ${JSON.stringify(pickRates)}`);

    // ③ バン率の取得
    const banRates = await page.$$eval(
      '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(3) > div > div > div',
      elements => {
        const rates = {};
        elements.forEach(element => {
          const img = element.querySelector('img');
          if (!img) return;
          const imgSrc = img.getAttribute('src');
          const filename = imgSrc.split('/').pop();
          let pokemon_name;
          if (filename.includes("Urshifu_Single")) {
            pokemon_name = "Urshifu";
          } else if (filename.includes("Meowscara")) {
            pokemon_name = "Meowscarada";
          } else {
            pokemon_name = filename.split('_').pop().split('.')[0];
          }
          const rateEl = element.querySelector('.sc-71f8e1a4-1');
          const ban_rate = rateEl ? rateEl.getAttribute('value') : null;
          rates[pokemon_name] = ban_rate;
        });
        return rates;
      }
    );
    log('INFO', `バン率: ${JSON.stringify(banRates)}`);

  } catch (error) {
    log('ERROR', error);
  } finally {
    if (browser) {
      await browser.close();
      log('INFO', 'ブラウザを閉じました');
    }
    if (db) {
      db.close((err) => {
        if (err) {
          log('ERROR', `DBクローズエラー: ${err.message}`);
        } else {
          log('INFO', 'SQLite DBを閉じました');
        }
      });
    }
  }
})();

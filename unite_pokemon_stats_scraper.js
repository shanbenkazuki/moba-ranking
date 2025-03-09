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

// SQLiteに新規ポケモンを挿入する関数（重複チェック付き）
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

// SQLiteから全ポケモンを取得する関数
function getAllPokemons(db) {
  return new Promise((resolve, reject) => {
    db.all('SELECT english_name FROM pokemons', (err, rows) => {
      if (err) {
        log('ERROR', `ポケモン取得エラー: ${err.message}`);
        return reject(err);
      }
      resolve(rows);
    });
  });
}

// patchesテーブルから最新のpatch_numberを取得する関数
function getLatestPatchNumber(db) {
  return new Promise((resolve, reject) => {
    db.get(
      'SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1',
      (err, row) => {
        if (err) {
          log('ERROR', `patchesテーブル取得エラー: ${err.message}`);
          return reject(err);
        }
        if (row) {
          log('INFO', `最新のpatch_number取得: ${row.patch_number}`);
          resolve(row.patch_number);
        } else {
          log('INFO', 'patchesテーブルにデータがありません');
          resolve(null);
        }
      }
    );
  });
}

// pokemon_statsテーブルへ挿入（重複チェック付き）
function insertPokemonStatsIfNotExists(db, stats) {
  return new Promise((resolve, reject) => {
    db.get(
      'SELECT pokemon_name FROM pokemon_stats WHERE pokemon_name = ? AND reference_date = ?',
      [stats.pokemon_name, stats.reference_date],
      (err, row) => {
        if (err) {
          log('ERROR', `pokemon_stats SELECTエラー: ${err.message}`);
          return reject(err);
        }
        if (row) {
          log('INFO', `重複のためpokemon_statsへはスキップ: ${stats.pokemon_name}`);
          return resolve(false);
        } else {
          db.run(
            `INSERT INTO pokemon_stats 
             (pokemon_name, win_rate, pick_rate, ban_rate, reference_date, patch_number, total_game_count) 
             VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [
              stats.pokemon_name,
              stats.win_rate,
              stats.pick_rate,
              stats.ban_rate,
              stats.reference_date,
              stats.patch_number,
              stats.total_game_count
            ],
            function (err) {
              if (err) {
                log('ERROR', `pokemon_stats INSERTエラー: ${err.message}`);
                return reject(err);
              }
              log('INFO', `pokemon_stats INSERT成功: ${stats.pokemon_name}`);
              resolve(true);
            }
          );
        }
      }
    );
  });
}

// スクレイピング取得したポケモン名をDB側の名前に合わせるための正規化関数
function normalizeScrapedName(name) {
  if (name === 'MrMime') return 'Mr. Mime';
  if (name === 'Ninetales') return 'Alolan Ninetales';
  if (name === 'Rapidash') return 'Galarian Rapidash';
  if (name === 'HoOh') return 'Ho-Oh';
  return name;
}

// 取得した各種レートのオブジェクトのキーを正規化する関数
function normalizeRates(rates) {
  const normalized = {};
  for (const key in rates) {
    normalized[normalizeScrapedName(key)] = rates[key];
  }
  return normalized;
}

(async () => {
  let browser;
  let db;
  try {
    // Puppeteerの起動
    browser = await puppeteer.launch({
      headless: true,
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
    // ★ 新しいポケモンの追加確認
    // =====================
    // pタグからポケモンの英語名を取得
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

    // 各英語名について、重複チェック後にINSERTする
    for (const englishName of pTexts) {
      try {
        await insertIfNotExists(db, englishName);
      } catch (err) {
        log('ERROR', `レコード処理エラー (${englishName}): ${err.message}`);
      }
    }

    // =====================
    // ★ 勝率・ピック率・バン率の取得
    // =====================
    // 勝率の取得
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

    // ピック率の取得
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

    // バン率の取得
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

    // ---------------------
    // 取得したレートのオブジェクトのキーを正規化する
    // ---------------------
    const normalizedWinRates = normalizeRates(winRates);
    const normalizedPickRates = normalizeRates(pickRates);
    const normalizedBanRates = normalizeRates(banRates);

    // =====================
    // ★ 参照日・総試合数・パッチ番号の取得
    // =====================
    // 参照日の取得
    await page.waitForSelector('div.m_4081bf90.mantine-Group-root > div:nth-child(1) > p.mantine-focus-auto.simpleStat_count__dG_xB.m_b6d8b162.mantine-Text-root', { timeout: 5000 });
    const rawReferenceDate = await page.evaluate(() => {
      const element = document.querySelector('div.m_4081bf90.mantine-Group-root > div:nth-child(1) > p.mantine-focus-auto.simpleStat_count__dG_xB.m_b6d8b162.mantine-Text-root');
      return element ? element.innerText : null;
    });
    const currentYear = new Date().getFullYear();
    const referenceDate = new Date(`${rawReferenceDate} ${currentYear}`).toISOString().split('T')[0];
    log('INFO', `整形済み参照日: ${referenceDate}`);

    // 総試合数の取得
    await page.waitForSelector('div.m_4081bf90.mantine-Group-root > div:nth-child(2) > p.mantine-focus-auto.simpleStat_count__dG_xB.m_b6d8b162.mantine-Text-root', { timeout: 5000 });
    const totalGameCountText = await page.evaluate(() => {
      const element = document.querySelector('div.m_4081bf90.mantine-Group-root > div:nth-child(2) > p.mantine-focus-auto.simpleStat_count__dG_xB.m_b6d8b162.mantine-Text-root');
      return element ? element.innerText : null;
    });
    log('INFO', `トータルゲームカウント: ${totalGameCountText}`);

    // 最新のパッチ番号をpatchesテーブルから取得
    const patchNumber = await getLatestPatchNumber(db);

    // =====================
    // ★ pokemon_statsテーブルへのデータ保存
    // =====================
    // pokemonsテーブルから全ポケモンの英語名を取得
    const pokemons = await getAllPokemons(db);
    for (const { english_name } of pokemons) {
      // 各ポケモンごとに勝率・ピック率・バン率を取得（取得できなければnull）
      const win_rate = normalizedWinRates[english_name] || null;
      const pick_rate = normalizedPickRates[english_name] || null;
      const ban_rate = normalizedBanRates[english_name] || null;

      const stats = {
        pokemon_name: english_name,
        win_rate: win_rate,
        pick_rate: pick_rate,
        ban_rate: ban_rate,
        reference_date: referenceDate,
        patch_number: patchNumber,
        total_game_count: parseInt(totalGameCountText, 10) || null
      };

      try {
        await insertPokemonStatsIfNotExists(db, stats);
      } catch (err) {
        log('ERROR', `pokemon_stats レコード処理エラー (${english_name}): ${err.message}`);
      }
    }
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

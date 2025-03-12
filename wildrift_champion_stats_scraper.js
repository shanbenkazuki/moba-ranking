const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// ログ出力用関数（日本時間のタイムスタンプ付き）
function logWithJST(message) {
  const now = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });
  const logMessage = `[${now}] ${message}\n`;
  const logPath = "/Users/yamamotokazuki/develop/moba-ranking/logs/wildrift_champion_stats_scraper.log";
  fs.appendFileSync(logPath, logMessage);
}

// 共通のデータ抽出処理（li要素からchampion名、胜率、登场率、BAN率を取得）
async function extractChampionData(page) {
  const data = await page.$$eval("#data-list > li", lis => {
    return lis.map(li => {
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

      return { name, 胜率: winRate, 登场率: pickRate, BAN率: banRate };
    }).filter(item => item.name !== '');
  });
  return data;
}

// 最新のpatch_number（patchesテーブルの最新release_date順でのpatch_numberカラムの値）を取得する関数
function getLatestPatchNumber() {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database("/Users/yamamotokazuki/develop/moba-ranking/wildrift.db", (err) => {
      if (err) return reject(err);
    });
    // release_dateで並び替えて最新のpatch_numberを取得
    db.get("SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1", (err, row) => {
      if (err) {
        db.close();
        return reject(err);
      }
      db.close();
      if (row) {
        resolve(row.patch_number);
      } else {
        resolve(null);
      }
    });
  });
}

// champion_statsテーブルへデータを挿入する関数
function insertChampionStats(championStats, patch_number) {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database("/Users/yamamotokazuki/develop/moba-ranking/wildrift.db", (err) => {
      if (err) return reject(err);
    });
    
    const stmt = db.prepare(`
      INSERT INTO champion_stats 
      (lane, champion_name, win_rate, pick_rate, ban_rate, reference_date, patch_number)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    
    // championStatsオブジェクトの構造は以下のようになっています。
    // {
    //   "参照日": referenceDate,
    //   "上单": [...],
    //   "打野": [...],
    //   "中路": [...],
    //   "下路": [...],
    //   "辅助": [...]
    // }
    const reference_date = championStats["参照日"];
    const lanes = ["上单", "打野", "中路", "下路", "辅助"];
    
    lanes.forEach(lane => {
      if (championStats[lane] && Array.isArray(championStats[lane])) {
        championStats[lane].forEach(champion => {
          stmt.run(
            lane,
            champion.name,
            champion.胜率,
            champion.登场率,
            champion.BAN率,
            reference_date,
            patch_number,
            (err) => {
              if (err) {
                console.error(`Insert error for lane ${lane}:`, err);
              }
            }
          );
        });
      }
    });
    
    stmt.finalize(err => {
      db.close();
      if (err) {
        return reject(err);
      }
      resolve();
    });
  });
}

// scraper_statusテーブルへスクレイピング結果を保存する関数
function insertScraperStatus(status, errorMessage) {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database("/Users/yamamotokazuki/develop/moba-ranking/moba.db", (err) => {
      if (err) return reject(err);
    });
    // 日本時間のタイムスタンプを取得（例："2025/3/12 15:30:00"）
    const jstDate = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });
    db.run(
      `INSERT INTO scraper_status (scraper_status, game_title, error_message, scraper_date)
       VALUES (?, ?, ?, ?)`,
      [status, 'wildrift', errorMessage, jstDate],
      function(err) {
        db.close();
        if (err) return reject(err);
        resolve();
      }
    );
  });
}

(async () => {
  try {
    logWithJST("スクリプト開始");

    // headlessモードでブラウザ起動
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const url = "https://lolm.qq.com/act/a20220818raider/index.html";
    await page.goto(url, { waitUntil: 'networkidle2' });
    logWithJST(`ページをオープン: ${url}`);

    // 参照日を取得（ページオープン後に実施）
    await page.waitForSelector("#data-time");
    const referenceDate = await page.$eval("#data-time", el => el.innerText.trim());
    logWithJST(`参照日を取得: ${referenceDate}`);

    // JSON出力用のオブジェクト
    let champion_stats = { "参照日": referenceDate };

    // ----- 上单（デフォルトタブ） -----
    await page.waitForSelector("#data-list > li");
    logWithJST("上单タブのセレクタ待機完了");
    const topData = await extractChampionData(page);
    champion_stats["上单"] = topData;
    logWithJST("上单データを取得完了");

    // ----- 打野 -----
    await page.waitForSelector("a.btn-place-jungle");
    await page.click("a.btn-place-jungle");
    logWithJST("打野ボタンをクリック");
    await page.waitForSelector("#data-list > li");
    const jungleData = await extractChampionData(page);
    champion_stats["打野"] = jungleData;
    logWithJST("打野データを取得完了");

    // ----- 中路 -----
    await page.waitForSelector("a.btn-place-mid");
    await page.click("a.btn-place-mid");
    logWithJST("中路ボタンをクリック");
    await page.waitForSelector("#data-list > li");
    const midData = await extractChampionData(page);
    champion_stats["中路"] = midData;
    logWithJST("中路データを取得完了");

    // ----- 下路 -----
    await page.waitForSelector("a.btn-place-bot");
    await page.click("a.btn-place-bot");
    logWithJST("下路ボタンをクリック");
    await page.waitForSelector("#data-list > li");
    const botData = await extractChampionData(page);
    champion_stats["下路"] = botData;
    logWithJST("下路データを取得完了");

    // ----- 辅助 -----
    await page.waitForSelector("a.btn-place-sup");
    await page.click("a.btn-place-sup");
    logWithJST("辅助ボタンをクリック");
    await page.waitForSelector("#data-list > li");
    const supData = await extractChampionData(page);
    champion_stats["辅助"] = supData;
    logWithJST("辅助データを取得完了");

    // ログファイルへスクレイピング結果を出力（JSON形式）
    const jsonOutput = JSON.stringify(champion_stats, null, 2);
    const outputFilePath = path.join("/Users/yamamotokazuki/develop/moba-ranking/logs", "wildrift_champion_stats_scraper.log");
    fs.appendFileSync(outputFilePath, `取得データ:\n${jsonOutput}\n`);
    logWithJST("全データをログファイルに出力完了");

    await browser.close();
    logWithJST("ブラウザを閉じました。スクレイピング終了");

    // --- SQLiteへの保存処理 ---
    logWithJST("patchesテーブルから最新のpatch_numberを取得中");
    const patch_number = await getLatestPatchNumber();
    logWithJST(`最新patch_numberを取得: ${patch_number}`);

    logWithJST("champion_statsテーブルへデータを保存中");
    await insertChampionStats(champion_stats, patch_number);
    logWithJST("champion_statsテーブルへデータ保存完了");

    // --- スクレイピング結果をscraper_statusテーブルへ保存（成功の場合） ---
    logWithJST("scraper_statusテーブルへ成功ステータスを保存中");
    await insertScraperStatus(0, null);
    logWithJST("scraper_statusテーブルへデータ保存完了");

  } catch (error) {
    logWithJST(`エラー発生: ${error}`);
    // --- エラー発生時、scraper_statusテーブルへ失敗情報を保存 ---
    try {
      await insertScraperStatus(1, error.toString());
      logWithJST("scraper_statusテーブルへエラーステータスを保存完了");
    } catch (err) {
      logWithJST(`scraper_status保存中に更にエラー発生: ${err}`);
    }
    process.exit(1);
  }
})();

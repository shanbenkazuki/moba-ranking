const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const { TwitterApi } = require('twitter-api-v2');
require('dotenv').config();

// --- ログ設定 --- //
const baseDir = "/Users/yamamotokazuki/develop/moba-ranking";

// ログディレクトリ（/logs/mlbb）を作成
const logDir = path.join(baseDir, "logs", "mlbb");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// 日本時間のタイムスタンプ生成（例：2025-03-13-15-30-45）
const timestampForLog = new Date().toLocaleString('ja-JP', {
  timeZone: 'Asia/Tokyo',
  hour12: false
}).replace(/[\/: ]/g, '-');

// ログファイルのパス
const logFilePath = path.join(logDir, `mlbb_tier_x_poster_${timestampForLog}.log`);

// ログ出力用のヘルパー関数
function logMessage(message) {
  console.log(message);
  const timeStampedMsg = `[${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', hour12: false })}] ${message}\n`;
  fs.appendFileSync(logFilePath, timeStampedMsg);
}

function logError(errorMessage) {
  console.error(errorMessage);
  const timeStampedMsg = `[${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', hour12: false })}] ERROR: ${errorMessage}\n`;
  fs.appendFileSync(logFilePath, timeStampedMsg);
}

// --- ヘルパー関数 --- //
function mean(arr) {
  return arr.reduce((sum, val) => sum + val, 0) / arr.length;
}

function stdDev(arr, arrMean) {
  const variance = arr.reduce((sum, val) => sum + Math.pow(val - arrMean, 2), 0) / arr.length;
  return Math.sqrt(variance);
}

function assignGrade(score) {
  if (score > 1.0) return 'S';
  else if (score > 0.5) return 'A';
  else if (score >= -0.5) return 'B';
  else if (score >= -1.0) return 'C';
  else return 'D';
}

function runQuery(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

(async () => {
  try {
    // ----------------------------
    // 1. 基本ディレクトリ設定
    // ----------------------------
    const outputDir = path.join(baseDir, "output");
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const heroImagesDir = path.join(baseDir, "hero_images");

    // ----------------------------
    // 2. SQLiteからデータ取得
    // ----------------------------
    const dbPath = path.join(baseDir, "data", "moba_log.db");
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
      if (err) logError("DBオープンエラー: " + err);
    });

    // 最新の reference_date を取得
    const latestDateRows = await runQuery(db, "SELECT MAX(reference_date) as latest_date FROM mlbb_stats");
    const latestDate = latestDateRows[0].latest_date;

    // 最新日付の mlbb_stats を取得（charactersテーブルとJOINしてキャラクター名も取得）
    const heroStats = await runQuery(db, `
      SELECT ms.*, c.english_name as hero_name 
      FROM mlbb_stats ms
      JOIN characters c ON ms.character_id = c.id
      WHERE ms.reference_date = ?
    `, [latestDate]);
    logMessage(`最新の reference_date (${latestDate}) のデータ件数: ${heroStats.length}`);

    // 英名→日本語名のマッピング取得（MLBBのキャラクターのみ）
    const heroMapRows = await runQuery(db, `
      SELECT c.english_name, c.japanese_name 
      FROM characters c
      JOIN games g ON c.game_id = g.id
      WHERE g.game_code = 'mlbb'
    `);
    const heroNameMap = {};
    heroMapRows.forEach(row => {
      heroNameMap[row.english_name] = row.japanese_name;
    });

    // 最新パッチ情報の取得（MLBBのパッチのみ）
    const patchRows = await runQuery(db, `
      SELECT p.patch_number 
      FROM patches p
      JOIN games g ON p.game_id = g.id
      WHERE g.game_code = 'mlbb'
      ORDER BY p.release_date DESC 
      LIMIT 1
    `);
    const patchNumber = (patchRows.length > 0) ? patchRows[0].patch_number : "N/A";

    db.close();

    // ----------------------------
    // 3. Zスコア・強さスコア算出
    // ----------------------------
    const winRates = heroStats.map(row => row.win_rate);
    const pickRates = heroStats.map(row => row.pick_rate);
    const banRates = heroStats.map(row => row.ban_rate);

    const winMean = mean(winRates);
    const winStd = stdDev(winRates, winMean);
    const pickMean = mean(pickRates);
    const pickStd = stdDev(pickRates, pickMean);
    const banMean = mean(banRates);
    const banStd = stdDev(banRates, banMean);

    heroStats.forEach(row => {
      row.win_rate_z = (row.win_rate - winMean) / winStd;
      row.pick_rate_z = (row.pick_rate - pickMean) / pickStd;
      row.ban_rate_z = (row.ban_rate - banMean) / banStd;
      const w_win = 0.5, w_ban = 0.3, w_pick = 0.2;
      row.strength_score = w_win * row.win_rate_z + w_ban * row.ban_rate_z + w_pick * row.pick_rate_z;
      row.grade = assignGrade(row.strength_score);
    });
    // strength_score の降順にソート
    heroStats.sort((a, b) => b.strength_score - a.strength_score);

    // ----------------------------
    // 4. HTML出力用文字列生成
    // ----------------------------
    const tierDescriptions = {
      'S': 'Meta Definers',
      'A': 'Top Picks',
      'B': 'Balanced Heroes',
      'C': 'Situational Picks',
      'D': 'Needs Buff'
    };

    const htmlHead = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MLBB Hero Tier List</title>
  <style>
    :root {
      --primary-color: #ffffff;
      --secondary-color: #000000;
      --accent-color: #333333;
      --bg-dark: #0a0a0a;
      --bg-card: #1a1a1a;
      --text-light: #ffffff;
      --text-secondary: #888888;
      --s-tier: #ffd700;
      --a-tier: #c9b037;
      --b-tier: #cd7f32;
      --c-tier: #b87333;
      --d-tier: #6c6c6c;
    }
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }
    body {
      background-color: var(--bg-dark);
      color: var(--text-light);
      padding: 0;
      margin: 0;
      line-height: 1.6;
    }
    .container {
      max-width: 1920px;
      margin: 0 auto;
      padding: 20px;
    }
    .header {
      text-align: center;
      padding: 60px 20px;
      background: linear-gradient(180deg, #000000, #1a1a1a);
      border-bottom: 1px solid #333333;
      margin-bottom: 40px;
    }
    .header h1 {
      font-size: 4em;
      font-weight: 300;
      margin-bottom: 20px;
      color: var(--text-light);
      letter-spacing: 8px;
      text-transform: uppercase;
    }
    .header h1 span {
      font-weight: 700;
    }
    .version-info {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 30px;
      font-size: 1.4em;
      font-weight: 500;
      color: var(--text-light);
      background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
      border: 2px solid #444444;
      padding: 20px 40px;
      border-radius: 0;
      margin-top: 30px;
      letter-spacing: 3px;
      text-transform: uppercase;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
    }
    .patch-info {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .patch-label {
      color: var(--text-secondary);
      font-size: 0.9em;
      font-weight: 300;
    }
    .patch-value {
      color: var(--s-tier);
      font-weight: 700;
      font-size: 1.1em;
    }
    .update-info {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .update-label {
      color: var(--text-secondary);
      font-size: 0.9em;
      font-weight: 300;
    }
    .update-value {
      color: var(--text-light);
      font-weight: 600;
    }
    .tier-section {
      margin-bottom: 50px;
      padding: 30px;
      border-radius: 0;
      background-color: var(--bg-card);
      border: 1px solid #333333;
      position: relative;
    }
    .tier-section::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 2px;
    }
    .tier-section.s-tier::before {
      background: var(--s-tier);
    }
    .tier-section.a-tier::before {
      background: var(--a-tier);
    }
    .tier-section.b-tier::before {
      background: var(--b-tier);
    }
    .tier-section.c-tier::before {
      background: var(--c-tier);
    }
    .tier-section.d-tier::before {
      background: var(--d-tier);
    }
    .tier-badge {
      position: absolute;
      top: 20px;
      right: 20px;
      width: 40px;
      height: 40px;
      border: 1px solid #333333;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4em;
      font-weight: 600;
      color: #000000;
    }
    .s-tier .tier-badge { 
      background: var(--s-tier);
      border-color: var(--s-tier);
    }
    .a-tier .tier-badge { 
      background: var(--a-tier);
      border-color: var(--a-tier);
    }
    .b-tier .tier-badge { 
      background: var(--b-tier);
      border-color: var(--b-tier);
    }
    .c-tier .tier-badge { 
      background: var(--c-tier);
      border-color: var(--c-tier);
    }
    .d-tier .tier-badge { 
      background: var(--d-tier);
      border-color: var(--d-tier);
      color: #ffffff;
    }
    .tier-title {
      font-size: 1.8em;
      margin-bottom: 30px;
      color: var(--text-light);
      font-weight: 300;
      text-transform: uppercase;
      letter-spacing: 3px;
      display: flex;
      align-items: center;
    }
    .tier-title::after {
      content: '';
      flex-grow: 1;
      height: 1px;
      margin-left: 20px;
      background: #333333;
    }
    .hero-list {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      justify-content: flex-start;
    }
    .hero {
      width: 100px;
      text-align: center;
      position: relative;
    }
    .hero-card {
      background: transparent;
      border: 1px solid #333333;
      border-radius: 0;
      padding: 8px;
    }
    .hero-img-container {
      position: relative;
      width: 84px;
      height: 84px;
      margin: 0 auto;
      border-radius: 0;
      overflow: hidden;
      border: 1px solid #333333;
    }
    .hero img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .hero-name {
      margin-top: 8px;
      font-size: 0.85em;
      color: var(--text-light);
      font-weight: 300;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      letter-spacing: 1px;
    }
    @media (max-width: 768px) {
      .header h1 { 
        font-size: 2.5em; 
        letter-spacing: 4px;
      }
      .version-info {
        flex-direction: column;
        gap: 15px;
        font-size: 1.2em;
        padding: 15px 20px;
        margin-top: 20px;
      }
      .hero-list { 
        justify-content: center; 
      }
      .tier-section { 
        padding: 20px 15px; 
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>モバイル・レジェンド <span>TIER LIST</span></h1>
    <div class="version-info">
      <div class="patch-info">
        <span class="patch-label">Patch:</span>
        <span class="patch-value">${patchNumber}</span>
      </div>
      <div class="update-info">
        <span class="update-label">更新日:</span>
        <span class="update-value">${latestDate}</span>
      </div>
    </div>
  </div>
  <div class="container">
`;

    const htmlTail = `
  </div>
</body>
</html>
`;

    let htmlBody = "";
    const grades = ['S', 'A', 'B', 'C', 'D'];
    grades.forEach(grade => {
      const filtered = heroStats.filter(row => row.grade === grade);
      if (filtered.length === 0) return;
      const description = tierDescriptions[grade] || "";
      htmlBody += `    <!-- ${grade} Tier -->\n`;
      htmlBody += `    <div class="tier-section ${grade.toLowerCase()}-tier">\n`;
      htmlBody += `      <div class="tier-badge">${grade}</div>\n`;
      htmlBody += `      <div class="tier-title">${grade} Tier - ${description}</div>\n`;
      htmlBody += `      <div class="hero-list">\n`;
      filtered.forEach(row => {
        const englishName = row.hero_name;
        const japaneseName = heroNameMap[englishName] || englishName;
        const winRate = row.win_rate;
        const heroImgPath = "file://" + path.join(heroImagesDir, `${englishName}.webp`);
        htmlBody += `        <div class="hero">\n`;
        htmlBody += `          <div class="hero-card">\n`;
        htmlBody += `            <div class="hero-img-container">\n`;
        htmlBody += `              <img src="${heroImgPath}" alt="${japaneseName}">\n`;
        htmlBody += `            </div>\n`;
        htmlBody += `            <div class="hero-name">${japaneseName}</div>\n`;
        htmlBody += `          </div>\n`;
        htmlBody += `        </div>\n`;
      });
      htmlBody += `      </div>\n`;
      htmlBody += `    </div>\n`;
    });

    const finalHtml = htmlHead + htmlBody + htmlTail;
    const htmlFilePath = path.join(outputDir, "hero_tier_list.html");
    fs.writeFileSync(htmlFilePath, finalHtml, "utf-8");
    logMessage(`HTMLファイルが ${htmlFilePath} に出力されました。`);

    // ----------------------------
    // 5. Puppeteerでスクリーンショット撮影
    // ----------------------------
    const browser = await puppeteer.launch({
      headless: true,
      defaultViewport: { width: 1920, height: 1080 }
    });
    const page = await browser.newPage();
    const fileUrl = "file://" + htmlFilePath;
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });
    // ヘッダーとコンテナが確実に読み込まれるのを待つ
    await page.waitForSelector('.header');
    await page.waitForSelector('.container');

    // ヘッダーとコンテナのそれぞれの位置と大きさを取得
    const headerElement = await page.$('.header');
    const containerElement = await page.$('.container');
    const headerBox = await headerElement.boundingBox();
    const containerBox = await containerElement.boundingBox();

    // ヘッダーとコンテナの領域を包括する矩形を計算
    const unionX = Math.min(headerBox.x, containerBox.x);
    const unionY = Math.min(headerBox.y, containerBox.y);
    const unionWidth = Math.max(headerBox.x + headerBox.width, containerBox.x + containerBox.width) - unionX;
    const unionHeight = (containerBox.y + containerBox.height) - unionY;

    // タイムスタンプを用いて一意なファイル名を作成
    const timestamp = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', hour12: false }).replace(/[\/: ]/g, '-');
    const screenshotPath = path.join(outputDir, `hero_tier_list_${timestamp}.png`);

    // ヘッダーとコンテナを含む領域のスクリーンショットを取得
    await page.screenshot({
      path: screenshotPath,
      clip: { x: unionX, y: unionY, width: unionWidth, height: unionHeight }
    });
    logMessage(`スクリーンショットが ${screenshotPath} に保存されました。`);

    await browser.close();

    // ----------------------------
    // 6. twitter-api-v2でスクリーンショットを添付してXに投稿
    // ----------------------------
    // Twitter APIの認証情報を環境変数から取得
    const apiKey = process.env.API_KEY;
    const apiSecretKey = process.env.API_SECRET_KEY;
    const accessToken = process.env.ACCESS_TOKEN;
    const accessTokenSecret = process.env.ACCESS_TOKEN_SECRET;
    const bearerToken = process.env.BEARER_TOKEN;

    // Twitterクライアントの初期化（v1.1とv2のエンドポイントに対応）
    const twitterClient = new TwitterApi({
      appKey: apiKey,
      appSecret: apiSecretKey,
      accessToken: accessToken,
      accessSecret: accessTokenSecret,
    });
    const rwClient = twitterClient.readWrite;

    // ツイートテキスト（patchNumber変数を利用）
    const tweetText = `今週のモバイル・レジェンドのTier表を公開します。

バージョン：${patchNumber}

#モバイル・レジェンド #モバレ #モバレジェ #MLBB`;

    // ツイート投稿の結果を保存するための変数
    let tweetPostStatus = 0; // 0: 成功, 1: 失敗
    let tweetErrorMessage = null;

    try {
      // メディアをアップロード（v1.1のエンドポイントを使用）
      const mediaId = await rwClient.v1.uploadMedia(screenshotPath);
      // ツイートを投稿（v2のエンドポイントを使用）
      await rwClient.v2.tweet(tweetText, {
        media: { media_ids: [mediaId] },
      });
      logMessage("ツイートが投稿されました。");
    } catch (error) {
      tweetPostStatus = 1;
      tweetErrorMessage = error.toString();
      logError("ツイート投稿中にエラーが発生しました: " + tweetErrorMessage);
    }

    // 日本時間の日付（YYYY-MM-DD形式）の取得
    const postDate = new Date()
      .toLocaleDateString('ja-JP', { timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit' })
      .replace(/\//g, '-');

    // data/moba_log.db に x_post_logs テーブルへ投稿結果を保存する
    const mobaDbPath = path.join(baseDir, "data", "moba_log.db");
    const mobaDb = new sqlite3.Database(mobaDbPath, sqlite3.OPEN_READWRITE, (err) => {
      if (err) {
        logError("moba_log.db オープンエラー: " + err);
      }
    });

    try {
      // MLBBのgame_idを取得
      const gameIdRows = await runQuery(mobaDb, "SELECT id FROM games WHERE game_code = 'mlbb'");
      const gameId = gameIdRows.length > 0 ? gameIdRows[0].id : null;

      if (gameId) {
        // 投稿結果を保存（Promiseでラップ）
        await new Promise((resolve, reject) => {
          mobaDb.run(
            "INSERT INTO x_post_logs (game_id, post_status, error_message, post_date) VALUES (?, ?, ?, ?)",
            [gameId, tweetPostStatus === 0, tweetErrorMessage, postDate],
            function(err) {
              if (err) {
                logError("x_post_logs テーブルへの保存エラー: " + err);
                reject(err);
              } else {
                logMessage("ツイート投稿の結果が x_post_logs に保存されました。");
                resolve();
              }
            }
          );
        });
      } else {
        logError("MLBBのgame_idが見つかりませんでした。");
      }
    } catch (error) {
      logError("x_post_logs への保存中にエラーが発生しました: " + error);
    }

    mobaDb.close();
  } catch (err) {
    logError("エラー: " + err);
  }
})();

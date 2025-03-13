const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const { TwitterApi } = require('twitter-api-v2');
require('dotenv').config();

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

// JSTのタイムスタンプを生成する関数
function getJstTimestamp() {
  const now = new Date();
  // 現在のローカルタイムとの差を考慮してJST（UTC+9）に調整
  const jst = new Date(now.getTime() + (9 * 60 + now.getTimezoneOffset()) * 60000);
  const year = jst.getFullYear();
  const month = String(jst.getMonth() + 1).padStart(2, '0');
  const day = String(jst.getDate()).padStart(2, '0');
  const hours = String(jst.getHours()).padStart(2, '0');
  const minutes = String(jst.getMinutes()).padStart(2, '0');
  const seconds = String(jst.getSeconds()).padStart(2, '0');
  const milliseconds = String(jst.getMilliseconds()).padStart(3, '0');
  return `${year}-${month}-${day}T${hours}-${minutes}-${seconds}-${milliseconds}`;
}

// JSTの日付（YYYY-MM-DD形式）を生成する関数
function getJstDate() {
  const now = new Date();
  const jst = new Date(now.getTime() + (9 * 60 + now.getTimezoneOffset()) * 60000);
  const year = jst.getFullYear();
  const month = String(jst.getMonth() + 1).padStart(2, '0');
  const day = String(jst.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

(async () => {
  try {
    // ----------------------------
    // 1. 基本ディレクトリ設定
    // ----------------------------
    const baseDir = "/Users/yamamotokazuki/develop/moba-ranking";
    const outputDir = path.join(baseDir, "output");
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    // championImagesDirには英語名の画像が入っている前提
    const championImagesDir = path.join(baseDir, "champion_images");

    // ----------------------------
    // 2. SQLiteからデータ取得
    // ----------------------------
    const dbPath = path.join(baseDir, "wildrift.db");
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, err => {
      if (err) console.error("DBオープンエラー:", err);
    });

    // 対象の5つのlane
    const lanes = ['上单', '打野', '中路', '下路', '辅助'];
    // 最新の reference_date を5つのlane全体から取得
    const latestDateRows = await runQuery(
      db,
      "SELECT MAX(reference_date) as latest_date FROM champion_stats WHERE lane IN (?,?,?,?,?)",
      lanes
    );
    const latestDate = latestDateRows[0].latest_date;

    // 最新日付の champion_stats を5つのlane全体から取得
    const championStats = await runQuery(
      db,
      "SELECT * FROM champion_stats WHERE reference_date = ? AND lane IN (?,?,?,?,?)",
      [latestDate, ...lanes]
    );
    console.log(`最新の reference_date (${latestDate}) のデータ件数: ${championStats.length}`);

    // championsテーブルから、chinese_name, japanese_name, english_name のマッピング取得
    const championMapRows = await runQuery(
      db,
      "SELECT chinese_name, japanese_name, english_name FROM champions"
    );
    const championMap = {};
    championMapRows.forEach(row => {
      // キーは chinese_name として、値に japanese_name, english_name を保持
      championMap[row.chinese_name] = { japanese: row.japanese_name, english: row.english_name };
    });

    // 最新パッチ情報（バージョン）の取得
    const patchRows = await runQuery(
      db,
      "SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1"
    );
    const patchNumber = (patchRows.length > 0) ? patchRows[0].patch_number : "N/A";

    db.close();

    // ----------------------------
    // 3. Zスコア・強さスコア算出
    // ----------------------------
    const winRates = championStats.map(row => row.win_rate);
    const pickRates = championStats.map(row => row.pick_rate);
    const banRates = championStats.map(row => row.ban_rate);

    const winMean = mean(winRates);
    const winStd = stdDev(winRates, winMean);
    const pickMean = mean(pickRates);
    const pickStd = stdDev(pickRates, pickMean);
    const banMean = mean(banRates);
    const banStd = stdDev(banRates, banMean);

    championStats.forEach(row => {
      row.win_rate_z = (row.win_rate - winMean) / winStd;
      row.pick_rate_z = (row.pick_rate - pickMean) / pickStd;
      row.ban_rate_z = (row.ban_rate - banMean) / banStd;
      const w_win = 0.5, w_ban = 0.3, w_pick = 0.2;
      row.strength_score = w_win * row.win_rate_z + w_ban * row.ban_rate_z + w_pick * row.pick_rate_z;
      row.grade = assignGrade(row.strength_score);
    });
    // strength_score の降順にソート
    championStats.sort((a, b) => b.strength_score - a.strength_score);

    // ----------------------------
    // 追加：各championのscoreをログ出力
    // ----------------------------
    championStats.forEach(row => {
      const key = row.champion_name; // champion_stats の名前は中国語表記と仮定
      const mapping = championMap[key];
      const englishName = mapping ? mapping.english : key;
      console.log(`${englishName} の score: ${row.strength_score.toFixed(3)}`);
    });

    // ----------------------------
    // 4. HTML出力用文字列生成（グリッドレイアウト：横軸=lane, 縦軸=grade）
    // ----------------------------
    // 縦軸にgradeの順序（上からS, A, B, C, D）
    const grades = ['S', 'A', 'B', 'C', 'D'];

    // CSSグリッドの設定：
    // 1列目は行ラベル（grade）、残りの列が lane
    let htmlHead = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ワイルドリフト ティアリスト</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
  <style>
    body {
      background-color: #010A13;
      font-family: 'Noto Sans JP', sans-serif;
      padding: 20px;
      color: #C8AA6E;
      background-image: url('file:///Users/yamamotokazuki/develop/moba-ranking/background.jpg');
      background-size: cover;
      background-position: center;
      background-blend-mode: multiply;
    }
    .title-container {
      text-align: center;
      margin-bottom: 20px;
    }
    .main-title {
      font-size: 3em;
      font-weight: 900;
      color: #F0E6D2;
      margin-bottom: 15px;
      text-shadow: 0 0 10px #785A28, 0 0 20px #785A28;
      text-transform: uppercase;
      letter-spacing: 2px;
    }
    .composite-grid {
      display: grid;
      grid-template-columns: 80px repeat(${lanes.length}, 1fr);
      gap: 12px;
      margin: 0 auto;
      max-width: 1400px;
    }
    .grid-header {
      background: linear-gradient(to bottom, #091428, #0A1428);
      text-align: center;
      padding: 15px 5px;
      font-weight: bold;
      border-radius: 4px;
      font-size: 18px;
      color: #C8AA6E;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5), inset 0 0 3px #C8AA6E;
      border: 1px solid #785A28;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .grid-grade-label {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      font-weight: 900;
      font-size: 34px;
      border-radius: 4px;
      text-shadow: 0 0 10px rgba(0, 0, 0, 0.7);
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
      letter-spacing: 2px;
    }
    .grade-S { 
      background: linear-gradient(135deg, #DCB14A, #A17622); 
      color: #fff;
      border: 1px solid #FFC659; 
    }
    .grade-A { 
      background: linear-gradient(135deg, #CECECE, #737373); 
      color: #fff; 
      border: 1px solid #E5E5E5;
    }
    .grade-B { 
      background: linear-gradient(135deg, #AD8A56, #5C4A2E); 
      color: #fff; 
      border: 1px solid #C8AA6E;
    }
    .grade-C { 
      background: linear-gradient(135deg, #2C5677, #1A3245); 
      color: #fff; 
      border: 1px solid #3A81AD;
    }
    .grade-D { 
      background: linear-gradient(135deg, #252525, #000000); 
      color: #B7B7B7; 
      border: 1px solid #444444;
    }
    .grid-cell {
      background-color: rgba(10, 20, 40, 0.85);
      border-radius: 4px;
      padding: 8px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      justify-items: center;
      align-content: start;
      min-height: 110px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5), inset 0 0 2px rgba(200, 170, 110, 0.3);
      border: 1px solid rgba(120, 90, 40, 0.3);
    }
    .hero {
      text-align: center;
      margin-bottom: 5px;
    }
    .hero-img-container {
      width: 60px;
      height: 60px;
      overflow: hidden;
      border-radius: 50%;
      border: 2px solid #785A28;
      box-shadow: 0 0 8px rgba(201, 170, 113, 0.6);
      margin: 0 auto;
    }
    .hero-img-container img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .hero-name {
      margin-top: 6px;
      font-size: 12px;
      font-weight: 700;
      color: #C8AA6E;
      text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }
    .version-info {
      text-align: center;
      margin-bottom: 25px;
      font-size: 1.1em;
      font-weight: bold;
      color: #3A81AD;
      text-shadow: 0 0 5px rgba(10, 200, 185, 0.3);
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="title-container">
    <div class="main-title">WILD RIFT TIER LIST</div>
  </div>
  <div class="version-info">バージョン ${patchNumber} | ${latestDate}</div>
  <div class="composite-grid">
    <!-- ヘッダー行：1列目は空、以降が lane ラベル -->
    <div class="grid-header"></div>`;
    
    // 中国語レーン名を日本語に変換する辞書（変更後）
    const laneTranslation = {
      '上单': 'バロン',
      '打野': 'ジャングル',
      '中路': 'ミッド',
      '下路': 'ドラゴン',
      '辅助': 'サポート'
    };
    
    lanes.forEach(lane => {
      htmlHead += `<div class="grid-header">${laneTranslation[lane]}</div>`;
    });
    
    let htmlBody = "";
    // 各行は grade ごとに作成（縦軸）
    grades.forEach(grade => {
      // 先頭セルに grade ラベル
      htmlBody += `<div class="grid-grade-label grade-${grade}">${grade}</div>`;
      lanes.forEach(lane => {
        // lane と grade でフィルタ
        const filtered = championStats.filter(row => row.lane === lane && row.grade === grade);
        
        // 降順で強さスコアでソート
        filtered.sort((a, b) => b.strength_score - a.strength_score);
        
        htmlBody += `<div class="grid-cell">`;
        filtered.forEach(row => {
          const key = row.champion_name; // champion_stats の名前は中国語表記と仮定
          const mapping = championMap[key] || {};
          const japaneseName = mapping.japanese || key;
          const englishName = mapping.english || key;
          const championImgPath = "file://" + path.join(championImagesDir, `${englishName}.webp`);
          
          htmlBody += `<div class="hero">
              <div class="hero-img-container">
                <img src="${championImgPath}" alt="${japaneseName}">
              </div>
              <div class="hero-name">${japaneseName}</div>
            </div>`;
        });
        htmlBody += `</div>`;
      });
    });
    
    const htmlTail = `
  </div>
</body>
</html>`;
    
    const finalHtml = htmlHead + htmlBody + htmlTail;
    const htmlFilePath = path.join(outputDir, "champion_tier_list.html");
    fs.writeFileSync(htmlFilePath, finalHtml, "utf-8");
    console.log(`HTMLファイルが ${htmlFilePath} に出力されました。`);

    // ----------------------------
    // 5. Puppeteerでスクリーンショット撮影（全体キャプチャ）
    // ----------------------------
    const browser = await puppeteer.launch({
      headless: true,
      defaultViewport: { width: 1400, height: 1080 }
    });
    const page = await browser.newPage();
    const fileUrl = "file://" + htmlFilePath;
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });
    await page.waitForSelector('.composite-grid');

    // ページ全体のスクリーンショット（フッターを含む）
    const bodyElement = await page.$('body');
    const bodyBox = await bodyElement.boundingBox();

    const timestamp = getJstTimestamp();
    const screenshotPath = path.join(outputDir, `wild_rift_tier_${timestamp}.png`);

    await page.screenshot({
      path: screenshotPath,
      clip: {
        x: bodyBox.x,
        y: bodyBox.y,
        width: bodyBox.width,
        height: bodyBox.height
      },
      fullPage: false
    });
    console.log(`スクリーンショットが ${screenshotPath} に保存されました。`);

    await browser.close();

    // ----------------------------
    // 6. twitter-api-v2でスクリーンショットを添付してXに投稿＆投稿結果をmoba.dbに記録
    // ----------------------------
    const apiKey = process.env.API_KEY;
    const apiSecretKey = process.env.API_SECRET_KEY;
    const accessToken = process.env.ACCESS_TOKEN;
    const accessTokenSecret = process.env.ACCESS_TOKEN_SECRET;
    const bearerToken = process.env.BEARER_TOKEN;

    const twitterClient = new TwitterApi({
      appKey: apiKey,
      appSecret: apiSecretKey,
      accessToken: accessToken,
      accessSecret: accessTokenSecret,
    });
    const rwClient = twitterClient.readWrite;

    const tweetText = `今週のワイルドリフトのTier表を公開します。

バージョン：${patchNumber}

#ワイルドリフト #WildRift`;

    // ツイート投稿の結果を記録するための変数
    let postStatus, errorMessage;
    try {
      const mediaId = await rwClient.v1.uploadMedia(screenshotPath);
      await rwClient.v2.tweet(tweetText, { media: { media_ids: [mediaId] } });
      console.log("ツイートが投稿されました。");
      postStatus = 0; // 成功の場合は0
      errorMessage = null;
    } catch (error) {
      console.error("ツイート投稿中にエラーが発生しました:", error);
      postStatus = 1; // 失敗の場合は1
      errorMessage = error.message ? error.message : String(error);
    }

    // moba.db の x_post_status テーブルに投稿結果を保存
    const mobaDbPath = path.join(baseDir, "moba.db");
    const mobaDb = new sqlite3.Database(mobaDbPath, sqlite3.OPEN_READWRITE, err => {
      if (err) console.error("moba DB オープンエラー:", err);
    });
    
    const postDate = getJstDate(); // "YYYY-MM-DD"形式のJST日付
    const insertSQL = "INSERT INTO x_post_status (post_status, game_title, error_message, post_date) VALUES (?, ?, ?, ?)";
    mobaDb.run(insertSQL, [postStatus, "wildrift", errorMessage, postDate], function(err) {
      if (err) {
         console.error("x_post_statusへの挿入エラー:", err);
      } else {
         console.log("x_post_statusにツイートの結果が保存されました。");
      }
      mobaDb.close();
    });
  } catch (err) {
    console.error("エラー:", err);
  }
})();

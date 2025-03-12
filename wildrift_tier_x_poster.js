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
      const key = row.champion_name; // champion_statsの名前は中国語表記と仮定
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
    // 1列目は行ラベル用(grade)、残りの列が lane
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
      background-color: #FAFAFA;
      font-family: 'Noto Sans JP', sans-serif;
      padding: 20px;
    }
    .composite-grid {
      display: grid;
      /* 1列目は grade ラベル、以降は lane なので列数は lanes.length + 1 */
      grid-template-columns: 150px repeat(${lanes.length}, 1fr);
      gap: 10px;
      margin: 0 auto;
      max-width: 1920px;
    }
    .grid-header, .grid-grade-label {
      background: #eee;
      text-align: center;
      padding: 10px;
      font-weight: bold;
      border: 1px solid #ccc;
    }
    .grid-cell {
      border: 1px solid #ccc;
      padding: 10px;
      min-height: 150px;
    }
    .hero {
      text-align: center;
      margin-bottom: 10px;
    }
    .hero-card {
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 5px 10px rgba(0,0,0,0.1);
    }
    .hero-img-container {
      width: 80px;
      height: 80px;
      margin: 0 auto;
      border-radius: 50%;
      overflow: hidden;
      border: 2px solid #fff;
      box-shadow: 0 3px 6px rgba(0,0,0,0.1);
      background: #f5f7fa;
    }
    .hero-img-container img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .hero-name {
      margin-top: 5px;
      font-size: 0.9em;
      font-weight: 700;
      color: #333;
    }
    .version-info {
      text-align: center;
      margin-bottom: 20px;
      font-size: 1.3em;
      font-weight: 700;
    }
    .footer {
      text-align: center;
      margin-top: 20px;
      font-size: 0.9em;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="version-info">バージョン ${patchNumber} ・ ${latestDate}</div>
  <div class="composite-grid">
    <!-- ヘッダー行：1列目は空、以降が lane のラベル -->
    <div class="grid-header"></div>`;
    
    // 横軸に lane ラベルを追加
    lanes.forEach(lane => {
      htmlHead += `<div class="grid-header">${lane}</div>`;
    });

    let htmlBody = "";
    // 縦軸に grade ごとの行を作成
    grades.forEach(grade => {
      // 先頭セルに grade ラベル
      htmlBody += `<div class="grid-grade-label">${grade} Tier</div>`;
      // 各 lane に対応するセル
      lanes.forEach(lane => {
        // lane と grade でフィルタ
        const filtered = championStats.filter(row => row.lane === lane && row.grade === grade);
        htmlBody += `<div class="grid-cell">`;
        filtered.forEach(row => {
          const key = row.champion_name; // champion_stats の名前は中国語表記と仮定
          const mapping = championMap[key] || {};
          const japaneseName = mapping.japanese || key;
          const englishName = mapping.english || key;
          const championImgPath = "file://" + path.join(championImagesDir, `${englishName}.webp`);
          htmlBody += `<div class="hero">
              <div class="hero-card">
                <div class="hero-img-container">
                  <img src="${championImgPath}" alt="${japaneseName}">
                </div>
                <div class="hero-name">${japaneseName}</div>
              </div>
            </div>`;
        });
        htmlBody += `</div>`;
      });
    });
    
    const htmlTail = `
  </div>
  <div class="footer">
    <p>ワイルドリフト ティアリスト ・ ${latestDate} ・ バージョン ${patchNumber}</p>
    <p>※勝率・ピック率・BAN率から算出</p>
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
      defaultViewport: { width: 1920, height: 1080 }
    });
    const page = await browser.newPage();
    const fileUrl = "file://" + htmlFilePath;
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });
    await page.waitForSelector('.composite-grid');

    const containerElement = await page.$('.composite-grid');
    const containerBox = await containerElement.boundingBox();

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const screenshotPath = path.join(outputDir, `champion_tier_list_${timestamp}.png`);

    await page.screenshot({
      path: screenshotPath,
      clip: {
        x: containerBox.x,
        y: containerBox.y,
        width: containerBox.width,
        height: containerBox.height
      },
      fullPage: false
    });
    console.log(`スクリーンショットが ${screenshotPath} に保存されました。`);

    await browser.close();

    // ----------------------------
    // 6. twitter-api-v2でスクリーンショットを添付してXに投稿
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

    try {
      // const mediaId = await rwClient.v1.uploadMedia(screenshotPath);
      // await rwClient.v2.tweet(tweetText, {
      //   media: { media_ids: [mediaId] },
      // });
      // console.log("ツイートが投稿されました。");
    } catch (error) {
      console.error("ツイート投稿中にエラーが発生しました:", error);
    }
  } catch (err) {
    console.error("エラー:", err);
  }
})();

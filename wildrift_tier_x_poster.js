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
    // championImagesDirは画像ファイル名が英語名で格納されている前提
    const championImagesDir = path.join(baseDir, "champion_images");

    // ----------------------------
    // 2. SQLiteからデータ取得
    // ----------------------------
    const dbPath = path.join(baseDir, "wildrift.db");
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
      if (err) console.error("DBオープンエラー:", err);
    });

    // 最新の reference_date を、lane が "上单" のデータから取得
    const latestDateRows = await runQuery(db, "SELECT MAX(reference_date) as latest_date FROM champion_stats WHERE lane = ?", ["上单"]);
    const latestDate = latestDateRows[0].latest_date;

    // 最新日付かつ lane が "上单" の champion_stats を取得
    const championStats = await runQuery(db, "SELECT * FROM champion_stats WHERE reference_date = ? AND lane = ?", [latestDate, "上单"]);
    console.log(`最新の reference_date (${latestDate}) のデータ件数: ${championStats.length}`);

    // championsテーブルから、chinese_name, japanese_name, english_name のマッピングを取得
    const championMapRows = await runQuery(db, "SELECT chinese_name, japanese_name, english_name FROM champions");
    const championMap = {};
    championMapRows.forEach(row => {
      // キーはchinese_nameとし、値にjapanese_nameとenglish_nameを保持
      championMap[row.chinese_name] = { japanese: row.japanese_name, english: row.english_name };
    });

    // 最新パッチ情報（バージョン）の取得（patches テーブルが共通の場合）
    const patchRows = await runQuery(db, "SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1");
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
      // championStats の champion_name は中国語表記と仮定し、mappingから英語名を取得
      const key = row.champion_name;
      const mapping = championMap[key];
      const englishName = mapping ? mapping.english : key;
      console.log(`${englishName} の score: ${row.strength_score.toFixed(3)}`);
    });

    // ----------------------------
    // 4. HTML出力用文字列生成
    // ----------------------------
    const tierDescriptions = {
      'S': 'チャンピオンクラス',
      'A': 'エースクラス',
      'B': 'バランスクラス',
      'C': '状況限定クラス',
      'D': '強化必要クラス'
    };

    const htmlHead = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ワイルドリフト ティアリスト</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
  <style>
    /* アニメーション削除 */
    
    :root {
      /* カラフルでポップなカラーパレット */
      --primary-color: #FF5F6D;
      --secondary-color: #3e4edd;
      --bg-color: #FAFAFA;
      --accent-color: #FFD700;
      --text-color: #333;
      --text-light: #666;
      --s-tier: linear-gradient(135deg, #FF9100, #F9455D);
      --a-tier: linear-gradient(135deg, #FDA7DF, #9C27B0);
      --b-tier: linear-gradient(135deg, #5EFCE8, #736EFE);
      --c-tier: linear-gradient(135deg, #A8FF78, #78FFD6);
      --d-tier: linear-gradient(135deg, #BDBBBE, #9D9EA3);
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Noto Sans JP', sans-serif;
    }
    
    body {
      background-color: var(--bg-color);
      color: var(--text-color);
      background-image: 
        radial-gradient(circle at 10% 20%, rgba(255, 200, 200, 0.2) 0%, transparent 20%),
        radial-gradient(circle at 90% 30%, rgba(200, 200, 255, 0.2) 0%, transparent 25%),
        radial-gradient(circle at 50% 60%, rgba(255, 255, 200, 0.2) 0%, transparent 30%);
      background-attachment: fixed;
    }
    
    .container {
      max-width: 1920px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .header {
      text-align: center;
      padding: 40px 20px;
      margin-bottom: 30px;
      position: relative;
      overflow: hidden;
      border-radius: 20px;
      background: white;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .header::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 10px;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .header h1 {
      font-size: 3.8em;
      font-weight: 900;
      margin-bottom: 15px;
      color: var(--text-color);
      letter-spacing: 2px;
      position: relative;
      display: inline-block;
    }
    
    .header h1::after {
      content: '';
      position: absolute;
      bottom: -5px;
      left: 0;
      width: 100%;
      height: 5px;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
      border-radius: 5px;
    }
    
    .header h1 span {
      color: var(--primary-color);
      position: relative;
    }
    
    .header h1 span::before {
      content: '★';
      position: absolute;
      top: -20px;
      right: -15px;
      font-size: 0.5em;
      color: var(--accent-color);
    }
    
    .version-info {
      display: inline-block;
      font-size: 1.3em;
      font-weight: 700;
      color: white;
      background: linear-gradient(90deg, var(--secondary-color), var(--primary-color));
      padding: 10px 30px;
      border-radius: 50px;
      margin-top: 15px;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
      position: relative;
      z-index: 1;
      overflow: hidden;
    }
    
    .version-info::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
      z-index: -1;
      transform: rotate(30deg);
    }
    
    .tier-section {
      margin-bottom: 40px;
      padding: 30px;
      border-radius: 20px;
      background-color: white;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      position: relative;
      overflow: hidden;
    }
    
    .tier-section.s-tier { border-top: 10px solid transparent; border-image: var(--s-tier) 1; }
    .tier-section.a-tier { border-top: 10px solid transparent; border-image: var(--a-tier) 1; }
    .tier-section.b-tier { border-top: 10px solid transparent; border-image: var(--b-tier) 1; }
    .tier-section.c-tier { border-top: 10px solid transparent; border-image: var(--c-tier) 1; }
    .tier-section.d-tier { border-top: 10px solid transparent; border-image: var(--d-tier) 1; }
    
    .tier-badge {
      position: absolute;
      top: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.2em;
      font-weight: 900;
      color: white;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
      z-index: 2;
    }
    
    .tier-badge::after {
      content: '';
      position: absolute;
      top: -3px;
      left: -3px;
      right: -3px;
      bottom: -3px;
      border-radius: 50%;
      background: white;
      z-index: -1;
    }
    
    .s-tier .tier-badge { background: var(--s-tier); }
    .a-tier .tier-badge { background: var(--a-tier); }
    .b-tier .tier-badge { background: var(--b-tier); }
    .c-tier .tier-badge { background: var(--c-tier); }
    .d-tier .tier-badge { background: var(--d-tier); }
    
    .tier-title {
      font-size: 2.2em;
      margin-bottom: 25px;
      color: var(--text-color);
      font-weight: 900;
      display: flex;
      align-items: center;
      position: relative;
      padding-left: 20px;
      padding-bottom: 10px;
    }
    
    .tier-title::before {
      content: '';
      position: absolute;
      left: 0;
      bottom: 0;
      width: 100%;
      height: 2px;
      background: rgba(0, 0, 0, 0.1);
    }
    
    .s-tier .tier-title::before { background: var(--s-tier); opacity: 0.3; }
    .a-tier .tier-title::before { background: var(--a-tier); opacity: 0.3; }
    .b-tier .tier-title::before { background: var(--b-tier); opacity: 0.3; }
    .c-tier .tier-title::before { background: var(--c-tier); opacity: 0.3; }
    .d-tier .tier-title::before { background: var(--d-tier); opacity: 0.3; }
    
    .hero-list {
      display: flex;
      flex-wrap: wrap;
      gap: 25px;
      justify-content: flex-start;
    }
    
    .hero {
      width: 120px;
      text-align: center;
      position: relative;
    }
    
    .hero-card {
      background: white;
      border-radius: 18px;
      padding: 10px;
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
    }
    
    .hero-img-container {
      position: relative;
      width: 90px;
      height: 90px;
      margin: 0 auto;
      border-radius: 50%;
      overflow: hidden;
      border: 4px solid rgba(255, 255, 255, 0.7);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
      background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    }
    
    .s-tier .hero-img-container { border-color: rgba(255, 145, 0, 0.7); box-shadow: 0 5px 15px rgba(255, 145, 0, 0.3); }
    .a-tier .hero-img-container { border-color: rgba(253, 167, 223, 0.7); box-shadow: 0 5px 15px rgba(253, 167, 223, 0.3); }
    .b-tier .hero-img-container { border-color: rgba(94, 252, 232, 0.7); box-shadow: 0 5px 15px rgba(94, 252, 232, 0.3); }
    .c-tier .hero-img-container { border-color: rgba(168, 255, 120, 0.7); box-shadow: 0 5px 15px rgba(168, 255, 120, 0.3); }
    .d-tier .hero-img-container { border-color: rgba(189, 187, 190, 0.7); box-shadow: 0 5px 15px rgba(189, 187, 190, 0.3); }
    
    .hero img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .hero-name {
      margin-top: 12px;
      font-size: 0.9em;
      color: var(--text-color);
      font-weight: 700;
      padding: 0 5px;
      line-height: 1.3;
      min-height: 2.6em;
    }
    
    .footer {
      text-align: center;
      margin-top: 50px;
      padding: 30px;
      color: var(--text-light);
      font-size: 1em;
      background: white;
      border-radius: 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      position: relative;
      overflow: hidden;
    }
    
    .footer::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 5px;
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    @media (max-width: 768px) {
      .header h1 { font-size: 2.5em; }
      .hero-list { justify-content: center; }
      .tier-section { padding: 20px 15px; }
      .tier-badge { width: 50px; height: 50px; font-size: 1.8em; }
      .tier-title { font-size: 1.8em; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>ワイルドリフト <span>ティアリスト</span></h1>
      <div class="version-info">バージョン ${patchNumber}</div>
    </div>
`;

    const htmlTail = `
    <div class="footer">
      <p>ワイルドリフト ティアリスト ${latestDate} • バージョン ${patchNumber}</p>
      <p style="margin-top: 10px; font-size: 0.9em;">※勝率・ピック率・BAN率から算出</p>
    </div>
  </div>
  
  <!-- スクリプト削除 -->
</body>
</html>
`;

    let htmlBody = "";
    const grades = ['S', 'A', 'B', 'C', 'D'];
    grades.forEach(grade => {
      const filtered = championStats.filter(row => row.grade === grade);
      if (filtered.length === 0) return;
      const description = tierDescriptions[grade] || "";
      htmlBody += `    <!-- ${grade} Tier -->\n`;
      htmlBody += `    <div class="tier-section ${grade.toLowerCase()}-tier">\n`;
      htmlBody += `      <div class="tier-badge">${grade}</div>\n`;
      htmlBody += `      <div class="tier-title">${grade} Tier</div>\n`;
      htmlBody += `      <div class="hero-list">\n`;
      filtered.forEach(row => {
        const key = row.champion_name; // champion_statsの名前は中国語表記と仮定
        const mapping = championMap[key] || {};
        // 日本語名は mapping から、なければそのまま表示
        const japaneseName = mapping.japanese || key;
        // 画像はenglish_nameを用いる（mappingがなければkeyをそのまま利用）
        const englishName = mapping.english || key;
        const championImgPath = "file://" + path.join(championImagesDir, `${englishName}.webp`);
        htmlBody += `        <div class="hero">\n`;
        htmlBody += `          <div class="hero-card">\n`;
        htmlBody += `            <div class="hero-img-container">\n`;
        htmlBody += `              <img src="${championImgPath}" alt="${japaneseName}">\n`;
        htmlBody += `            </div>\n`;
        htmlBody += `            <div class="hero-name">${japaneseName}</div>\n`;
        htmlBody += `          </div>\n`;
        htmlBody += `        </div>\n`;
      });
      htmlBody += `      </div>\n`;
      htmlBody += `    </div>\n`;
    });

    const finalHtml = htmlHead + htmlBody + htmlTail;
    const htmlFilePath = path.join(outputDir, "champion_tier_list.html");
    fs.writeFileSync(htmlFilePath, finalHtml, "utf-8");
    console.log(`HTMLファイルが ${htmlFilePath} に出力されました。`);

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
    await page.waitForSelector('.header');
    await page.waitForSelector('.container');

    const containerElement = await page.$('.container');
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

#ワイルドリフト #WildRift #上单`;

    try {
      const mediaId = await rwClient.v1.uploadMedia(screenshotPath);
      await rwClient.v2.tweet(tweetText, {
        media: { media_ids: [mediaId] },
      });
      console.log("ツイートが投稿されました。");
    } catch (error) {
      console.error("ツイート投稿中にエラーが発生しました:", error);
    }
  } catch (err) {
    console.error("エラー:", err);
  }
})();

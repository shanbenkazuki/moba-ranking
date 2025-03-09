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
    const pokemonImagesDir = path.join(baseDir, "pokemon_images");

    // ----------------------------
    // 2. SQLiteからデータ取得
    // ----------------------------
    const dbPath = path.join(baseDir, "unite.db");
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
      if (err) console.error("DBオープンエラー:", err);
    });

    // 最新の reference_date を取得
    const latestDateRows = await runQuery(db, "SELECT MAX(reference_date) as latest_date FROM pokemon_stats");
    const latestDate = latestDateRows[0].latest_date;

    // 最新日付の pokemon_stats を取得
    const pokemonStats = await runQuery(db, "SELECT * FROM pokemon_stats WHERE reference_date = ?", [latestDate]);
    console.log(`最新の reference_date (${latestDate}) のデータ件数: ${pokemonStats.length}`);

    // 英名→日本語名のマッピング取得
    const pokemonMapRows = await runQuery(db, "SELECT english_name, japanese_name FROM pokemons");
    const pokemonNameMap = {};
    pokemonMapRows.forEach(row => {
      pokemonNameMap[row.english_name] = row.japanese_name;
    });

    // 最新パッチ情報（バージョン）の取得
    const patchRows = await runQuery(db, "SELECT patch_number FROM patches ORDER BY release_date DESC LIMIT 1");
    const patchNumber = (patchRows.length > 0) ? patchRows[0].patch_number : "N/A";

    db.close();

    // ----------------------------
    // 3. Zスコア・強さスコア算出
    // ----------------------------
    const winRates = pokemonStats.map(row => row.win_rate);
    const pickRates = pokemonStats.map(row => row.pick_rate);
    const banRates = pokemonStats.map(row => row.ban_rate);

    const winMean = mean(winRates);
    const winStd = stdDev(winRates, winMean);
    const pickMean = mean(pickRates);
    const pickStd = stdDev(pickRates, pickMean);
    const banMean = mean(banRates);
    const banStd = stdDev(banRates, banMean);

    pokemonStats.forEach(row => {
      row.win_rate_z = (row.win_rate - winMean) / winStd;
      row.pick_rate_z = (row.pick_rate - pickMean) / pickStd;
      row.ban_rate_z = (row.ban_rate - banMean) / banStd;
      const w_win = 0.5, w_ban = 0.3, w_pick = 0.2;
      row.strength_score = w_win * row.win_rate_z + w_ban * row.ban_rate_z + w_pick * row.pick_rate_z;
      row.grade = assignGrade(row.strength_score);
    });
    // strength_score の降順にソート
    pokemonStats.sort((a, b) => b.strength_score - a.strength_score);

    // ----------------------------
    // 4. HTML出力用文字列生成
    // ----------------------------
    const tierDescriptions = {
      'S': 'Meta Definers',
      'A': 'Top Picks',
      'B': 'Balanced Picks',
      'C': 'Situational Picks',
      'D': 'Needs Buff'
    };

    const htmlHead = `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ポケモンユナイト TIER LIST</title>
  <style>
    :root {
      --primary-color: #fb4f3a;
      --secondary-color: #222831;
      --accent-color: #ffd700;
      --bg-dark: #1a1a1a;
      --bg-card: #252a34;
      --text-light: #f0f0f0;
      --text-secondary: #aaa;
      --s-tier: linear-gradient(135deg, #ff7b00, #ff0050);
      --a-tier: linear-gradient(135deg, #9c27b0, #3f51b5);
      --b-tier: linear-gradient(135deg, #2196f3, #00bcd4);
      --c-tier: linear-gradient(135deg, #4caf50, #8bc34a);
      --d-tier: linear-gradient(135deg, #9e9e9e, #607d8b);
    }
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    body {
      background-color: var(--bg-dark);
      color: var(--text-light);
      padding: 0;
      margin: 0;
    }
    .container {
      max-width: 1920px;
      margin: 0 auto;
      padding: 20px;
    }
    .header {
      text-align: center;
      padding: 40px 20px;
      background: linear-gradient(to right, #1a1a1a, #252a34, #1a1a1a);
      border-bottom: 3px solid var(--primary-color);
      margin-bottom: 30px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .header h1 {
      font-size: 3.5em;
      font-weight: 800;
      margin-bottom: 10px;
      color: var(--text-light);
      text-transform: uppercase;
      letter-spacing: 2px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    }
    .header h1 span {
      color: var(--primary-color);
    }
    .version-info {
      display: inline-block;
      font-size: 1.2em;
      font-weight: 600;
      color: var(--text-light);
      background-color: var(--primary-color);
      padding: 8px 20px;
      border-radius: 30px;
      margin-top: 15px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .tier-section {
      margin-bottom: 40px;
      padding: 25px;
      border-radius: 15px;
      background-color: var(--bg-card);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
      position: relative;
      overflow: hidden;
    }
    .tier-section::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 5px;
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
      top: 15px;
      right: 15px;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8em;
      font-weight: 800;
      color: white;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .s-tier .tier-badge { background: var(--s-tier); }
    .a-tier .tier-badge { background: var(--a-tier); }
    .b-tier .tier-badge { background: var(--b-tier); }
    .c-tier .tier-badge { background: var(--c-tier); }
    .d-tier .tier-badge { background: var(--d-tier); }
    .tier-title {
      font-size: 2em;
      margin-bottom: 20px;
      color: var(--text-light);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      display: flex;
      align-items: center;
    }
    .tier-title::after {
      content: '';
      flex-grow: 1;
      height: 1px;
      margin-left: 15px;
      background: rgba(255, 255, 255, 0.2);
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
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      position: relative;
    }
    .hero:hover { transform: translateY(-10px); }
    .hero-card {
      background: rgba(0, 0, 0, 0.3);
      border-radius: 12px;
      padding: 8px;
      transition: all 0.3s ease;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .hero:hover .hero-card { box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5); }
    .hero-img-container {
      position: relative;
      width: 84px;
      height: 84px;
      margin: 0 auto;
      border-radius: 12px;
      overflow: hidden;
      border: 2px solid rgba(255, 255, 255, 0.1);
    }
    .s-tier .hero:hover .hero-img-container { border-color: rgba(255, 123, 0, 0.6); }
    .a-tier .hero:hover .hero-img-container { border-color: rgba(156, 39, 176, 0.6); }
    .b-tier .hero:hover .hero-img-container { border-color: rgba(33, 150, 243, 0.6); }
    .c-tier .hero:hover .hero-img-container { border-color: rgba(76, 175, 80, 0.6); }
    .d-tier .hero:hover .hero-img-container { border-color: rgba(158, 158, 158, 0.6); }
    .hero img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }
    .hero:hover img { transform: scale(1.1); }
    .hero-name {
      margin-top: 8px;
      font-size: 0.9em;
      color: var(--text-light);
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .stats-overlay {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      font-size: 0.75em;
      padding: 2px 0;
      opacity: 0;
      transition: opacity 0.3s;
    }
    .hero:hover .stats-overlay { opacity: 1; }
    .footer {
      text-align: center;
      margin-top: 50px;
      padding: 20px;
      color: var(--text-secondary);
      font-size: 0.9em;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    @media (max-width: 768px) {
      .header h1 { font-size: 2.5em; }
      .hero-list { justify-content: center; }
      .tier-section { padding: 20px 15px; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>ポケモンユナイト <span>TIER LIST</span></h1>
    <div class="version-info">バージョン ${patchNumber}</div>
  </div>
  <div class="container">
`;

    const htmlTail = `
    <div class="footer">
      ポケモンユナイト Tier List ${latestDate} • バージョン ${patchNumber}
    </div>
  </div>
</body>
</html>
`;

    let htmlBody = "";
    const grades = ['S', 'A', 'B', 'C', 'D'];
    grades.forEach(grade => {
      const filtered = pokemonStats.filter(row => row.grade === grade);
      if (filtered.length === 0) return;
      const description = tierDescriptions[grade] || "";
      htmlBody += `    <!-- ${grade} Tier -->\n`;
      htmlBody += `    <div class="tier-section ${grade.toLowerCase()}-tier">\n`;
      htmlBody += `      <div class="tier-badge">${grade}</div>\n`;
      htmlBody += `      <div class="tier-title">${grade} Tier - ${description}</div>\n`;
      htmlBody += `      <div class="hero-list">\n`;
      filtered.forEach(row => {
        const englishName = row.pokemon_name; // カラム名に合わせる
        const japaneseName = pokemonNameMap[englishName] || englishName;
        const winRate = row.win_rate;
        const pokemonImgPath = "file://" + path.join(pokemonImagesDir, `${englishName}.webp`);
        htmlBody += `        <div class="hero">\n`;
        htmlBody += `          <div class="hero-card">\n`;
        htmlBody += `            <div class="hero-img-container">\n`;
        htmlBody += `              <img src="${pokemonImgPath}" alt="${japaneseName}">\n`;
        htmlBody += `              <div class="stats-overlay">WR: ${winRate.toFixed(1)}%</div>\n`;
        htmlBody += `            </div>\n`;
        htmlBody += `            <div class="hero-name">${japaneseName}</div>\n`;
        htmlBody += `          </div>\n`;
        htmlBody += `        </div>\n`;
      });
      htmlBody += `      </div>\n`;
      htmlBody += `    </div>\n`;
    });

    const finalHtml = htmlHead + htmlBody + htmlTail;
    const htmlFilePath = path.join(outputDir, "pokemon_tier_list.html");
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

    const headerElement = await page.$('.header');
    const containerElement = await page.$('.container');
    const headerBox = await headerElement.boundingBox();
    const containerBox = await containerElement.boundingBox();

    const unionX = Math.min(headerBox.x, containerBox.x);
    const unionY = Math.min(headerBox.y, containerBox.y);
    const unionWidth = Math.max(headerBox.x + headerBox.width, containerBox.x + containerBox.width) - unionX;
    const unionHeight = (containerBox.y + containerBox.height) - unionY;

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const screenshotPath = path.join(outputDir, `pokemon_tier_list_${timestamp}.png`);

    await page.screenshot({
      path: screenshotPath,
      clip: { x: unionX, y: unionY, width: unionWidth, height: unionHeight }
    });
    console.log(`スクリーンショットが ${screenshotPath} に保存されました。`);

    await browser.close();

    // ----------------------------
    // 6. twitter-api-v2でスクリーンショットを添付してXに投稿
    // ----------------------------
//     const apiKey = process.env.API_KEY;
//     const apiSecretKey = process.env.API_SECRET_KEY;
//     const accessToken = process.env.ACCESS_TOKEN;
//     const accessTokenSecret = process.env.ACCESS_TOKEN_SECRET;
//     const bearerToken = process.env.BEARER_TOKEN;

//     const twitterClient = new TwitterApi({
//       appKey: apiKey,
//       appSecret: apiSecretKey,
//       accessToken: accessToken,
//       accessSecret: accessTokenSecret,
//     });
//     const rwClient = twitterClient.readWrite;

//     const tweetText = `今週のポケモンユナイトのTier表を公開します。

// バージョン：${patchNumber}

// #ポケモンユナイト #PokemonUnite`;

//     try {
//       const mediaId = await rwClient.v1.uploadMedia(screenshotPath);
//       await rwClient.v2.tweet(tweetText, {
//         media: { media_ids: [mediaId] },
//       });
//       console.log("ツイートが投稿されました。");
//     } catch (error) {
//       console.error("ツイート投稿中にエラーが発生しました:", error);
//     }
  } catch (err) {
    console.error("エラー:", err);
  }
})();

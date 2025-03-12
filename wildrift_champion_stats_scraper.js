const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// ログ出力用の関数（日本時間でタイムスタンプ付き）
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
      const winRate = winRateEl ? winRateEl.innerText.trim() : '';
  
      const pickRateEl = li.querySelector('div:nth-child(5)');
      const pickRate = pickRateEl ? pickRateEl.innerText.trim() : '';
  
      const banRateEl = li.querySelector('div:nth-child(6)');
      const banRate = banRateEl ? banRateEl.innerText.trim() : '';
  
      return { name, 胜率: winRate, 登场率: pickRate, BAN率: banRate };
    }).filter(item => item.name !== '');
  });
  return data;
}

(async () => {
  try {
    logWithJST("スクリプト開始");

    // headlessモードでブラウザを起動
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

    // JSON形式に整形
    const jsonOutput = JSON.stringify(champion_stats, null, 2);

    // ログファイルへ出力
    const outputFilePath = path.join("/Users/yamamotokazuki/develop/moba-ranking/logs", "wildrift_champion_stats_scraper.log");
    fs.appendFileSync(outputFilePath, `取得データ:\n${jsonOutput}\n`);
    logWithJST("全データをログファイルに出力完了");

    await browser.close();
    logWithJST("ブラウザを閉じました。スクリプト終了");
  } catch (error) {
    logWithJST(`エラー発生: ${error}`);
    process.exit(1);
  }
})();

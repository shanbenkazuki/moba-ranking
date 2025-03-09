const puppeteer = require('puppeteer');

// ログ出力用の簡易関数
function log(level, message) {
  console.log(`[${level}] ${message}`);
}

(async () => {
  let browser;
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

    // ここにその後の処理を追加可能

  } catch (error) {
    log('ERROR', error);
  } finally {
    if (browser) {
      await browser.close();
      log('INFO', 'ブラウザを閉じました');
    }
  }
})();

# Mobile Legends Tier & Stats System

## 概要

本プロジェクトは、Mobile Legends のヒーロー統計データの収集から分析、Tier 表の生成、そして X（旧 Twitter）への自動投稿までを一貫して行うシステムです。  
以下の 2 つの主要な Python スクリプトで構成されています。

1. **mlbb_hero_stats_scraper.py**  
   - Mobile Legends のランキングページから各ヒーローの統計データ（勝率、ピック率、BAN率など）をスクレイピングし、SQLite データベースに保存します。

2. **mlbb_tier_poster.py**  
   - SQLite データベースから最新のヒーロースタッツを取得し、zスコア・重み付けによりヒーローの強さスコアを算出。  
   - 得られたスコアを元に S, A, B, C, D の各 Tier に分類し、HTML 形式で視覚的な Tier 表を生成。  
   - Selenium により HTML のスクリーンショットを撮影し、Tweepy を用いて X（Twitter）へ投稿します。

## プロジェクト構成

```
project_root/
├── logs/                       # ログファイル出力先
├── hero_images/                # ヒーロー画像（.webp形式、ファイル名は英語名と一致）
├── output/                     # 生成された HTML とスクリーンショット画像
├── mlbb.db                     # SQLite データベース（hero_stats, heroes, patches テーブルを含む）
├── mlbb_hero_stats_scraper.py  # スクレイピングおよびデータ保存スクリプト
├── mlbb_tier_poster.py         # Tier 表生成と Twitter への投稿スクリプト
└── README.md                   # 本ドキュメント
```

## 必要環境・依存パッケージ

- **Python 3.x**
- **SQLite3**（Python 標準ライブラリ）
- **Google Chrome** と **ChromeDriver**（`webdriver_manager` により自動管理）
- **Twitter API 認証情報**（環境変数に設定：`API_KEY`, `API_SECRET_KEY`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`, `BEARER_TOKEN`）

使用パッケージ:
- pandas
- scipy
- selenium
- webdriver_manager
- tweepy
- beautifulsoup4

依存パッケージは、以下のような `requirements.txt` にまとめると便利です。

```bash
pip install -r requirements.txt
```

## セットアップ

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/yourusername/mlbb-tier-system.git
   cd mlbb-tier-system
   ```

2. **SQLite データベース**
   - プロジェクトルートに `mlbb.db` を配置してください。  
   - 必要なテーブル（`hero_stats`, `heroes`, `patches`）のスキーマは各自で用意してください。

3. **ヒーロー画像**
   - `hero_images/` ディレクトリに各ヒーローの画像ファイル（`.webp`形式）を配置します。  
   - ファイル名はヒーローの英語名と一致させてください。

4. **Twitter API 認証情報**
   - 環境変数に以下の認証情報を設定してください:
     - `API_KEY`
     - `API_SECRET_KEY`
     - `ACCESS_TOKEN`
     - `ACCESS_TOKEN_SECRET`
     - `BEARER_TOKEN`

## 使用方法

### 1. ヒーロー統計データのスクレイピングと保存  
`mlbb_hero_stats_scraper.py` を実行すると、Mobile Legends のランキングページから以下の処理を行います:

- **Selenium によるページ操作:**
  - ヘッドレス Chrome を使用して Mobile Legends のランキングページ（`https://m.mobilelegends.com/rank`）をオープン。
  - プライバシーポリシーのポップアップを自動でクローズ。
  - 期間範囲タブから『Past 7 days』、ランク選択タブから『Mythic』ランクを選択。

- **データの抽出:**
  - ページスクロールにより全データを読み込み、BeautifulSoup で各ヒーローの名前、勝率、ピック率、BAN率を抽出。
  - 参照日時（reference date）や最新パッチ番号も取得。

- **SQLite への保存:**
  - 抽出したデータを、既存の `mlbb.db` の `hero_stats` テーブルへ保存。  
  - ヒーローが `heroes` テーブルに存在しない場合は、新規登録も実施。

- **ログ出力:**
  - ログは `logs/` ディレクトリに、実行日付付き（例：`mlbb_scraping_YYYY-MM-DD.log`）で保存されます。

実行コマンド:
```bash
python mlbb_hero_stats_scraper.py
```

### 2. Tier 表生成と Twitter への自動投稿  
`mlbb_tier_poster.py` を実行すると、以下の処理が行われます:

- **データ取得と分析:**
  - SQLite データベースから最新のヒーロースタッツを取得。
  - `win_rate`, `pick_rate`, `ban_rate` の Zスコアを計算し、各ヒーローの強さスコアを重み付けして算出。
  - 強さスコアに基づき、各ヒーローに S, A, B, C, D の評価を付与。

- **HTML 生成:**
  - 各 Tier ごとにヒーロー画像と名前を表示する HTML を生成し、`output/hero_tier_list.html` に出力。

- **スクリーンショット撮影:**
  - Selenium を使用して生成した HTML を開き、スクリーンショット（`output/hero_tier_list_screenshot.png`）を撮影。

- **Twitter 投稿:**
  - Tweepy を用いて、スクリーンショット画像と最新パッチ情報付きのツイートを投稿。

- **ログ出力:**
  - ログは `logs/mlbb_tier_poster.log` に記録されます。

実行コマンド:
```bash
python mlbb_tier_poster.py
```

## ログについて

- **スクレイピング処理**  
  ログファイルは `logs/mlbb_scraping_YYYY-MM-DD.log` として保存され、処理の進捗やエラー情報を詳細に記録します。

- **Tier 表生成・投稿処理**  
  ログは `logs/mlbb_tier_poster.log` に記録され、各工程の実行状況が確認できます。

## 注意点

- CSS セレクタは Mobile Legends のページ構造に依存しているため、サイトの変更時は適宜修正が必要です。
- Twitter への投稿処理において、API 認証情報が正しく設定されているか確認してください。
- 実行環境に合わせたパスの設定（例: `base_dir` や `db_path`）を適宜変更してください。



~/Library/LaunchAgents/com.moba_ranking.mlbb_hero_stats_scraper.plist
毎日1時に実行 


launchctl start com.moba_ranking.mlbb_hero_stats_scraper

node mlbb_tier_x_poster.js

launchctl start com.moba_ranking.mlbb_tier_x_poster


launchctl load ~/Library/LaunchAgents/com.moba_ranking.mlbb_tier_x_poster.plist
launchctl unload ~/Library/LaunchAgents/com.moba_ranking.mlbb_tier_x_poster.plist
毎週木曜日の1時10分に実行


launchctl load ~/Library/LaunchAgents/com.moba_ranking.unite_pokemon_stats_scraper.plist
launchctl unload ~/Library/LaunchAgents/com.moba_ranking.unite_pokemon_stats_scraper.plist
毎日1時30分に実行

launchctl load ~/Library/LaunchAgents/com.moba_ranking.unite_tier_x_poster.plist
毎週月曜日の1時40分に実行

launchctl load ~/Library/LaunchAgents/com.moba_ranking.wildrift_champion_stats_scraper.plist
毎日1時50分に実行

launchctl load ~/Library/LaunchAgents/com.moba_ranking.wildrift_tier_x_poster.plist
毎週火曜日の2時00分に実行

node mlbb_hero_stats_scraper.js

launchctl load ~/Library/LaunchAgents/com.moba_ranking.commitdb.plist

launchctl load ~/Library/LaunchAgents/com.moba_ranking.mlbb_tier_x_poster.plist
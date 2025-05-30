# MOBAランキング自動更新システム

## 概要
本プロジェクトは、以下の3つのゲームタイトルの勝率・Pick率・BAN率をスクレイピングし、Tier表を作成してX（旧Twitter）に自動投稿するシステムです。

- **モバイル・レジェンド（Mobile Legends: Bang Bang）**
- **ポケモンユナイト（Pokémon UNITE）**
- **ワイルドリフト（League of Legends: Wild Rift）**

ジョブのスケジューリングには **launchd** を使用し、自動的にデータ取得・Tier表公開が行われます。

## 動作概要
### スクレイピング & データ取得
各ゲームの勝率・Pick率・BAN率のデータをWebスクレイピングにより取得し、データベースに保存します。

### Tier表作成 & 自動投稿
取得したデータをもとにTier表画像を作成し、指定したスケジュールでX（旧Twitter）に自動投稿します。

## ジョブスケジュール
以下のスケジュールでスクレイピングとTier表の公開が行われます。

| ゲームタイトル | スクレイピング実行時間 | Tier表公開時間 |
|----------------|----------------|----------------|
| モバイル・レジェンド | 毎日 1:00 | 毎週金曜日 18:00 |
| ポケモンユナイト | 毎日 1:10 | 毎週月曜日 18:00 |
| ワイルドリフト | 毎日 1:20 | 毎週水曜日 18:00 |

## ジョブ登録情報
ジョブの管理には `launchd` を使用し、plistファイルを以下のディレクトリに保存しています。

```
~/Library/LaunchAgents/
```

### plistファイル一覧
#### モバイル・レジェンド
- **スクレイピング:** `com.moba_ranking.mlbb_hero_stats_scraper.plist`
- **Tier表公開:** `com.moba_ranking.mlbb_tier_x_poster.plist`

#### ポケモンユナイト
- **スクレイピング:** `com.moba_ranking.unite_pokemon_stats_scraper.plist`
- **Tier表公開:** `com.moba_ranking.unite_tier_x_poster.plist`

#### ワイルドリフト
- **スクレイピング:** `com.moba_ranking.wildrift_champion_stats_scraper.plist`
- **Tier表公開:** `com.moba_ranking.wildrift_tier_x_poster.plist`

## launchd コマンド
ジョブの登録・解除・実行は以下のコマンドで管理します。

### ジョブの登録
```
launchctl load ~/Library/LaunchAgents/{plistファイル名}
```

### ジョブの解除
```
launchctl unload ~/Library/LaunchAgents/{plistファイル名}
```

### 即時実行
```
launchctl start {plistラベル名}
```

### 登録ジョブの一覧確認
```
launchctl list | grep com.moba_ranking
```

## 自動コミット
データベースの変更を自動的にGitリポジトリへコミットするスクリプト `commit_db.sh` を用意しています。

## データベース構成（ER図）

- [moba_log](docs/er_moba_log.md)

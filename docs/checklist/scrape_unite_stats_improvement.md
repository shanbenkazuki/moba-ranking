# scrape_unite_stats.py 改善実装計画書

## 概要
`scrape_unite_stats.py`を改善し、以下の要件を満たすよう修正する：
- unite_api_content.htmlファイルの出力を停止
- 取得データをdata/moba_log.dbに保存（gameのid=2）
- charactersテーブルへの存在チェック・新規登録機能の追加
- 未登録キャラクターの画像をpokemon_images/に保存

## 実装チェックリスト

### 1. HTMLファイル出力の停止
- [ ] HTMLコンテンツをファイルに保存している処理を削除
  - [ ] `with open('unite_api_content.html', 'w', encoding='utf-8') as f:` を削除
  - [ ] HTMLファイル保存に関するprintメッセージを削除

### 2. データベース接続・操作機能の追加
- [ ] SQLiteデータベース接続機能をインポート
  - [ ] `import sqlite3` を追加
- [ ] DBファイルパス定数を定義
  - [ ] `DB_PATH = 'data/moba_log.db'` を定義
- [ ] DB接続ヘルパー関数を実装
  - [ ] `connect_db()` 関数を作成

### 3. キャラクター存在チェック機能の実装
- [ ] charactersテーブル存在チェック関数を実装
  - [ ] `check_character_exists(pokemon_name)` 関数を作成
  - [ ] game_id=2でフィルタリング
  - [ ] english_nameでの検索機能
- [ ] 既存キャラクターのcharacter_id取得機能を実装
  - [ ] `get_character_id(pokemon_name)` 関数を作成

### 4. 新規キャラクター登録機能の実装
- [ ] charactersテーブルへの新規キャラクター登録機能を実装
  - [ ] `register_new_character(pokemon_name)` 関数を作成
  - [ ] game_id=2を設定
  - [ ] english_nameに正規化されたpokemon_nameを設定
  - [ ] 登録後のcharacter_idを取得して返す機能

### 5. 画像ダウンロード機能の実装
#### 5.1 画像取得のための依存関係追加
- [ ] httpxライブラリをインポート
  - [ ] `import httpx` を追加
- [ ] pathlibライブラリをインポート
  - [ ] `from pathlib import Path` を追加

#### 5.2 画像ダウンロード機能
- [ ] 画像ダウンロード関数を実装
  - [ ] `download_pokemon_image(pokemon_name, img_src)` 関数を作成
  - [ ] pokemon_images/ディレクトリの作成確認
  - [ ] ファイル拡張子の適切な判定
  - [ ] 画像ファイルの保存機能

#### 5.3 未登録キャラクターの画像情報取得
- [ ] 未登録キャラクター専用の画像取得機能を実装
  - [ ] `scrape_unite_image.py`の`UniteImageScraper`クラスを参考に実装
  - [ ] `https://unite.pokemon.com/en-us/pokemon/`へのアクセス機能
  - [ ] ポケモンカードリストからの画像URL取得機能
- [ ] 未登録キャラクターのみを対象とした画像取得
  - [ ] `get_missing_pokemon_images(missing_pokemon_names)` 関数を作成
  - [ ] 未登録キャラクター名のリストを引数として受け取る
  - [ ] 該当キャラクターの画像URLのみを抽出・返却
- [ ] 画像URL取得とダウンロードの分離
  - [ ] 画像URL取得：`extract_pokemon_image_urls(pokemon_names)` 
  - [ ] 画像ダウンロード：`download_pokemon_image(pokemon_name, img_url)`
  - [ ] エラー処理：取得失敗時のフォールバック機能

### 6. 統計データベース保存機能の実装
#### 6.1 unite_statsテーブルへの保存
- [ ] unite_stats保存関数を実装
  - [ ] `save_unite_stats(character_id, stats_data, reference_date)` 関数を作成
  - [ ] win_rate, pick_rate, ban_rateの保存
  - [ ] reference_dateの設定（メタ情報から取得）
  - [ ] 重複データのチェック・更新機能

#### 6.2 unite_game_summaryテーブルへの保存
- [ ] unite_game_summary保存関数を実装
  - [ ] `save_unite_game_summary(total_games, reference_date)` 関数を作成
  - [ ] total_game_countの保存
  - [ ] reference_dateでの重複チェック・更新機能

### 7. メイン処理の統合・修正
#### 7.1 データ処理フローの修正
- [ ] extract_pokemon_stats関数の戻り値を活用
  - [ ] メタ情報（last_updated, total_games_analyzed）の取得
  - [ ] pokemon_dataリストの取得
- [ ] 各ポケモンデータの処理ループを実装
  - [ ] キャラクター存在チェック
  - [ ] 未登録の場合：画像ダウンロード → キャラクター登録
  - [ ] character_id取得
  - [ ] 統計データ保存

#### 7.2 バッチ処理の実装
- [ ] 全体処理のトランザクション対応
  - [ ] DB操作のcommit/rollback処理
- [ ] エラーハンドリングの強化
  - [ ] 各段階でのエラー処理
  - [ ] 失敗時のログ出力

### 8. ログ・進捗表示の改善
- [ ] 処理進捗の詳細ログを追加
  - [ ] キャラクター存在チェック結果
  - [ ] 新規登録されたキャラクター数
  - [ ] 画像ダウンロード成功/失敗
  - [ ] データベース保存結果
- [ ] 統計情報の表示
  - [ ] 処理前後のキャラクター数
  - [ ] 保存された統計データ数

### 9. テスト・動作確認
- [ ] データベースファイルの存在確認
  - [ ] `data/moba_log.db` ファイルの確認
- [ ] テーブルスキーマの確認
  - [ ] characters, unite_stats, unite_game_summaryテーブルの存在確認
- [ ] 実際のデータでの動作テスト
  - [ ] 既存キャラクターでの動作確認
  - [ ] 新規キャラクターでの動作確認
  - [ ] 画像ダウンロード機能の確認

### 10. 最終調整・最適化
- [ ] 不要なコード・コメントの削除
- [ ] 関数の適切な分離・整理
- [ ] パフォーマンスの最適化
  - [ ] データベースクエリの最適化
  - [ ] 画像ダウンロードの並列処理検討

## 実装順序
1. HTMLファイル出力停止（即座に適用可能）
2. データベース接続機能の実装
3. キャラクター存在チェック・登録機能の実装
4. 画像ダウンロード機能の実装
   - **注意**: `scrape_unite_image.py`の機能を流用し、`https://unite.pokemon.com/en-us/pokemon/`から画像を取得
   - `https://uniteapi.dev/meta`のHTMLには高品質な画像URLが含まれていないため、別サイトからの取得が必要
5. 統計データ保存機能の実装
6. メイン処理の統合・修正
7. テスト・動作確認
8. 最終調整・最適化

## 注意点
- game_id=2 はPokemon UNITEを示す
- 画像ファイル名はキャラクター名を正規化したものを使用
- 既存のバージョンチェック機能は維持
- エラー発生時でもスクレイピングを継続する仕組みを維持 
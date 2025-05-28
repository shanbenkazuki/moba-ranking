# MOBAランキングシステム データベース設計書

## 概要
このディレクトリには、MOBAランキングシステムで使用される統合データベース`moba_log.db`の設計ドキュメントが含まれています。

## 統合データベース: moba_log.db

### 設計アプローチ
**ゲーム別統計テーブルアプローチ**を採用し、各ゲームの統計データを独立したテーブルで管理しています。共通統計データ（勝率、ピック率、バン率）も各ゲーム固有のstatsテーブルに含めることで、シンプルで直感的な設計を実現しています。

### テーブル構成（9テーブル）

#### 共通テーブル
1. **games** - ゲーム基本情報マスター（3ゲーム）
2. **characters** - 全ゲームのキャラクター基本情報（323体）
3. **patches** - 全ゲームのパッチ情報

#### ゲーム別統計テーブル
4. **mlbb_stats** - MLBB統計データ（勝率、ピック率、バン率、ランク情報）
5. **unite_stats** - Unite統計データ（勝率、ピック率、バン率）
5.1. **unite_game_summary** - Unite全体統計データ（日付別総ゲーム数）
6. **wildrift_stats** - Wild Rift統計データ（勝率、ピック率、バン率、レーン情報）

#### システムログテーブル
8. **scraper_logs** - スクレイピング処理ログ
9. **x_post_logs** - X（旧Twitter）投稿ログ

### 設計の特徴

#### ✅ **メリット**
- **シンプルな構造**: 中間テーブルを排除し、直感的なデータアクセス
- **ゲーム特化**: 各ゲームの特性に最適化されたテーブル設計
- **高いパフォーマンス**: JOINの削減により高速なクエリ実行
- **拡張性**: 新ゲーム追加時は新テーブル作成のみ
- **データ整合性**: 外部キー制約で参照整合性を保証
- **型安全性**: ゲーム固有の制約やデータ型を適切に設定可能

#### 🎯 **各ゲームの統計データ**
- **MLBB**: 勝率、ピック率、バン率 + ランク情報（Mythic、Legend等）
- **Unite**: 勝率、ピック率、バン率 + 全体統計（日付別総ゲーム数を別テーブルで管理）
- **Wild Rift**: 勝率、ピック率、バン率 + レーン情報（Top、Jungle、Mid、ADC、Support）

## ファイル構成

### 📋 **設計ドキュメント**
- `schema_comparison.md` - 3つのアプローチ比較表

### 🗄️ **SQLファイル（採用版）**
- `moba_log_schema.sql` - **正式スキーマ定義**
- `data_migration.sql` - **データ移行スクリプト**
- `sample_queries.sql` - **サンプルクエリ集**

### 📈 **既存データベース設計**
- `moba_db_er_diagram.md` - システム管理DB設計
- `mlbb_db_er_diagram.md` - MLBB専用DB設計
- `unite_db_er_diagram.md` - Unite専用DB設計
- `wildrift_db_er_diagram.md` - Wild Rift専用DB設計

### 📁 **アーカイブ**
- `archive/` - 検討段階のファイル（統合テーブルアプローチ、JSON拡張アプローチ等）

## 使用方法

### 1. データベース作成
```bash
sqlite3 moba_log.db < moba_log_schema.sql
```

### 2. データ移行
```bash
# 既存データベースのパスを修正してから実行
sqlite3 moba_log.db < data_migration.sql
```

### 3. 簡単なクエリ例
```sql
-- MLBBの最新統計（直接アクセス）
SELECT * FROM mlbb_stats ms
JOIN characters c ON ms.character_id = c.id
WHERE ms.reference_date = (SELECT MAX(reference_date) FROM mlbb_stats);

-- Wild Riftのレーン別統計
SELECT * FROM wildrift_stats ws
JOIN characters c ON ws.character_id = c.id
WHERE ws.lane = 'ADC';

-- Uniteの高ゲーム数キャラクター
SELECT * FROM unite_stats us
JOIN characters c ON us.character_id = c.id
WHERE us.reference_date = (SELECT MAX(reference_date) FROM unite_stats);

-- Uniteの日付別総ゲーム数
SELECT * FROM unite_game_summary
ORDER BY reference_date DESC;
```

## データ統計

### 移行前（4つの分離DB）
| データベース | テーブル数 | 総レコード数 | 特徴 |
|-------------|-----------|-------------|------|
| **moba.db** | 2テーブル | 263件 | システム管理 |
| **mlbb.db** | 3テーブル | 1,783件 | ヒーロー128体 |
| **unite.db** | 3テーブル | 721件 | ポケモン72体 |
| **wildrift.db** | 3テーブル | 8,101件 | チャンピオン123体 |

### 移行後（統合DB）
| テーブル | 予想レコード数 | 説明 |
|---------|---------------|------|
| **games** | 3件 | ゲーム基本情報 |
| **characters** | 323件 | 全キャラクター統合 |
| **patches** | 5件 | 全パッチ情報統合 |
| **mlbb_stats** | 1,654件 | MLBB統計データ（共通+固有） |
| **unite_stats** | 648件 | Unite統計データ（共通のみ） |
| **unite_game_summary** | 9件 | Unite全体統計（日付別総ゲーム数） |
| **wildrift_stats** | 7,975件 | Wild Rift統計データ（共通+固有） |
| **scraper_logs** | 237件 | スクレイピングログ |
| **x_post_logs** | 26件 | X投稿ログ |

## 統合のメリット

1. **データ一元管理**: 4つのDBを1つに集約
2. **ゲーム横断分析**: 複数ゲーム間での比較分析が可能
3. **運用効率化**: データベース管理の簡素化
4. **高速アクセス**: 中間テーブルなしの直接アクセス
5. **拡張性**: 新しいゲーム追加時の対応が容易
6. **データ整合性**: 統一されたスキーマによる品質向上
7. **型安全性**: ゲーム固有データの適切な制約設定

## 設計変更のポイント

### 変更前（テーブル分離アプローチ）
- `character_stats_base`テーブルで共通統計データを管理
- ゲーム固有テーブルは固有データのみ
- 複雑なJOINが必要

### 変更後（ゲーム別統計テーブルアプローチ）
- 各ゲームのstatsテーブルに共通統計データも含める
- シンプルな構造で直感的なアクセス
- JOINの削減によるパフォーマンス向上

## 注意事項

- 全テーブルに`id`（AUTO INCREMENT）、`created_at`、`updated_at`を追加
- 外部キー制約により、データの整合性が保証される
- 各ゲームの統計データは独立したテーブルで管理
- `updated_at`自動更新トリガーを実装 
# データベース設計アプローチ比較

## 3つのアプローチ

### 1. 統合テーブル（現在の設計）
全ゲームの統計データを一つのテーブルに格納し、ゲーム固有フィールドはNULL許可

### 2. テーブル分離
共通統計データと各ゲーム固有データを別テーブルに分離

### 3. JSON拡張フィールド
共通統計データ + JSON形式でゲーム固有データを格納

## 比較表

| 項目 | 統合テーブル | テーブル分離 | JSON拡張 |
|------|-------------|-------------|----------|
| **テーブル数** | 6テーブル | 9テーブル | 6テーブル |
| **NULL値の発生** | 多い | 少ない | 少ない |
| **クエリの複雑さ** | 簡単 | 中程度 | 中程度 |
| **型安全性** | 高い | 高い | 低い |
| **パフォーマンス** | 良い | 良い | 中程度 |
| **拡張性** | 低い | 高い | 高い |
| **データ整合性** | 中程度 | 高い | 低い |
| **開発・保守性** | 簡単 | 中程度 | 中程度 |

## 詳細比較

### 🔄 **統合テーブル（現在の設計）**

#### メリット
- **シンプル**: 一つのテーブルで全データを管理
- **クエリが簡単**: JOINが少なく、理解しやすい
- **パフォーマンス**: 単一テーブルアクセスで高速

#### デメリット
- **NULL値が多い**: Wild Riftの`lane`はMLBB/Uniteでは常にNULL
- **意味の曖昧さ**: どのフィールドがどのゲームで使われるか不明確
- **拡張性の問題**: 新しいゲーム固有フィールド追加時にテーブル変更が必要

```sql
-- 例：Wild Riftのレーン別統計
SELECT win_rate, lane FROM character_stats 
WHERE character_id = 123 AND lane IS NOT NULL;

-- 問題：MLBBやUniteでもlaneフィールドが存在するが意味がない
```

### 🔀 **テーブル分離**

#### メリット
- **正規化**: 各ゲームのデータが適切に分離
- **型安全性**: 各フィールドの意味が明確
- **拡張性**: 新ゲーム追加時は新テーブル作成のみ
- **データ整合性**: ゲーム固有制約を適切に設定可能

#### デメリット
- **複雑性**: テーブル数が増加
- **JOIN必要**: ゲーム固有データ取得時に複数テーブルJOIN
- **管理コスト**: 複数テーブルの保守が必要

```sql
-- 例：Wild Riftのレーン別統計
SELECT csb.win_rate, wr.lane 
FROM character_stats_base csb
JOIN wildrift_stats wr ON csb.id = wr.base_stat_id
WHERE csb.character_id = 123;
```

### 📄 **JSON拡張フィールド**

#### メリット
- **柔軟性**: スキーマ変更なしで新フィールド追加可能
- **拡張性**: 新ゲーム固有データを簡単に追加
- **テーブル数**: 統合テーブルと同じ構造を維持

#### デメリット
- **型安全性**: JSON内のデータ型チェックが困難
- **パフォーマンス**: JSON関数使用でクエリが重くなる可能性
- **SQLite制限**: 古いバージョンではJSON関数が制限的

```sql
-- 例：Wild Riftのレーン別統計
SELECT win_rate, json_extract(game_specific_data, '$.lane') as lane
FROM character_stats 
WHERE character_id = 123 
  AND json_extract(game_specific_data, '$.lane') IS NOT NULL;
```

## 推奨アプローチ

### 🎯 **推奨：テーブル分離**

以下の理由から、**テーブル分離**を推奨します：

#### 1. **データの意味が明確**
```sql
-- MLBBのランク情報
SELECT rank_info FROM mlbb_stats WHERE base_stat_id = 1;

-- Wild Riftのレーン情報  
SELECT lane FROM wildrift_stats WHERE base_stat_id = 1;
```

#### 2. **型安全性と制約**
```sql
-- Wild Riftのレーン制約
CREATE TABLE wildrift_stats (
    lane TEXT CHECK (lane IN ('Top', 'Jungle', 'Mid', 'ADC', 'Support'))
);
```

#### 3. **将来の拡張性**
新しいゲームが追加された場合：
```sql
-- 新ゲーム用テーブル追加
CREATE TABLE newgame_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_stat_id INTEGER NOT NULL,
    new_specific_field TEXT,
    FOREIGN KEY (base_stat_id) REFERENCES character_stats_base(id)
);
```

#### 4. **パフォーマンス最適化**
```sql
-- ゲーム固有インデックス
CREATE INDEX idx_wildrift_lane ON wildrift_stats(lane);
CREATE INDEX idx_mlbb_rank ON mlbb_stats(rank_info);
```

## 実装方針

1. **基本設計**: テーブル分離アプローチを採用
2. **共通データ**: `character_stats_base`テーブル
3. **ゲーム固有データ**: 各ゲーム専用テーブル
4. **ビュー作成**: 使いやすさのためのビューを提供

```sql
-- 使いやすさのためのビュー例
CREATE VIEW v_wildrift_stats AS
SELECT 
    c.japanese_name,
    csb.win_rate,
    csb.pick_rate,
    csb.ban_rate,
    wr.lane,
    csb.reference_date
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
LEFT JOIN wildrift_stats wr ON csb.id = wr.base_stat_id
WHERE g.game_code = 'wildrift';
```

この設計により、データの整合性を保ちながら、各ゲームの固有情報を適切に管理できます。 
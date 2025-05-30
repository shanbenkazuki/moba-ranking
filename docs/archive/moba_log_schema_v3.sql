-- moba_log.db 統合データベース スキーマ定義 v3
-- 作成日: 2024年
-- 説明: JSON拡張フィールドを使用したアプローチ

-- 外部キー制約を有効化
PRAGMA foreign_keys = ON;

-- 1. games テーブル（ゲーム基本情報マスター）
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_code TEXT NOT NULL UNIQUE CHECK (game_code IN ('mlbb', 'unite', 'wildrift')),
    game_name TEXT NOT NULL,
    game_name_jp TEXT NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. characters テーブル（全ゲームのキャラクター基本情報）
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    english_name TEXT NOT NULL,
    japanese_name TEXT,
    chinese_name TEXT,
    role_style TEXT,
    release_date DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    UNIQUE (game_id, english_name)
);

-- 3. patches テーブル（全ゲームのパッチ情報）
CREATE TABLE patches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    patch_number TEXT NOT NULL,
    release_date DATE,
    english_note TEXT,
    japanese_note TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    UNIQUE (game_id, patch_number)
);

-- 4. character_stats テーブル（統計データ + JSON拡張）
CREATE TABLE character_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    patch_id INTEGER,
    win_rate NUMERIC,
    pick_rate NUMERIC,
    ban_rate NUMERIC,
    reference_date DATE NOT NULL,
    -- ゲーム固有データをJSONで格納
    game_specific_data TEXT, -- JSON形式
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (patch_id) REFERENCES patches(id) ON DELETE SET NULL,
    UNIQUE (character_id, reference_date, json_extract(game_specific_data, '$.lane'))
);

-- 5. scraper_logs テーブル（スクレイピング処理ログ）
CREATE TABLE scraper_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    scraper_status BOOLEAN NOT NULL CHECK (scraper_status IN (0, 1)),
    error_message TEXT,
    scraper_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

-- 6. x_post_logs テーブル（X投稿ログ）
CREATE TABLE x_post_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    post_status BOOLEAN NOT NULL CHECK (post_status IN (0, 1)),
    error_message TEXT,
    post_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

-- インデックス作成（パフォーマンス向上）
CREATE INDEX idx_characters_game_english ON characters(game_id, english_name);
CREATE INDEX idx_characters_japanese_name ON characters(japanese_name);
CREATE INDEX idx_patches_game_patch ON patches(game_id, patch_number);
CREATE INDEX idx_character_stats_character_date ON character_stats(character_id, reference_date);
CREATE INDEX idx_character_stats_patch ON character_stats(patch_id);
CREATE INDEX idx_character_stats_reference_date ON character_stats(reference_date);
-- JSON拡張フィールド用インデックス
CREATE INDEX idx_character_stats_lane ON character_stats(json_extract(game_specific_data, '$.lane'));
CREATE INDEX idx_character_stats_rank ON character_stats(json_extract(game_specific_data, '$.rank_info'));
CREATE INDEX idx_scraper_logs_game_date ON scraper_logs(game_id, scraper_date);
CREATE INDEX idx_x_post_logs_game_date ON x_post_logs(game_id, post_date);

-- 初期データ挿入（ゲーム情報）
INSERT INTO games (game_code, game_name, game_name_jp, description) VALUES
('mlbb', 'Mobile Legends: Bang Bang', 'モバイルレジェンド', 'MOBAゲーム'),
('unite', 'Pokémon UNITE', 'ポケモンユナイト', 'ポケモンMOBAゲーム'),
('wildrift', 'League of Legends: Wild Rift', 'リーグ・オブ・レジェンド ワイルドリフト', 'LOLモバイル版');

-- updated_at自動更新トリガー作成
CREATE TRIGGER update_games_updated_at
    AFTER UPDATE ON games FOR EACH ROW
BEGIN
    UPDATE games SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_characters_updated_at
    AFTER UPDATE ON characters FOR EACH ROW
BEGIN
    UPDATE characters SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_patches_updated_at
    AFTER UPDATE ON patches FOR EACH ROW
BEGIN
    UPDATE patches SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_character_stats_updated_at
    AFTER UPDATE ON character_stats FOR EACH ROW
BEGIN
    UPDATE character_stats SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_scraper_logs_updated_at
    AFTER UPDATE ON scraper_logs FOR EACH ROW
BEGIN
    UPDATE scraper_logs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_x_post_logs_updated_at
    AFTER UPDATE ON x_post_logs FOR EACH ROW
BEGIN
    UPDATE x_post_logs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ===== JSON使用例 =====

-- MLBB データ挿入例
-- INSERT INTO character_stats (character_id, patch_id, win_rate, pick_rate, ban_rate, reference_date, game_specific_data)
-- VALUES (1, 1, 55.2, 12.5, 8.3, '2024-01-15', '{"rank_info": "Mythic"}');

-- Unite データ挿入例
-- INSERT INTO character_stats (character_id, patch_id, win_rate, pick_rate, ban_rate, reference_date, game_specific_data)
-- VALUES (2, 2, 52.8, 15.2, 5.1, '2024-01-15', '{"total_game_count": 1250}');

-- Wild Rift データ挿入例
-- INSERT INTO character_stats (character_id, patch_id, win_rate, pick_rate, ban_rate, reference_date, game_specific_data)
-- VALUES (3, 3, 48.9, 18.7, 12.4, '2024-01-15', '{"lane": "ADC"}');

-- ===== JSON検索クエリ例 =====

-- Wild Riftのレーン別統計取得
-- SELECT 
--     c.japanese_name,
--     cs.win_rate,
--     json_extract(cs.game_specific_data, '$.lane') as lane
-- FROM character_stats cs
-- JOIN characters c ON cs.character_id = c.id
-- JOIN games g ON c.game_id = g.id
-- WHERE g.game_code = 'wildrift'
--   AND json_extract(cs.game_specific_data, '$.lane') = 'ADC';

-- MLBBのランク別統計取得
-- SELECT 
--     c.japanese_name,
--     cs.win_rate,
--     json_extract(cs.game_specific_data, '$.rank_info') as rank_info
-- FROM character_stats cs
-- JOIN characters c ON cs.character_id = c.id
-- JOIN games g ON c.game_id = g.id
-- WHERE g.game_code = 'mlbb'
--   AND json_extract(cs.game_specific_data, '$.rank_info') = 'Mythic'; 
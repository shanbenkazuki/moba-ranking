-- moba_log.db 統合データベース 正式スキーマ定義
-- 作成日: 2025-05-28
-- 説明: ゲーム別統計テーブルアプローチによる統合データベース（正式版）

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

-- 4. mlbb_stats テーブル（MLBB統計データ：共通+固有）
CREATE TABLE mlbb_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    patch_id INTEGER,
    win_rate NUMERIC,
    pick_rate NUMERIC,
    ban_rate NUMERIC,
    reference_date DATE NOT NULL,
    rank_info TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (patch_id) REFERENCES patches(id) ON DELETE SET NULL,
    UNIQUE (character_id, reference_date)
);

-- 5. unite_stats テーブル（Unite統計データ：共通+固有）
CREATE TABLE unite_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    patch_id INTEGER,
    win_rate NUMERIC,
    pick_rate NUMERIC,
    ban_rate NUMERIC,
    reference_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (patch_id) REFERENCES patches(id) ON DELETE SET NULL,
    UNIQUE (character_id, reference_date)
);

-- 5.1. unite_game_summary テーブル（Unite全体統計データ）
CREATE TABLE unite_game_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_date DATE NOT NULL UNIQUE,
    total_game_count INTEGER NOT NULL,
    patch_id INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patch_id) REFERENCES patches(id) ON DELETE SET NULL
);

-- 6. wildrift_stats テーブル（Wild Rift統計データ：共通+固有）
CREATE TABLE wildrift_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    patch_id INTEGER,
    win_rate NUMERIC,
    pick_rate NUMERIC,
    ban_rate NUMERIC,
    reference_date DATE NOT NULL,
    lane TEXT CHECK (lane IN ('上单', '打野', '中路', '下路', '辅助')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (patch_id) REFERENCES patches(id) ON DELETE SET NULL,
    UNIQUE (character_id, reference_date, lane)
);

-- 7. scraper_logs テーブル（スクレイピング処理ログ）
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

-- 8. x_post_logs テーブル（X投稿ログ）
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
CREATE INDEX idx_mlbb_stats_character_date ON mlbb_stats(character_id, reference_date);
CREATE INDEX idx_mlbb_stats_patch ON mlbb_stats(patch_id);
CREATE INDEX idx_mlbb_stats_reference_date ON mlbb_stats(reference_date);
CREATE INDEX idx_unite_stats_character_date ON unite_stats(character_id, reference_date);
CREATE INDEX idx_unite_stats_patch ON unite_stats(patch_id);
CREATE INDEX idx_unite_stats_reference_date ON unite_stats(reference_date);
CREATE INDEX idx_unite_game_summary_reference_date ON unite_game_summary(reference_date);
CREATE INDEX idx_unite_game_summary_patch ON unite_game_summary(patch_id);
CREATE INDEX idx_wildrift_stats_character_date ON wildrift_stats(character_id, reference_date);
CREATE INDEX idx_wildrift_stats_patch ON wildrift_stats(patch_id);
CREATE INDEX idx_wildrift_stats_reference_date ON wildrift_stats(reference_date);
CREATE INDEX idx_wildrift_stats_lane ON wildrift_stats(lane);
CREATE INDEX idx_scraper_logs_game_date ON scraper_logs(game_id, scraper_date);
CREATE INDEX idx_x_post_logs_game_date ON x_post_logs(game_id, post_date);

-- 初期データ挿入（ゲーム情報）
INSERT INTO games (game_code, game_name, game_name_jp, description) VALUES
('mlbb', 'Mobile Legends: Bang Bang', 'モバイルレジェンド', 'MOBAゲーム'),
('unite', 'Pokémon UNITE', 'ポケモンユナイト', 'ポケモンMOBAゲーム'),
('wildrift', 'League of Legends: Wild Rift', 'リーグ・オブ・レジェンド ワイルドリフト', 'LOLモバイル版');

-- 使いやすさのためのビュー作成
-- MLBB統計ビュー（簡略化）
CREATE VIEW v_mlbb_stats AS
SELECT 
    ms.id,
    c.id as character_id,
    c.english_name,
    c.japanese_name,
    c.role_style,
    ms.win_rate,
    ms.pick_rate,
    ms.ban_rate,
    ms.reference_date,
    ms.rank_info,
    p.patch_number,
    ms.created_at,
    ms.updated_at
FROM mlbb_stats ms
JOIN characters c ON ms.character_id = c.id
LEFT JOIN patches p ON ms.patch_id = p.id;

-- Unite統計ビュー（簡略化）
CREATE VIEW v_unite_stats AS
SELECT 
    us.id,
    c.id as character_id,
    c.english_name,
    c.japanese_name,
    c.role_style,
    us.win_rate,
    us.pick_rate,
    us.ban_rate,
    us.reference_date,
    p.patch_number,
    us.created_at,
    us.updated_at
FROM unite_stats us
JOIN characters c ON us.character_id = c.id
LEFT JOIN patches p ON us.patch_id = p.id;

-- Wild Rift統計ビュー（簡略化）
CREATE VIEW v_wildrift_stats AS
SELECT 
    wr.id,
    c.id as character_id,
    c.english_name,
    c.japanese_name,
    c.chinese_name,
    c.role_style,
    wr.win_rate,
    wr.pick_rate,
    wr.ban_rate,
    wr.reference_date,
    wr.lane,
    p.patch_number,
    wr.created_at,
    wr.updated_at
FROM wildrift_stats wr
JOIN characters c ON wr.character_id = c.id
LEFT JOIN patches p ON wr.patch_id = p.id;

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

CREATE TRIGGER update_mlbb_stats_updated_at
    AFTER UPDATE ON mlbb_stats FOR EACH ROW
BEGIN
    UPDATE mlbb_stats SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_unite_stats_updated_at
    AFTER UPDATE ON unite_stats FOR EACH ROW
BEGIN
    UPDATE unite_stats SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_unite_game_summary_updated_at
    AFTER UPDATE ON unite_game_summary FOR EACH ROW
BEGIN
    UPDATE unite_game_summary SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_wildrift_stats_updated_at
    AFTER UPDATE ON wildrift_stats FOR EACH ROW
BEGIN
    UPDATE wildrift_stats SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
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
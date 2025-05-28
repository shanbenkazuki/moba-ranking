-- データ移行スクリプト v3（ゲーム別統計テーブルアプローチ用）
-- 既存の4つのデータベース（moba.db, mlbb.db, unite.db, wildrift.db）から
-- 統合データベース（moba_log.db）へのデータ移行

-- 注意: このスクリプトは既存データベースをATTACHして実行する想定
-- 実行前に既存データベースファイルのパスを確認してください

-- 既存データベースをアタッチ
ATTACH DATABASE '/Users/yamamotokazuki/develop/moba-ranking/moba.db' AS moba_db;
ATTACH DATABASE '/Users/yamamotokazuki/develop/moba-ranking/mlbb.db' AS mlbb_db;
ATTACH DATABASE '/Users/yamamotokazuki/develop/moba-ranking/unite.db' AS unite_db;
ATTACH DATABASE '/Users/yamamotokazuki/develop/moba-ranking/wildrift.db' AS wildrift_db;

-- ===== 既存データクリア =====
-- 外部キー制約により、関連データも自動削除される

DELETE FROM x_post_logs;
DELETE FROM scraper_logs;
DELETE FROM wildrift_stats;
DELETE FROM unite_game_summary;
DELETE FROM unite_stats;
DELETE FROM mlbb_stats;
DELETE FROM patches;
DELETE FROM characters;
-- gamesテーブルは初期データがあるのでクリアしない

-- ===== MLBB データ移行 =====

-- MLBBキャラクター移行
INSERT INTO characters (
    game_id, english_name, japanese_name, role_style, release_date, 
    created_at, updated_at
)
SELECT 
    1 as game_id,
    english_name,
    japanese_name,
    role as role_style,
    release_date,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM mlbb_db.heroes;

-- MLBBパッチ移行
INSERT INTO patches (
    game_id, patch_number, release_date, english_note, japanese_note,
    created_at, updated_at
)
SELECT 
    1 as game_id,
    patch_number,
    release_date,
    english_note,
    japanese_note,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM mlbb_db.patches;

-- MLBB統計データ移行（共通+固有データを直接移行）
INSERT INTO mlbb_stats (
    character_id, patch_id, win_rate, pick_rate, ban_rate, 
    reference_date, rank_info, created_at, updated_at
)
SELECT 
    c.id as character_id,
    p.id as patch_id,
    hs.win_rate,
    hs.pick_rate,
    hs.ban_rate,
    hs.reference_date,
    hs.rank as rank_info,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM mlbb_db.hero_stats hs
JOIN characters c ON c.english_name = hs.hero_name AND c.game_id = 1
LEFT JOIN patches p ON p.patch_number = hs.patch_number AND p.game_id = 1;

-- ===== UNITE データ移行 =====

-- UNITEキャラクター移行
INSERT INTO characters (
    game_id, english_name, japanese_name, role_style, release_date,
    created_at, updated_at
)
SELECT 
    2 as game_id,
    english_name,
    japanese_name,
    style as role_style,
    release_date,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM unite_db.pokemons;

-- UNITEパッチ移行
INSERT INTO patches (
    game_id, patch_number, release_date, english_note, japanese_note,
    created_at, updated_at
)
SELECT 
    2 as game_id,
    patch_number,
    release_date,
    english_note,
    japanese_note,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM unite_db.patches;

-- UNITE統計データ移行（共通データのみ）
INSERT INTO unite_stats (
    character_id, patch_id, win_rate, pick_rate, ban_rate, 
    reference_date, created_at, updated_at
)
SELECT 
    c.id as character_id,
    p.id as patch_id,
    ps.win_rate,
    ps.pick_rate,
    ps.ban_rate,
    ps.reference_date,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM unite_db.pokemon_stats ps
JOIN characters c ON c.english_name = ps.pokemon_name AND c.game_id = 2
LEFT JOIN patches p ON p.patch_number = ps.patch_number AND p.game_id = 2;

-- UNITE全体統計データ移行（日付ごとの総ゲーム数）
INSERT INTO unite_game_summary (
    reference_date, total_game_count, patch_id, created_at, updated_at
)
SELECT DISTINCT
    ps.reference_date,
    ps.total_game_count,
    p.id as patch_id,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM unite_db.pokemon_stats ps
LEFT JOIN patches p ON p.patch_number = ps.patch_number AND p.game_id = 2
WHERE ps.total_game_count IS NOT NULL;

-- ===== WILD RIFT データ移行 =====

-- Wild Riftキャラクター移行
INSERT INTO characters (
    game_id, english_name, japanese_name, chinese_name, role_style, release_date,
    created_at, updated_at
)
SELECT 
    3 as game_id,
    english_name,
    japanese_name,
    chinese_name,
    role as role_style,
    release_date,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM wildrift_db.champions;

-- Wild Riftパッチ移行
INSERT INTO patches (
    game_id, patch_number, release_date, english_note, japanese_note,
    created_at, updated_at
)
SELECT 
    3 as game_id,
    patch_number,
    release_date,
    english_note,
    japanese_note,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM wildrift_db.patches;

-- Wild Rift統計データ移行（共通+固有データを直接移行）
-- 注意: Wild Riftはレーン別データなので、レーンごとに別レコードとして扱う
INSERT INTO wildrift_stats (
    character_id, patch_id, win_rate, pick_rate, ban_rate, 
    reference_date, lane, created_at, updated_at
)
SELECT 
    c.id as character_id,
    p.id as patch_id,
    cs.win_rate,
    cs.pick_rate,
    cs.ban_rate,
    cs.reference_date,
    cs.lane,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM wildrift_db.champion_stats cs
JOIN characters c ON c.chinese_name = cs.champion_name AND c.game_id = 3
LEFT JOIN patches p ON p.patch_number = cs.patch_number AND p.game_id = 3;

-- ===== システムログ移行 =====

-- スクレイピングログ移行
INSERT INTO scraper_logs (
    game_id, scraper_status, error_message, scraper_date,
    created_at, updated_at
)
SELECT 
    g.id as game_id,
    ss.scraper_status,
    ss.error_message,
    ss.scraper_date,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM moba_db.scraper_status ss
JOIN games g ON g.game_code = ss.game_title;

-- X投稿ログ移行
INSERT INTO x_post_logs (
    game_id, post_status, error_message, post_date,
    created_at, updated_at
)
SELECT 
    g.id as game_id,
    xps.post_status,
    xps.error_message,
    xps.post_date,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM moba_db.x_post_status xps
JOIN games g ON g.game_code = xps.game_title;

-- データベースをデタッチ
DETACH DATABASE moba_db;
DETACH DATABASE mlbb_db;
DETACH DATABASE unite_db;
DETACH DATABASE wildrift_db;

-- 移行結果確認用クエリ
SELECT 'Migration Summary (Game-Specific Stats Table Approach)' as info;

SELECT 
    'Games' as table_name,
    COUNT(*) as record_count
FROM games
UNION ALL
SELECT 
    'Characters' as table_name,
    COUNT(*) as record_count
FROM characters
UNION ALL
SELECT 
    'Patches' as table_name,
    COUNT(*) as record_count
FROM patches
UNION ALL
SELECT 
    'MLBB Stats' as table_name,
    COUNT(*) as record_count
FROM mlbb_stats
UNION ALL
SELECT 
    'Unite Stats' as table_name,
    COUNT(*) as record_count
FROM unite_stats
UNION ALL
SELECT 
    'Unite Game Summary' as table_name,
    COUNT(*) as record_count
FROM unite_game_summary
UNION ALL
SELECT 
    'Wild Rift Stats' as table_name,
    COUNT(*) as record_count
FROM wildrift_stats
UNION ALL
SELECT 
    'Scraper Logs' as table_name,
    COUNT(*) as record_count
FROM scraper_logs
UNION ALL
SELECT 
    'X Post Logs' as table_name,
    COUNT(*) as record_count
FROM x_post_logs;

-- ゲーム別キャラクター数確認
SELECT 
    g.game_name_jp,
    COUNT(c.id) as character_count
FROM games g
LEFT JOIN characters c ON g.id = c.game_id
GROUP BY g.id, g.game_name_jp
ORDER BY g.id;

-- ゲーム別統計データ数確認
SELECT 
    'MLBB' as game_name,
    COUNT(*) as stats_count
FROM mlbb_stats
UNION ALL
SELECT 
    'Unite' as game_name,
    COUNT(*) as stats_count
FROM unite_stats
UNION ALL
SELECT 
    'Wild Rift' as game_name,
    COUNT(*) as stats_count
FROM wildrift_stats;

-- 各ゲームの最新統計データサンプル確認
SELECT 'MLBB Latest Stats Sample' as info;
SELECT 
    c.english_name,
    ms.win_rate,
    ms.pick_rate,
    ms.ban_rate,
    ms.rank_info,
    ms.reference_date
FROM mlbb_stats ms
JOIN characters c ON ms.character_id = c.id
WHERE ms.reference_date = (SELECT MAX(reference_date) FROM mlbb_stats)
LIMIT 5;

SELECT 'Unite Latest Stats Sample' as info;
SELECT 
    c.english_name,
    us.win_rate,
    us.pick_rate,
    us.ban_rate,
    us.reference_date
FROM unite_stats us
JOIN characters c ON us.character_id = c.id
WHERE us.reference_date = (SELECT MAX(reference_date) FROM unite_stats)
LIMIT 5;

SELECT 'Unite Game Summary Sample' as info;
SELECT 
    reference_date,
    total_game_count,
    p.patch_number
FROM unite_game_summary ugs
LEFT JOIN patches p ON ugs.patch_id = p.id
ORDER BY reference_date DESC
LIMIT 5;

SELECT 'Wild Rift Latest Stats Sample' as info;
SELECT 
    c.english_name,
    wr.win_rate,
    wr.pick_rate,
    wr.ban_rate,
    wr.lane,
    wr.reference_date
FROM wildrift_stats wr
JOIN characters c ON wr.character_id = c.id
WHERE wr.reference_date = (SELECT MAX(reference_date) FROM wildrift_stats)
LIMIT 5; 
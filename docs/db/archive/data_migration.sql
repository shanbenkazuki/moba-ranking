-- データ移行スクリプト
-- 既存の4つのデータベース（moba.db, mlbb.db, unite.db, wildrift.db）から
-- 統合データベース（moba_log.db）へのデータ移行

-- 注意: このスクリプトは既存データベースをATTACHして実行する想定
-- 実行前に既存データベースファイルのパスを確認してください

-- 既存データベースをアタッチ
ATTACH DATABASE 'path/to/moba.db' AS moba_db;
ATTACH DATABASE 'path/to/mlbb.db' AS mlbb_db;
ATTACH DATABASE 'path/to/unite.db' AS unite_db;
ATTACH DATABASE 'path/to/wildrift.db' AS wildrift_db;

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

-- MLBB統計データ移行
INSERT INTO character_stats (
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

-- UNITE統計データ移行
INSERT INTO character_stats (
    character_id, patch_id, win_rate, pick_rate, ban_rate, 
    reference_date, total_game_count, created_at, updated_at
)
SELECT 
    c.id as character_id,
    p.id as patch_id,
    ps.win_rate,
    ps.pick_rate,
    ps.ban_rate,
    ps.reference_date,
    ps.total_game_count,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM unite_db.pokemon_stats ps
JOIN characters c ON c.english_name = ps.pokemon_name AND c.game_id = 2
LEFT JOIN patches p ON p.patch_number = ps.patch_number AND p.game_id = 2;

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

-- Wild Rift統計データ移行
INSERT INTO character_stats (
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
JOIN characters c ON c.english_name = cs.champion_name AND c.game_id = 3
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
SELECT 'Migration Summary' as info;

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
    'Character Stats' as table_name,
    COUNT(*) as record_count
FROM character_stats
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
    g.game_name,
    COUNT(c.id) as character_count
FROM games g
LEFT JOIN characters c ON g.id = c.game_id
GROUP BY g.id, g.game_name
ORDER BY g.id; 
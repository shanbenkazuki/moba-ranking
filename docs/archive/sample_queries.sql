-- moba_log.db サンプルクエリ集
-- 統合データベースの活用例

-- ===== 基本的なデータ確認クエリ =====

-- 1. 全ゲームの基本情報確認
SELECT 
    id,
    game_code,
    game_name,
    game_name_jp,
    description
FROM games
ORDER BY id;

-- 2. ゲーム別キャラクター数
SELECT 
    g.game_name_jp,
    COUNT(c.id) as character_count
FROM games g
LEFT JOIN characters c ON g.id = c.game_id
GROUP BY g.id, g.game_name_jp
ORDER BY character_count DESC;

-- 3. ゲーム別パッチ数
SELECT 
    g.game_name_jp,
    COUNT(p.id) as patch_count
FROM games g
LEFT JOIN patches p ON g.id = p.game_id
GROUP BY g.id, g.game_name_jp
ORDER BY patch_count DESC;

-- ===== キャラクター関連クエリ =====

-- 4. 全ゲームのキャラクター一覧（ゲーム別）
SELECT 
    g.game_name_jp,
    c.english_name,
    c.japanese_name,
    c.role_style,
    c.release_date
FROM characters c
JOIN games g ON c.game_id = g.id
ORDER BY g.id, c.english_name;

-- 5. 特定のキャラクター名で検索（部分一致）
SELECT 
    g.game_name_jp,
    c.english_name,
    c.japanese_name,
    c.role_style
FROM characters c
JOIN games g ON c.game_id = g.id
WHERE c.english_name LIKE '%Jinx%' 
   OR c.japanese_name LIKE '%ジンクス%'
ORDER BY g.id;

-- 6. ロール/スタイル別キャラクター数
SELECT 
    g.game_name_jp,
    c.role_style,
    COUNT(*) as character_count
FROM characters c
JOIN games g ON c.game_id = g.id
WHERE c.role_style IS NOT NULL
GROUP BY g.id, g.game_name_jp, c.role_style
ORDER BY g.id, character_count DESC;

-- ===== 統計データ関連クエリ =====

-- 7. 最新の統計データ（ゲーム別トップ10勝率）
WITH latest_stats AS (
    SELECT 
        character_id,
        MAX(reference_date) as latest_date
    FROM character_stats
    GROUP BY character_id
)
SELECT 
    g.game_name_jp,
    c.japanese_name,
    c.english_name,
    cs.win_rate,
    cs.pick_rate,
    cs.ban_rate,
    cs.reference_date
FROM character_stats cs
JOIN latest_stats ls ON cs.character_id = ls.character_id 
                    AND cs.reference_date = ls.latest_date
JOIN characters c ON cs.character_id = c.id
JOIN games g ON c.game_id = g.id
WHERE cs.win_rate IS NOT NULL
ORDER BY g.id, cs.win_rate DESC
LIMIT 30;

-- 8. ゲーム横断での勝率比較（上位キャラクター）
WITH game_top_characters AS (
    SELECT 
        g.game_name_jp,
        c.japanese_name,
        c.english_name,
        AVG(cs.win_rate) as avg_win_rate,
        COUNT(cs.id) as stat_count,
        ROW_NUMBER() OVER (PARTITION BY g.id ORDER BY AVG(cs.win_rate) DESC) as rank_in_game
    FROM character_stats cs
    JOIN characters c ON cs.character_id = c.id
    JOIN games g ON c.game_id = g.id
    WHERE cs.win_rate IS NOT NULL
    GROUP BY g.id, c.id
    HAVING COUNT(cs.id) >= 5  -- 統計データが5件以上あるキャラクターのみ
)
SELECT 
    game_name_jp,
    japanese_name,
    english_name,
    ROUND(avg_win_rate, 2) as avg_win_rate,
    stat_count,
    rank_in_game
FROM game_top_characters
WHERE rank_in_game <= 5
ORDER BY game_name_jp, rank_in_game;

-- 9. 時系列での勝率変化（特定キャラクター）
SELECT 
    g.game_name_jp,
    c.japanese_name,
    cs.reference_date,
    cs.win_rate,
    cs.pick_rate,
    cs.ban_rate,
    LAG(cs.win_rate) OVER (ORDER BY cs.reference_date) as prev_win_rate,
    cs.win_rate - LAG(cs.win_rate) OVER (ORDER BY cs.reference_date) as win_rate_change
FROM character_stats cs
JOIN characters c ON cs.character_id = c.id
JOIN games g ON c.game_id = g.id
WHERE c.english_name = 'Jinx'  -- 特定キャラクター名を指定
ORDER BY cs.reference_date;

-- ===== システムログ関連クエリ =====

-- 10. スクレイピング成功率（ゲーム別・月別）
SELECT 
    g.game_name_jp,
    strftime('%Y-%m', sl.scraper_date) as month,
    COUNT(*) as total_attempts,
    SUM(sl.scraper_status) as successful_attempts,
    ROUND(CAST(SUM(sl.scraper_status) AS FLOAT) / COUNT(*) * 100, 2) as success_rate
FROM scraper_logs sl
JOIN games g ON sl.game_id = g.id
GROUP BY g.id, strftime('%Y-%m', sl.scraper_date)
ORDER BY month DESC, g.id;

-- 11. 最近のエラー状況
SELECT 
    g.game_name_jp,
    sl.scraper_date,
    sl.error_message,
    'Scraper' as log_type
FROM scraper_logs sl
JOIN games g ON sl.game_id = g.id
WHERE sl.scraper_status = 0 
  AND sl.error_message IS NOT NULL
  AND sl.scraper_date >= date('now', '-30 days')

UNION ALL

SELECT 
    g.game_name_jp,
    xpl.post_date,
    xpl.error_message,
    'X Post' as log_type
FROM x_post_logs xpl
JOIN games g ON xpl.game_id = g.id
WHERE xpl.post_status = 0 
  AND xpl.error_message IS NOT NULL
  AND xpl.post_date >= date('now', '-30 days')

ORDER BY scraper_date DESC;

-- ===== 高度な分析クエリ =====

-- 12. ゲーム別メタ分析（高ピック率・高バン率キャラクター）
SELECT 
    g.game_name_jp,
    c.japanese_name,
    AVG(cs.win_rate) as avg_win_rate,
    AVG(cs.pick_rate) as avg_pick_rate,
    AVG(cs.ban_rate) as avg_ban_rate,
    CASE 
        WHEN AVG(cs.pick_rate) > 15 AND AVG(cs.ban_rate) > 20 THEN 'Meta Dominant'
        WHEN AVG(cs.pick_rate) > 10 OR AVG(cs.ban_rate) > 15 THEN 'Meta Relevant'
        ELSE 'Niche'
    END as meta_status
FROM character_stats cs
JOIN characters c ON cs.character_id = c.id
JOIN games g ON c.game_id = g.id
WHERE cs.reference_date >= date('now', '-90 days')  -- 過去90日間
GROUP BY g.id, c.id
HAVING COUNT(cs.id) >= 3  -- 最低3回の統計データ
ORDER BY g.id, avg_pick_rate DESC;

-- 13. パッチ間での統計変化
WITH patch_stats AS (
    SELECT 
        c.id as character_id,
        g.game_name_jp,
        c.japanese_name,
        p.patch_number,
        AVG(cs.win_rate) as avg_win_rate,
        AVG(cs.pick_rate) as avg_pick_rate
    FROM character_stats cs
    JOIN characters c ON cs.character_id = c.id
    JOIN games g ON c.game_id = g.id
    JOIN patches p ON cs.patch_id = p.id
    GROUP BY c.id, p.id
)
SELECT 
    ps1.game_name_jp,
    ps1.japanese_name,
    ps1.patch_number as current_patch,
    ps1.avg_win_rate as current_win_rate,
    ps2.patch_number as previous_patch,
    ps2.avg_win_rate as previous_win_rate,
    ROUND(ps1.avg_win_rate - ps2.avg_win_rate, 2) as win_rate_change
FROM patch_stats ps1
JOIN patch_stats ps2 ON ps1.character_id = ps2.character_id
WHERE ps1.patch_number > ps2.patch_number
  AND ABS(ps1.avg_win_rate - ps2.avg_win_rate) > 2  -- 2%以上の変化
ORDER BY ABS(ps1.avg_win_rate - ps2.avg_win_rate) DESC;

-- ===== データ品質チェッククエリ =====

-- 14. データ整合性チェック
SELECT 'Orphaned character_stats' as check_type, COUNT(*) as count
FROM character_stats cs
LEFT JOIN characters c ON cs.character_id = c.id
WHERE c.id IS NULL

UNION ALL

SELECT 'Characters without stats' as check_type, COUNT(*) as count
FROM characters c
LEFT JOIN character_stats cs ON c.id = cs.character_id
WHERE cs.character_id IS NULL

UNION ALL

SELECT 'Invalid win_rate values' as check_type, COUNT(*) as count
FROM character_stats
WHERE win_rate < 0 OR win_rate > 100

UNION ALL

SELECT 'Future reference_dates' as check_type, COUNT(*) as count
FROM character_stats
WHERE reference_date > date('now');

-- 15. 最新データ更新状況
SELECT 
    g.game_name_jp,
    MAX(cs.reference_date) as latest_stats_date,
    COUNT(DISTINCT cs.character_id) as characters_with_recent_stats,
    julianday('now') - julianday(MAX(cs.reference_date)) as days_since_update
FROM character_stats cs
JOIN characters c ON cs.character_id = c.id
JOIN games g ON c.game_id = g.id
GROUP BY g.id, g.game_name_jp
ORDER BY days_since_update; 
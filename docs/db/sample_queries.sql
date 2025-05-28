-- moba_log.db サンプルクエリ集 v2
-- テーブル分離アプローチ用の活用例

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

-- 3. ゲーム別統計データ数
SELECT 
    g.game_name_jp,
    COUNT(csb.id) as base_stats_count,
    COUNT(ms.id) as mlbb_specific_count,
    COUNT(us.id) as unite_specific_count,
    COUNT(wr.id) as wildrift_specific_count
FROM games g
LEFT JOIN characters c ON g.id = c.game_id
LEFT JOIN character_stats_base csb ON c.id = csb.character_id
LEFT JOIN mlbb_stats ms ON csb.id = ms.base_stat_id
LEFT JOIN unite_stats us ON csb.id = us.base_stat_id
LEFT JOIN wildrift_stats wr ON csb.id = wr.base_stat_id
GROUP BY g.id, g.game_name_jp
ORDER BY g.id;

-- ===== ビューを使った簡単なクエリ =====

-- 4. MLBBの最新統計データ（ビュー使用）
SELECT 
    japanese_name,
    english_name,
    win_rate,
    pick_rate,
    ban_rate,
    rank_info,
    reference_date
FROM v_mlbb_stats
WHERE reference_date = (
    SELECT MAX(reference_date) FROM v_mlbb_stats
)
ORDER BY win_rate DESC
LIMIT 10;

-- 5. Uniteの総ゲーム数上位キャラクター（ビュー使用）
SELECT 
    japanese_name,
    english_name,
    win_rate,
    pick_rate,
    total_game_count,
    reference_date
FROM v_unite_stats
WHERE total_game_count IS NOT NULL
ORDER BY total_game_count DESC
LIMIT 10;

-- 6. Wild Riftのレーン別統計（ビュー使用）
SELECT 
    lane,
    COUNT(*) as character_count,
    AVG(win_rate) as avg_win_rate,
    AVG(pick_rate) as avg_pick_rate
FROM v_wildrift_stats
WHERE lane IS NOT NULL
GROUP BY lane
ORDER BY avg_win_rate DESC;

-- ===== ゲーム固有データを活用したクエリ =====

-- 7. MLBBのランク別統計
SELECT 
    ms.rank_info,
    COUNT(*) as character_count,
    AVG(csb.win_rate) as avg_win_rate,
    AVG(csb.pick_rate) as avg_pick_rate,
    AVG(csb.ban_rate) as avg_ban_rate
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
JOIN mlbb_stats ms ON csb.id = ms.base_stat_id
WHERE g.game_code = 'mlbb'
  AND ms.rank_info IS NOT NULL
GROUP BY ms.rank_info
ORDER BY avg_win_rate DESC;

-- 8. Wild Riftの特定レーンでの最強キャラクター
SELECT 
    c.japanese_name,
    c.english_name,
    csb.win_rate,
    csb.pick_rate,
    csb.ban_rate,
    wr.lane,
    csb.reference_date
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
JOIN wildrift_stats wr ON csb.id = wr.base_stat_id
WHERE g.game_code = 'wildrift'
  AND wr.lane = 'ADC'  -- 特定レーンを指定
  AND csb.reference_date >= date('now', '-30 days')
ORDER BY csb.win_rate DESC
LIMIT 5;

-- 9. Uniteの高ゲーム数キャラクターの勝率分析
SELECT 
    c.japanese_name,
    c.english_name,
    csb.win_rate,
    csb.pick_rate,
    us.total_game_count,
    CASE 
        WHEN us.total_game_count >= 1000 THEN 'High Volume'
        WHEN us.total_game_count >= 500 THEN 'Medium Volume'
        ELSE 'Low Volume'
    END as volume_category
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
JOIN unite_stats us ON csb.id = us.base_stat_id
WHERE g.game_code = 'unite'
  AND us.total_game_count IS NOT NULL
ORDER BY us.total_game_count DESC;

-- ===== ゲーム横断分析クエリ =====

-- 10. 全ゲームでの最高勝率キャラクター比較
WITH game_top_characters AS (
    SELECT 
        g.game_name_jp,
        c.japanese_name,
        c.english_name,
        csb.win_rate,
        csb.pick_rate,
        csb.reference_date,
        ROW_NUMBER() OVER (PARTITION BY g.id ORDER BY csb.win_rate DESC) as rank_in_game
    FROM character_stats_base csb
    JOIN characters c ON csb.character_id = c.id
    JOIN games g ON c.game_id = g.id
    WHERE csb.reference_date >= date('now', '-7 days')
)
SELECT 
    game_name_jp,
    japanese_name,
    english_name,
    win_rate,
    pick_rate,
    reference_date
FROM game_top_characters
WHERE rank_in_game = 1
ORDER BY win_rate DESC;

-- 11. ゲーム別メタ分析（高ピック率キャラクター）
SELECT 
    g.game_name_jp,
    COUNT(CASE WHEN csb.pick_rate > 15 THEN 1 END) as high_pick_characters,
    COUNT(CASE WHEN csb.ban_rate > 20 THEN 1 END) as high_ban_characters,
    AVG(csb.win_rate) as avg_win_rate,
    AVG(csb.pick_rate) as avg_pick_rate,
    AVG(csb.ban_rate) as avg_ban_rate
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
WHERE csb.reference_date >= date('now', '-30 days')
GROUP BY g.id, g.game_name_jp
ORDER BY avg_pick_rate DESC;

-- ===== 時系列分析クエリ =====

-- 12. 特定キャラクターの勝率推移（全ゲーム）
SELECT 
    g.game_name_jp,
    c.japanese_name,
    csb.reference_date,
    csb.win_rate,
    csb.pick_rate,
    LAG(csb.win_rate) OVER (PARTITION BY c.id ORDER BY csb.reference_date) as prev_win_rate,
    csb.win_rate - LAG(csb.win_rate) OVER (PARTITION BY c.id ORDER BY csb.reference_date) as win_rate_change
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
WHERE c.japanese_name LIKE '%ジンクス%'  -- 特定キャラクター名で検索
ORDER BY g.id, csb.reference_date;

-- 13. パッチ間での統計変化分析
WITH patch_comparison AS (
    SELECT 
        c.id as character_id,
        g.game_name_jp,
        c.japanese_name,
        p.patch_number,
        AVG(csb.win_rate) as avg_win_rate,
        AVG(csb.pick_rate) as avg_pick_rate,
        COUNT(*) as data_points
    FROM character_stats_base csb
    JOIN characters c ON csb.character_id = c.id
    JOIN games g ON c.game_id = g.id
    JOIN patches p ON csb.patch_id = p.id
    GROUP BY c.id, p.id
    HAVING COUNT(*) >= 3  -- 最低3回のデータポイント
)
SELECT 
    pc1.game_name_jp,
    pc1.japanese_name,
    pc1.patch_number as current_patch,
    pc1.avg_win_rate as current_win_rate,
    pc2.patch_number as previous_patch,
    pc2.avg_win_rate as previous_win_rate,
    ROUND(pc1.avg_win_rate - pc2.avg_win_rate, 2) as win_rate_change
FROM patch_comparison pc1
JOIN patch_comparison pc2 ON pc1.character_id = pc2.character_id
WHERE pc1.patch_number > pc2.patch_number
  AND ABS(pc1.avg_win_rate - pc2.avg_win_rate) > 3  -- 3%以上の変化
ORDER BY ABS(pc1.avg_win_rate - pc2.avg_win_rate) DESC;

-- ===== システム監視クエリ =====

-- 14. スクレイピング成功率（ゲーム別・月別）
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

-- 15. 最新データ更新状況
SELECT 
    g.game_name_jp,
    MAX(csb.reference_date) as latest_stats_date,
    COUNT(DISTINCT csb.character_id) as characters_with_recent_stats,
    julianday('now') - julianday(MAX(csb.reference_date)) as days_since_update
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
GROUP BY g.id, g.game_name_jp
ORDER BY days_since_update;

-- ===== データ品質チェッククエリ =====

-- 16. データ整合性チェック
SELECT 'Orphaned character_stats_base' as check_type, COUNT(*) as count
FROM character_stats_base csb
LEFT JOIN characters c ON csb.character_id = c.id
WHERE c.id IS NULL

UNION ALL

SELECT 'Characters without stats' as check_type, COUNT(*) as count
FROM characters c
LEFT JOIN character_stats_base csb ON c.id = csb.character_id
WHERE csb.character_id IS NULL

UNION ALL

SELECT 'MLBB stats without base' as check_type, COUNT(*) as count
FROM mlbb_stats ms
LEFT JOIN character_stats_base csb ON ms.base_stat_id = csb.id
WHERE csb.id IS NULL

UNION ALL

SELECT 'Unite stats without base' as check_type, COUNT(*) as count
FROM unite_stats us
LEFT JOIN character_stats_base csb ON us.base_stat_id = csb.id
WHERE csb.id IS NULL

UNION ALL

SELECT 'Wild Rift stats without base' as check_type, COUNT(*) as count
FROM wildrift_stats wr
LEFT JOIN character_stats_base csb ON wr.base_stat_id = csb.id
WHERE csb.id IS NULL;

-- 17. ゲーム固有データのカバレッジ確認
SELECT 
    g.game_name_jp,
    COUNT(csb.id) as total_base_stats,
    COUNT(ms.id) as mlbb_specific_stats,
    COUNT(us.id) as unite_specific_stats,
    COUNT(wr.id) as wildrift_specific_stats,
    CASE g.game_code
        WHEN 'mlbb' THEN ROUND(CAST(COUNT(ms.id) AS FLOAT) / COUNT(csb.id) * 100, 2)
        WHEN 'unite' THEN ROUND(CAST(COUNT(us.id) AS FLOAT) / COUNT(csb.id) * 100, 2)
        WHEN 'wildrift' THEN ROUND(CAST(COUNT(wr.id) AS FLOAT) / COUNT(csb.id) * 100, 2)
    END as coverage_percentage
FROM character_stats_base csb
JOIN characters c ON csb.character_id = c.id
JOIN games g ON c.game_id = g.id
LEFT JOIN mlbb_stats ms ON csb.id = ms.base_stat_id
LEFT JOIN unite_stats us ON csb.id = us.base_stat_id
LEFT JOIN wildrift_stats wr ON csb.id = wr.base_stat_id
GROUP BY g.id, g.game_name_jp, g.game_code
ORDER BY g.id; 
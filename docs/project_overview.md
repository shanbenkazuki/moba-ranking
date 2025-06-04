launchctl kickstart -k gui/$(id -u)/com.moba_ranking.scrape_mlbb_stats

node mlbb_tier_x_poster.js

launchctl kickstart -k gui/$(id -u)/com.moba_ranking.scrape_unite_stats
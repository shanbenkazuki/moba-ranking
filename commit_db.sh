#!/bin/bash
# リポジトリのディレクトリへ移動
cd /Users/yamamotokazuki/develop/moba-ranking/ || exit 1

# 前日の日付を取得（macOSの場合）
yesterday=$(date -v-1d +"%Y-%m-%d")

# 各DBファイルをgit管理下に追加
git add mlbb.db unite.db wildrift.db

# コミット（メッセージに前日の日付を使用）
git commit -m "~$yesterday"

# GitHubへプッシュ（リモート名やブランチ名は環境に合わせて調整）
git push origin main

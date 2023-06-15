import sqlite3

from datetime import datetime
from moba_insert_data import get_mlbb_hero_data

# SQLiteデータベースに接続
conn = sqlite3.connect('moba_database.sqlite3')
cursor = conn.cursor()

# mlbbのデータを保存するテーブルを作成
cursor.execute('''
  CREATE TABLE IF NOT EXISTS mlbb_hero_info (
    name TEXT UNIQUE,
    name_en TEXT UNIQUE,
    role TEXT,
    sub_role TEXT,
    suggested_lane TEXT,
    article_url TEXT,
    image_url TEXT,
    created_at TEXT,
    updated_at TEXT
  )
''')

heroes = get_mlbb_hero_data()

# heroesのデータを追加
for hero, info in heroes.items():
    name = info['name_jp']
    name_en = hero
    role = info['role']
    sub_role = info['sub_role']
    suggested_lane = info['suggested_lane']
    article_url = info['article_url']
    image_url = info['image_url']
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # データを挿入
    try:
        # データを挿入
        cursor.execute('''
            INSERT INTO mlbb_hero_info (name, name_en, role, sub_role, suggested_lane, article_url, image_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, name_en, role, sub_role, suggested_lane, article_url, image_url, created_at, updated_at))
    except sqlite3.IntegrityError:
        print(f"Duplicated entry: {name}")


# 変更を保存
conn.commit()

# データベース接続を閉じる
conn.close()

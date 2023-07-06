import sqlite3

from datetime import datetime
from moba_insert_data import get_mlbb_equipments

# SQLiteデータベースに接続
conn = sqlite3.connect('moba_database.sqlite3')
cursor = conn.cursor()

# mlbbのデータを保存するテーブルを作成
cursor.execute('''
  CREATE TABLE IF NOT EXISTS mlbb_equipments (
    name_ja TEXT UNIQUE,
    name_en TEXT UNIQUE,
    type TEXT,
    image_url TEXT,
    created_at TEXT,
    updated_at TEXT
  )
''')

equipments = get_mlbb_equipments()

# heroesのデータを追加
for equipment, info in equipments.items():
    name_ja = info['name']
    name_en = equipment
    type = info['type']
    image_url = info['image_url']
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # データを挿入
    try:
        # データを挿入
        cursor.execute('''
            INSERT INTO mlbb_equipments (name_ja, name_en, type, image_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name_ja, name_en, type, image_url, created_at, updated_at))
    except sqlite3.IntegrityError:
        print(f"Duplicated entry: {name_ja}")


# 変更を保存
conn.commit()

# データベース接続を閉じる
conn.close()

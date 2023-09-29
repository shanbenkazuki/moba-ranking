import sqlite3
from datetime import datetime
from moba_insert_data import get_mlbb_hero_data

conn = sqlite3.connect('moba_database.sqlite3')
cursor = conn.cursor()

cursor.execute('''
  CREATE TABLE IF NOT EXISTS mlbb_hero_info (
    name_en TEXT UNIQUE,
    name_jp TEXT,
    role TEXT,
    translate_term TEXT,
    article_url TEXT,
    image_url TEXT,
    created_at TEXT,
    updated_at TEXT
  )
''')

heroes = get_mlbb_hero_data()

for hero, info in heroes.items():
    name_en = hero
    name_jp = info['name_jp']
    role = info['role']
    translate_term = info.get('translate_term', '')
    article_url = info['article_url']
    image_url = info['image_url']
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute('''
            INSERT INTO mlbb_hero_info (name_en, name_jp, role, translate_term, article_url, image_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name_en, name_jp, role, translate_term, article_url, image_url, created_at, updated_at))
    except sqlite3.IntegrityError:
        print(f"Duplicated entry: {name_jp}")

conn.commit()
conn.close()

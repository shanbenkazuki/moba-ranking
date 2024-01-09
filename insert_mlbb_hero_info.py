import sqlite3
import json

from datetime import datetime

conn = sqlite3.connect('moba_database.sqlite3')
cursor = conn.cursor()

cursor.execute('''
  CREATE TABLE IF NOT EXISTS mlbb_hero_info (
    name_en TEXT UNIQUE,
    name_jp TEXT,
    role TEXT,
    article_url TEXT,
    image_url TEXT,
    created_at TEXT,
    updated_at TEXT
  )
''')

hero_dict = {}

with open('mlbb_hero.json', 'r') as f:
  mlbb_hero = json.load(f)

for hero in mlbb_hero:
  name_en = hero['name_en']
  name_jp = hero['name_jp']
  role = hero['role']
  article_url = hero['article_url']
  image_url = hero['image_url']
  created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  try:
    cursor.execute('''
      INSERT INTO mlbb_hero_info (name_en, name_jp, role, article_url, image_url, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name_en, name_jp, role, article_url, image_url, created_at, updated_at))
  except sqlite3.IntegrityError:
    print(f"Duplicated entry: {name_jp}")

conn.commit()
conn.close()

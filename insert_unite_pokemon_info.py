import sqlite3
import json

from datetime import datetime
from moba_insert_data import get_unite_pokemon_data


# SQLiteデータベースに接続
conn = sqlite3.connect('moba_database.sqlite3')
cursor = conn.cursor()

# mlbbのデータを保存するテーブルを作成
cursor.execute('''
  CREATE TABLE IF NOT EXISTS unite_pokemon_info (
    name TEXT UNIQUE,
    name_en TEXT UNIQUE,
    style TEXT,
    article_url TEXT,
    image_url TEXT,
    created_at TEXT,
    updated_at TEXT
  )
''')

pokemons = get_unite_pokemon_data()

print(pokemons)

with open('unite_pokemon.json', 'r') as f:
  pokemons = json.load(f)

# データを追加
for pokemon, data in pokemons.items():
  name_en = pokemon
  name = data['name']
  style = data['style']
  article_url = data['article_url']
  image_url = data['image_url']
  created_at = datetime.now().strftime('%Y-%m-%d')
  updated_at = datetime.now().strftime('%Y-%m-%d')

  # SQLクエリを実行してデータを追加
  try:
    cursor.execute(
      '''
      INSERT INTO unite_pokemon_info (name, name_en, style, article_url, image_url, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      ''',
      (name, name_en, style, article_url, image_url, created_at, updated_at)
    )
  except sqlite3.IntegrityError:
    print(f"Duplicate entry: {name_en}")

# 変更を保存
conn.commit()

# データベース接続を閉じる
conn.close()

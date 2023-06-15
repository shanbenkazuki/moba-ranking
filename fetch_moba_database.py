import sqlite3

DATABASE_PATH = 'moba_database.sqlite3'

def get_db_connection():
  return sqlite3.connect(DATABASE_PATH)

def create_table_if_not_exists(cursor, table_name):
  create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
      name TEXT,
      winrate REAL,
      pickrate REAL,
      score REAL,
      rank TEXT,
      reference_date TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
  '''
  cursor.execute(create_table_query)

def save_data_to_database(table, data, fetch_reference_date):
  with get_db_connection() as conn:
    cursor = conn.cursor()
    create_table_if_not_exists(cursor, table)

    for name, stats in data.items():
      if is_duplicate_entry(cursor, table, fetch_reference_date, name):
        continue
      save_data_to_table(cursor, table, fetch_reference_date, name, stats)

    conn.commit()

def is_duplicate_entry(cursor, table, reference_date, name):
  query = f'''
    SELECT COUNT(*) FROM {table} WHERE reference_date = ? AND name = ?
  '''
  cursor.execute(query, (reference_date, name))
  count = cursor.fetchone()[0]
  return count > 0

def save_data_to_table(cursor, table, reference_date, name, stats):
  insert_query = f'''
    INSERT INTO {table} (name, winrate, pickrate, score, rank, reference_date)
    VALUES (?, ?, ?, ?, ?, ?)
  '''
  cursor.execute(insert_query, (name, stats['winrate'], stats['pickrate'], stats['score'], stats['rank'], reference_date))

def get_pokemon_data():
  conn = get_db_connection()
  cursor = conn.cursor()
  query = "SELECT name, name_en, style, article_url, image_url FROM unite_pokemon_info"
  cursor.execute(query)
  rows = cursor.fetchall()

  processed_data = {}
  for row in rows:
    name, name_en, style, article_url, image_url = row
    processed_data[name_en] = {
      "name_jp": name,
      "style": style,
      "article_url": article_url,
      "image_url": image_url
    }
  cursor.close()
  conn.close()
  return processed_data


def get_hero_data():
  conn = get_db_connection()
  cursor = conn.cursor()
  query = "SELECT * FROM mlbb_hero_info"
  cursor.execute(query)
  rows = cursor.fetchall()

  results = {}
  for row in rows:
    name, name_en, role, sub_role, suggested_lane, article_url, image_url, created_at, updated_at = row
    result = {
      "name_jp": name,
      "name_en": name_en,
      "role": role,
      "sub_role": sub_role,
      "suggested_lane": suggested_lane,
      "article_url": article_url,
      "image_url": image_url,
      "created_at": created_at,
      "updated_at": updated_at
    }
    results[name_en] = result

  conn.close()
  return results

def save_to_hero_meta_data(hero_meta_data, fetch_reference_date):
  # SQLiteデータベースに接続
  conn = sqlite3.connect('moba_database.sqlite3')
  c = conn.cursor()

  # テーブルが存在しない場合にのみ作成する
  create_table_query = '''
  CREATE TABLE IF NOT EXISTS hero_meta_data (
    name TEXT,
    win_rate REAL,
    pick_rate REAL,
    ban_rate REAL,
    score REAL,
    rank TEXT,
    reference_date DATE,
    PRIMARY KEY (name, reference_date)
  );
  '''

  c.execute(create_table_query)

  # データを辞書からテーブルに挿入するためのSQL文を定義
  insert_query = '''
  INSERT INTO hero_meta_data (name, win_rate, pick_rate, ban_rate, score, rank, reference_date)
  VALUES (?, ?, ?, ?, ?, ?, ?)
  '''

  reference_date = fetch_reference_date

  for hero, data_dict in hero_meta_data.items():
    try:
      c.execute(insert_query, (hero, data_dict['win_rate'], data_dict['pick_rate'], data_dict['ban_rate'],
                              data_dict['Score'], data_dict['Rank'], reference_date))
    except sqlite3.IntegrityError:
      error_message = f"Duplicate entry found for {hero} on {reference_date}"
      print(error_message)

  # 変更を保存
  conn.commit()

  # 接続を閉じる
  conn.close()

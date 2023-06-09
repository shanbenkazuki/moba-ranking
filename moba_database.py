import sqlite3

# database設定を一か所で管理します
DATABASE_PATH = 'moba_database.sqlite3'

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def create_table_if_not_exists(cursor, table_name):
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            name TEXT,
            winrate REAL,
            pickrate REAL,
            score REAL,
            rank TEXT,
            reference_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def save_data_to_database(table, data, fetch_reference_date):
    with get_db_connection() as conn:  # 自動的に閉じるためのwith文
        cursor = conn.cursor()
        create_table_if_not_exists(cursor, table)  # tableが存在しなければ作成

        for name, stats in data.items():
            if is_duplicate_entry(cursor, table, fetch_reference_date, name):
                continue

            save_data_to_table(cursor, table, fetch_reference_date, name, stats)

        conn.commit()

def is_duplicate_entry(cursor, table, reference_date, name):
    cursor.execute(f'''
        SELECT COUNT(*) FROM {table} WHERE reference_date = ? AND name = ?
    ''', (reference_date, name))
    count = cursor.fetchone()[0]
    return count > 0  # 重複している場合はTrueを返す

def save_data_to_table(cursor, table, reference_date, name, stats):
    cursor.execute(f'''
        INSERT INTO {table} (name, winrate, pickrate, score, rank, reference_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, stats['winrate'], stats['pickrate'], stats['score'], stats['rank'], reference_date))

import sqlite3
import os

# ==== Target Databases ====
DB_PATHS = [
    "data/moba_log.db"
]

OUTPUT_DIR = os.path.join(os.getcwd(), "docs")
README_PATH = os.path.join(os.getcwd(), "README.md")

# ==== Type Mapping ====
type_map = {
    "integer": "int",
    "int": "int",
    "text": "string",
    "varchar": "string",
    "char": "string",
    "real": "float",
    "float": "float",
    "double": "float",
    "numeric": "float",
    "decimal": "float",
    "blob": "binary",
    "boolean": "bool",
    "datetime": "date",
    "date": "date"
}


def map_column_type(sqlite_type):
    if not sqlite_type:
        return "string"
    base_type = sqlite_type.strip().lower().split("(")[0]
    return type_map.get(base_type, "string")


def get_unique_columns(cursor, table_name):
    """主キー以外で、単一カラムのUNIQUE制約が設定されているカラム名を返す"""
    unique_columns = set()
    
    # 主キーのカラムを取得
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    pk_columns = {col[1] for col in cursor.fetchall() if col[5] > 0}

    # インデックスの調査
    cursor.execute(f"PRAGMA index_list('{table_name}')")
    indexes = cursor.fetchall()
    for index in indexes:
        index_name = index[1]
        is_unique = index[2]
        if is_unique:
            cursor.execute(f"PRAGMA index_info('{index_name}')")
            indexed_columns = cursor.fetchall()
            # インデックスが単一カラムの場合のみ対象とする
            if len(indexed_columns) == 1:
                col_name = indexed_columns[0][2]
                if col_name not in pk_columns:  # 主キーは除外
                    unique_columns.add(col_name)

    return unique_columns


def is_unique_column(cursor, table, column):
    """指定したカラムが単一カラムのUNIQUE制約を持つかをチェックする"""
    cursor.execute(f"PRAGMA index_list('{table}')")
    indexes = cursor.fetchall()
    for index in indexes:
        if index[2]:  # UNIQUEの場合
            cursor.execute(f"PRAGMA index_info('{index[1]}')")
            columns = cursor.fetchall()
            # インデックスが単一カラムの場合のみチェックする
            if len(columns) == 1 and columns[0][2] == column:
                return True
    return False


def generate_mermaid_er(db_path, output_dir, custom_db_name=None):
    db_filename = os.path.basename(db_path)
    default_db_name = os.path.splitext(db_filename)[0]
    # custom_db_nameが指定されていなければdefault_db_nameを使う
    db_name = custom_db_name if custom_db_name else default_db_name
    output_file = f"er_{db_name}.md"

    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # テーブル定義の取得
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    table_defs = {row[0]: row[1] for row in cursor.fetchall() if not row[0].startswith("sqlite_")}
    tables = list(table_defs.keys())

    mermaid_code = ["erDiagram"]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        unique_columns = get_unique_columns(cursor, table)
        table_sql = table_defs[table].upper()

        mermaid_code.append(f"    {table} {{")
        for col in columns:
            col_name = col[1]
            col_type = map_column_type(col[2])
            constraints = []

            if col[5] > 0:
                constraints.append("PK")
                if "AUTOINCREMENT" in table_sql and col_type == "int":
                    constraints.append("AUTOINCREMENT")
            if col[3] == 1:
                constraints.append("NOT NULL")
            if col_name in unique_columns:
                constraints.append("UNIQUE")
            if col[4] is not None:
                default_val = str(col[4]).strip("'\"").replace(" ", "_")
                constraints.append(f"DEFAULT={default_val}")

            if constraints:
                constraint_str = " ".join(constraints)
                mermaid_code.append(f"        {col_type} {col_name} \"{constraint_str}\"")
            else:
                mermaid_code.append(f"        {col_type} {col_name}")
        mermaid_code.append("    }")

    # 外部キーリレーションシップの追加
    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        for fk in fks:
            ref_table = fk[2]
            from_col = fk[3]
            to_col = fk[4]
            if ref_table in tables:
                relation_label = f"{table}.{from_col} → {ref_table}.{to_col}"
                # 一対一判定（外部キー列が単一カラムのUNIQUE制約の場合）
                is_unique_fk = is_unique_column(cursor, table, from_col)
                connector = "||--||" if is_unique_fk else "||--o{"
                mermaid_code.append(f"    {ref_table} {connector} {table} : \"{relation_label}\"")

    output_path = os.path.join(output_dir, output_file)
    with open(output_path, "w") as f:
        f.write("```mermaid\n" + "\n".join(mermaid_code) + "\n```")

    conn.close()
    print(f"✅ {db_name} のER図を {output_path} に出力しました！")
    return output_file, db_name


def update_readme(readme_path, er_files_info):
    er_section = "## データベース構成（ER図）\n\n" + "\n".join(
        [f"- [{name}](docs/{file})" for file, name in er_files_info]
    ) + "\n"

    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
    else:
        content = ""

    if "## データベース構成（ER図）" in content:
        before, _ = content.split("## データベース構成（ER図）", 1)
        new_content = before.strip() + "\n\n" + er_section
    else:
        new_content = content.strip() + "\n\n" + er_section

    with open(readme_path, "w") as f:
        f.write(new_content)

    print(f"📘 README.md を更新しました！")


# ===== Main Execution =====
if __name__ == "__main__":
    name_counts = {}  # db名の出現回数管理用
    er_files_info = []
    for db_path in DB_PATHS:
        db_filename = os.path.basename(db_path)
        default_db_name = os.path.splitext(db_filename)[0]
        # 既に出現していれば連番を付与
        if default_db_name in name_counts:
            name_counts[default_db_name] += 1
            custom_db_name = f"{default_db_name}{name_counts[default_db_name]}"
        else:
            name_counts[default_db_name] = 1
            custom_db_name = default_db_name

        er_file, used_db_name = generate_mermaid_er(db_path, OUTPUT_DIR, custom_db_name=custom_db_name)
        er_files_info.append((er_file, used_db_name))
    update_readme(README_PATH, er_files_info)

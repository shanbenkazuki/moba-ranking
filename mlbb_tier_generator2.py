import sqlite3
import csv
import pandas as pd
from scipy.stats import zscore

# SQLiteからデータ抽出してCSV出力
db_path = '/Users/yamamotokazuki/develop/moba-ranking/mlbb.db'
output_csv = 'hero_stats_latest.csv'

# SQLiteに接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 最新のreference_dateを取得
cursor.execute("SELECT MAX(reference_date) FROM hero_stats")
latest_date = cursor.fetchone()[0]

# 最新のreference_dateの行を抽出
cursor.execute("SELECT * FROM hero_stats WHERE reference_date = ?", (latest_date,))
rows = cursor.fetchall()

# カラム名を取得
column_names = [description[0] for description in cursor.description]

# CSVファイルへ書き込み
with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(column_names)  # ヘッダーを書き込み
    writer.writerows(rows)         # データを書き込み

# 接続をクローズ
conn.close()
print(f"CSVファイル '{output_csv}' が作成されました。最新の reference_date: {latest_date} のデータ件数: {len(rows)}")

# CSVファイルをPandas DataFrameとして読み込み
df = pd.read_csv(output_csv)

# 各指標（勝率、選択率、BAN率）のZスコアを計算
df['win_rate_z'] = zscore(df['win_rate'])
df['pick_rate_z'] = zscore(df['pick_rate'])
df['ban_rate_z'] = zscore(df['ban_rate'])

# 各指標の重みを設定（例：勝率0.5、BAN率0.3、選択率0.2）
w_win = 0.5
w_ban = 0.3
w_pick = 0.2

# 合成強さスコアの算出（各指標のZスコアに重みを乗せて総和）
df['strength_score'] = (w_win * df['win_rate_z'] +
                        w_ban * df['ban_rate_z'] +
                        w_pick * df['pick_rate_z'])

# 強さスコアのZスコアに基づいてS,A,B,C,Dのグレードを割り当てる関数
def assign_grade(z):
    if z > 1.0:
        return 'S'
    elif z > 0.5:
        return 'A'
    elif z >= -0.5:
        return 'B'
    elif z >= -1.0:
        return 'C'
    else:
        return 'D'

# 各キャラにグレードを割り当てる
df['grade'] = df['strength_score'].apply(assign_grade)

# 強さスコアが高い順にソートし、上位10キャラを表示
df_sorted = df.sort_values(by='strength_score', ascending=False)
print("Top 10 heroes by composite strength score (with grades):")
print(df_sorted[['hero_name', 'strength_score', 'grade']].head(10))

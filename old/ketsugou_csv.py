import pandas as pd
import glob

# CSVファイルがあるディレクトリのパス
path = '/Users/yamamotokazuki/Documents/private/programming/RUNTEQ生の技術資料' # ここにディレクトリのパスを設定
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
  df = pd.read_csv(filename, index_col=None, header=0)
  li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

# 結合されたデータフレームをCSVとして出力
# frame.to_csv('portfolio_tech.csv', index=False)

df = pd.read_csv('portfolio_tech.csv')

# データのないカラムを削除
df.dropna(axis=1, how='all', inplace=True)

# 変更を保存
df.to_csv('portfolio_tech.csv', index=False)
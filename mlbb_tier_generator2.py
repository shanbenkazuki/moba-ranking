import pandas as pd
from scipy.stats import zscore
from io import StringIO

# CSVデータを文字列として定義
csv_data = """hero_name,win_rate,pick_rate,ban_rate,reference_date,rank,patch_number
Lolita,58.14,0.16,0.39,2025-03-06,Mythic,1.9.47
Julian,56.4,1.68,48.87,2025-03-06,Mythic,1.9.47
Argus,55.4,0.7,4.84,2025-03-06,Mythic,1.9.47
Carmilla,55.29,0.34,0.3,2025-03-06,Mythic,1.9.47
Floryn,55.28,0.43,2.57,2025-03-06,Mythic,1.9.47
Melissa,55.06,1.31,5.15,2025-03-06,Mythic,1.9.47
Popol and Kupa,54.97,0.61,0.9,2025-03-06,Mythic,1.9.47
Belerick,54.63,1.23,9.88,2025-03-06,Mythic,1.9.47
Hylos,54.16,0.83,3.84,2025-03-06,Mythic,1.9.47
Badang,54.11,1.54,26.82,2025-03-06,Mythic,1.9.47
Khaleed,53.98,0.46,2.23,2025-03-06,Mythic,1.9.47
Miya,53.93,3.94,16.85,2025-03-06,Mythic,1.9.47
Aulus,53.82,0.34,0.22,2025-03-06,Mythic,1.9.47
Yi Sun-shin,53.62,0.42,0.92,2025-03-06,Mythic,1.9.47
Gatotkaca,53.46,2.52,11.25,2025-03-06,Mythic,1.9.47
Wanwan,53.42,0.37,1.42,2025-03-06,Mythic,1.9.47
Masha,53.28,0.07,0.06,2025-03-06,Mythic,1.9.47
Sun,53.15,1.75,52.18,2025-03-06,Mythic,1.9.47
Gloo,52.84,0.09,0.26,2025-03-06,Mythic,1.9.47
Cecilion,52.66,2.52,24.24,2025-03-06,Mythic,1.9.47
Edith,52.59,0.37,0.14,2025-03-06,Mythic,1.9.47
Zhask,52.55,0.67,1.52,2025-03-06,Mythic,1.9.47
Terizla,52.25,0.53,0.53,2025-03-06,Mythic,1.9.47
Baxia,52.17,0.09,0.07,2025-03-06,Mythic,1.9.47
Bane,52.02,0.5,0.19,2025-03-06,Mythic,1.9.47
Atlas,51.86,0.39,0.61,2025-03-06,Mythic,1.9.47
Hilda,51.46,0.82,10.54,2025-03-06,Mythic,1.9.47
Minsitthar,51.38,0.48,1.25,2025-03-06,Mythic,1.9.47
Barats,51.26,0.26,0.55,2025-03-06,Mythic,1.9.47
Uranus,51.26,0.56,0.61,2025-03-06,Mythic,1.9.47
Khufra,51.18,0.17,0.45,2025-03-06,Mythic,1.9.47
Irithel,51.16,0.82,1.19,2025-03-06,Mythic,1.9.47
Alpha,51.16,2.96,4.12,2025-03-06,Mythic,1.9.47
Silvanna,51.13,0.79,0.26,2025-03-06,Mythic,1.9.47
Hanabi,51.06,2.62,2.04,2025-03-06,Mythic,1.9.47
Suyou,50.94,0.71,11.67,2025-03-06,Mythic,1.9.47
Gord,50.9,0.48,0.33,2025-03-06,Mythic,1.9.47
Ruby,50.9,0.42,0.26,2025-03-06,Mythic,1.9.47
Zhuxin,50.88,0.57,67.64,2025-03-06,Mythic,1.9.47
Helcurt,50.83,0.68,5.95,2025-03-06,Mythic,1.9.47
Rafaela,50.78,0.23,0.2,2025-03-06,Mythic,1.9.47
Alucard,50.71,0.76,0.53,2025-03-06,Mythic,1.9.47
Benedetta,50.69,0.58,0.86,2025-03-06,Mythic,1.9.47
Lukas,50.68,0.71,22,2025-03-06,Mythic,1.9.47
Harley,50.66,1.31,16.77,2025-03-06,Mythic,1.9.47
Vale,50.57,0.84,0.25,2025-03-06,Mythic,1.9.47
Chang'e,50.52,1.6,0.69,2025-03-06,Mythic,1.9.47
Minotaur,50.5,0.15,0.16,2025-03-06,Mythic,1.9.47
Vexana,50.5,1.81,1.14,2025-03-06,Mythic,1.9.47
Lylia,50.49,0.4,0.14,2025-03-06,Mythic,1.9.47
Aurora,50.48,0.76,0.64,2025-03-06,Mythic,1.9.47
Saber,50.45,1.17,58.99,2025-03-06,Mythic,1.9.47
Cyclops,50.34,0.76,0.21,2025-03-06,Mythic,1.9.47
Yin,50.25,1.31,15.39,2025-03-06,Mythic,1.9.47
Ixia,50.24,0.47,0.45,2025-03-06,Mythic,1.9.47
Hanzo,50.17,0.49,90.89,2025-03-06,Mythic,1.9.47
Zilong,50.05,1.76,1.19,2025-03-06,Mythic,1.9.47
Cici,50.02,1.14,4.09,2025-03-06,Mythic,1.9.47
Eudora,50.01,1.57,8.16,2025-03-06,Mythic,1.9.47
Alice,49.93,0.14,0.27,2025-03-06,Mythic,1.9.47
Kagura,49.76,0.55,0.41,2025-03-06,Mythic,1.9.47
Natalia,49.66,0.54,4.25,2025-03-06,Mythic,1.9.47
Layla,49.65,3.3,16.32,2025-03-06,Mythic,1.9.47
Angela,49.61,1.51,4.01,2025-03-06,Mythic,1.9.47
Akai,49.56,0.33,0.33,2025-03-06,Mythic,1.9.47
Odette,49.49,0.73,0.2,2025-03-06,Mythic,1.9.47
Luo Yi,49.48,0.32,0.22,2025-03-06,Mythic,1.9.47
Valir,49.48,0.75,0.69,2025-03-06,Mythic,1.9.47
Xavier,49.37,0.82,0.71,2025-03-06,Mythic,1.9.47
Hayabusa,49.3,0.86,77.66,2025-03-06,Mythic,1.9.47
Guinevere,49.28,0.49,0.26,2025-03-06,Mythic,1.9.47
Aamon,49.17,0.6,1.07,2025-03-06,Mythic,1.9.47
X.Borg,49.17,0.41,0.3,2025-03-06,Mythic,1.9.47
Johnson,49.11,1.16,2.77,2025-03-06,Mythic,1.9.47
Aldous,49.04,0.56,0.43,2025-03-06,Mythic,1.9.47
Estes,48.96,0.72,16.51,2025-03-06,Mythic,1.9.47
Kadita,48.81,0.24,0.13,2025-03-06,Mythic,1.9.47
Phoveus,48.78,0.35,0.94,2025-03-06,Mythic,1.9.47
Thamuz,48.77,0.49,0.21,2025-03-06,Mythic,1.9.47
Lunox,48.76,0.25,0.16,2025-03-06,Mythic,1.9.47
Diggie,48.55,0.12,1.79,2025-03-06,Mythic,1.9.47
Yve,48.55,0.04,0.24,2025-03-06,Mythic,1.9.47
Roger,48.47,0.45,0.17,2025-03-06,Mythic,1.9.47
Kaja,48.34,0.04,0.06,2025-03-06,Mythic,1.9.47
Pharsa,48.22,0.64,0.22,2025-03-06,Mythic,1.9.47
Nana,48.22,2.34,5.75,2025-03-06,Mythic,1.9.47
Selena,48.19,1.62,15.34,2025-03-06,Mythic,1.9.47
Jawhead,48.19,0.61,0.39,2025-03-06,Mythic,1.9.47
Ling,48.16,0.64,4.37,2025-03-06,Mythic,1.9.47
Harith,48.16,0.66,6.09,2025-03-06,Mythic,1.9.47
Moskov,48.09,0.94,0.4,2025-03-06,Mythic,1.9.47
Freya,48.08,0.31,0.52,2025-03-06,Mythic,1.9.47
Tigreal,47.82,1.96,8.42,2025-03-06,Mythic,1.9.47
Leomord,47.73,0.11,0.07,2025-03-06,Mythic,1.9.47
Beatrix,47.72,0.45,0.2,2025-03-06,Mythic,1.9.47
Brody,47.69,0.29,0.16,2025-03-06,Mythic,1.9.47
Yu Zhong,47.61,0.52,0.5,2025-03-06,Mythic,1.9.47
Natan,47.41,0.17,0.07,2025-03-06,Mythic,1.9.47
Bruno,47.38,0.46,0.21,2025-03-06,Mythic,1.9.47
Novaria,47.25,0.32,0.29,2025-03-06,Mythic,1.9.47
Fredrinn,47.17,0.12,0.08,2025-03-06,Mythic,1.9.47
Lapu-Lapu,47.14,0.14,0.05,2025-03-06,Mythic,1.9.47
Karrie,46.96,1,0.94,2025-03-06,Mythic,1.9.47
Chip,46.93,0.05,0.91,2025-03-06,Mythic,1.9.47
Dyrroth,46.92,1.35,0.65,2025-03-06,Mythic,1.9.47
Clint,46.86,0.77,0.26,2025-03-06,Mythic,1.9.47
Franco,46.86,2.31,7.9,2025-03-06,Mythic,1.9.47
Faramis,46.66,0.04,0.09,2025-03-06,Mythic,1.9.47
Karina,46.5,1.02,6.45,2025-03-06,Mythic,1.9.47
Mathilda,46.5,0.17,0.92,2025-03-06,Mythic,1.9.47
Chou,46.39,1.6,2.22,2025-03-06,Mythic,1.9.47
Martis,46.3,0.56,0.56,2025-03-06,Mythic,1.9.47
Nolan,46.06,0.31,0.71,2025-03-06,Mythic,1.9.47
Arlott,45.8,0.18,0.17,2025-03-06,Mythic,1.9.47
Gusion,45.72,0.84,0.71,2025-03-06,Mythic,1.9.47
Granger,45.55,2.16,69.95,2025-03-06,Mythic,1.9.47
Claude,45.22,0.6,0.33,2025-03-06,Mythic,1.9.47
Grock,45.08,0.06,0.05,2025-03-06,Mythic,1.9.47
Esmeralda,44.98,0.52,0.53,2025-03-06,Mythic,1.9.47
Joy,44.96,0.37,31.44,2025-03-06,Mythic,1.9.47
Lancelot,44.28,0.98,0.94,2025-03-06,Mythic,1.9.47
Kimmy,44.21,0.21,0.07,2025-03-06,Mythic,1.9.47
Paquito,44.04,0.21,0.1,2025-03-06,Mythic,1.9.47
Balmond,43.92,0.5,0.17,2025-03-06,Mythic,1.9.47
Fanny,42.77,0.92,54.42,2025-03-06,Mythic,1.9.47
Lesley,42.42,1.09,0.48,2025-03-06,Mythic,1.9.47
Valentina,41.47,0.09,0.09,2025-03-06,Mythic,1.9.47
"""

# CSVデータを DataFrame として読み込み
df = pd.read_csv(StringIO(csv_data))

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

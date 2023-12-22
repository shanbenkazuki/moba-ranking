import streamlit as st
import requests
import json

from PIL import Image
from io import BytesIO

# Streamlit アプリ
st.title('キャラクター評価')

st.header('モバイル・レジェンド')

# mlbb_ranking.jsonを読み込む
with open('mlbb_ranking.json', 'r') as f:
  hero_list = json.load(f)

# hero_listを使って各ランクごとに画像を表示
for rank in ["S+", "S", "A+", "A", "B", "C"]:
  images = [img for img in hero_list if img['rank'] == rank]

  # 画像がある場合のみ処理
  if images:
    # ランク表示用の列と8個の画像表示用の列を作成
    st.write(rank)

    # 画像表示用の列を設定
    for i in range(0, len(images), 8):
      cols = st.columns(8)
      # 各画像を表示
      for j, img in enumerate(images[i:i+8]):
        # 画像の読み込み
        response = requests.get(img['url'])
        # もしImage.open()でエラーが出たら、そのurlを表示
        try:
          image = Image.open(BytesIO(response.content))
        except:
          st.write(img['url'])
          continue
        # 列に画像を配置
        cols[j].image(image, caption=img["url"].split('/')[-1].split('.')[0], width=100)
import streamlit as st
import requests
import json

from PIL import Image
from io import BytesIO

# 画像をキャッシュするための関数
@st.cache_data
def load_image(url):
  try:
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image
  except Exception as e:
    return None

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
        image = load_image(img['url'])
        if image:
          # 列に画像を配置
          cols[j].image(image, caption=img["url"].split('/')[-1].split('.')[0], width=100)
        else:
          st.write(f"画像を読み込めませんでした: {img['url']}")

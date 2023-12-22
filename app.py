import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Streamlit アプリ
st.title('キャラクター評価')

st.header('モバイル・レジェンド')

# 画像のURLとランクのリスト
images_data = [
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/b66daae3e01fdd8dbdb50402d76fb078.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f0c110d9a15585baa0852329e8fed25d.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/78ef917e47557ed58c40e692357a2064.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0edb9f6f87539ca5a2da25dc21e08583.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/1265901a2b71fc97446d13f62b6149e1.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/1af73462bf1210f0be2fcebef72c466e.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0d67a5848994af687d6292ed21eccb45.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/06ddf4d8640ea33fe9b6a130832731eb.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/d4fee8a2ced4b1a050579cad3f931be6.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/11209c370fae29ed6fcf84e6e50d6c44.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/97e6c91d285f91791b8ca6c04cda08c5.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/73e764a256967032460d38bbe1898634.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0aa0771789789992af78c268c2305b4d.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/fb3c23b44b979f1a5c87620758b381f2.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/fb16d2c7d673d5df8a2511a57b0a2758.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/2474a0674887837aa9e1155425ccdf0d.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/bcda7c66e778f9ba4af863c7ba897369.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/b940bfa5488aed57379d0ed3d144699c.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/d9c3d7d54863e3fb87843e6b662c5a8a.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Jhonson.webp",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/4230571605be681167997550190ac09f.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/172c65292d9581fc77c5fa3bd9158862.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/44b249aae051615b047a55d1f508305d.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/d60f187b97af23e77a859ea58b348833.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/033a1675cc7da75fc31b80dd2e8bb0ea.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/85468496a318e8a884f5f237788eb52c.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/07040db4437dca39b9fd6b88771e7aef.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/5ad0161d035ea8d1c8a2828b846178a3.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Miya.webp",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/ebec4e5ebdc08f2b35fd4b9f386c857e.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/fe1928eb5800698133b31724c5595820.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Moskov.webp",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/2e0f2ff8b29202abd88830a40d6920dc.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f10d918a353b13e6d1a1bb6e780f0a3f.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/eaa1b2162e53da976e31cb7d64e4bc84.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/93a93ab28e4b7a81e94e0684db481bf3.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/3328413767bb1e2a6ac69af8aa8b9ddd.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/5c851c7f33e01b9b2ad966062b9655e1.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/df6dccd98c4365acbd400f74993b658b.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/c2abf12ad8dff3c342ffa4de81a7d419.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/95b04290a7240bc6e078eb30bff1c660.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/d067ac8cf26e7aae2ccfcb7d4d3f1a19.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/55d397810a9a6faa3de5498c5e43217e.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/91b46b37144b72667ae73782e85bea5e.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/cf1d4a8b9dabe816fa7b2c9d4ed72dd4.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/11/Bruno.webp",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0ed0cd46de895d0c76f143042cbcd746.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/10/8d1a06df532b3ee618caedd9ef1d91a6.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/66fba0613e265576d38503d97e9e5c5b-1.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/b4c252404821f59f038af290c486cd32.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/72ab0c3616e00e185ceff62ec92a0b0b.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/6245b7117d5f488824114e053b560ba3.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/023da83e07bd2c4344a49792d62f1ae0.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/1624c5cb118cd1803d12e0e895529979.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/984fca2a782545cd898324efccab5541.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/236dd6ea36875c3552a470735120282f.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0962722a17f00217d86c86b8896cd757.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/82a04090a5020545e16e092f8cd7cdf6.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/ddf68775441cd995ae638cb753527d51.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/9dda5826a0dd9d0ceb8a6a58dd54a00e.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/db1ec438d476d2673048606a33872451.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/e7876ea8e0d04a4bb02fa7a1cb896a43.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f31a9a89117ddbcaf0acdbdb1548ee08.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f2b69989ce0aa99a298d2f1026a8ace4.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/96ecbc37a99365081b902a85f4a999cb.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/e1f27858ece868d96a06fb72e9cc4c45.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/7c69f6568dda691fdb300a3ca5f3edc4.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/06/3680a55351b66b980b38f16b68b805fd.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/c8489278c24f4d0905497bc65268a976.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/2abb9937dc084632ef3dd253048f84cf.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/4d9871ab96d4bc4379199f7691e08d51.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/bb60559408f9451e6711bc2ea17274ed.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/7c72074e0a8d65fecdbdbb006963daaf-1.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/36867bee78bc29c54d03580e123eb909.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0cb7e30347295c6dbfd326f3840b911e.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/1063e686b2a6267e7f634f7af6577898.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/e594f689cdbfa4197482d51700aea0e4.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/5b5d611c059bfc669be0fc4798ffafe6.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/8ef4e2f8649742cfdc608ecda1c2fab8-1.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/360f7a357974a2f76a1d974b4c32ba54.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/07/8cb95e8ccad36f28b4b1c3adb617697b.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/0d51fbad90e30c4a2cf792ac433c8bf0.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/e64d24919824d0784acd1b0dcd61d55e.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/54c2518564fa0b1c2471fd5b4132ccef.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f015ecb16a4db8a9c0ee2078521494ce.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/944ae80c67a104dbd764169b39a64dfa.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/db5800ca32632370f1d577efc3e566e0.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/12e39680e620ea80e72f2964f9101e3c.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/629fcbc38e11095b937e296830258c1a.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/11/X-Borg.webp",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/83d87022861e09c2135bf89913b35287.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/52ad572ce4671342d78fc78109520ff2.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/07/49d5a6440a6e5bb1812f30d6d10a9717.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/29d68470d1d2277353a628b8d8165468.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/10/27ca9c4ce2d9377a92f3eecbb47c926d.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f9bda04d39caf4b27479a6b2bf630609.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/b1fda677d68a27826313731a2d01c4af.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/751c652d38cbdf2c354dd651a234b830.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/4aed42f35a76ad7a2b30ef2d099563d5.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/f6832b36e748902bde71aa14438a1f9d.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/e867b7d21c4922d52317c4300fdec399.png",
    "rank": "S+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/e7636de2fba637caffa121077c811da3.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/3c2664c885eaa7b42489361c61a16581.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/04/cd3de9b88d819c63ede2cfdf986f60e1.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/287030e95de643895e7565e2fe1ddfc6.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/b1163c13e213bd4a5260e3f693bc253f.png",
    "rank": "C"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/748e3830a6ee5452052e4548a19c2409.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/556c9123683b7bde3e0ecf7bfb2d30b8.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/92fb5f11cb814a69ec26876ed425c59e.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/1e519c119f6b843fc12ee254f2a16e94.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/00403a0a46cd20f2ba3699c38a8200f9.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/92cd3776d4f54c69dd2121182632be13.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/09672a0c5c44fcdb4c4ed5a98c3e419a.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/07/c9bd25940b7d7098a8ddf9e39581e38d.png",
    "rank": "B"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/05/79b1f3af8a06c72b239769c27a28a64d.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/06/707b0c79d516ba9bf095cbca54c5765d.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/10/ff45c5812c571e1bf95b901900204e14.png",
    "rank": "A"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2022/12/e35f4db78a8be49f13072a82ccee9dba.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/03/4312171f0509002d4e1a9eda9e85db71-1.png",
    "rank": "A+"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/05/fb5cfa0dd612fee70a0ed298b999e623.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/07/37a2f484344ad960e29e81bc186686cf.png",
    "rank": "S"
  },
  {
    "url": "https://shanbenzzz.com/wp-content/uploads/2023/10/4524e8421153e590eb371945d9c26b28-2.png",
    "rank": "S+"
  }
]

# 各ランクごとに画像を表示
for rank in ["S+", "S", "A+", "A", "B", "C"]:
  images = [img for img in images_data if img["rank"] == rank]
  
  # 画像がある場合のみ処理
  if images:
    # ランク表示用の列と8個の画像表示用の列を作成
    # 最初の行にランクを表示
    st.write(rank)
    
    # 画像表示用の列を設定
    for i in range(0, len(images), 8):
      cols = st.columns(8)
      # 各画像を表示
      for j, img in enumerate(images[i:i+8]):
        # 画像の読み込み
        response = requests.get(img["url"])
        image = Image.open(BytesIO(response.content))
        # 列に画像を配置
        # cols[j].image(image, caption=img["url"].split('/')[-1].split('.')[0], width=100)
        cols[j].image(image, width=100)
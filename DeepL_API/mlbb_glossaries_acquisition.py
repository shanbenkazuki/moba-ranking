import requests

# DeepL APIのエンドポイントとあなたのAPIキーを設定します。
DEEPL_API_URL = "https://api-free.deepl.com/v2/glossaries"
API_KEY = "6a352362-c808-e11c-3e6f-58867695116a:fx"

# APIリクエストを作成します。
headers = {
  "Authorization": f"DeepL-Auth-Key {API_KEY}"
}

# APIリクエストを送信します。
response = requests.get(DEEPL_API_URL, headers=headers)

# 応答を確認します。
if response.status_code == 200:
  glossaries = response.json()
  print(glossaries)
else:
  print(f"用語集の取得に失敗しました。エラーコード: {response.status_code}")
  print(f"エラーメッセージ: {response.text}")

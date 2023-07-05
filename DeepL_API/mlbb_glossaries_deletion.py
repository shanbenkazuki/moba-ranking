import requests

url = "https://api-free.deepl.com/v2/glossaries/68c3485f-2992-4b1f-90df-70ab8e2e3364"
API_KEY = '6a352362-c808-e11c-3e6f-58867695116a:fx'

headers = {
    'Authorization': f'DeepL-Auth-Key {API_KEY}'
}

response = requests.delete(url, headers=headers)

# レスポンスの確認
if response.status_code == 204:
    print("用語集が正常に削除されました")
else:
    print("用語集の削除に失敗しました")

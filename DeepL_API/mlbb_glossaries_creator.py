import requests

from fetch_moba_database import get_hero_data

url = 'https://api-free.deepl.com/v2/glossaries'
API_KEY = '6a352362-c808-e11c-3e6f-58867695116a:fx'

entries = ""
hero_data = get_hero_data()

for entry in hero_data.values():
  name_jp = entry['name_jp']
  name_en = entry['name_en']
  entries += f"{name_en},{name_jp}\n"

entries = entries.rstrip("\n")

data = {
  'name': 'mlbb',
  'source_lang': 'en',
  'target_lang': 'ja',
  'entries': f'{entries}',
  'entries_format': 'csv'
}

headers = {
  'Authorization': f'DeepL-Auth-Key {API_KEY}'
}

response = requests.post(url, data=data, headers=headers)
response_data = response.json()

# レスポンスの確認
print(response_data)

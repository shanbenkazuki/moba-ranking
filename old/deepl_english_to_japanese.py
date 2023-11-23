import requests

mlbb_glossary_id = '13509ac4-4270-4d46-a2ce-49ff711d355a'
API_KEY = '6a352362-c808-e11c-3e6f-58867695116a:fx'

def conv_mlbb_en_to_ja_translation(text):

  params = {
    'auth_key' : API_KEY,
    'text' : text,
    'source_lang' : 'EN',
    "target_lang": 'JA',
    'glossary_id': '13509ac4-4270-4d46-a2ce-49ff711d355a'
  }

  request = requests.post("https://api-free.deepl.com/v2/translate", data=params)
  result = request.json()

  return result['translations'][0]['text']
import requests
from bs4 import BeautifulSoup

def get_mlbb_version():
  DISPLAY_URL = 'https://apps.apple.com/jp/app/%E3%83%A2%E3%83%90%E3%82%A4%E3%83%AB-%E3%83%AC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%89-bang-bang/id1160056295'

  response = requests.get(DISPLAY_URL)
  html = response.text
  soup = BeautifulSoup(html, 'html.parser')

  element = soup.select_one('body > div.ember-view > main > div.animation-wrapper.is-visible > section.l-content-width.section.section--bordered.whats-new > div.l-row.whats-new__content > div.l-column.small-12.medium-3.large-4.small-valign-top.whats-new__latest > div > p')
  if element:
    version = element.text.replace("バージョン ", "")
    return version
  else:
    print("バージョン情報が見つかりませんでした。")

def get_unite_version():
  DISPLAY_URL = 'https://apps.apple.com/jp/app/pok%C3%A9mon-unite/id1512321575'

  response = requests.get(DISPLAY_URL)
  html = response.text
  soup = BeautifulSoup(html, 'html.parser')

  element = soup.select_one('body > div.ember-view > main > div.animation-wrapper.is-visible > section.l-content-width.section.section--bordered.whats-new > div.l-row.whats-new__content > div.l-column.small-12.medium-3.large-4.small-valign-top.whats-new__latest > div > p')
  if element:
    version = element.text.replace("バージョン ", "")
    return version
  else:
    print("バージョン情報が見つかりませんでした。")

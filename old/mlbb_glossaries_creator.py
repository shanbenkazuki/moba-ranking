# -*- coding: utf-8 -*-
import requests

from components.fetch_moba_database import get_hero_data


url = 'https://api-free.deepl.com/v2/glossaries'
API_KEY = '6a352362-c808-e11c-3e6f-58867695116a:fx'

entries = """Lolita,ロイン\nPhoveus,フォヴィウス\nUranus,ウラノス\nAulus,アウルス\nCecilion,セシリオン\nYve,イヴ\nValentina,バレンティナ\nClint,クリント\nDiggie,ディガー\nAldous,アウラド\nEsmeralda,エスメラルダ\nKimmy,ジミー\nGloo,グルー\nPopol and Kupa,ボボル&クバ\nLylia,リリア\nMathilda,マチルダ\nFreya,フレイヤ\nMasha,マーシャ\nIrithel,エレシル\nJohnson,ジェイソン\nKaja,カチャ\nLancelot,ランスロット\nSun,悟空\nKhufra,クッフラー\nCarmilla,カーミラ\nYi Sun-shin,イスンシン\nBane,ベイン\nArgus,アルゴス\nMiya,マイヤ\nClaude,クラウド\nFanny,ファニー\nMoskov,モスコブ\nRafaela,ラファエル\nKadita,カティタ\nKhaleed,カレード\nHelcurt,ハカート\nHylos,ヘラクレス\nYu Zhong,ゾン\nAlice,アリス\nOdette,オデット\nBeatrix,ビアトリクス\nRuby,ルビー\nCyclops,サイクロプス\nKagura,カグラ\nVale,ヴェル\nBruno,ブルーノ\nWanwan,琥珀\nGusion,ゴセン\nBarats,バラッツ\nLunox,星夢\nRoger,ロジャー\nEudora,エウドラ\nLuo Yi,ローイ\nFloryn,フローラ\nGranger,グレンジャー\nBaxia,玄覇\nHanzo,半蔵\nYin,寅\nSelena,セリナ\nZilong,子龍\nAurora,オーロラ\nChang'e,嫦娥\nFranco,フランコ\nBrody,ブロディ\nNatalia,ナタリア\nHayabusa,隼\nAtlas,アテラス\nLing,リン\nPharsa,ファーサ\nDyrroth,ディアス\nBelerick,ベレリック\nMinotaur,ミノタウル\nSilvanna,シルバンナ\nMelissa,メリッサ\nJawhead,メタルヘッド\nAkai,ガイ\nEdith,イーディス\nAngela,アンジェラ\nKarina,カリナ\nBenedetta,ベラ\nFaramis,ファラミス\nPaquito,パキート\nLapu-Lapu,ラプラプ\nAlucard,アルカード\nEstes,エスタス\nHanabi,ハナビ\nSaber,セイバー\nBadang,バターン\nGatotkaca,ガトートカチャ\nX.Borg,エックス\nNatan,ニュート\nChou,シュウ\nLeomord,レオモルド\nGrock,ガレック\nLesley,ラズリー\nHarley,ハーリー\nBalmond,バルモンド\nValir,ヴァリル\nHilda,ヒルダ\nAlpha,アルファ\nGuinevere,グネヴィア\nZhask,ザスク\nAamon,アモン\nMinsitthar,マイシータール\nGord,グールド\nNana,ナナ\nKarrie,キャリー\nThamuz,デームス\nTigreal,ティグラル\nMartis,マーティス\nHarith,ハリス\nLayla,ライラ\nTerizla,ディスラー\nVexana,サナ\nXavier,ザビエル\nJulian,ジュリアン\nFredrinn,フレッドリン\nJoy,ジョイ\nArlott,アーロット\nNovaria,ノヴァリア\nIxia,イクシア"""
# hero_data = get_hero_data()

# for entry in hero_data.values():
#   name_jp = entry['name_jp']
#   name_en = entry['name_en']
#   entries += f"{name_en},{name_jp}\n"

# entries = entries.rstrip("\n")

print(repr(entries))

# data = {
#   'name': 'mlbb',
#   'source_lang': 'en',
#   'target_lang': 'ja',
#   'entries': f'{entries}',
#   'entries_format': 'csv'
# }

# headers = {
#   'Authorization': f'DeepL-Auth-Key {API_KEY}'
# }

# response = requests.post(url, data=data, headers=headers)
# response_data = response.json()

# # レスポンスの確認
# print(response_data)

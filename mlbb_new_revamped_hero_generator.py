from DeepL_API.en_to_ja_translation_generator import conv_mlbb_en_to_ja_translation
from copy_text import get_new_revamped_hero_txt

text = get_new_revamped_hero_txt()

print('<!-- wp:table {"className":"sp_block_ is-style-regular min_width30_"} -->')

# 'strip()' 関数は先頭/末尾の空白を除去するために使用されます
# 'split' 関数でテキストを行ごとに分割します
paragraphs = text.strip().split("\n")

# リスト内包表記を用いて空の文字列 '' を除去します
paragraphs = [p for p in paragraphs if p != '']

# この文字列には、全体のHTMLテーブルが格納されます
html = '<figure class="wp-block-table sp_block_ is-style-regular min_width30_"><table><tbody>'

# リスト 'paragraphs' 内の各2行目をループ処理します
# 'range' 関数を用いて0からリストの長さまで2ステップでループします
for i in range(0, len(paragraphs), 2):
  # 現在の行はタイトルと見なされます
  # 'strip' 関数は、角括弧 '[]' を除去するために使用されます
  title = paragraphs[i].strip("[]")
  
  # 次の行は、前のタイトルに関連する内容と見なされます
  content = paragraphs[i+1]

  # 現在の行のHTMLが生成されます
  # タイトルと内容がそれぞれ対応するHTMLに挿入されます
  # 'f-string' フォーマットを使用して、これらの値を動的にHTML文字列に挿入します
  html += f'''
  <tr>
    <td>
      <span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black" aria-hidden="true">&nbsp;</span>
      <strong><span class="swl-cell-text-centered">{title}</span></strong>
    </td>
    <td>{conv_mlbb_en_to_ja_translation(content)}</td>
  </tr>
  '''

# 全ての行が処理された後、テーブル、ボディ、フィギュアの閉じタグが追加されます
html += '</tbody></table></figure>'

# 完成したHTML文字列を出力します
print(html)
print('<!-- /wp:table -->')
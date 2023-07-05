text = """
[Passive - Siphon Starlium]

Ixia marks enemies hit. If her Basic Attack hits an enemy marked twice, she deals extra damage and recovers an equal amount of HP.

[Skill 1 - Dual Beam]

Ixia uses her weapon to send Starlium-charged energy beams in front, dealing physical damage to enemies in a rectangle area and slowing them while gaining extra Movement Speed. Enemies hit by two energy beams take twice the damage.

[Skill 2 - Star Helix]

Ixia uses her special Sand Hunter skill and sends out a canister of Starlium energy in the target direction, knocking back nearby enemies, pulling them to the middle after a short delay and dealing Physical Damage.

[Ultimate - Full Barrage]

Ixia disassembles her weapon into 6 smaller weapons and enters the full Barrage state. In this state, Ixia's skills can be cast in a wider range and her Basic Attack can be used on at most 6 enemy units in the fan-shaped area.
"""


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
        <td>{content}</td>
    </tr>
    '''

# 全ての行が処理された後、テーブル、ボディ、フィギュアの閉じタグが追加されます
html += '</tbody></table></figure>'

# 完成したHTML文字列を出力します
print(html)
print('<!-- /wp:table -->')
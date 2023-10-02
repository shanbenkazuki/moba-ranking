import sqlite3

from copy_text import get_equipment_list

equipments = get_equipment_list()

# sqlite3に接続
conn = sqlite3.connect('moba_database.sqlite3')

# カーソルを取得
c = conn.cursor()

# Store the fetched image URLs in this list
image_urls = []

# 配列のデータを読み込み、テーブルからimage_urlを取得
for equipment in equipments:
    # データを取得
    c.execute('SELECT image_url FROM mlbb_equipments WHERE name_ja = ?', (equipment,))
    result = c.fetchone()
    
    # データを保存 or エラーメッセージを保存
    if result:
        image_urls.append(result[0])
    else:
        print(f"No image_url found for equipment: {equipment}")
        image_urls.append('')  # Add a placeholder for missing URLs

# データベース接続を閉じる
conn.close()

# Use the image URLs list to create the HTML string
html_template = """
<!-- wp:table {{"className":"is-style-regular is-all-centered"}} -->
<figure class="wp-block-table is-style-regular is-all-centered"><table><tbody><tr><td>
<img class="wp-image-2528" style="width: 50px;" src="{0}" alt="">
<img class="wp-image-4091" style="width: 50px;" src="{1}" alt=""> 
<img class="wp-image-2530" style="width: 50px;" src="{2}" alt="">
<img class="wp-image-3459" style="width: 50px;" src="{3}" alt=""> 
<img class="wp-image-2546" style="width: 50px;" src="{4}" alt="">
<img class="wp-image-3908" style="width: 50px;" src="{5}" alt=""> 
</td></tr></tbody></table></figure>
<!-- /wp:table -->
"""

# Format the HTML string with the fetched image URLs
formatted_html = html_template.format(*image_urls)

# Print or use the formatted HTML as needed
print(formatted_html)

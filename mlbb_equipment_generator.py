import re

from fetch_moba_database import get_mlbb_equipments
from copy_text import get_hero_adjust_txt

text = get_hero_adjust_txt()

equipment_data_line = text.strip().split("\n\n")

# テキストからヒーロー名を取得
equipment_name = re.search(r'\[(.*?)\]', equipment_data_line[0]).group(1)

# ヒーロー名からヒーローの画像データを取得
equipments = get_mlbb_equipments()
equipment_image_url = equipments[equipment_name]['image_url']

image_html = f'''
<!-- wp:image {{"align":"center","id":1146,"width":125,"height":125,"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image aligncenter size-full is-resized">
  <img src="{equipment_image_url}" alt="" class="wp-image-1146" width="125" height="125"/>
</figure>
<!-- /wp:image -->
'''

print(image_html)
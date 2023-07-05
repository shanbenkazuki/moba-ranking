from fetch_moba_database import get_hero_data
from DeepL_API.en_to_ja_translation_generator import conv_mlbb_en_to_ja_translation
from copy_text import get_hero_adjust_txt

text = get_hero_adjust_txt()

hero_data_line = text.strip().split("\n\n")

# テキストからヒーロー名を取得
hero_data_name = hero_data_line[0]
split_line = hero_data_name.split(' ')
name = ' '.join([i.strip('[]()') for i in split_line if i.strip('[]()')])
hero_name = name.split(" ")[0]

# ヒーロー名からヒーローの画像データを取得
hero_data = get_hero_data()
hero_image_url = hero_data[hero_name]['image_url']

image_html = f'''
<!-- wp:image {{"align":"center","id":1146,"width":125,"height":125,"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image aligncenter size-full is-resized">
  <img src="{hero_image_url}" alt="" class="wp-image-1146" width="125" height="125"/>
</figure>
<!-- /wp:image -->
'''

print(image_html)

# アコーディオンのHTMLを生成
description = hero_data_line[1]

description_html = f'''
<!-- wp:loos/accordion {{"className":"u-mb-ctrl u-mb-10"}} -->
<div class="swell-block-accordion u-mb-ctrl u-mb-10"><!-- wp:loos/accordion-item -->
  <details class="swell-block-accordion__item" data-swl-acc="wrapper">
    <summary class="swell-block-accordion__title" data-swl-acc="header"><span
        class="swell-block-accordion__label">説明</span><span class="swell-block-accordion__icon c-switchIconBtn"
        data-swl-acc="icon" aria-hidden="true" data-opened="false"><i class="__icon--closed icon-caret-down"></i><i
          class="__icon--opened icon-caret-up"></i></span></summary>
    <div class="swell-block-accordion__body" data-swl-acc="body"><!-- wp:paragraph -->
      <p>
        {conv_mlbb_en_to_ja_translation(description)}
      </p>
      <!-- /wp:paragraph -->
    </div>
  </details>
  <!-- /wp:loos/accordion-item -->
</div>
<!-- /wp:loos/accordion -->
'''

print(description_html)

# ヒーロー調整用のHTMLを生成
hero_adjust_trs = ''

counter = 0
for element in hero_data_line[2:]:
  if counter % 2 == 0:
    # 偶数番目の処理
    hero_adjust_trs += '<tr><td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black"aria-hidden="true">&nbsp;</span><strong><span class="swl-cell-text-centered">'
    hero_adjust_trs += element
    hero_adjust_trs += '</span></strong></td><td>'
  else:
    # 奇数番目の処理
    hero_adjust_trs += conv_mlbb_en_to_ja_translation(element)
    hero_adjust_trs += '</td></tr>'
  counter += 1

hero_adjust_html = f'''
<!-- wp:table {{"className":"sp_block_ is-style-regular min_width30_"}} -->
<figure class="wp-block-table sp_block_ is-style-regular min_width30_">
  <table>
    <tbody>
      {hero_adjust_trs}
    </tbody>
  </table>
</figure>
<!-- /wp:table -->
'''

print(hero_adjust_html)
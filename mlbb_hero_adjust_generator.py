from fetch_moba_database import get_hero_data
from DeepL_API.en_to_ja_translation_generator import conv_mlbb_en_to_ja_translation

text = """
[Harley] (~)

As a dexterous assassin, Harley needs more mobility and smoother skill combos. Therefore, we made it easier for him to trick enemies with Skill 2 and optimized the skill combo where he could only use Basic Attacks after Skill 1. Also, we added an HP loss preview for his Ultimate so that both sides can gauge how to best act. Finally, we tuned down his early and mid-game damage to balance out the Basic Attack changes.

[Passive] (↑)

New Effect: Dealing damage with Basic Attacks or skills increases Harley's Attack Speed by 5-10% (scales with his level). Stacks up to 10.

[Skill 1] (↓)

Effect Removed: Attack Speed increases with each hit that damages an enemy.

[Skill 2] (↑)

Movement Speed: +30% for 4s >> +60% maximum, decaying over 4s.
Cooldown Reduction: 8.5-6.5s >> 11-8s (the skill now enters cooldown immediately after its first attack, instead of that being determined by whether the second attack was launched or not).
Mana Cost: 60-110 >> 75-0

[Ultimate] (~)

You can now preview the HP loss of the enemy he's about to hit.
Total Damage Ratio: 50% >> 30%-50% (scales with level)
Second Attack's Damage: 100-200 + 30% Magic Power >> 200 + 50% Magic Power
"""

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
# trタグのS+のスタートタグ
def create_tr_splus_start_tag():
    return '<tr><td><span style="--the-cell-bg: #ff9900" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">S+</mark></span></td><td><span style="--the-cell-bg: #ffeecc" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのSのスタートタグ
def create_tr_s_start_tag():
    return '<tr><td><span style="--the-cell-bg: #ff6666" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">S</mark></span></td><td><span style="--the-cell-bg: #ffeeee" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのA+のスタートタグ
def create_tr_aplus_start_tag():
    return '<tr><td><span style="--the-cell-bg: #ff00cc" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">A+</mark></span></td><td><span style="--the-cell-bg: #ffe7fa" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのAのスタートタグ
def create_tr_a_start_tag():
    return '<tr><td><span style="--the-cell-bg: #6666ff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">A</mark></span></td><td><span style="--the-cell-bg: #eeeeff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのBのスタートタグ
def create_tr_b_start_tag():
    return '<tr><td><span style="--the-cell-bg: #53abff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">B</mark></span></td><td><span style="--the-cell-bg: #f0f8ff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのCのスタートタグ
def create_tr_c_start_tag():
    return '<tr><td><span style="--the-cell-bg: #0dbc0d" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">C</mark></span></td><td><span style="--the-cell-bg: #eeffee" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのエンドタグ
def create_tr_end_tag():
    return '</td></tr>'

# ヒーローのaタグ（画像あり）
def create_hero_a_tag(hero_image_url, hero_article_url):
    return '<a href="' + hero_article_url + '" data-type="URL" data-id="' + hero_article_url + '"><img class="alignnone wp-image-1088" style="width: 60px;" src="' + hero_image_url + '" alt=""></a>'

# ヒーローのaタグ（画像なし）
def create_hero_img_tag(image_url):
    return '<img class="alignnone wp-image-1088" style="width: 60px;" src="' + image_url + '" alt="">'
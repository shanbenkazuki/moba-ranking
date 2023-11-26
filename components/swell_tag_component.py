# trタグのS+のスタートタグ
def createTrSPlusStartTag():
    return '<tr><td><span style="--the-cell-bg: #ff9900" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">S+</mark></span></td><td><span style="--the-cell-bg: #ffeecc" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのSのスタートタグ
def createTrSStartTag():
    return '<tr><td><span style="--the-cell-bg: #ff6666" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">S</mark></span></td><td><span style="--the-cell-bg: #ffeeee" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのA+のスタートタグ
def createTrAPlusStartTag():
    return '<tr><td><span style="--the-cell-bg: #ff00cc" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">A+</mark></span></td><td><span style="--the-cell-bg: #ffe7fa" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのAのスタートタグ
def createTrAStartTag():
    return '<tr><td><span style="--the-cell-bg: #6666ff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">A</mark></span></td><td><span style="--the-cell-bg: #eeeeff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのBのスタートタグ
def createTrBStartTag():
    return '<tr><td><span style="--the-cell-bg: #53abff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">B</mark></span></td><td><span style="--the-cell-bg: #f0f8ff" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのCのスタートタグ
def createTrCStartTag():
    return '<tr><td><span style="--the-cell-bg: #0dbc0d" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span><span class="swl-cell-text-centered"><mark style="background-color:rgba(0, 0, 0, 0)" class="has-inline-color has-white-color">C</mark></span></td><td><span style="--the-cell-bg: #eeffee" data-text-color="black" aria-hidden="true" class="swl-cell-bg">&nbsp;</span>'

# trタグのエンドタグ
def createTrEndTag():
    return '</td></tr>'

# ヒーローのaタグ（画像あり）
def createHeroATag(heroImageURL, heroArticleURL):
    return '<a href="' + heroArticleURL + '" data-type="URL" data-id="' + heroArticleURL + '"><img class="alignnone wp-image-1088" style="width: 60px;" src="' + heroImageURL + '" alt=""></a>'

# ヒーローのaタグ（画像なし）
def createHeroImgTag(imageUrl):
    return '<img class="alignnone wp-image-1088" style="width: 60px;" src="' + imageUrl + '" alt="">'
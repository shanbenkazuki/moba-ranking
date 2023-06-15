import re
from googletrans import Translator

translator = Translator()

# 見出しh3タグの生成
def createH3Heading(name):
    return '<!-- wp:heading {"level":3} --><h3>' + name + '</h3><!-- /wp:heading -->'

# 見出しh4タグの生成
def createHeading(name):
    return '<!-- wp:heading {"level":4} --><h4>' + name + '</h4><!-- /wp:heading -->'

# 初期テーブルスタートタグの生成
def createStartTag():
    return '<!-- wp:table {"className":"is-style-regular"} --><figure class="wp-block-table is-style-regular"><table><tbody>'

# 初期テーブルエンドタグの生成
def createEndTag():
    return '</tbody></table></figure><!-- /wp:table -->'

# ヒーロー画像タグの生成
def createImgTag(image,status):
    statusTag = createStatusTag(status)
    return '<tr><td><span class="swl-cell-text-centered"><img class="wp-image-1050" style="width: 150px;" src="' + image + '" alt=""></span><span class="swl-cell-text-centered">' + statusTag + '</span></td></tr>'

def fetchStatus(td):
    if not td.find(text=re.compile("ADJUST")) == None:
        return td.find(text=re.compile("ADJUST"))
    elif not td.find(text=re.compile("BUFF")) == None:
        return td.find(text=re.compile("BUFF"))
    elif not td.find(text=re.compile("NERF")) == None:
        return td.find(text=re.compile("NERF"))
    else:
        return ""

# 調整状態タグの生成
def createStatusTag(status):
    if "NERF" in status:
        return '<span class="swl-bg-color has-swl-deep-02-background-color">' + status + '</span>'
    elif "BUFF" in status:
        return '<span class="swl-bg-color has-swl-deep-01-background-color">' + status + '</span>'
    elif "ADJUST" in status:
        return '<span class="swl-bg-color has-swl-deep-04-background-color">' + status + '</span>'
    else :
        return status

#強調タグ（スキル、パッシブ、ステータスなど）の生成
def createStrongTag(strongStr, status):
    statusTag = createStatusTag(status)
    #強調タグにして返す
    return '<tr><td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black" aria-hidden="true">&nbsp;</span><strong><span class="swl-cell-text-centered">' + strongStr + statusTag + '</span></strong></td></tr>'

#liコンテンツ
def createLiContentTag(td):
    content=''
    lis = td.find_all('li')
    for li in lis:
        liTextJa = translator.translate(li.text, src="en", dest="ja").text
        content += (liTextJa + '<br>')
    return '<tr><td>' + content + '</td></tr>'


#↓Tierで使うタグ

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
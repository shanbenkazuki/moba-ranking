import time
import sys
import conv.mobile_legends.convJaMlbbBattlefield as convJaMlbbBattlefield
import conv.mobile_legends.convImgMlbbBattlefield as convImgMlbbBattlefield
import conv.mobile_legends.convJaEnTerm as convJaEnTerm

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from googletrans import Translator

PATCH_URL = "https://mobile-legends.fandom.com/wiki/Patch_Notes_1.6.66"
WAIT_TIME = 20
FETCH_TABLE_SELECTOR = "#mw-content-text > div.mw-parser-output > table:nth-child(38)"

# 画面遷移
driver = webdriver.Chrome()
driver.get(PATCH_URL)
driver.implicitly_wait(WAIT_TIME)

# 見出しタグの生成
def createHeading(heroName):
    return '<!-- wp:heading {"level":4} --><h4>' + heroName + '</h4><!-- /wp:heading -->'

# 初期テーブルスタートタグの生成
def createStartTag():
    return '<!-- wp:table {"className":"is-style-regular"} --><figure class="wp-block-table is-style-regular"><table><tbody>'

# 初期テーブルエンドタグの生成
def createEndTag():
    return '</tbody></table></figure><!-- /wp:table -->'

# ヒーロー画像タグの生成
def createImgTag(spellImage,status):
    statusTag = createStatusTag(status)
    return '<tr><td><span class="swl-cell-text-centered"><img class="wp-image-1050" style="width: 150px;" src="' + spellImage + '" alt=""></span><span class="swl-cell-text-centered">' + statusTag + '</span></td></tr>'

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
def createTdStrongTag(strongStr, status):
    # 用語があれば日本語に変換
    attributeJa = convJaEnTerm.convJaEnTerm(strongStr)
    # 調整状態のタグを生成
    statusTag = createStatusTag(status)
    #強調タグにして返す
    return '<tr><td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black" aria-hidden="true">&nbsp;</span><strong><span class="swl-cell-text-centered">' + attributeJa + statusTag + '</span></strong></td></tr>'

def createSpanStrongTag(tr):
    strongStr = tr.find_all('span')[0].text
    status = ""
    #print(tr.find_all('span'))
    if tr.find_all('span')[0] is None:
        status = ""
    else:
        status = tr.find_all('span')[0].text
    # 用語があれば日本語に変換
    attributeJa = convJaEnTerm.convJaEnTerm(strongStr)
    # 調整状態のタグを生成
    statusTag = createStatusTag(status)
    #強調タグにして返す
    return '<tr><td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black" aria-hidden="true">&nbsp;</span><strong><span class="swl-cell-text-centered">' + attributeJa + statusTag + '</span></strong></td></tr>'

def createContentTag(tr):
    content=''
    lis = tr.find_all('li')
    for li in lis:
        liTextJa = translator.translate(li.text, src="en", dest="ja").text
        content += (liTextJa + '<br>')
    return '<tr><td>' + content + '</td></tr>'

def createTdContentTag(tr):
    tdText = tr.find_all('td')[1].contents[0]
    content = translator.translate(tdText, src="en", dest="ja").text
    return '<tr><td>' + content + '</td></tr>'

# ヒーロー調整テーブル抽出
heroAdjustments = BeautifulSoup(driver.page_source, 'html.parser').select(FETCH_TABLE_SELECTOR)

# 試行する
tryNum = 0
while len(heroAdjustments) == 0:
    # ページ情報抽出
    driver.get(PATCH_URL)
    heroAdjustments = BeautifulSoup(driver.page_source, 'html.parser').select(FETCH_TABLE_SELECTOR)
    print("試行")
    tryNum += 1
    if tryNum == 5:
        break

# 5回試行して正常に取れない場合、終了
if len(heroAdjustments) == 0:
    print("失敗")
    driver.close()
    driver.quit()
    sys.exit()

# 調整ヒーローテーブルのtrタグをすべて取得
trs = heroAdjustments[0].find_all('tr')
trsEndLen = len(trs)
translator = Translator()

# 調整スペルテーブルの作成
for i, tr in enumerate(trs):
    # tdがいくつあるか
    tdLen = len(tr.find_all('td'))
    if tdLen==2:
        # i=0以外でテーブルエンドタグをつける
        if i>0:
            #初期テーブルエンドタグ作成
            print(createEndTag())
        # スペル名取得
        spellNameEn = tr.find_all('td')[0].find_all('span')[0].text
        #spellNameEn = tr.find_all('td')[0].find_all('span')[1].text
        # 取得したヒーロー名を日本語に変換
        spellNameJa = convJaMlbbBattlefield.convJaSpell(spellNameEn)
        #h3見出し作成
        print(createHeading(spellNameJa))
        #初期テーブルスタートタグ作成
        print(createStartTag())
        #調整状態取得
        status = tr.find_all('td')[0].find_all('span')[1].text
        #取得したヒーロー名を画像URLに変換
        spellImage = convImgMlbbBattlefield.convJaSpell(spellNameEn)
        #画像タグ作成
        print(createImgTag(spellImage,status))
        #行が1の場合
        if i==8:
            print(createTdContentTag(tr))
    elif tdLen==1:
        # 画像があるかないか
        isImage = tr.find_all('td')[0].find('a')
        # 画像がない場合
        if isImage is None:
            #強調文字の取得
            strongStr = tr.find_all('td')[0].contents[0]
            #調整状態の取得
            status = ""
            # if tr.find_all('span')[0] is None:
            #     status = ""
            # else:
            #     status = tr.find_all('span')[0].text
            print(createTdStrongTag(strongStr, status))
            print(createContentTag(tr))
        # 画像がある場合
        else:
            #スキル項目取得（強調）
            strongStr = tr.find_all('td')[0].find_all('span')[0].text
            status = tr.find_all('td')[0].find_all('span')[1].text
            print(createSpanStrongTag(strongStr,status))
            print(createContentTag(tr))
    #trsEndLenと同じときエンドタグをつける
    if (i+1)==trsEndLen:
        print(createEndTag())

driver.close()
driver.quit()

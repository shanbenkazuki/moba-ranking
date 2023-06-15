import time
import sys
import re
import conv.mobile_legends.convJaMlbbBattlefield as convJaMlbbBattlefield
import conv.mobile_legends.convImgMlbbBattlefield as convImgMlbbBattlefield
import conv.mobile_legends.convJaEnTerm as convJaEnTerm

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from googletrans import Translator

PATCH_URL = "https://mobile-legends.fandom.com/wiki/Patch_Notes_1.6.66"
WAIT_TIME = 20
FETCH_TABLE_SELECTOR = "#mw-content-text > div.mw-parser-output > table:nth-child(40)"

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
def createImgTag(buildImage,status):
    statusTag = createStatusTag(status)
    return '<tr><td><span class="swl-cell-text-centered"><img class="wp-image-1050" style="width: 150px;" src="' + buildImage + '" alt=""></span><span class="swl-cell-text-centered">' + statusTag + '</span></td></tr>'

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

def createStrongTag(strongStr,status):
    # 用語があれば日本語に変換
    attributeJa = convJaEnTerm.convJaEnTerm(strongStr)
    # 調整状態のタグを生成
    statusTag = createStatusTag(status)
    #強調タグにして返す
    return '<tr><td><span class="swl-cell-bg has-swl-gray-background-color" data-text-color="black" aria-hidden="true">&nbsp;</span><strong><span class="swl-cell-text-centered">' + attributeJa + statusTag + '</span></strong></td></tr>'

def createLiContentTag(td):
    content=''
    lis = td.find_all('li')
    for li in lis:
        liTextJa = translator.translate(li.text, src="en", dest="ja").text
        content += (liTextJa + '<br>')
    return '<tr><td>' + content + '</td></tr>'

def createSecondPContentTag(td):
    pText = td.find('p')
    content = translator.translate(pText, src="en", dest="ja").text
    return '<tr><td>' + content + '</td></tr>'

def createSecondTdContentTag(td):
    tdText = td.contents[0]
    content = translator.translate(tdText, src="en", dest="ja").text
    return '<tr><td>' + content + '</td></tr>'

def createFirstTdContentTag(td):
    tdText = td.contents[0]
    content = translator.translate(tdText, src="en", dest="ja").text
    return '<tr><td>' + content + '</td></tr>'

def fetchStatus(td):
    if not td.find(text=re.compile("ADJUST")) == None:
        return td.find(text=re.compile("ADJUST"))
    elif not td.find(text=re.compile("BUFF")) == None:
        return td.find(text=re.compile("BUFF"))
    elif not td.find(text=re.compile("NERF")) == None:
        return td.find(text=re.compile("NERF"))
    else:
        return ""

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
    firstTdTag  = tr.find_all('td')[0]
    if tdLen==2:
        secandTdTag = tr.find_all('td')[1]
        # i=0以外でテーブルエンドタグをつける
        if i>0:
            #初期テーブルエンドタグ作成
            print(createEndTag())
        # 名称取得
        #buildNameEn = firstTdTag.find_all('span')[0].text
        buildNameEn = ""
        if firstTdTag.find('a') == None:
            buildNameEn = firstTdTag.contents[0]
        else :
            buildNameEn = firstTdTag.find('a').get('title')
        #buildNameEn = firstTdTag.find_all('span')[1].text
        #buildNameEn = firstTdTag.find_all('a')[1].text
        # 日本語に変換
        buildNameJa = convJaMlbbBattlefield.convJaBuild(buildNameEn)
        #見出し作成
        print(createHeading(buildNameJa))
        #初期テーブルスタートタグ作成
        print(createStartTag())
        #調整状態取得
        status = fetchStatus(firstTdTag)
        #取得したヒーロー名を画像URLに変換
        buildImage = convImgMlbbBattlefield.convJaBuild(buildNameEn)
        #画像タグ作成
        print(createImgTag(buildImage,status))
        #行が1、強調あり、内容がli
        if i==28:
            #print(createSecondTdContentTag(tr))
            #調整状態取得
            strongStr = secandTdTag.find('p').text
            status = fetchStatus(secandTdTag)
            createStrongTag(strongStr,status)
            print(createLiContentTag(secandTdTag))
        #行が1、強調なし、内容がtd
        if i==29:
            print(createSecondTdContentTag(secandTdTag))
    elif tdLen==1:
        #画像があってもtdが2つにわかれていない場合
        if i==4 or i==13 or i==15:
            #初期テーブルエンドタグ作成
            print(createEndTag())
            #見出し作成
            buildNameEn = firstTdTag.find('a').get('title')
            # 日本語に変換
            buildNameJa = convJaMlbbBattlefield.convJaBuild(buildNameEn)
            print(createHeading(buildNameJa))
             #初期テーブルスタートタグ作成
            print(createStartTag())
            #調整状態取得
            status = fetchStatus(firstTdTag)
            #取得したヒーロー名を画像URLに変換
            buildImage = convImgMlbbBattlefield.convJaBuild(buildNameEn)
            #画像タグ作成
            print(createImgTag(buildImage,status))
            continue
        #強調文字の取得
        #strongStr = firstTdTag.find_all('span')[0].text
        # pタグの有無
        pTag = firstTdTag.find('p')
        #pタグがなければコンテンツタグに移行
        if pTag is None:
            print(createFirstTdContentTag(firstTdTag))
            continue
        strongStr = pTag.contents[0]
        #調整状態の取得
        status = fetchStatus(firstTdTag)
        print(createStrongTag(strongStr,status))
        print(createLiContentTag(tr))
    #trsEndLenと同じときエンドタグをつける
    if (i+1)==trsEndLen:
        print(createEndTag())

driver.close()
driver.quit()

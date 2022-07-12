import time
import sys
import conv.mobile_legends.convJaMlbbHero as convJaMlbbHero
import conv.mobile_legends.convImgMlbbHero as convImgMlbbHero
import conv.mobile_legends.convJaEnTerm as convJaEnTerm
import common.tagComponent as tag

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from googletrans import Translator


PATCH_URL = "https://mobile-legends.fandom.com/wiki/Patch_Notes_1.6.66"
WAIT_TIME = 20
FETCH_TABLE_SELECTOR = "#mw-content-text > div.mw-parser-output > table:nth-child(61)"

# 画面遷移
driver = webdriver.Chrome()
driver.get(PATCH_URL)
driver.implicitly_wait(WAIT_TIME)

# 調整テーブル抽出
adjustsTable = BeautifulSoup(driver.page_source, 'html.parser').select(FETCH_TABLE_SELECTOR)

# 初回失敗時、5回まで再試行
tryNum = 0
while len(adjustsTable) == 0:
    # ページ情報抽出
    print("再試行")
    driver.get(PATCH_URL)
    time.sleep(2)
    adjustsTable = BeautifulSoup(driver.page_source, 'html.parser').select(FETCH_TABLE_SELECTOR)
    tryNum += 1
    # 正常に取れない場合、終了
    if tryNum == 5:
        print("失敗")
        driver.close()
        driver.quit()
        sys.exit()

# 調整テーブルのtrタグをすべて取得
trs = adjustsTable[0].find_all('tr')
trsEndLen = len(trs)
translator = Translator()

for i, tr in enumerate(trs):
    # tdがいくつあるか
    tdLen = len(tr.find_all('td'))
    firstTdTag  = tr.find_all('td')[0]
    if tdLen==2:
        secandTdTag = tr.find_all('td')[1]
        # i=0以外でテーブルエンドタグをつける
        if i>0:
            #初期テーブルエンドタグ作成
            print(tag.createEndTag())
        # 取得
        nameEn = firstTdTag.find('a').get('title')
        nameJa = convJaMlbbHero.convJaHeroName(nameEn)
        status = tag.fetchStatus(firstTdTag)
        heroImage = convImgMlbbHero.convImgHeroName(nameEn)
        # 表示
        print(tag.createH3Heading(nameJa))
        print(tag.createStartTag())
        print(tag.createImgTag(heroImage,status))
    elif tdLen==1:
        # 画像があるかないか
        isImage = firstTdTag.find('a')
        status = tag.fetchStatus(firstTdTag)
        # 画像がない場合
        if isImage is None:
            strongStr = convJaEnTerm.convJaEnTerm(firstTdTag.contents[0])
            print(tag.createStrongTag(strongStr, status))
            print(tag.createLiContentTag(firstTdTag))
        # 画像がある場合
        else:
            #スキル項目取得（強調）
            strongStr = firstTdTag.find_all('span')[0].text
            status = tag.fetchStatus(firstTdTag)
            print(tag.createStrongTag(strongStr,status))
            print(tag.createLiContentTag(firstTdTag))
    #trsEndLenと同じときエンドタグをつける
    if (i+1)==trsEndLen:
        print(tag.createEndTag())

driver.close()
driver.quit()

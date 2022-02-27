import time
import convMlbbHero as convMlbbHero
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

loginUrl = "https://m.mobilelegends.com/en/rank"

#ランキング画面遷移
profilePath = '/Users/kazuki/Library/Application Support/Google/Chrome/Profile 5'
profilefolder = '--user-data-dir=' + profilePath
 
profileOptions = Options()
profileOptions.add_argument(profilefolder)
 
driver = webdriver.Chrome(options = profileOptions)
driver.get(loginUrl)

#変換されるまで待機
time.sleep(2)

#ミシック400ポイント表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/div[1]/div[2]/ul/li[3]").click()

#変換されるまで待機
time.sleep(2)

#BAN率の昇順表示に切り替え
driver.find_element(by=By.XPATH, value="//*[@id='rank']/ul/li[7]").click()

#変換されるまで待機
time.sleep(2)

#ページ取得
html = driver.page_source

#ランキング抽出
soup = BeautifulSoup(html, 'html.parser')

#BAN率が高いヒーロー10体の名前を取得
allHeroList = soup.select(".slotwrapper > ul > li > a > div:nth-of-type(1) > span", limit=10)
#BAN率が高いヒーロー10体の勝率を取得
banRateList = soup.select(".slotwrapper > ul > li > a > div:nth-of-type(4)", limit=10)
#統計日を取得
statisticsDate = soup.select_one(".time").string

#ターミナルに表示
print("* 統計参照時期：''" + statisticsDate + "''")
print("[-]")
print("|CENTER|CENTER|c")
print("|ヒーロー|COLSORT:BAN率|h")
for i, hero in enumerate(allHeroList):
    hero = convMlbbHero.convertHeroName(hero.string)
    print("|" + hero +"|"+ banRateList[i].string + "|")  
print("[END]")

driver.close()
driver.quit()
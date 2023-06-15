from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
#ドロップダウン用
from selenium.webdriver.support.select import Select
#日付
import datetime
import locale
import time

loginUrl = "https://ariake.gsol.mydns.jp/gsol/login"
userCd = "yamamotok"
passWd = "gsol6119"

# ログイン画面遷移
profilePath = '/Users/kazuki/Library/Application Support/Google/Chrome/Profile 5'
profilefolder = '--user-data-dir=' + profilePath
 
profileOptions = Options()
profileOptions.add_argument(profilefolder)
 
driver = webdriver.Chrome(options = profileOptions)

driver.get(loginUrl)

# 要素が見つかるまで待機設定
driver.implicitly_wait(10)

# ユーザコード入力
driver.find_element(by=By.ID, value='im_user').clear()
driver.find_element(by=By.ID, value='im_user').send_keys(userCd)
# パスワード入力
driver.find_element(by=By.ID, value='im_password').clear()
driver.find_element(by=By.ID, value='im_password').send_keys(passWd)
# ログインクリック
driver.find_element(by=By.CLASS_NAME, value='imui-btn-login').click()

#勤怠一覧遷移
driver.get("https://ariake.gsol.mydns.jp/gsol/attendance/list/list")

#現在日付をクリックしてモーダル表示
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
dt_now = datetime.datetime.now()
nowDate = dt_now.strftime('%-m月%d日（%a）')
driver.find_element(by=By.XPATH, value="//*[text()=\""+ nowDate +"\"]").click()

#モーダル入力
#勤務体系 出勤日
kinmuDropdown = driver.find_element(by=By.NAME, value='shiftPatternCd')
select = Select(kinmuDropdown)
select.select_by_index(1) 
#業務 
#開始 09:00 業務 CA_SES1
driver.find_element(by=By.NAME, value='attendStartTime').click()
driver.find_element(by=By.XPATH, value="//*[text()=\"09\"]").click()
#終了 18:00
driver.find_element(by=By.NAME, value='attendEndTime').click()
driver.find_element(by=By.XPATH, value="//*[text()=\"18\"]").click()
#業務 CA_SES1
gyoumuDropdown = driver.find_element(by=By.NAME, value='businessCd')
select = Select(gyoumuDropdown)
select.select_by_index(2) 

#立替金
# 部門 その他
tatekaeDropdown = driver.find_element(by=By.NAME, value='departmentCd')
select = Select(tatekaeDropdown)
select.select_by_index(3) 
#業務 CA_SES1
tatekaeGyoumuDropdown = driver.find_element(by=By.XPATH, value="//*[@id='advancesPaidList']/tbody/tr/td[2]/select")
select = Select(tatekaeGyoumuDropdown)
select.select_by_index(1) 
#区分
kubunDropdown = driver.find_element(by=By.NAME, value='advancesPaidCd')
select = Select(kubunDropdown)
select.select_by_index(4) 
#費用300
driver.find_element(by=By.NAME, value='expense').send_keys("300")

#登録クリック
driver.find_element(by=By.ID, value='registerAttendanceButton').click()

#モーダル決定クリック
driver.find_element(by=By.XPATH, value="/html/body/div[13]/div[3]/div/button[1]").click()

#変換されるまで待機
time.sleep(2)

driver.close()
driver.quit()
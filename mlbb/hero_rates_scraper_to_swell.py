# 必要なライブラリをインポート
import sys
import os

# プロジェクトのルートディレクトリをパスに追加します
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pandas as pd
from components import swell_tag_component as tag
import time

# Seleniumとその関連ライブラリをインポートします（ウェブサイトの自動操作に使用）
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# ヒーローのスコアに基づいてランクを決定する
def get_rank_from_score(score):
  if score >= 1.0:
    return 'S+'
  elif score >= 0.5:
    return 'S'
  elif score >= 0:
    return 'A+'
  elif score >= -0.5:
    return 'A'
  elif score >= -1.0:
    return 'B'
  else:
    return 'C'


# ウェブサイトのURLと待機時間を設定します
DISPLAY_URL = "https://m.mobilelegends.com/rank"
WAIT_TIME = 10

# Chromeブラウザの設定を行います
chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

service = Service(ChromeDriverManager().install())

# Chromeブラウザを起動します
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(WAIT_TIME)

# ブラウザウィンドウを最大化します
driver.maximize_window()

# 指定されたURLにアクセスします
driver.get(DISPLAY_URL)

# 5秒間待機します
time.sleep(5)

# ページ上の特定の要素をクリックします
xpath = '//*[@id="root"]/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[2]'
element = driver.find_element(By.XPATH, xpath)
element.click()

time.sleep(5)

# 別の要素をクリックします
new_xpath = '//*[@id="root"]/div/div[2]/div/div[1]/div[1]/div[1]/div[1]/div/div[3]'
new_element = driver.find_element(By.XPATH, new_xpath)
new_element.click()

time.sleep(5)

# 特定の要素が表示されるまで待機します
target_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > div.mt-2673591.mt-empty > div > div.mt-2684927.mt-empty > div.mt-2684827.mt-empty > div'))
)

# 対象の要素までスクロールします
driver.execute_script("arguments[0].scrollIntoView();", target_element)

# ページの最下部までスクロールしてデータを読み込みます
last_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
while True:
    driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", target_element)
    time.sleep(2)  # データの読み込みを待機
    new_height = driver.execute_script("return arguments[0].scrollHeight", target_element)
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(5)

# ページのHTMLを解析してヒーローの情報を取得します
rateList = BeautifulSoup(driver.page_source, 'html.parser').select("#root > div > div.mt-2673591.mt-empty > div > div.mt-2684927.mt-empty > div.mt-2684827.mt-empty > div > div")

# 各ヒーローのデータを収集します
hero_meta_data = []
for heroRate in rateList:
   hero_name = heroRate.select_one("div.mt-2693555 > div.mt-2693412 > span").text
   pick_rate = float(heroRate.select_one("div.mt-2684925 > span").text.replace("%", ""))
   win_rate = float(heroRate.select_one("div.mt-2684926 > span").text.replace("%", ""))
   ban_rate = float(heroRate.select_one("div.mt-2687632 > span").text.replace("%", ""))
   hero_meta_data.append({
       'hero': hero_name,
       'win_rate': win_rate,
       'pick_rate': pick_rate,
       'ban_rate': ban_rate
   })

# データをPandasのDataFrameに変換します
df = pd.DataFrame(hero_meta_data)

# ヒーロー名をインデックスに設定します
df.set_index('hero', inplace=True)

# 各指標のz-scoreを計算します
df['win_rate_z'] = (df['win_rate'] - df['win_rate'].mean()) / df['win_rate'].std(ddof=0)
df['pick_rate_z'] = (df['pick_rate'] - df['pick_rate'].mean()) / df['pick_rate'].std(ddof=0)
df['ban_rate_z'] = (df['ban_rate'] - df['ban_rate'].mean()) / df['ban_rate'].std(ddof=0)
df['interaction'] = df['win_rate_z'] * df['pick_rate_z']
df['z_score'] = 0.6 * df['win_rate_z'] + 0.25 * df['pick_rate_z'] + 0.15 * df['ban_rate_z'] - 0.2 * df['interaction']

# 既存のヒーローデータを読み込みます
hero_csv = pd.read_csv("/Users/yamamotokazuki/develop/moba-ranking-rails/db/csv/hero.csv")

# データの整合性をチェックします
for _, row in hero_csv.iterrows():
    hero = row['name_en']
    if hero not in df.index:
        print(f"Hero '{hero}' not found in df index")
    else:
        z_score = df.loc[hero, 'z_score']
        if pd.isna(z_score):
            print(f"Z-score for hero '{hero}' is NaN")

# ヒーローの情報を辞書形式で保存します
hero_dict = {}
for _, row in hero_csv.iterrows():
    hero = row['name_en']
    hero_dict[hero] = {
        'role': row['role'],
        'image_url': row['tier_img_url'],
        'z_score': df.loc[hero, 'z_score'] if hero in df.index and 'z_score' in df.columns else None
    }

# hero_dictをroleごとに分ける
tank_hero_dict = {}
fighter_hero_dict = {}
support_hero_dict = {}
assassin_hero_dict = {}
marksman_hero_dict = {}
mage_hero_dict = {}

for role, data in hero_dict.items():
  if data['role'] == 'Tank':
    tank_hero_dict[role] = data
  elif data['role'] == 'Fighter':
    fighter_hero_dict[role] = data
  elif data['role'] == 'Support':
    support_hero_dict[role] = data
  elif data['role'] == 'Assassin':
    assassin_hero_dict[role] = data
  elif data['role'] == 'Marksman':
    marksman_hero_dict[role] = data
  elif data['role'] == 'Mage':
    mage_hero_dict[role] = data

# zscoreをもとにtierを作成する
splus_fighter_hero = ''
s_fighter_hero = ''
aplus_fighter_hero = ''
a_fighter_hero = ''
b_fighter_hero = ''
c_fighter_hero = ''

splus_tank_hero = ''
s_tank_hero = ''
aplus_tank_hero = ''
a_tank_hero = ''
b_tank_hero = ''
c_tank_hero = ''

splus_support_hero = ''
s_support_hero = ''
aplus_support_hero = ''
a_support_hero = ''
b_support_hero = ''
c_support_hero = ''

splus_assassin_hero = ''
s_assassin_hero = ''
aplus_assassin_hero = ''
a_assassin_hero = ''
b_assassin_hero = ''
c_assassin_hero = ''

splus_marksman_hero = ''
s_marksman_hero = ''
aplus_marksman_hero = ''
a_marksman_hero = ''
b_marksman_hero = ''
c_marksman_hero = ''

splus_mage_hero = ''
s_mage_hero = ''
aplus_mage_hero = ''
a_mage_hero = ''
b_mage_hero = ''
c_mage_hero = ''

# zscoreをもとにtierを分ける
for hero, data in tank_hero_dict.items():
    tier_hero_img_tag = tag.create_hero_img_tag(data['image_url'])
    if get_rank_from_score(data['z_score']) == 'S+':
        splus_tank_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'S':
        s_tank_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A+':
        aplus_tank_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A':
        a_tank_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'B':
        b_tank_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'C':
        c_tank_hero += tier_hero_img_tag

for hero, data in fighter_hero_dict.items():
    tier_hero_img_tag = tag.create_hero_img_tag(data['image_url'])
    if get_rank_from_score(data['z_score']) == 'S+':
        splus_fighter_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'S':
        s_fighter_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A+':
        aplus_fighter_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A':
        a_fighter_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'B':
        b_fighter_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'C':
        c_fighter_hero += tier_hero_img_tag

for hero, data in support_hero_dict.items():
    tier_hero_img_tag = tag.create_hero_img_tag(data['image_url'])
    if get_rank_from_score(data['z_score']) == 'S+':
        splus_support_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'S':
        s_support_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A+':
        aplus_support_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A':
        a_support_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'B':
        b_support_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'C':
        c_support_hero += tier_hero_img_tag

for hero, data in assassin_hero_dict.items():
    tier_hero_img_tag = tag.create_hero_img_tag(data['image_url'])
    if get_rank_from_score(data['z_score']) == 'S+':
        splus_assassin_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'S':
        s_assassin_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A+':
        aplus_assassin_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A':
        a_assassin_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'B':
        b_assassin_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'C':
        c_assassin_hero += tier_hero_img_tag

for hero, data in marksman_hero_dict.items():
    tier_hero_img_tag = tag.create_hero_img_tag(data['image_url'])
    if get_rank_from_score(data['z_score']) == 'S+':
        splus_marksman_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'S':
        s_marksman_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A+':
        aplus_marksman_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A':
        a_marksman_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'B':
        b_marksman_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'C':
        c_marksman_hero += tier_hero_img_tag

for hero, data in mage_hero_dict.items():
    tier_hero_img_tag = tag.create_hero_img_tag(data['image_url'])
    if get_rank_from_score(data['z_score']) == 'S+':
        splus_mage_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'S':
        s_mage_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A+':
        aplus_mage_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'A':
        a_mage_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'B':
        b_mage_hero += tier_hero_img_tag
    elif get_rank_from_score(data['z_score']) == 'C':
        c_mage_hero += tier_hero_img_tag

# 出力ディレクトリを作成（存在しない場合）
output_dir = 'mlbb/swell_text'
os.makedirs(output_dir, exist_ok=True)

reference_date_str = BeautifulSoup(driver.page_source, 'html.parser').select_one("#root > div > div.mt-2673591.mt-empty > div > div.mt-2693420.mt-empty > div.mt-2693423.mt-empty > div.mt-2693419.mt-text > span").text

reference_date = datetime.strptime(reference_date_str, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d')

# 出力ファイルのパスを設定（日付を含む）
output_file = os.path.join(output_dir, f'tier_{reference_date}.txt')

# ファイルに書き込む
with open(output_file, 'w', encoding='utf-8') as f:
    # タブ始まり
    f.write('<!-- wp:loos/tab {"tabId":"55c27d22","tabWidthPC":"flex-50","tabHeaders":["ファイター","メイジ","タンク","アサシン","ハンター","サポート"],"className":"is-style-balloon"} -->\n')
    f.write('<div class="swell-block-tab is-style-balloon" data-width-pc="flex-50" data-width-sp="auto"><ul class="c-tabList" role="tablist"><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="true" aria-controls="tab-55c27d22-0" data-onclick="tabControl">ファイター</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-1" data-onclick="tabControl">メイジ</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-2" data-onclick="tabControl">タンク</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-3" data-onclick="tabControl">アサシン</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-4" data-onclick="tabControl">ハンター</button></li><li class="c-tabList__item" role="presentation"><button role="tab" class="c-tabList__button" aria-selected="false" aria-controls="tab-55c27d22-5" data-onclick="tabControl">サポート</button></li></ul><div class="c-tabBody">\n')

    # Fighter
    f.write('<!-- wp:loos/tab-body {"tabId":"55c27d22"} --><div id="tab-55c27d22-0" class="c-tabBody__item" aria-hidden="false"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>\n')
    # tr追加場所
    # S+
    f.write(tag.create_tr_splus_start_tag() + splus_fighter_hero + tag.create_tr_end_tag() + '\n')
    # S
    f.write(tag.create_tr_s_start_tag() + s_fighter_hero + tag.create_tr_end_tag() + '\n')
    # A+
    f.write(tag.create_tr_aplus_start_tag() + aplus_fighter_hero + tag.create_tr_end_tag() + '\n')
    # A
    f.write(tag.create_tr_a_start_tag() + a_fighter_hero + tag.create_tr_end_tag() + '\n')
    # B
    f.write(tag.create_tr_b_start_tag() + b_fighter_hero + tag.create_tr_end_tag() + '\n')
    # C
    f.write(tag.create_tr_c_start_tag() + c_fighter_hero + tag.create_tr_end_tag() + '\n')
    f.write('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->\n')

    # Mage
    f.write('<!-- wp:loos/tab-body {"id":1,"tabId":"55c27d22"} --><div id="tab-55c27d22-1" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>\n')
    f.write(tag.create_tr_splus_start_tag() + splus_mage_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_s_start_tag() + s_mage_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_aplus_start_tag() + aplus_mage_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_a_start_tag() + a_mage_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_b_start_tag() + b_mage_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_c_start_tag() + c_mage_hero + tag.create_tr_end_tag() + '\n')
    f.write('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->\n')

    # Tank
    f.write('<!-- wp:loos/tab-body {"id":2,"tabId":"55c27d22"} --><div id="tab-55c27d22-2" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>\n')
    f.write(tag.create_tr_splus_start_tag() + splus_tank_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_s_start_tag() + s_tank_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_aplus_start_tag() + aplus_tank_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_a_start_tag() + a_tank_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_b_start_tag() + b_tank_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_c_start_tag() + c_tank_hero + tag.create_tr_end_tag() + '\n')
    f.write('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->\n')

    # Assassin
    f.write('<!-- wp:loos/tab-body {"id":3,"tabId":"55c27d22"} --><div id="tab-55c27d22-3" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>\n')
    f.write(tag.create_tr_splus_start_tag() + splus_assassin_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_s_start_tag() + s_assassin_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_aplus_start_tag() + aplus_assassin_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_a_start_tag() + a_assassin_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_b_start_tag() + b_assassin_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_c_start_tag() + c_assassin_hero + tag.create_tr_end_tag() + '\n')
    f.write('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->\n')

    # Marksman
    f.write('<!-- wp:loos/tab-body {"id":4,"tabId":"55c27d22"} --><div id="tab-55c27d22-4" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>\n')
    f.write(tag.create_tr_splus_start_tag() + splus_marksman_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_s_start_tag() + s_marksman_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_aplus_start_tag() + aplus_marksman_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_a_start_tag() + a_marksman_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_b_start_tag() + b_marksman_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_c_start_tag() + c_marksman_hero + tag.create_tr_end_tag() + '\n')
    f.write('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->\n')

    # Support
    f.write('<!-- wp:loos/tab-body {"id":5,"tabId":"55c27d22"} --><div id="tab-55c27d22-5" class="c-tabBody__item" aria-hidden="true"><!-- wp:table {"className":"is-style-regular is-all-centered\u002d\u002dva td_to_th_"} --><figure class="wp-block-table is-style-regular is-all-centered--va td_to_th_"><table><tbody>\n')
    f.write(tag.create_tr_splus_start_tag() + splus_support_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_s_start_tag() + s_support_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_aplus_start_tag() + aplus_support_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_a_start_tag() + a_support_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_b_start_tag() + b_support_hero + tag.create_tr_end_tag() + '\n')
    f.write(tag.create_tr_c_start_tag() + c_support_hero + tag.create_tr_end_tag() + '\n')
    f.write('</tbody></table></figure><!-- /wp:table --></div><!-- /wp:loos/tab-body -->\n')

    #タブ終わり
    f.write('</div></div><!-- /wp:loos/tab -->\n')

print(f"Output has been written to {output_file}")
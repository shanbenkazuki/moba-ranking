import asyncio
import nodriver as uc
import re
import csv
import os
import sys

from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加します
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from components import fetch_moba_database as fmd

async def main():
    # データベースからポケモンの名前を取得
    pokemon_names = fmd.get_pokemon_data(["name_en"])

    browser = await uc.start()
    page = await browser.get('https://uniteapi.dev/meta')

    await page.wait(20)

    # game_info = await page.query_selector('#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > h3')

    game_info = await page.query_selector('#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.m_4081bf90.mantine-Group-root > div:nth-child(1) > p.mantine-focus-auto.simpleStat_count__dG_xB.m_b6d8b162.mantine-Text-root')

    date_string = game_info.text_all

    # date_string = "July 7"
    year = "2024"

# 日付文字列をdatetimeオブジェクトに変換
    date_object = datetime.strptime(f"{date_string} {year}", "%B %d %Y")

    # 新しい形式で日付を出力
    stats_date = date_object.strftime("%Y-%m-%d")

    game_info = await page.query_selector('#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.m_4081bf90.mantine-Group-root > div:nth-child(2) > p.mantine-focus-auto.simpleStat_count__dG_xB.m_b6d8b162.mantine-Text-root')

    game_count = int(game_info.text_all)

    # 日付の抽出
    # date_match = re.search(r"(\w+\s\d{1,2})", game_info.text_all)
    # if date_match:
    #     english_date = date_match.group(1)
    #     # 英語の日付を日本語の形式に変換
    #     stats_date = english_date.split()
    #     month_dict = {
    #         "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
    #         "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"
    #     }
    #     stats_date = f"2024-{month_dict[stats_date[0]]}-{stats_date[1].zfill(2)}"
    # else:
    #     stats_date = None

    # # ゲーム数の抽出
    # game_count_match = re.search(r"(\d+)\s*games", game_info.text_all)
    # if game_count_match:
    #     game_count = int(game_count_match.group(1))
    # else:
    #     game_count = None

    # 勝率を取得
    win_rates = {}
    win_rate_selector = '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(1) > div > div'
    
    win_rate_html = await page.query_selector(win_rate_selector)
 
    if win_rate_html:
        pokemon_elements = await win_rate_html.query_selector_all('#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(1) > div > div > div')
        for pokemon_element in pokemon_elements:

            img_element = await pokemon_element.query_selector('img')

            if img_element:
                img_src = img_element.attrs.get('src')
            filename = img_src.split("/")[-1]

            if "Urshifu_Single" in filename:
                pokemon_name = "Urshifu"
            elif "Meowscara" in filename:
                pokemon_name = "Meowscarada"
            else:
                pokemon_name = filename.split("_")[-1].split(".")[0]
            win_rate_element = await pokemon_element.query_selector('.sc-71f8e1a4-1')

            if win_rate_element:
                win_rate = win_rate_element.attrs.get('value')
            win_rates[pokemon_name] = win_rate

    # ピック率を取得
    pick_rates = {}
    pick_rate_selector = '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(2) > div > div'
    
    pick_rate_html = await page.query_selector(pick_rate_selector)
    if pick_rate_html:
        pokemon_elements = await pick_rate_html.query_selector_all('#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(2) > div > div > div')
        for pokemon_element in pokemon_elements:

            img_element = await pokemon_element.query_selector('img')

            if img_element:
                img_src = img_element.attrs.get('src')
            filename = img_src.split("/")[-1]

            if "Urshifu_Single" in filename:
                pokemon_name = "Urshifu"
            elif "Meowscara" in filename:
                pokemon_name = "Meowscarada"
            else:
                pokemon_name = filename.split("_")[-1].split(".")[0]
            pick_rate_element = await pokemon_element.query_selector('.sc-71f8e1a4-1')

            if pick_rate_element:
                pick_rate = pick_rate_element.attrs.get('value')
            pick_rates[pokemon_name] = pick_rate

    # バン率を取得
    ban_rates = {}
    ban_rate_selector = '#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(3) > div > div'
    ban_rate_html = await page.query_selector(ban_rate_selector)
    if ban_rate_html:
        pokemon_elements = await ban_rate_html.query_selector_all('#__next > div.m_89ab340.mantine-AppShell-root > main > div > div.sc-eaff77bf-0.bvmFlh > div.sc-eaff77bf-0.fJbBUh > div:nth-child(3) > div > div > div')
        for pokemon_element in pokemon_elements:

            img_element = await pokemon_element.query_selector('img')

            if img_element:
                img_src = img_element.attrs.get('src')
            filename = img_src.split("/")[-1]

            if "Urshifu_Single" in filename:
                pokemon_name = "Urshifu"
            elif "Meowscara" in filename:
                pokemon_name = "Meowscarada"
            else:
                pokemon_name = filename.split("_")[-1].split(".")[0]
            ban_rate_element = await pokemon_element.query_selector('.sc-71f8e1a4-1')

            if ban_rate_element:
                ban_rate = ban_rate_element.attrs.get('value')
            ban_rates[pokemon_name] = ban_rate

    # 出力先のディレクトリを指定
    output_dir = "/Users/yamamotokazuki/develop/moba-ranking-rails/db/csv/pokemon_rates"

    # 出力先のディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)

    # CSVファイル名を作成
    filename = f"{output_dir}/pokemon_rates_{stats_date}_{game_count}.csv"

    # CSVファイルに書き込む
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Pokemon', 'win_rate', 'pick_rate', 'ban_rate'])  # ヘッダー行を書き込む
        for pokemon in pokemon_names:
            name = pokemon[0]
            win_rate = win_rates.get(name, '-')
            pick_rate = pick_rates.get(name, '-')
            ban_rate = ban_rates.get(name, '-')
            writer.writerow([name, win_rate, pick_rate, ban_rate])  # データ行を書き込む

    print(f"CSV file '{filename}' has been created.")

if __name__ == '__main__':

    # since asyncio.run never worked (for me)
    uc.loop().run_until_complete(main())
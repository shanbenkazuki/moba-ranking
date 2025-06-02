import nodriver as uc
import asyncio
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# バージョンチェック機能をインポート
from check_unite_version import extract_latest_update_info, save_patch_to_database

def extract_pokemon_stats(content):
    """HTMLコンテンツからポケモンの統計データを抽出"""
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(content, 'html.parser')
    
    def extract_meta_information():
        """更新日とトータルゲーム数を抽出してmeta情報を作成"""
        meta = {}
        
        # 更新日を抽出
        last_updated_element = soup.find('p', class_='mantine-focus-auto simpleStat_count__dG_xB m_b6d8b162 mantine-Text-root')
        if last_updated_element:
            last_updated_text = last_updated_element.get_text().strip()
            
            # 英語の月名を数値に変換
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            
            # "June 1" 形式を解析
            match = re.match(r'(\w+)\s+(\d+)', last_updated_text)
            if match:
                month_name, day = match.groups()
                month = month_map.get(month_name)
                day = int(day)
                
                if month:
                    # 年を算出（現在の日付と比較して適切な年を決定）
                    current_date = datetime.now()
                    current_year = current_date.year
                    
                    # 仮の更新日を作成
                    try:
                        update_date = datetime(current_year, month, day)
                        
                        # 更新日が未来すぎる場合（3ヶ月以上先）は前年とみなす
                        if update_date > current_date + timedelta(days=90):
                            update_date = datetime(current_year - 1, month, day)
                        # 更新日が過去すぎる場合（9ヶ月以上前）は翌年とみなす
                        elif update_date < current_date - timedelta(days=270):
                            update_date = datetime(current_year + 1, month, day)
                        
                        meta['last_updated'] = update_date.strftime('%Y-%m-%d')
                    except ValueError:
                        # 日付が無効な場合（例：2月30日など）
                        meta['last_updated'] = f"{current_year}-{month:02d}-{day:02d}"
        
        # トータルゲーム数を抽出
        total_games_elements = soup.find_all('p', class_='mantine-focus-auto simpleStat_count__dG_xB m_b6d8b162 mantine-Text-root')
        for element in total_games_elements:
            # 次の要素がTotal Games Analyzedかチェック
            next_element = element.find_next_sibling('p')
            if next_element and 'Total Games Analyzed' in next_element.get_text():
                total_games_text = element.get_text().strip()
                # 数値のみを抽出（カンマを削除して整数に変換）
                total_games = re.sub(r'[^\d]', '', total_games_text)
                if total_games:
                    meta['total_games_analyzed'] = int(total_games)
                break
        
        return meta
    
    def get_section_by_heading(heading_text):
        """ヘading要素を基準にセクションを取得する（より堅牢な方法）"""
        # ヘadingを探す
        heading = soup.find('h2', string=re.compile(heading_text, re.IGNORECASE))
        if not heading:
            return []
        
        # ヘadingから親コンテナを探す
        section_container = heading.find_parent('div', class_=re.compile(r'sc-d5d8a548-0|iVUifA'))
        if not section_container:
            # フォールバック: より上位の親要素を探す
            section_container = heading.find_parent('div')
            for _ in range(3):  # 最大3レベル上まで探す
                if section_container and section_container.find_all('div', class_=re.compile(r'mantine-Group-root')):
                    break
                section_container = section_container.find_parent('div') if section_container else None
        
        if section_container:
            # セクション内のポケモンデータ要素を取得
            return section_container.find_all('div', class_=re.compile(r'mantine-Group-root'))
        
        return []
    
    def get_section_by_css_fallback(css_selector):
        """フォールバック用のCSSセレクタ"""
        try:
            return soup.select(css_selector)
        except:
            return []
    
    # より堅牢な方法でセクションを取得（ヘading基準 + フォールバック）
    win_rate_elements = get_section_by_heading("Win rate last week")
    if not win_rate_elements:
        win_rate_elements = get_section_by_css_fallback('div.m_6d731127.mantine-Stack-root > div:nth-child(5) > div:nth-child(1) > div > div > div')
    
    pick_rate_elements = get_section_by_heading("Pick rate last week")
    if not pick_rate_elements:
        pick_rate_elements = get_section_by_css_fallback('div.m_6d731127.mantine-Stack-root > div:nth-child(5) > div:nth-child(3) > div > div > div')
    
    ban_rate_elements = get_section_by_heading("Ban rate last week")
    if not ban_rate_elements:
        ban_rate_elements = get_section_by_css_fallback('div.m_6d731127.mantine-Stack-root > div:nth-child(5) > div:nth-child(2) > div > div > div')
    
    def extract_pokemon_data_from_section(section_elements, data_type=""):
        """セクション内からポケモンデータを抽出"""
        pokemon_data = []
        
        for element in section_elements:
            # 各要素内でimg要素を探す（複数の候補パターン）
            img_element = (
                element.find('img', alt=re.compile(r'Avatar of the pokemon')) or
                element.find('img', alt=re.compile(r'pokemon', re.IGNORECASE)) or
                element.find('img', src=re.compile(r'/Sprites/'))
            )
            
            # value属性を持つdiv要素を探す（統計データ）
            value_element = (
                element.find('div', attrs={'value': True}) or
                element.find('div', string=re.compile(r'\d+\.\d+\s*%')) or
                element.find('div', class_=re.compile(r'sc-71f8e1a4-1'))
            )
            
            if img_element and value_element:
                # alt属性からポケモン名を抽出
                alt_text = img_element.get('alt', '')
                pokemon_name = None
                
                if 'Avatar of the pokemon' in alt_text:
                    pokemon_name = alt_text.replace('Avatar of the pokemon ', '')
                    
                    # Mewtwoの場合は、srcsetまたはsrc属性から詳細な形態を取得
                    if pokemon_name == 'Mewtwo':
                        srcset = img_element.get('srcset', '')
                        src = img_element.get('src', '')
                        
                        # srcsetから形態を判定
                        if 'MewtwoX' in srcset:
                            pokemon_name = 'Mewtwo-X'
                        elif 'MewtwoY' in srcset:
                            pokemon_name = 'Mewtwo-Y'
                        # フォールバック: srcから形態を判定
                        elif 'MewtwoX' in src:
                            pokemon_name = 'Mewtwo-X'
                        elif 'MewtwoY' in src:
                            pokemon_name = 'Mewtwo-Y'
                            
                elif alt_text and alt_text != 'Pokemon image':
                    pokemon_name = alt_text
                else:
                    # フォールバック: src属性からポケモン名を抽出
                    src = img_element.get('src', '')
                    if '/Sprites/' in src:
                        pokemon_name = src.split('/')[-1].replace('t_Square_', '').replace('.png', '')
                
                # ポケモン名の空白とピリオドをハイフンに変換
                if pokemon_name:
                    pokemon_name = re.sub(r'[ .]+', '-', pokemon_name)
                
                # value属性から値を抽出
                rate_value = value_element.get('value')
                if not rate_value:
                    # フォールバック: テキストから数値を抽出
                    text_content = value_element.get_text()
                    match = re.search(r'(\d+\.\d+)', text_content)
                    if match:
                        rate_value = match.group(1)
                
                if pokemon_name and rate_value:
                    try:
                        rate_float = float(rate_value)
                        pokemon_data.append({
                            'pokemon_name': pokemon_name,
                            'rate': rate_float
                        })
                    except ValueError:
                        continue
        
        print(f"取得した{data_type}データ: {len(pokemon_data)}件")
        return pokemon_data
    
    # 各セクションからデータを抽出
    win_rate_data = extract_pokemon_data_from_section(win_rate_elements, "勝率")
    pick_rate_data = extract_pokemon_data_from_section(pick_rate_elements, "Pick率")
    ban_rate_data = extract_pokemon_data_from_section(ban_rate_elements, "BAN率")
    
    # データを統合
    all_pokemon_data = {}
    
    # 勝率データを追加
    for data in win_rate_data:
        pokemon_name = data['pokemon_name']
        if pokemon_name not in all_pokemon_data:
            all_pokemon_data[pokemon_name] = {}
        all_pokemon_data[pokemon_name]['win_rate'] = data['rate']
    
    # Pick率データを追加
    for data in pick_rate_data:
        pokemon_name = data['pokemon_name']
        if pokemon_name not in all_pokemon_data:
            all_pokemon_data[pokemon_name] = {}
        all_pokemon_data[pokemon_name]['pick_rate'] = data['rate']
    
    # BAN率データを追加
    for data in ban_rate_data:
        pokemon_name = data['pokemon_name']
        if pokemon_name not in all_pokemon_data:
            all_pokemon_data[pokemon_name] = {}
        all_pokemon_data[pokemon_name]['ban_rate'] = data['rate']
    
    # リスト形式に変換
    result = []
    for pokemon_name, stats in all_pokemon_data.items():
        pokemon_stats = {'pokemon_name': pokemon_name}
        pokemon_stats.update(stats)
        result.append(pokemon_stats)
    
    # 統計情報を出力
    print(f"統合後のポケモンデータ: {len(result)}件")
    
    # メタ情報を抽出
    meta = extract_meta_information()
    
    # メタ情報を統合
    result_with_meta = {
        'meta': meta,
        'pokemon_data': result
    }
    
    # 統計情報を出力
    print(f"メタ情報: 更新日={meta.get('last_updated', 'N/A')}, 総ゲーム数={meta.get('total_games_analyzed', 'N/A')}")
    
    return result_with_meta

async def main():
    # スクレイピング前にバージョンチェックを実行
    print("=" * 60)
    print("🔍 Pokémon UNITE バージョンチェックを開始します...")
    print("=" * 60)
    
    try:
        update_info = extract_latest_update_info()
        
        if update_info:
            print(f"✅ 最新のアップデート情報を取得しました")
            print("-" * 40)
            
            if "date" in update_info:
                print(f"📅 日付: {update_info['date']}")
            
            if "update_datetime" in update_info:
                print(f"🕐 アップデート日時: {update_info['update_datetime']}")
            
            if "version" in update_info:
                print(f"🏷️  バージョン: {update_info['version']}")
            
            if "content" in update_info:
                print(f"📝 内容: {update_info['content'][:100]}..." if len(update_info['content']) > 100 else f"📝 内容: {update_info['content']}")
                
            print("-" * 40)
            
            # データベースに保存
            print("💾 データベースに保存中...")
            if save_patch_to_database(update_info):
                print("✅ データベースへの保存が完了しました")
            else:
                print("❌ データベースへの保存に失敗しました")
        else:
            print("⚠️  アップデート情報を取得できませんでしたが、スクレイピングを継続します")
            
    except Exception as e:
        print(f"⚠️  バージョンチェック中にエラーが発生しましたが、スクレイピングを継続します: {e}")
    
    print("=" * 60)
    print("📊 統計データのスクレイピングを開始します...")
    print("=" * 60)
    
    # ブラウザを開始（ヘッドレスではない設定で、より人間らしく）
    browser = await uc.start()
    
    try:
        # https://uniteapi.dev/meta にアクセス
        print("https://uniteapi.dev/meta にアクセス中...")
        page = await browser.get('https://uniteapi.dev/meta')
        
        # "Pokémon Unite Meta Tierlist"のテキストが見えるまで待機（サイトに到達したことを確認）
        print("サイトの読み込み確認中...")
        await page.find("Pokémon Unite Meta Tierlist")
        print("サイトに正常にアクセスできました。")
        
        # HTMLコンテンツを取得
        print("HTMLコンテンツを取得中...")
        content = await page.get_content()
        
        # ファイルにも保存
        with open('unite_api_content.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("HTMLコンテンツを 'unite_api_content.html' に保存しました。")
        
        # BeautifulSoupでデータを抽出
        print("\nHTMLコンテンツを解析してポケモン統計データを抽出中...")
        pokemon_stats_with_meta = extract_pokemon_stats(content)
        
        # JSON形式でコンソールに出力
        print("\n" + "="*50)
        print("ポケモン統計データ（JSON形式）:")
        print("="*50)
        print(json.dumps(pokemon_stats_with_meta, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    finally:
        # ブラウザを終了
        try:
            browser.stop()
        except:
            print("ブラウザの停止中にエラーが発生しましたが、処理は完了しました。")

if __name__ == '__main__':
    # asyncioのイベントループを実行
    uc.loop().run_until_complete(main())

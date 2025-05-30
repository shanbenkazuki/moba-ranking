import os
import shutil
import filecmp
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Set

# 色の定義
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def get_project_root() -> Path:
    """スクリプトの場所からプロジェクトのルートディレクトリを取得"""
    return Path(__file__).parent

def find_plist_files(directory: Path) -> List[Path]:
    """指定されたディレクトリ内のすべての.plistファイルを再帰的に検索"""
    return list(directory.rglob("*.plist"))

def run_launchctl_command(command: str, file_path: str) -> bool:
    """launchctlコマンドを実行し、結果を表示"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}エラー: {command}{Colors.NC}")
        print(f"{Colors.RED}エラー内容: {e.stderr}{Colors.NC}")
        return False

def is_target_file(file_name: str) -> bool:
    """対象のファイルかどうかを判定（com.moba_rankingで始まるファイルのみ）"""
    return file_name.startswith("com.moba_ranking")

def sync_files(source_dir: Path, target_dir: Path) -> Dict[str, List[str]]:
    """ソースディレクトリのファイルをターゲットディレクトリに同期"""
    result = {
        "created": [],  # 新規作成されたファイル
        "updated": [],  # 更新されたファイル
        "deleted": [],  # 削除されたファイル
    }

    # ソースディレクトリのファイル名のセットを作成
    source_files = {f.name for f in find_plist_files(source_dir)}
    
    # ターゲットディレクトリのファイルをチェック
    for target_file in target_dir.glob("*.plist"):
        if is_target_file(target_file.name) and target_file.name not in source_files:
            # ファイルがソースに存在しない場合（削除された）
            result["deleted"].append(target_file.name)
            # ファイルを削除
            target_file.unlink()

    # 通常の同期処理
    for source_file in find_plist_files(source_dir):
        # ファイル名のみを取得（フォルダ構造を無視）
        file_name = source_file.name
        if not is_target_file(file_name):
            continue

        target_file = target_dir / file_name

        # ファイルが存在しない場合は新規作成
        if not target_file.exists():
            shutil.copy2(source_file, target_file)
            result["created"].append(file_name)
        # ファイルが存在し、内容が異なる場合は更新
        elif not filecmp.cmp(source_file, target_file, shallow=False):
            shutil.copy2(source_file, target_file)
            result["updated"].append(file_name)

    return result

def main():
    # プロジェクトのルートディレクトリを取得
    project_root = get_project_root()
    
    # ソースディレクトリとターゲットディレクトリの設定
    source_dir = project_root / "launchagents"
    target_dir = Path.home() / "Library/LaunchAgents"

    print("LaunchAgentsの同期を開始します...")
    print(f"ソース: {source_dir}")
    print(f"ターゲット: {target_dir}")
    print("----------------------------------------")

    # ファイルの同期
    result = sync_files(source_dir, target_dir)

    # 削除されたファイルを表示してbootout
    if result["deleted"]:
        print(f"\n{Colors.RED}削除されたファイル:{Colors.NC}")
        for file_name in result["deleted"]:
            print(f"{Colors.RED}削除: {Colors.NC}{file_name}")
            # launchctl bootoutコマンドを実行 (new‑style, GUI domain)
            label = file_name[:-6] if file_name.endswith(".plist") else file_name
            bootout_command = f"launchctl bootout gui/{os.getuid()}/{label}"
            if run_launchctl_command(bootout_command, file_name):
                print(f"{Colors.GREEN}bootout成功: {file_name}{Colors.NC}")

    # 新規作成されたファイルを表示してbootstrap
    if result["created"]:
        print(f"\n{Colors.BLUE}新規作成されたファイル:{Colors.NC}")
        for file_name in result["created"]:
            print(f"{Colors.BLUE}作成: {Colors.NC}{file_name}")
            # launchctl bootstrapコマンドを実行 (new‑style, GUI domain)
            bootstrap_command = f"launchctl bootstrap gui/{os.getuid()} ~/Library/LaunchAgents/{file_name}"
            if run_launchctl_command(bootstrap_command, file_name):
                print(f"{Colors.GREEN}bootstrap成功: {file_name}{Colors.NC}")

    # 更新されたファイルを表示してbootoutしてからbootstrap
    if result["updated"]:
        print(f"\n{Colors.GREEN}更新されたファイル:{Colors.NC}")
        for file_name in result["updated"]:
            print(f"{Colors.GREEN}更新: {Colors.NC}{file_name}")
            # launchctl bootout→bootstrap (new‑style, GUI domain)
            label = file_name[:-6] if file_name.endswith(".plist") else file_name
            bootout_command = f"launchctl bootout gui/{os.getuid()}/{label}"
            if run_launchctl_command(bootout_command, file_name):
                print(f"{Colors.GREEN}bootout成功: {file_name}{Colors.NC}")
                # 再読み込み
                bootstrap_command = f"launchctl bootstrap gui/{os.getuid()} ~/Library/LaunchAgents/{file_name}"
                if run_launchctl_command(bootstrap_command, file_name):
                    print(f"{Colors.GREEN}bootstrap成功: {file_name}{Colors.NC}")

    print("\n----------------------------------------")
    total_changes = len(result["created"]) + len(result["updated"]) + len(result["deleted"])
    if total_changes == 0:
        print(f"{Colors.YELLOW}すべてのファイルは最新の状態です。{Colors.NC}")
    else:
        print(f"{Colors.GREEN}合計 {total_changes} 個のファイルを処理しました。{Colors.NC}")
        print(f"- 新規作成: {len(result['created'])} 個")
        print(f"- 更新: {len(result['updated'])} 個")
        print(f"- 削除: {len(result['deleted'])} 個")

if __name__ == "__main__":
    main() 
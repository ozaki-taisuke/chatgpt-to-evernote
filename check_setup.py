"""
セットアップチェックスクリプト
プロジェクトが正しくセットアップされているか確認する
"""
import os
import sys

def check_python_version():
    """Pythonバージョンをチェック"""
    print("🔍 Pythonバージョン確認...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ✗ Python 3.8以上が必要です（現在: {version.major}.{version.minor}.{version.micro}）")
        return False

def check_dependencies():
    """依存ライブラリをチェック"""
    print("\n🔍 依存ライブラリ確認...")
    modules = [
        'watchdog',
        'dotenv',
        'requests',
        'bs4',
        'lxml',
        'evernote'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✓ {module}")
        except ImportError:
            print(f"   ✗ {module} がインストールされていません")
            all_ok = False
    
    if not all_ok:
        print("\n   pip install -r requirements.txt を実行してください")
    
    return all_ok

def check_env_file():
    """環境変数ファイルをチェック"""
    print("\n🔍 環境設定ファイル確認...")
    
    if not os.path.exists('.env'):
        print("   ✗ .env ファイルが見つかりません")
        print("   .env.example を .env にコピーして設定してください")
        return False
    
    print("   ✓ .env ファイルが存在します")
    
    # .envファイルの内容をチェック
    from dotenv import load_dotenv
    load_dotenv()
    
    issues = []
    
    # OAuth認証のチェック
    consumer_key = os.getenv('EVERNOTE_CONSUMER_KEY', '')
    consumer_secret = os.getenv('EVERNOTE_CONSUMER_SECRET', '')
    
    # APIトークンのチェック
    token = os.getenv('EVERNOTE_API_TOKEN', '')
    
    # いずれかの認証方法が設定されているか確認
    has_oauth = (consumer_key and consumer_key != 'your_consumer_key_here' and
                 consumer_secret and consumer_secret != 'your_consumer_secret_here')
    has_token = (token and token != 'your_evernote_api_token_here')
    
    if has_oauth:
        print("   ✓ OAuth認証情報が設定されています")
    elif has_token:
        print("   ✓ Developer Tokenが設定されています")
    else:
        issues.append("Evernote認証情報が設定されていません（EVERNOTE_CONSUMER_KEY + EVERNOTE_CONSUMER_SECRET または EVERNOTE_API_TOKEN）")
    
    # ChatGPTパスのチェック
    path = os.getenv('CHATGPT_DATA_PATH', '')
    if not path or 'YourName' in path:
        issues.append("CHATGPT_DATA_PATH が正しく設定されていません")
    else:
        if os.path.exists(path):
            print(f"   ✓ CHATGPT_DATA_PATH が設定されています: {path}")
        else:
            issues.append(f"CHATGPT_DATA_PATH のフォルダが存在しません: {path}")
    
    if issues:
        print("\n   ⚠️  以下の項目を .env ファイルで設定してください:")
        for issue in issues:
            print(f"      - {issue}")
        return False
    
    return True

def check_files():
    """必要なファイルが存在するかチェック"""
    print("\n🔍 プロジェクトファイル確認...")
    
    required_files = [
        'main.py',
        'config.py',
        'file_monitor.py',
        'evernote_sync.py',
        'duplicate_manager.py',
        'requirements.txt',
        '.gitignore',
        'README.md'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} が見つかりません")
            all_ok = False
    
    return all_ok

def main():
    """メイン処理"""
    print("=" * 60)
    print("ChatGPT → Evernote セットアップチェック")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_files(),
        check_env_file()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ すべてのチェックが完了しました！")
        print("\n次のコマンドでスクリプトを実行できます:")
        print("  python main.py")
        print("または")
        print("  .\\start_sync.bat")
    else:
        print("⚠️  いくつかの問題が見つかりました")
        print("上記のメッセージを確認して、必要な修正を行ってください")
        print("\n詳細は SETUP.md を参照してください")
    print("=" * 60)

if __name__ == "__main__":
    main()

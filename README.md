# ChatGPT → Evernote 自動同期スクリプト

ChatGPT Windowsデスクトップアプリの会話ログを自動的にEvernoteに保存するPythonスクリプトです。

## 概要

このスクリプトは以下の機能を提供します：

- **自動監視**: ChatGPTアプリのキャッシュフォルダを常時監視
- **自動同期**: 新規会話や更新を検知し、Evernoteに自動保存
- **重複防止**: 同じ会話を何度も保存しないよう管理
- **柔軟な設定**: 環境変数で簡単にカスタマイズ可能
- **バックグラウンド実行**: 常駐プロセスとして動作

## システム要件

- **OS**: Windows 11 / 10
- **Python**: 3.8以上
- **ChatGPT**: 公式Windowsデスクトップアプリ
- **Evernote**: 有料プラン（APIアクセス可能なアカウント）

## インストール

### 1. リポジトリのクローン

```powershell
git clone https://github.com/ozaki-taisuke/chatgpt-to-evernote
cd chatgpt-to-evernote
```

### 2. 仮想環境の作成（推奨）

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. 依存ライブラリのインストール

```powershell
pip install -r requirements.txt
```

### 4. Python 3.11互換性パッチの適用（Python 3.11以降の場合）

Python 3.11以降を使用している場合、evernote3ライブラリに互換性問題があります。以下のパッチを実行してください：

```powershell
python patch_evernote.py
```

このスクリプトは自動的にevernote3ライブラリを修正し、バックアップを作成します。

## 初期設定

> ⚠️ **Python 3.11以降のユーザーへ**: 初期設定の前に上記の「Python 3.11互換性パッチの適用」を実行してください。

### 1. Evernote API認証情報の取得

**方法A: OAuth認証（推奨）**

Evernote Developer Supportから提供された認証情報を使用：

1. メールで届いた1Passwordリンクにアクセス
2. **Username**（Consumer Key）をコピー
3. **Password**（Consumer Secret）をコピー

**方法B: Developer Token（代替）**

1. [Evernote Developer Portal](https://dev.evernote.com/) にアクセス
2. アカウントでログイン
3. 新しいAPIキーを作成
4. **Developer Token**をコピー

### 2. ChatGPTデータフォルダの確認

ChatGPTデスクトップアプリのキャッシュフォルダを探します。**インストール方法により異なります**：

**一般的なインストール（公式サイトからダウンロード）:**
```
C:\Users\<ユーザー名>\AppData\Roaming\ChatGPT
```

**Microsoft Store版:**
```
C:\Users\<ユーザー名>\AppData\Local\Packages\OpenAI.ChatGPT-Desktop_<ID>\LocalCache\Roaming\ChatGPT
```

**確認方法:**

**方法1: PowerShellで検索（推奨）**
```powershell
# Store版のパスを確認
Get-AppxPackage | Where-Object {$_.Name -like "*ChatGPT*"} | Select-Object InstallLocation, PackageFamilyName

# 実際のデータフォルダを探す
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "*ChatGPT*" -Directory
```

**方法2: 手動で探す**
1. `Win + R` → `%localappdata%\Packages` と入力
2. `OpenAI.ChatGPT-Desktop_` で始まるフォルダを探す
3. その中の `LocalCache\Roaming\ChatGPT` を確認

### 3. 環境変数ファイルの作成

`.env.example` を `.env` にコピーし、実際の値を設定します：

```powershell
Copy-Item .env.example .env
```

`.env` ファイルを編集：

**OAuth認証を使用する場合（推奨）:**

```ini
# Evernote API設定（OAuth認証）
EVERNOTE_CONSUMER_KEY=your_consumer_key_from_1password
EVERNOTE_CONSUMER_SECRET=your_consumer_secret_from_1password
EVERNOTE_NOTEBOOK_NAME=ChatGPT Logs
EVERNOTE_ENVIRONMENT=production

# ChatGPTデータフォルダ
CHATGPT_DATA_PATH=C:\Users\YourName\AppData\Roaming\ChatGPT

# 監視対象の拡張子
WATCH_EXTENSIONS=.html,.json,.txt

# その他の設定
LOG_LEVEL=INFO
LOG_FILE=chatgpt_evernote_sync.log
DUPLICATE_DB_PATH=./sync_history.db
```

**Developer Tokenを使用する場合（代替）:**

```ini
# Evernote API設定（Developer Token）
EVERNOTE_API_TOKEN=your_developer_token_here
EVERNOTE_NOTEBOOK_NAME=ChatGPT Logs
EVERNOTE_ENVIRONMENT=production

# ChatGPTデータフォルダ
# 一般的なインストール版の場合:
CHATGPT_DATA_PATH=C:\Users\YourName\AppData\Roaming\ChatGPT
# Microsoft Store版の場合（IDは環境により異なる）:
# CHATGPT_DATA_PATH=C:\Users\YourName\AppData\Local\Packages\OpenAI.ChatGPT-Desktop_2p2nqsd0c76g0\LocalCache\Roaming\ChatGPT

# 監視対象の拡張子（注意: .ldb/.logはバイナリ形式のため除外）
WATCH_EXTENSIONS=.html,.json,.txt

# その他の設定
LOG_LEVEL=INFO
LOG_FILE=chatgpt_evernote_sync.log
DUPLICATE_DB_PATH=./sync_history.db
```

> ⚠️ **重要**: `.env` ファイルは個人情報を含むため、絶対にGitにコミットしないでください（`.gitignore`で除外済み）

### 4. セットアップの確認

設定が正しく完了しているか確認します：

```powershell
python check_setup.py
```

すべてのチェック項目が ✓ になれば準備完了です。

## 使い方

### OAuth認証の初回セットアップ

OAuth認証（Consumer Key/Secret）を使用する場合、初回起動時にブラウザで認証を行います。

**方法1: メインスクリプトから認証（標準）**

1. スクリプトを起動：
```powershell
python main.py
```

2. 自動的にブラウザが開きます（開かない場合は表示されたURLを手動でコピー）

3. Evernoteにログインし、アプリケーションを認証

4. 認証後、ブラウザのURL欄を確認して `oauth_verifier=` の後の値をコピー
   - 例: `http://localhost/?oauth_token=xxx&oauth_verifier=ABCD1234`
   - この場合、`ABCD1234` がVerification Code

5. ターミナルに戻り、Verification Codeを貼り付けて Enter

6. 認証が完了すると、トークンが `.evernote_oauth_token` に保存されます

**方法2: 専用ヘルパースクリプトで認証（推奨・localhost問題がある場合）**

localhost リダイレクトで画面が表示されない場合は、こちらを使用：

```powershell
python oauth_helper.py
```

このスクリプトは対話的に認証を進め、同じトークンファイルを作成します。次回以降は自動的にこのトークンが使用されます。

### 基本的な起動

**方法1: Pythonコマンドで起動**
```powershell
python main.py
```

**方法2: バッチファイルで起動（推奨）**
```powershell
.\start_sync.bat
```

または、`start_sync.bat` をダブルクリック

スクリプトが起動すると：

1. ChatGPTフォルダの監視を開始
2. 新しいファイルや更新を自動検知
3. Evernoteにノートを自動作成
4. コンソールとログファイルに処理状況を記録

### 停止方法

```
Ctrl + C
```

## 自動起動設定（オプション）

### 方法1: Windowsタスクスケジューラ

1. タスクスケジューラを開く（`Win + R` → `taskschd.msc`）
2. 「基本タスクの作成」を選択
3. 以下のように設定：
   - **トリガー**: コンピューターの起動時
   - **操作**: プログラムの開始
   - **プログラム**: `C:\path\to\venv\Scripts\python.exe`
   - **引数**: `C:\path\to\chatgpt-to-evernote\main.py`
   - **開始**: `C:\path\to\chatgpt-to-evernote`

### 方法2: スタートアップフォルダ

1. `start_sync.bat` を右クリック → **ショートカットを作成**
2. `Win + R` → `shell:startup` と入力してスタートアップフォルダを開く
3. 作成したショートカットをスタートアップフォルダにコピー

これでWindows起動時に自動的にスクリプトが開始されます。

## プロジェクト構造

```
chatgpt-to-evernote/
├── .github/
│   └── copilot-instructions.md # プロジェクト情報
├── main.py                 # メインスクリプト
├── config.py              # 設定読み込み
├── file_monitor.py        # ファイル監視
├── evernote_sync.py       # Evernote連携
├── duplicate_manager.py   # 重複防止
├── oauth_helper.py        # OAuth認証ヘルパー
├── patch_evernote.py      # Python 3.11互換性パッチ
├── requirements.txt       # 依存ライブラリ
├── .env.example          # 設定ファイルサンプル
├── .env                  # 実際の設定ファイル（要作成）
├── .gitignore            # Git除外設定
├── start_sync.bat        # Windows起動用バッチファイル
├── check_setup.py        # セットアップチェックスクリプト
├── SETUP.md              # セットアップガイド
├── QUICKSTART_OAUTH.md   # OAuth認証クイックスタート
├── PROGRESS.md           # 開発進捗記録
└── README.md             # このファイル
```

## トラブルシューティング

### 問題: "Evernote認証情報が設定されていません"

**解決策**: `.env` ファイルに以下のいずれかを設定してください：
- OAuth認証: `EVERNOTE_CONSUMER_KEY` と `EVERNOTE_CONSUMER_SECRET`
- Developer Token: `EVERNOTE_API_TOKEN`

### 問題: Python 3.11で "AttributeError: module 'inspect' has no attribute 'getargspec'"

**原因**: evernote3ライブラリがPython 3.11以降に対応していない

**解決策**:
```powershell
python patch_evernote.py
```
このパッチを実行すると自動的に修正されます。バックアップも自動作成されます。

### 問題: OAuth認証で "Verification Code" が表示されない / localhost画面が真っ白

**原因**: localhostへのリダイレクト時に認証コードを表示するページがない

**解決策**:
1. ブラウザのURL欄を確認：`http://localhost/?oauth_token=xxx&oauth_verifier=ABCD1234`
2. `oauth_verifier=` の後ろの値（例: `ABCD1234`）をコピー
3. ターミナルに貼り付け

**または、専用ヘルパーを使用:**
```powershell
python oauth_helper.py
```
このスクリプトが対話的に認証を進めてくれます。

### 問題: "保存済みトークンが使用できません"

**解決策**:
1. `.evernote_oauth_token` ファイルを削除
2. スクリプトを再起動して再度OAuth認証を実行

### 問題: "ChatGPTデータフォルダが見つかりません"

**原因**: Microsoft Store版は特殊なパス構造を使用している

**解決策**: 
1. **Store版かどうかを確認:**
```powershell
Get-AppxPackage | Where-Object {$_.Name -like "*ChatGPT*"}
```

2. **Store版の場合、正しいパスを探す:**
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "*ChatGPT*" -Directory
```
表示されたフォルダ内の `LocalCache\Roaming\ChatGPT` を `.env` に設定

3. **一般インストール版の場合:**
```
C:\Users\<ユーザー名>\AppData\Roaming\ChatGPT
```

4. エクスプローラーで隠しフォルダを表示する設定にする

### 問題: "Evernote接続テスト失敗"

**解決策**:
1. 認証情報が正しいか確認（OAuth: Consumer Key/Secret、または Developer Token）
2. インターネット接続を確認
3. `EVERNOTE_ENVIRONMENT` が `production` か `sandbox` のいずれかになっているか確認

### 問題: ファイルが検知されない

**解決策**:
1. `WATCH_EXTENSIONS` に正しい拡張子が設定されているか確認
2. ChatGPTアプリが実際にファイルを作成しているか確認（エクスプローラーで監視）
3. ログファイルを確認し、デバッグ情報を確認

### 問題: "An invalid XML character (Unicode: 0x1) was found" エラー

**原因**: LevelDB形式（`.ldb` / `.log`）のバイナリファイルはENML変換できない

**現状**: ChatGPTの会話データはLevelDB形式で保存されており、直接読み取れません

**対応状況**:
- 現在、`.ldb` と `.log` ファイルは監視対象から除外されています
- 将来的に `plyvel` ライブラリを使用したLevelDB解析機能を追加予定

**回避策**:
- ChatGPTアプリから会話をエクスポート（Share → Copy機能など）
- エクスポートしたテキストを監視対象の拡張子（`.txt`など）で保存

## 開発・カスタマイズ

### ログレベルの変更

`.env` ファイルで `LOG_LEVEL` を変更：

```ini
LOG_LEVEL=DEBUG  # より詳細なログ
```

### ChatGPTファイル形式のカスタマイズ

`file_monitor.py` の `extract_text_from_file()` 関数を編集して、実際のChatGPTファイル形式に合わせてテキスト抽出ロジックをカスタマイズできます。

### 同期履歴のリセット

```powershell
python -c "from duplicate_manager import DuplicateManager; DuplicateManager('./sync_history.db').clear_history()"
```

## セキュリティとプライバシー

- **APIトークン**: `.env` ファイルに保存され、`.gitignore` で除外されています
- **会話ログ**: ローカルに保存されるログファイルには会話内容が含まれる可能性があります
- **Git管理**: 個人情報を含むファイルは絶対にコミットしないでください

## TODO / 改善予定

- [ ] ChatGPTファイル形式の詳細な解析と最適化
- [ ] HTML→ENML変換の改善
- [ ] リトライ機能の強化
- [ ] GUI版の作成
- [ ] macOS/Linux対応

## ライセンス

MIT License

## 作者

Ozaki Taisuke
- [ozkk.jp](https://ozkk.jp/)
- [@ozata92](https://x.com/ozata92)

## 貢献

プルリクエストや Issue は歓迎します！

## 参考リンク

- [Evernote API Documentation](https://dev.evernote.com/doc/)
- [Watchdog Documentation](https://python-watchdog.readthedocs.io/)
- [Python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

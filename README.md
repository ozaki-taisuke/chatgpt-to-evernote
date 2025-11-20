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

## 初期設定

### 1. Evernote APIトークンの取得

1. [Evernote Developer Portal](https://dev.evernote.com/) にアクセス
2. アカウントでログイン
3. 新しいAPIキーを作成
4. **Developer Token**（APIトークン）をコピー

### 2. ChatGPTデータフォルダの確認

ChatGPTデスクトップアプリのキャッシュフォルダを探します：

```
C:\Users\<ユーザー名>\AppData\Roaming\ChatGPT
```

または、以下の方法で探すことができます：

1. ChatGPTアプリを開く
2. `Win + R` → `%appdata%` と入力
3. `ChatGPT` フォルダを探す

### 3. 環境変数ファイルの作成

`.env.example` を `.env` にコピーし、実際の値を設定します：

```powershell
Copy-Item .env.example .env
```

`.env` ファイルを編集：

```ini
# Evernote API設定
EVERNOTE_API_TOKEN=your_actual_token_here
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

> ⚠️ **重要**: `.env` ファイルは個人情報を含むため、絶対にGitにコミットしないでください（`.gitignore`で除外済み）

## 使い方

### 基本的な起動

```powershell
python main.py
```

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

バッチファイル `start_sync.bat` を作成：

```batch
@echo off
cd /d "C:\path\to\chatgpt-to-evernote"
call venv\Scripts\activate
python main.py
```

このファイルをスタートアップフォルダに配置：

```
C:\Users\<ユーザー名>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

## プロジェクト構造

```
chatgpt-to-evernote/
├── main.py                 # メインスクリプト
├── config.py              # 設定読み込み
├── file_monitor.py        # ファイル監視
├── evernote_sync.py       # Evernote連携
├── duplicate_manager.py   # 重複防止
├── requirements.txt       # 依存ライブラリ
├── .env.example          # 設定ファイルサンプル
├── .env                  # 実際の設定ファイル（要作成）
├── .gitignore            # Git除外設定
└── README.md             # このファイル
```

## トラブルシューティング

### 問題: "EVERNOTE_API_TOKEN が設定されていません"

**解決策**: `.env` ファイルに正しいAPIトークンを設定してください。

### 問題: "ChatGPTデータフォルダが見つかりません"

**解決策**: 
1. ChatGPTアプリが正しくインストールされているか確認
2. `.env` ファイルの `CHATGPT_DATA_PATH` を実際のパスに変更
3. エクスプローラーで隠しフォルダを表示する設定にする

### 問題: "Evernote接続テスト失敗"

**解決策**:
1. APIトークンが正しいか確認
2. インターネット接続を確認
3. `EVERNOTE_ENVIRONMENT` が `production` か `sandbox` のいずれかになっているか確認

### 問題: ファイルが検知されない

**解決策**:
1. `WATCH_EXTENSIONS` に正しい拡張子が設定されているか確認
2. ChatGPTアプリが実際にファイルを作成しているか確認（エクスプローラーで監視）
3. ログファイルを確認し、デバッグ情報を確認

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

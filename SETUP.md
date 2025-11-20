# プロジェクトセットアップガイド

## ✅ 完了した作業

### 1. プロジェクト構造の作成
以下のファイルが作成されました：

```
chatgpt-to-evernote/
├── .github/
│   └── copilot-instructions.md  # プロジェクト情報
├── main.py                      # メインスクリプト
├── config.py                    # 設定管理
├── file_monitor.py              # ファイル監視
├── evernote_sync.py             # Evernote連携
├── duplicate_manager.py         # 重複防止
├── requirements.txt             # 依存ライブラリ
├── .env.example                 # 設定サンプル
├── .env                         # 実際の設定ファイル（要編集）
├── .gitignore                   # Git除外設定
├── start_sync.bat               # Windows起動用バッチファイル
└── README.md                    # 詳細ドキュメント
```

### 2. 依存ライブラリのインストール
✅ すべてのライブラリがインストール済み：
- watchdog (ファイル監視)
- python-dotenv (環境変数管理)
- requests (HTTP通信)
- beautifulsoup4 (HTML解析)
- lxml (XML/HTML解析)
- evernote3 (Evernote SDK)
- oauth2 (OAuth認証)

### 3. Python 3.11互換性パッチ（Python 3.11以降のみ）
✅ Python 3.11以降を使用している場合、`patch_evernote.py` を実行してevernote3ライブラリを修正する必要があります。

**確認方法:**
```powershell
python --version
```

**Python 3.11以降の場合、パッチを適用:**
```powershell
python patch_evernote.py
```

このスクリプトは自動的に：
- evernote3ライブラリの問題箇所を修正（`inspect.getargspec` → `inspect.getfullargspec`）
- 元のファイルのバックアップを作成
- 適用結果を表示

### 4. 設定ファイルの準備
✅ `.env` ファイルが作成されました（要編集）

---

## 🔧 次に必要な作業

### ステップ1: Evernote認証情報の取得

**方法A: OAuth認証（推奨）**

Evernote Developer Supportから提供された認証情報を使用：

1. メールで届いた1Passwordリンクにアクセス
2. メールアドレスで認証
3. **Username欄の値** = Consumer Key をコピー
4. **Password欄の値** = Consumer Secret をコピー

**方法B: Developer Token（代替）**

1. [Evernote Developer Portal](https://dev.evernote.com/) にアクセス
2. アカウントでログイン
3. 新しいAPIキーを作成
4. **Developer Token** をコピー

### ステップ2: ChatGPTデータフォルダの確認

以下のいずれかの方法で確認：

**方法1: PowerShellで確認（推奨・Store版対応）**

**Store版かどうかを確認:**
```powershell
Get-AppxPackage | Where-Object {$_.Name -like "*ChatGPT*"}
```

**Store版の場合、データフォルダを探す:**
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "*ChatGPT*" -Directory
```
表示されたフォルダ内の `LocalCache\Roaming\ChatGPT` が実際のパスです。

例：
```
C:\Users\ozata\AppData\Local\Packages\OpenAI.ChatGPT-Desktop_2p2nqsd0c76g0\LocalCache\Roaming\ChatGPT
```

**方法2: エクスプローラーから（一般インストール版）**
```
Win + R → %appdata% と入力 → ChatGPT フォルダを探す
```

一般的なパス：
```
C:\Users\<ユーザー名>\AppData\Roaming\ChatGPT
```

**方法3: エクスプローラーから（Store版）**
```
Win + R → %localappdata%\Packages と入力
→ OpenAI.ChatGPT-Desktop_ で始まるフォルダを探す
→ LocalCache\Roaming\ChatGPT を確認
```

### ステップ3: .envファイルの編集

エディタで `.env` ファイルを開き、以下を設定：

**OAuth認証を使用する場合（推奨）:**

```ini
# 取得したConsumer KeyとSecretを設定
EVERNOTE_CONSUMER_KEY=your_actual_consumer_key
EVERNOTE_CONSUMER_SECRET=your_actual_consumer_secret

# 確認したChatGPTのパスを設定
# 一般インストール版の例:
CHATGPT_DATA_PATH=C:\Users\<あなたのユーザー名>\AppData\Roaming\ChatGPT
# Microsoft Store版の例（IDは環境により異なります）:
# CHATGPT_DATA_PATH=C:\Users\<あなたのユーザー名>\AppData\Local\Packages\OpenAI.ChatGPT-Desktop_2p2nqsd0c76g0\LocalCache\Roaming\ChatGPT

# その他はデフォルトでOK（必要に応じて変更）
EVERNOTE_NOTEBOOK_NAME=ChatGPT Logs
EVERNOTE_ENVIRONMENT=production
WATCH_EXTENSIONS=.html,.json,.txt  # 注意: .ldb/.logはバイナリのため除外
LOG_LEVEL=INFO
```

**Developer Tokenを使用する場合（代替）:**

```ini
# 取得したAPIトークンを設定
EVERNOTE_API_TOKEN=S=s1:U=xxxxx:E=xxxxx...

# 確認したChatGPTのパスを設定
CHATGPT_DATA_PATH=C:\Users\<あなたのユーザー名>\AppData\Roaming\ChatGPT

# その他はデフォルトでOK（必要に応じて変更）
EVERNOTE_NOTEBOOK_NAME=ChatGPT Logs
EVERNOTE_ENVIRONMENT=production
WATCH_EXTENSIONS=.html,.json,.txt
LOG_LEVEL=INFO
```

### ステップ4: スクリプトの実行

**方法1: 直接実行**
```powershell
python main.py
```

**OAuth認証の場合:** 初回起動時にブラウザでEvernote認証が必要です：
1. 自動的にブラウザが開く
2. Evernoteにログインして認証
3. 認証後、ブラウザのURL欄を確認：`http://localhost/?oauth_token=xxx&oauth_verifier=ABCD1234`
4. `oauth_verifier=` の後の値（例: `ABCD1234`）をコピー
5. ターミナルに貼り付けて Enter
6. 認証完了後、`.evernote_oauth_token` に保存されます
7. 次回以降は自動的にトークンが使用されます

**localhost画面が真っ白な場合:**

専用ヘルパースクリプトを使用：
```powershell
python oauth_helper.py
```
このスクリプトが対話的に認証を進めてくれます。

**方法2: バッチファイル使用**
```powershell
.\start_sync.bat
```

**停止方法:**
```
Ctrl + C
```

---

## 📋 動作確認チェックリスト

- [ ] Python 3.8以上がインストールされている
- [ ] すべての依存ライブラリがインストールされている
- [ ] `.env` ファイルが作成されている
- [ ] Evernote APIトークンを取得した
- [ ] `.env` に実際のAPIトークンを設定した
- [ ] ChatGPTデータフォルダのパスを確認した
- [ ] `.env` に正しいパスを設定した
- [ ] スクリプトが起動することを確認した

---

## 🐛 トラブルシューティング

### エラー: "Evernote認証情報が設定されていません"

**原因:** `.env` ファイルに認証情報が設定されていない

**解決策:**
1. `.env` ファイルを開く
2. OAuth使用時: `EVERNOTE_CONSUMER_KEY` と `EVERNOTE_CONSUMER_SECRET` を実際の値に変更
3. Developer Token使用時: `EVERNOTE_API_TOKEN` を実際のトークンに変更
4. ファイルを保存

### エラー: Python 3.11で "AttributeError: module 'inspect' has no attribute 'getargspec'"

**原因:** evernote3ライブラリがPython 3.11以降に対応していない

**解決策:**
```powershell
python patch_evernote.py
```
このパッチを実行すると、evernote3ライブラリが自動的に修正されます。

---

### エラー: OAuth認証で "Verification Code" の入力を求められる

**原因:** 初回起動時の正常な動作です

**解決策:**
1. ブラウザで表示されるEvernote認証ページにログイン
2. アプリケーションを認証
3. 表示される英数字のコード（Verification Code）をコピー
4. ターミナルに貼り付けて Enter を押す

### エラー: "ChatGPTデータフォルダが見つかりません"

**原因:** 指定されたパスが存在しない、またはMicrosoft Store版を使用している

**解決策:**

**Store版かどうかを確認:**
```powershell
Get-AppxPackage | Where-Object {$_.Name -like "*ChatGPT*"}
```

**Store版の場合、正しいパスを探す:**
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "*ChatGPT*" -Directory
```
表示されたフォルダ内の `LocalCache\Roaming\ChatGPT` を `.env` に設定

**一般版の場合:**
1. ChatGPTアプリがインストールされているか確認
2. エクスプローラーで隠しフォルダを表示する設定にする
3. `%appdata%\ChatGPT` が存在するか確認

### エラー: "Evernote接続テスト失敗"

**原因:** APIトークンが無効または環境設定が間違っている

**解決策:**
1. APIトークンをコピー&ペーストし直す
2. `EVERNOTE_ENVIRONMENT` が `production` になっているか確認
3. インターネット接続を確認

---

## 🚀 自動起動の設定（オプション）

### Windowsスタートアップに追加

1. `start_sync.bat` を右クリック → ショートカットを作成
2. `Win + R` → `shell:startup` と入力
3. 作成したショートカットをスタートアップフォルダに移動

これでWindows起動時に自動的にスクリプトが開始されます。

---

## 📝 ログとデータファイル

スクリプト実行後、以下のファイルが作成されます：

- `chatgpt_evernote_sync.log` - 処理ログ
- `sync_history.db` - 同期履歴データベース

これらのファイルは `.gitignore` で除外されているため、Gitにコミットされません。

---

## 💡 使い方のヒント

1. **初回実行時**: まずは短時間実行して動作を確認
2. **ログ確認**: `chatgpt_evernote_sync.log` でエラーや警告を確認
3. **Evernote確認**: 指定したノートブックにノートが作成されているか確認
4. **ChatGPTファイル形式**: 実際のファイル構造に合わせて `file_monitor.py` をカスタマイズ

---

## 📚 詳細情報

詳しい使い方やカスタマイズについては `README.md` を参照してください。

---

**作成日:** 2025年11月20日
**Python:** 3.11.9
**環境:** Windows 11

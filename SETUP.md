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

### 3. 設定ファイルの準備
✅ `.env` ファイルが作成されました（要編集）

---

## 🔧 次に必要な作業

### ステップ1: Evernote APIトークンの取得

1. [Evernote Developer Portal](https://dev.evernote.com/) にアクセス
2. アカウントでログイン
3. 新しいAPIキーを作成
4. **Developer Token** をコピー

### ステップ2: ChatGPTデータフォルダの確認

以下のいずれかの方法で確認：

**方法1: エクスプローラーから**
```
Win + R → %appdata% と入力 → ChatGPT フォルダを探す
```

**方法2: PowerShellで確認**
```powershell
Test-Path "$env:APPDATA\ChatGPT"
```

一般的なパス：
```
C:\Users\<ユーザー名>\AppData\Roaming\ChatGPT
```

### ステップ3: .envファイルの編集

エディタで `.env` ファイルを開き、以下を設定：

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

### エラー: "EVERNOTE_API_TOKEN が設定されていません"

**原因:** `.env` ファイルにAPIトークンが設定されていない

**解決策:**
1. `.env` ファイルを開く
2. `EVERNOTE_API_TOKEN=your_evernote_api_token_here` を実際のトークンに変更
3. ファイルを保存

### エラー: "ChatGPTデータフォルダが見つかりません"

**原因:** 指定されたパスが存在しない

**解決策:**
1. ChatGPTアプリがインストールされているか確認
2. エクスプローラーで隠しフォルダを表示する設定にする
3. 実際のパスを確認して `.env` に設定

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

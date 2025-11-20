# クイックスタートガイド - OAuth認証

このガイドでは、Evernote Developer Supportから提供されたOAuth認証情報（Consumer KeyとConsumer Secret）を使用したセットアップ方法を説明します。

## 📝 準備するもの

- Evernote Developer Supportから届いたメールの1Passwordリンク
- Consumer Key（Usernameフィールドに記載）
- Consumer Secret（Passwordフィールドに記載）

## 🚀 セットアップ手順（5分）

### 1. 認証情報の確認

メールで届いた1Passwordリンクにアクセスして、以下を確認：
- **Username欄** → これが `EVERNOTE_CONSUMER_KEY`
- **Password欄** → これが `EVERNOTE_CONSUMER_SECRET`

### 2. .envファイルの編集

プロジェクトフォルダの `.env` ファイルを開き、以下を設定：

```ini
# 1Passwordから取得した値を設定
EVERNOTE_CONSUMER_KEY=（Username欄の値をここにペースト）
EVERNOTE_CONSUMER_SECRET=（Password欄の値をここにペースト）

# ChatGPTのデータフォルダパスを設定
# 一般インストール版の場合:
CHATGPT_DATA_PATH=C:\Users\（あなたのユーザー名）\AppData\Roaming\ChatGPT
# Microsoft Store版の場合（IDは環境により異なります）:
# CHATGPT_DATA_PATH=C:\Users\（あなたのユーザー名）\AppData\Local\Packages\OpenAI.ChatGPT-Desktop_xxx\LocalCache\Roaming\ChatGPT

# 以下はそのままでOK
EVERNOTE_NOTEBOOK_NAME=ChatGPT Logs
EVERNOTE_ENVIRONMENT=production
```

保存して閉じる。

**Store版の場合の正確なパスの確認方法:**
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "*ChatGPT*" -Directory
```

### 3. セットアップ確認

PowerShellで以下を実行：

```powershell
python check_setup.py
```

すべて ✓ になっていることを確認。

**Python 3.11以降を使用している場合:**

互換性パッチを適用：
```powershell
python patch_evernote.py
```

### 4. 初回起動（OAuth認証）

```powershell
python main.py
```

**初回のみ、以下の手順が必要です：**

1. 自動的にブラウザが開く（開かない場合は表示されたURLを手動でコピー）
2. Evernoteにログイン
3. アプリケーションに対するアクセスを「許可」
4. 認証後、**ブラウザのURL欄**を確認：
   ```
   http://localhost/?oauth_token=xxx&oauth_verifier=ABCD1234
   ```
5. `oauth_verifier=` の後の値（例: `ABCD1234`）をコピー
6. PowerShellのウィンドウに戻る
7. "Verification codeを入力してください:" というプロンプトにコードをペースト
8. Enterを押す

**localhostページが真っ白で何も表示されない場合:**

別の方法として、専用ヘルパースクリプトを使用：
```powershell
python oauth_helper.py
```
このスクリプトが対話的に認証を進め、同じトークンファイルを作成します。

**認証完了！**

次回以降は自動的にログインされます（トークンは `.evernote_oauth_token` に保存されます）。

### 5. 動作確認

スクリプトが起動したら：

- ログに "Evernote接続成功" と表示されることを確認
- ChatGPTアプリでテスト会話を作成
- Evernoteにノートが自動作成されることを確認

### 6. 停止

```
Ctrl + C
```

## 🎯 次回以降の起動

認証は初回のみなので、次回からは：

```powershell
python main.py
```

または

```powershell
.\start_sync.bat
```

だけでOKです！

## ❓ よくある質問

**Q: Verification Codeはどこに表示される？**
A: Evernote認証ページで「許可」をクリックした後、**ブラウザのURL欄**に表示されます。
```
http://localhost/?oauth_token=xxx&oauth_verifier=ABCD1234
```
この例では `ABCD1234` がVerification Codeです。

**Q: localhostページが真っ白で何も表示されない**
A: 正常です。URL欄の `oauth_verifier=` の後の値をコピーするか、`python oauth_helper.py` を使用してください。

**Q: Python 3.11で動かない**
A: `python patch_evernote.py` を実行して互換性パッチを適用してください。

**Q: ChatGPTフォルダが見つからない（Microsoft Store版）**
A: 以下のコマンドで探してください：
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "*ChatGPT*" -Directory
```
表示されたフォルダ内の `LocalCache\Roaming\ChatGPT` が正しいパスです。

**Q: 認証に失敗した場合は？**
A: `.evernote_oauth_token` ファイルを削除して、再度 `python main.py` を実行してください。

**Q: Developer Tokenは使えないの？**
A: 使えます。`.env` で `EVERNOTE_CONSUMER_KEY` と `EVERNOTE_CONSUMER_SECRET` の代わりに `EVERNOTE_API_TOKEN` を設定してください。

**Q: 自動起動したい**
A: `start_sync.bat` のショートカットをWindowsスタートアップフォルダに配置してください（詳細はREADME.md参照）。

## 📚 詳細情報

- 完全なドキュメント: `README.md`
- 詳細なセットアップ: `SETUP.md`
- トラブルシューティング: `README.md` の該当セクション

---

**作成日:** 2025年11月20日

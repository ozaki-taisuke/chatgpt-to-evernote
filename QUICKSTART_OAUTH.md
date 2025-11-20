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
CHATGPT_DATA_PATH=C:\Users\（あなたのユーザー名）\AppData\Roaming\ChatGPT

# 以下はそのままでOK
EVERNOTE_NOTEBOOK_NAME=ChatGPT Logs
EVERNOTE_ENVIRONMENT=production
```

保存して閉じる。

### 3. セットアップ確認

PowerShellで以下を実行：

```powershell
python check_setup.py
```

すべて ✓ になっていることを確認。

### 4. 初回起動（OAuth認証）

```powershell
python main.py
```

**初回のみ、以下の手順が必要です：**

1. 自動的にブラウザが開く（開かない場合は表示されたURLを手動でコピー）
2. Evernoteにログイン
3. アプリケーションに対するアクセスを「許可」
4. 画面に表示される **Verification Code**（英数字）をコピー
5. PowerShellのウィンドウに戻る
6. "Verification codeを入力してください:" というプロンプトにコードをペースト
7. Enterを押す

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
A: Evernote認証ページで「許可」をクリックした後、画面に表示される英数字のコードです。

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

# ChatGPT to Evernote 自動同期スクリプト - プロジェクトセットアップ

## プロジェクト概要
ChatGPT Windowsデスクトップアプリの会話ログを自動的にEvernoteに保存するPythonスクリプト

## セットアップ進捗

- [x] copilot-instructions.mdファイルを作成
- [x] プロジェクト要件の確認
- [x] プロジェクト構造の作成
- [x] requirements.txtの作成
- [x] メインスクリプトの実装
- [x] README.mdの作成

## 開発ガイドライン

### セキュリティ
- APIキーやトークンは環境変数または.envファイルで管理
- .envファイルは.gitignoreに追加済み
- 会話ログなどの個人情報は絶対にコミットしない

### コーディング規約
- Python 3.x使用
- 型ヒントを活用
- エラーハンドリングを適切に実装
- ログ出力で動作を追跡可能に

### プロジェクト構造
```
chatgpt-to-evernote/
├── main.py                 # メインスクリプト
├── config.py              # 設定読み込み
├── file_monitor.py        # ファイル監視
├── evernote_sync.py       # Evernote連携
├── duplicate_manager.py   # 重複防止
├── requirements.txt       # 依存ライブラリ
├── .env.example          # 設定ファイルサンプル
└── README.md             # ドキュメント
```

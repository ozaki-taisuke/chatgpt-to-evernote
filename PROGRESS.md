# プロジェクト進捗レポート

**日付:** 2025年11月20日  
**プロジェクト:** ChatGPT → Evernote 自動同期スクリプト

---

## ✅ 完了した作業

### 1. プロジェクト基盤の構築
- [x] プロジェクト構造の作成
- [x] 必要なPythonモジュール実装
  - `main.py` - メインスクリプト
  - `config.py` - 環境変数管理
  - `file_monitor.py` - ファイル監視（watchdog使用）
  - `evernote_sync.py` - Evernote API連携
  - `duplicate_manager.py` - SQLiteベース重複防止
- [x] `.gitignore` による個人情報保護
- [x] `requirements.txt` による依存関係管理

### 2. Evernote OAuth認証の実装
- [x] OAuth 1.0a認証フローの実装
- [x] Consumer Key/Secret による認証
- [x] アクセストークンの永続化（`.evernote_oauth_token`）
- [x] トークンの自動再利用
- [x] OAuth認証ヘルパースクリプト（`oauth_helper.py`）作成

### 3. Python 3.11互換性の確保
- [x] Evernote SDK (evernote3) の互換性問題を特定
  - `inspect.getargspec` が Python 3.11で削除されている
- [x] パッチスクリプト（`patch_evernote.py`）作成
  - `inspect.getargspec` → `inspect.getfullargspec` に置換
- [x] 依存パッケージ追加（`oauth2`）

### 4. ChatGPTデータフォルダの特定
- [x] Microsoft Store版ChatGPTのデータ保存場所を発見
  - 通常版: `%APPDATA%\ChatGPT` （存在しない）
  - Store版: `%LOCALAPPDATA%\Packages\OpenAI.ChatGPT-Desktop_xxx\LocalCache\Roaming\ChatGPT`
- [x] 会話データの保存形式を確認
  - `IndexedDB` - LevelDB形式
  - `Local Storage` - LevelDB形式
  - その他: JSON, ログファイル

### 5. 動作確認
- [x] スクリプトの起動成功
- [x] Evernote認証成功
- [x] ファイル監視の動作確認
- [x] ファイル変更の検知成功

---

## 🚧 現在の課題

### 課題1: LevelDBファイルの処理
**問題:**
- ChatGPTの会話データは**LevelDB形式**（バイナリ）で保存されている
- バイナリファイルをそのまま読み込むと、制御文字（Unicode: 0x1など）が含まれる
- ENML（Evernote Markup Language）はXML形式で、無効な文字を許容しない
- Evernote APIエラー: `An invalid XML character (Unicode: 0x1) was found`

**影響:**
- `.ldb`および`.log`ファイルをEvernoteに保存できない
- 会話の実際の内容を取得できない

**現在の対応:**
- `.ldb`と`.log`を監視対象から一時的に除外

### 課題2: 会話データの抽出方法
**問題:**
- LevelDBは低レベルのkey-valueストア
- データ構造が不明
- 直接読み込むには専門的なライブラリ（`plyvel`など）が必要

**検討すべき解決策:**

1. **LevelDBライブラリを使用**
   - `plyvel` または `python-leveldb` でLevelDBを直接読み込み
   - データ構造を解析して会話内容を抽出
   - **利点:** 完全なデータアクセス
   - **欠点:** データ構造の解析が必要、複雑

2. **ChatGPTのエクスポート機能を利用**
   - ChatGPTアプリの設定から会話をエクスポート
   - エクスポートされたファイルを監視
   - **利点:** シンプル、信頼性が高い
   - **欠点:** 手動操作が必要、リアルタイム同期不可

3. **IndexedDBをブラウザ技術で読み込み**
   - Puppeteerなどでブラウザ経由でIndexedDBにアクセス
   - **利点:** JavaScriptエコシステムが利用可能
   - **欠点:** 複雑、Electronアプリへのアクセス権限が必要

4. **別のファイル形式を監視**
   - ChatGPTアプリが出力する他のファイル形式を探す
   - **利点:** バイナリ解析不要
   - **欠点:** そのようなファイルが存在するか不明

### 課題3: ログの文字化け
**問題:**
- ログファイル（`.log`）が文字化けして表示される
- エンコーディングの問題（Shift_JISとUTF-8の混在）

**影響:**
- デバッグが困難
- ユーザビリティの低下

**対応:**
- ログ出力のエンコーディングをUTF-8に統一する必要

---

## 📋 次のステップ

### 優先度: 高
1. **LevelDB読み込み機能の実装**
   - `plyvel`ライブラリの導入
   - LocalStorage LevelDBの読み込みテスト
   - 会話データ構造の解析

2. **データ抽出ロジックの作成**
   - LevelDBから会話データを抽出
   - テキスト形式に変換
   - ENMLに安全に変換

### 優先度: 中
3. **ログ文字化けの修正**
   - ログファイルのエンコーディングをUTF-8に設定
   - コンソール出力のエンコーディング対応

4. **エラーハンドリングの強化**
   - バイナリファイル検出時のスキップ処理
   - より詳細なエラーメッセージ

### 優先度: 低
5. **ドキュメントの拡充**
   - LevelDB処理に関するドキュメント追加
   - トラブルシューティングガイド更新

---

## 🔍 技術的な発見

### Microsoft Store版ChatGPTの特徴
- UWPアプリケーションサンドボックス内で動作
- データは`Packages`フォルダ内に隔離
- 通常のElectronアプリとは異なるパス構造

### Evernote SDK (evernote3) の問題
- Python 3.11で非推奨APIを使用
- メンテナンスが停止している可能性
- 将来的には別のSDKへの移行を検討すべき

### LevelDBの特性
- Googleが開発したkey-valueストア
- Chromeブラウザでも使用（IndexedDB、LocalStorage）
- バイナリ形式でデータ効率が高い
- 直接テキストとして読み込むことは不可能

---

## 📝 メモ

- `.env`ファイルには個人情報（Consumer Key/Secret、ファイルパス）が含まれる
- `.evernote_oauth_token`にはアクセストークンが保存される
- これらのファイルは`.gitignore`で除外済み
- `sync_history.db`には同期履歴が記録される（個人情報なし）

---

**レポート作成者:** GitHub Copilot  
**環境:** Windows 11, Python 3.11.9

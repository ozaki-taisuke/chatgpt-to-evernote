"""
ChatGPT → Evernote 自動同期スクリプト
メインエントリーポイント
"""
import os
import sys
import time
import logging
from datetime import datetime

# 自作モジュール
from config import config
from file_monitor import FileMonitor, extract_text_from_file, generate_note_title
from evernote_sync import EvernoteSync
from duplicate_manager import DuplicateManager


def setup_logging():
    """ロギング設定"""
    log_level = getattr(logging, config.log_level)
    
    # ログフォーマット
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Windowsコンソールの文字化け対策
    # 標準出力のエンコーディングをUTF-8に設定
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    
    # ルートロガー設定
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # コンソール出力（UTF-8）
            logging.StreamHandler(sys.stdout),
            # ファイル出力
            logging.FileHandler(
                config.log_file, 
                encoding='utf-8',
                mode='a'
            )
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("ChatGPT → Evernote 自動同期スクリプト 起動")
    logger.info("=" * 60)
    
    return logger


def process_file(
    file_path: str,
    evernote: EvernoteSync,
    duplicate_manager: DuplicateManager,
    logger: logging.Logger
):
    """
    検知されたファイルを処理してEvernoteに同期
    
    Args:
        file_path: ファイルパス
        evernote: EvernoteSyncインスタンス
        duplicate_manager: DuplicateManagerインスタンス
        logger: ロガー
    """
    try:
        logger.info(f"処理開始: {file_path}")
        
        # ファイル情報取得
        file_mtime = os.path.getmtime(file_path)
        
        # 重複チェック
        if duplicate_manager.is_already_synced(file_path, file_mtime):
            logger.info(f"スキップ（同期済み）: {file_path}")
            return
        
        # テキスト抽出
        logger.info("テキストを抽出中...")
        content = extract_text_from_file(file_path)
        
        if not content or len(content.strip()) < 10:
            logger.warning(f"内容が空またはデータ不足: {file_path}")
            return
        
        # ノートタイトル生成
        title = generate_note_title(file_path)
        
        # Evernoteにノート作成
        logger.info("Evernoteにノートを作成中...")
        note_guid = evernote.create_note(
            title=title,
            content=content,
            source_file=file_path,
            is_html=file_path.lower().endswith('.html')
        )
        
        if note_guid:
            # 同期済みとしてマーク
            duplicate_manager.mark_as_synced(file_path, file_mtime, note_guid)
            logger.info(f"✓ 同期成功: {title}")
        else:
            logger.error(f"✗ 同期失敗: {file_path}")
    
    except Exception as e:
        logger.error(f"ファイル処理エラー: {file_path} - {e}", exc_info=True)


def main():
    """メイン処理"""
    # ロギング設定
    logger = setup_logging()
    
    try:
        # 設定情報表示
        logger.info(f"監視パス: {config.chatgpt_data_path}")
        logger.info(f"監視拡張子: {', '.join(config.watch_extensions)}")
        logger.info(f"保存先ノートブック: {config.evernote_notebook_name}")
        logger.info(f"Evernote環境: {config.evernote_environment}")
        
        # 重複管理初期化
        logger.info("重複管理を初期化中...")
        duplicate_manager = DuplicateManager(config.duplicate_db_path)
        sync_count = duplicate_manager.get_sync_count()
        logger.info(f"既存同期履歴: {sync_count}件")
        
        # Evernote接続
        logger.info("Evernoteに接続中...")
        
        # OAuth または APIトークンで認証
        if config.use_oauth:
            evernote = EvernoteSync(
                notebook_name=config.evernote_notebook_name,
                sandbox=(config.evernote_environment == 'sandbox'),
                consumer_key=config.evernote_consumer_key,
                consumer_secret=config.evernote_consumer_secret
            )
        else:
            evernote = EvernoteSync(
                notebook_name=config.evernote_notebook_name,
                sandbox=(config.evernote_environment == 'sandbox'),
                api_token=config.evernote_api_token
            )
        
        # 接続テスト
        if not evernote.test_connection():
            logger.error("Evernote接続テスト失敗")
            return 1
        
        # ファイル監視コールバック関数
        def file_callback(file_path: str):
            process_file(file_path, evernote, duplicate_manager, logger)
        
        # ファイル監視開始
        logger.info("ファイル監視を設定中...")
        monitor = FileMonitor(
            watch_path=config.chatgpt_data_path,
            callback=file_callback,
            watch_extensions=config.watch_extensions,
            recursive=True
        )
        
        monitor.start()
        
        # メインループ（Ctrl+C で終了）
        try:
            while monitor.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n終了シグナルを受信しました")
        
        # 監視停止
        monitor.stop()
        
        # 終了時の統計情報
        final_sync_count = duplicate_manager.get_sync_count()
        logger.info(f"最終同期数: {final_sync_count}件")
        logger.info("プログラムを終了しました")
        
        return 0
    
    except ValueError as e:
        logger.error(f"設定エラー: {e}")
        logger.error(".env ファイルを確認してください")
        return 1
    
    except ImportError as e:
        logger.error(f"モジュールインポートエラー: {e}")
        logger.error("pip install -r requirements.txt を実行してください")
        return 1
    
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

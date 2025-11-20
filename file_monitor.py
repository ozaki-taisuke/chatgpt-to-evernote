"""
ファイル監視モジュール
指定されたディレクトリを監視し、新規作成・更新されたファイルを検知する
"""
import os
import time
import logging
from typing import Callable, List
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class ChatGPTFileHandler(FileSystemEventHandler):
    """ChatGPTファイル変更ハンドラー"""
    
    def __init__(
        self, 
        callback: Callable[[str], None],
        watch_extensions: List[str],
        debounce_seconds: float = 2.0
    ):
        """
        Args:
            callback: ファイル検知時に呼び出されるコールバック関数
            watch_extensions: 監視対象の拡張子リスト
            debounce_seconds: 連続イベントを無視する秒数
        """
        super().__init__()
        self.callback = callback
        self.watch_extensions = [ext.lower() for ext in watch_extensions]
        self.debounce_seconds = debounce_seconds
        self.last_processed = {}  # ファイルパス -> 最終処理時刻
        
        logger.info(f"監視対象拡張子: {', '.join(self.watch_extensions)}")
    
    def _should_process(self, file_path: str) -> bool:
        """
        ファイルを処理すべきか判定
        
        Args:
            file_path: ファイルパス
        
        Returns:
            処理すべき場合True
        """
        # 拡張子チェック
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.watch_extensions:
            return False
        
        # ファイルの存在確認
        if not os.path.exists(file_path):
            return False
        
        # デバウンス処理（同じファイルの連続イベントを無視）
        current_time = time.time()
        last_time = self.last_processed.get(file_path, 0)
        
        if current_time - last_time < self.debounce_seconds:
            logger.debug(f"デバウンス: {file_path}")
            return False
        
        self.last_processed[file_path] = current_time
        return True
    
    def on_created(self, event: FileSystemEvent):
        """ファイル作成イベント"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        logger.debug(f"ファイル作成検知: {file_path}")
        
        if self._should_process(file_path):
            logger.info(f"新規ファイル検知: {file_path}")
            self._process_file(file_path)
    
    def on_modified(self, event: FileSystemEvent):
        """ファイル更新イベント"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        logger.debug(f"ファイル更新検知: {file_path}")
        
        if self._should_process(file_path):
            logger.info(f"ファイル更新検知: {file_path}")
            self._process_file(file_path)
    
    def _process_file(self, file_path: str):
        """
        ファイルを処理
        
        Args:
            file_path: ファイルパス
        """
        try:
            # 少し待機（ファイル書き込み完了を待つ）
            time.sleep(0.5)
            
            # コールバック関数を呼び出し
            self.callback(file_path)
            
        except Exception as e:
            logger.error(f"ファイル処理エラー: {file_path} - {e}")


class FileMonitor:
    """ファイル監視クラス"""
    
    def __init__(
        self, 
        watch_path: str,
        callback: Callable[[str], None],
        watch_extensions: List[str],
        recursive: bool = True
    ):
        """
        Args:
            watch_path: 監視対象ディレクトリパス
            callback: ファイル検知時のコールバック関数
            watch_extensions: 監視対象の拡張子リスト
            recursive: サブディレクトリも監視する場合True
        """
        self.watch_path = watch_path
        self.callback = callback
        self.watch_extensions = watch_extensions
        self.recursive = recursive
        
        # 監視対象パスの存在確認
        if not os.path.exists(watch_path):
            logger.warning(f"監視対象パスが存在しません: {watch_path}")
            logger.warning("パスが作成されるまで待機します...")
        
        # イベントハンドラー作成
        self.event_handler = ChatGPTFileHandler(
            callback=callback,
            watch_extensions=watch_extensions
        )
        
        # オブザーバー作成
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler, 
            watch_path, 
            recursive=recursive
        )
        
        logger.info(f"ファイル監視を初期化: {watch_path} (再帰: {recursive})")
    
    def start(self):
        """監視を開始"""
        try:
            self.observer.start()
            logger.info("ファイル監視を開始しました")
            logger.info(f"監視パス: {self.watch_path}")
            logger.info(f"監視拡張子: {', '.join(self.watch_extensions)}")
            logger.info("Ctrl+C で終了します...")
            
        except Exception as e:
            logger.error(f"監視開始エラー: {e}")
            raise
    
    def stop(self):
        """監視を停止"""
        try:
            self.observer.stop()
            self.observer.join()
            logger.info("ファイル監視を停止しました")
            
        except Exception as e:
            logger.error(f"監視停止エラー: {e}")
    
    def is_alive(self) -> bool:
        """
        監視が稼働中か確認
        
        Returns:
            稼働中の場合True
        """
        return self.observer.is_alive()


def extract_text_from_file(file_path: str) -> str:
    """
    ファイルからテキストを抽出
    
    TODO: 実際のChatGPTファイル形式に合わせて実装を改善する必要があります
    現時点では以下の形式に対応:
    - .txt: プレーンテキスト
    - .json: JSON形式（会話データを想定）
    - .html: HTML形式
    
    Args:
        file_path: ファイルパス
    
    Returns:
        抽出されたテキスト
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    try:
        # プレーンテキスト
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # JSON形式
        elif ext == '.json':
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # TODO: 実際のJSON構造に合わせて調整
                # 現時点では全体をJSON文字列として返す
                return json.dumps(data, indent=2, ensure_ascii=False)
        
        # HTML形式
        elif ext == '.html':
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            # HTMLからテキストを抽出
            soup = BeautifulSoup(html_content, 'lxml')
            
            # スクリプトとスタイルタグを除去
            for script in soup(['script', 'style']):
                script.decompose()
            
            # テキスト抽出
            text = soup.get_text()
            
            # 空白行を整理
            lines = [line.strip() for line in text.splitlines()]
            lines = [line for line in lines if line]
            
            return '\n'.join(lines)
        
        else:
            # その他の形式はバイナリとして読み込み試行
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    except Exception as e:
        logger.error(f"テキスト抽出エラー: {file_path} - {e}")
        return f"[テキスト抽出失敗: {str(e)}]"


def generate_note_title(file_path: str) -> str:
    """
    ファイルパスからノートタイトルを生成
    
    Args:
        file_path: ファイルパス
    
    Returns:
        ノートタイトル
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filename = os.path.basename(file_path)
    
    return f"ChatGPTログ - {filename} - {timestamp}"

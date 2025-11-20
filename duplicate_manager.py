"""
重複管理モジュール
同じ会話が複数回Evernoteに保存されないようにハッシュ管理を行う
"""
import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DuplicateManager:
    """重複チェック管理クラス"""
    
    def __init__(self, db_path: str):
        """
        Args:
            db_path: SQLiteデータベースファイルのパス
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """データベースとテーブルの初期化"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    file_mtime REAL NOT NULL,
                    evernote_note_guid TEXT,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # インデックス作成
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_hash 
                ON sync_history(file_hash)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"重複管理データベースを初期化しました: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"データベース初期化エラー: {e}")
            raise
    
    def calculate_file_hash(self, file_path: str, mtime: float) -> str:
        """
        ファイルパスと更新日時からハッシュ値を生成
        
        Args:
            file_path: ファイルパス
            mtime: ファイルの更新日時（timestamp）
        
        Returns:
            SHA256ハッシュ文字列
        """
        hash_input = f"{file_path}_{mtime}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()
    
    def is_already_synced(self, file_path: str, mtime: float) -> bool:
        """
        ファイルがすでに同期済みかチェック
        
        Args:
            file_path: ファイルパス
            mtime: ファイルの更新日時
        
        Returns:
            同期済みの場合True
        """
        file_hash = self.calculate_file_hash(file_path, mtime)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id FROM sync_history WHERE file_hash = ?',
                (file_hash,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except sqlite3.Error as e:
            logger.error(f"重複チェックエラー: {e}")
            return False
    
    def mark_as_synced(
        self, 
        file_path: str, 
        mtime: float, 
        note_guid: Optional[str] = None
    ) -> bool:
        """
        ファイルを同期済みとしてマーク
        
        Args:
            file_path: ファイルパス
            mtime: ファイルの更新日時
            note_guid: EvernoteのノートGUID（オプション）
        
        Returns:
            成功した場合True
        """
        file_hash = self.calculate_file_hash(file_path, mtime)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sync_history 
                (file_hash, file_path, file_mtime, evernote_note_guid)
                VALUES (?, ?, ?, ?)
            ''', (file_hash, file_path, mtime, note_guid))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"同期履歴に記録: {file_path}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"同期履歴の記録エラー: {e}")
            return False
    
    def get_sync_count(self) -> int:
        """
        同期済みファイルの総数を取得
        
        Returns:
            同期済みファイル数
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sync_history')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except sqlite3.Error as e:
            logger.error(f"同期数取得エラー: {e}")
            return 0
    
    def clear_history(self) -> bool:
        """
        同期履歴をクリア（デバッグ用）
        
        Returns:
            成功した場合True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sync_history')
            
            conn.commit()
            conn.close()
            
            logger.info("同期履歴をクリアしました")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"履歴クリアエラー: {e}")
            return False

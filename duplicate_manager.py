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
            
            # 同期履歴テーブル（既存）
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
            
            # ファイルパス→ノートGUID対応テーブル（新規）
            # 1ファイル = 1ノートを維持するための管理テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_note_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    note_guid TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # インデックス作成
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_hash 
                ON sync_history(file_hash)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_path 
                ON file_note_mapping(file_path)
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
    
    def get_note_guid_by_path(self, file_path: str) -> Optional[str]:
        """
        ファイルパスに対応するEvernoteノートGUIDを取得
        
        Args:
            file_path: ファイルパス
        
        Returns:
            ノートGUID、存在しない場合はNone
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT note_guid FROM file_note_mapping WHERE file_path = ?',
                (file_path,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                logger.debug(f"ノートGUID取得: {file_path} -> {result[0]}")
                return result[0]
            else:
                logger.debug(f"ノートGUID未登録: {file_path}")
                return None
            
        except sqlite3.Error as e:
            logger.error(f"ノートGUID取得エラー: {e}")
            return None
    
    def save_note_guid_for_path(self, file_path: str, note_guid: str) -> bool:
        """
        ファイルパスとEvernoteノートGUIDの対応を保存
        
        Args:
            file_path: ファイルパス
            note_guid: EvernoteノートGUID
        
        Returns:
            成功した場合True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # UPSERTロジック（INSERT OR REPLACE）
            cursor.execute('''
                INSERT INTO file_note_mapping (file_path, note_guid, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(file_path) 
                DO UPDATE SET note_guid = excluded.note_guid, updated_at = CURRENT_TIMESTAMP
            ''', (file_path, note_guid))
            
            conn.commit()
            conn.close()
            
            logger.info(f"ノートGUIDを保存: {file_path} -> {note_guid}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"ノートGUID保存エラー: {e}")
            return False
    
    def get_file_note_count(self) -> int:
        """
        管理中のファイル→ノート対応の総数を取得
        
        Returns:
            対応数
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM file_note_mapping')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except sqlite3.Error as e:
            logger.error(f"ファイル→ノート対応数取得エラー: {e}")
            return 0

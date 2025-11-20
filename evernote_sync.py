"""
Evernote連携モジュール
Evernote APIを使用してノートを作成する
"""
import logging
from datetime import datetime
from typing import Optional
import hashlib

try:
    from evernote.api.client import EvernoteClient
    from evernote.edam.type.ttypes import Note, Notebook
    from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
    from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException
    EVERNOTE_AVAILABLE = True
except ImportError:
    EVERNOTE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Evernote SDK (evernote3) がインストールされていません")

logger = logging.getLogger(__name__)


class EvernoteSync:
    """Evernote同期クラス"""
    
    def __init__(self, api_token: str, notebook_name: str, sandbox: bool = False):
        """
        Args:
            api_token: Evernote APIトークン
            notebook_name: 保存先ノートブック名
            sandbox: サンドボックス環境を使用する場合True
        """
        if not EVERNOTE_AVAILABLE:
            raise ImportError(
                "Evernote SDK がインストールされていません。\n"
                "pip install evernote3 を実行してください。"
            )
        
        self.api_token = api_token
        self.notebook_name = notebook_name
        self.sandbox = sandbox
        
        try:
            self.client = EvernoteClient(token=api_token, sandbox=sandbox)
            self.note_store = self.client.get_note_store()
            self.notebook_guid = self._get_or_create_notebook()
            
            logger.info(f"Evernote接続成功: ノートブック '{notebook_name}'")
            
        except Exception as e:
            logger.error(f"Evernote接続エラー: {e}")
            raise
    
    def _get_or_create_notebook(self) -> str:
        """
        指定されたノートブックのGUIDを取得、なければ作成
        
        Returns:
            ノートブックGUID
        """
        try:
            # 既存のノートブックを検索
            notebooks = self.note_store.listNotebooks()
            
            for notebook in notebooks:
                if notebook.name == self.notebook_name:
                    logger.info(f"既存のノートブックを使用: {self.notebook_name}")
                    return notebook.guid
            
            # ノートブックが存在しない場合は作成
            logger.info(f"新しいノートブックを作成: {self.notebook_name}")
            notebook = Notebook()
            notebook.name = self.notebook_name
            notebook = self.note_store.createNotebook(notebook)
            
            return notebook.guid
            
        except Exception as e:
            logger.error(f"ノートブック取得/作成エラー: {e}")
            # デフォルトノートブックを使用
            logger.warning("デフォルトノートブックを使用します")
            return self.note_store.getDefaultNotebook().guid
    
    def create_note(
        self, 
        title: str, 
        content: str, 
        source_file: str,
        is_html: bool = False
    ) -> Optional[str]:
        """
        Evernoteノートを作成
        
        Args:
            title: ノートタイトル
            content: ノート本文（テキストまたはHTML）
            source_file: 元ファイルパス
            is_html: contentがHTMLの場合True
        
        Returns:
            作成されたノートのGUID、失敗時はNone
        """
        try:
            # ENML形式に変換
            if is_html:
                enml_content = self._html_to_enml(content, source_file)
            else:
                enml_content = self._text_to_enml(content, source_file)
            
            # ノート作成
            note = Note()
            note.title = title
            note.content = enml_content
            note.notebookGuid = self.notebook_guid
            
            created_note = self.note_store.createNote(note)
            
            logger.info(f"Evernoteノート作成成功: {title}")
            return created_note.guid
            
        except EDAMUserException as e:
            logger.error(f"Evernoteユーザーエラー: {e.errorCode} - {e.parameter}")
            return None
        except EDAMSystemException as e:
            logger.error(f"Evernoteシステムエラー: {e.errorCode} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"ノート作成エラー: {e}")
            return None
    
    def _text_to_enml(self, text: str, source_file: str) -> str:
        """
        プレーンテキストをENML形式に変換
        
        Args:
            text: プレーンテキスト
            source_file: 元ファイルパス
        
        Returns:
            ENML形式の文字列
        """
        # テキストをHTMLエスケープ
        import html
        escaped_text = html.escape(text)
        
        # 改行を<br/>に変換
        formatted_text = escaped_text.replace('\n', '<br/>')
        
        # メタ情報
        meta_info = f"""
        <div style="color: #666; font-size: 0.9em; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px;">
            <strong>取得日時:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <strong>元ファイル:</strong> {html.escape(source_file)}<br/>
        </div>
        """
        
        enml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
{meta_info}
<div>{formatted_text}</div>
</en-note>'''
        
        return enml
    
    def _html_to_enml(self, html_content: str, source_file: str) -> str:
        """
        HTMLをENML形式に変換
        
        Args:
            html_content: HTML文字列
            source_file: 元ファイルパス
        
        Returns:
            ENML形式の文字列
        """
        # TODO: より高度なHTML→ENML変換が必要な場合はBeautifulSoupで処理
        # 現時点ではシンプルな変換のみ実装
        
        import html
        
        # メタ情報
        meta_info = f"""
        <div style="color: #666; font-size: 0.9em; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px;">
            <strong>取得日時:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <strong>元ファイル:</strong> {html.escape(source_file)}<br/>
        </div>
        """
        
        enml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
{meta_info}
<div>{html_content}</div>
</en-note>'''
        
        return enml
    
    def test_connection(self) -> bool:
        """
        Evernote接続テスト
        
        Returns:
            接続成功の場合True
        """
        try:
            user = self.client.get_user_store().getUser()
            logger.info(f"Evernote接続テスト成功: ユーザー {user.username}")
            return True
        except Exception as e:
            logger.error(f"Evernote接続テスト失敗: {e}")
            return False

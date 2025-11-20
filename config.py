"""
設定ファイル読み込みモジュール
環境変数と.envファイルから設定を読み込む
"""
import os
from typing import List
from dotenv import load_dotenv
import logging

# .envファイルを読み込む
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """アプリケーション設定クラス"""
    
    def __init__(self):
        self._validate_config()
    
    @property
    def evernote_api_token(self) -> str:
        """Evernote APIトークン（オプション、OAuth使用時は不要）"""
        return os.getenv('EVERNOTE_API_TOKEN', '')
    
    @property
    def evernote_consumer_key(self) -> str:
        """Evernote Consumer Key（OAuth認証用）"""
        return os.getenv('EVERNOTE_CONSUMER_KEY', '')
    
    @property
    def evernote_consumer_secret(self) -> str:
        """Evernote Consumer Secret（OAuth認証用）"""
        return os.getenv('EVERNOTE_CONSUMER_SECRET', '')
    
    @property
    def use_oauth(self) -> bool:
        """OAuth認証を使用するかどうか"""
        return bool(self.evernote_consumer_key and self.evernote_consumer_secret)
    
    @property
    def evernote_notebook_name(self) -> str:
        """保存先ノートブック名"""
        return os.getenv('EVERNOTE_NOTEBOOK_NAME', 'ChatGPT Logs')
    
    @property
    def evernote_environment(self) -> str:
        """Evernote環境（production or sandbox）"""
        env = os.getenv('EVERNOTE_ENVIRONMENT', 'production').lower()
        if env not in ['production', 'sandbox']:
            logger.warning(f"無効なEVERNOTE_ENVIRONMENT: {env}. 'production'を使用します。")
            return 'production'
        return env
    
    @property
    def chatgpt_data_path(self) -> str:
        """ChatGPTデータフォルダパス"""
        path = os.getenv('CHATGPT_DATA_PATH', '')
        if not path:
            # デフォルトパスを試行
            username = os.getenv('USERNAME', '')
            default_path = f"C:\\Users\\{username}\\AppData\\Roaming\\ChatGPT"
            logger.warning(
                f"CHATGPT_DATA_PATH が設定されていません。"
                f"デフォルトパス '{default_path}' を試行します。"
            )
            return default_path
        return path
    
    @property
    def watch_extensions(self) -> List[str]:
        """監視対象の拡張子リスト"""
        extensions_str = os.getenv('WATCH_EXTENSIONS', '.html,.json,.txt')
        extensions = [ext.strip() for ext in extensions_str.split(',')]
        # 先頭に . がない場合は追加
        return [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    @property
    def watch_interval(self) -> int:
        """監視間隔（秒）"""
        try:
            return int(os.getenv('WATCH_INTERVAL', '5'))
        except ValueError:
            logger.warning("無効なWATCH_INTERVAL値。デフォルトの5秒を使用します。")
            return 5
    
    @property
    def log_level(self) -> str:
        """ログレベル"""
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            logger.warning(f"無効なLOG_LEVEL: {level}. 'INFO'を使用します。")
            return 'INFO'
        return level
    
    @property
    def log_file(self) -> str:
        """ログファイルパス"""
        return os.getenv('LOG_FILE', 'chatgpt_evernote_sync.log')
    
    @property
    def duplicate_db_path(self) -> str:
        """重複管理データベースパス"""
        return os.getenv('DUPLICATE_DB_PATH', './sync_history.db')
    
    def _validate_config(self):
        """設定の検証"""
        try:
            # OAuth または APIトークンのいずれかが必要
            has_oauth = self.use_oauth
            has_token = bool(self.evernote_api_token and 
                           self.evernote_api_token != 'your_evernote_api_token_here')
            
            if not has_oauth and not has_token:
                raise ValueError(
                    "Evernote認証情報が設定されていません。\n"
                    ".env ファイルに以下のいずれかを設定してください:\n"
                    "  - EVERNOTE_CONSUMER_KEY と EVERNOTE_CONSUMER_SECRET (OAuth認証)\n"
                    "  - EVERNOTE_API_TOKEN (Developer Token)\n"
                )
            
            if has_oauth:
                logger.info("OAuth認証を使用します")
            else:
                logger.info("Developer Token認証を使用します")
            
            # ChatGPTデータパスの存在確認
            if not os.path.exists(self.chatgpt_data_path):
                logger.warning(
                    f"ChatGPTデータフォルダが見つかりません: {self.chatgpt_data_path}\n"
                    f"パスが正しいか確認してください。"
                )
        except ValueError as e:
            logger.error(f"設定エラー: {e}")
            raise


# グローバル設定インスタンス
try:
    config = Config()
except Exception as e:
    logger.error(f"設定の読み込みに失敗しました: {e}")
    raise

"""
ChatGPT to Evernote - ローカルサーバー

Chrome拡張からのリクエストを受けてEvernoteに保存する
アプリケーション化対応:ダブルクリック起動、システムトレイ常駐
"""

import sys
import os
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import pystray
from PIL import Image, ImageDraw
import threading
import webbrowser

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from evernote_sync import EvernoteSync
from duplicate_manager import DuplicateManager
from config import Config

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evernote_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask設定
app = Flask(__name__)
CORS(app)  # Chrome拡張からのアクセス許可

# グローバル変数
evernote = None
duplicate_manager = None
server_thread = None
icon = None


def initialize_services():
    """サービス初期化"""
    global evernote, duplicate_manager
    
    try:
        logger.info("🔧 サービス初期化中...")
        
        # 設定読み込み
        config = Config()
        
        # Evernote接続
        # サンドボックス環境かどうか
        sandbox = config.evernote_environment == 'sandbox'
        
        # OAuth認証の場合
        if config.use_oauth:
            evernote = EvernoteSync(
                notebook_name=config.evernote_notebook_name,
                sandbox=sandbox,
                consumer_key=config.evernote_consumer_key,
                consumer_secret=config.evernote_consumer_secret
            )
        # Developer Token の場合
        else:
            evernote = EvernoteSync(
                notebook_name=config.evernote_notebook_name,
                sandbox=sandbox,
                api_token=config.evernote_api_token
            )
        
        logger.info("✅ Evernote接続成功")
        
        # 重複管理（データベースパスを指定）
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sync_history.db')
        duplicate_manager = DuplicateManager(db_path=db_path)
        logger.info("✅ 重複管理初期化完了")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 初期化エラー: {e}", exc_info=True)
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'ok',
        'service': 'ChatGPT to Evernote',
        'version': '1.0.0'
    })


@app.route('/api/save', methods=['POST'])
def save_conversation():
    """Chrome拡張から会話を受け取ってEvernoteに保存"""
    try:
        data = request.json
        
        conversation_id = data.get('conversationId', '')
        title = data.get('title', 'ChatGPT会話')
        messages = data.get('messages', [])
        url = data.get('url', '')
        
        logger.info(f"📥 会話受信: {title} (ID: {conversation_id})")
        
        # Evernote形式に変換
        content = format_conversation_to_enml(title, messages, url)
        
        # 既存ノートをチェック
        existing_guid = duplicate_manager.get_note_guid_by_path(conversation_id)
        
        if existing_guid:
            # 更新
            logger.info(f"🔄 既存ノート更新: {title}")
            note_guid = evernote.update_note(
                note_guid=existing_guid,
                title=title,
                content=content
            )
            action = 'updated'
        else:
            # 新規作成
            logger.info(f"✨ 新規ノート作成: {title}")
            note_guid = evernote.create_note(
                title=title,
                content=content,
                tags=['ChatGPT', '自動同期']
            )
            
            # GUID保存
            duplicate_manager.save_note_guid_for_path(conversation_id, note_guid)
            action = 'created'
        
        logger.info(f"✅ 保存完了: {title}")
        
        return jsonify({
            'success': True,
            'note_guid': note_guid,
            'action': action,
            'message': f'保存完了: {title}'
        })
        
    except Exception as e:
        logger.error(f"❌ 保存エラー: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def format_conversation_to_enml(title, messages, url):
    """会話をENML形式に変換"""
    enml = '<?xml version="1.0" encoding="UTF-8"?>'
    enml += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    enml += '<en-note>'
    
    # タイトル
    enml += f'<h1>{escape_html(title)}</h1>'
    
    # URL
    if url:
        enml += f'<p><a href="{escape_html(url)}">元の会話を開く</a></p>'
    
    enml += '<hr/>'
    
    # メッセージ
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        
        if role == 'user':
            enml += '<div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">'
            enml += '<strong>👤 あなた:</strong><br/>'
        else:
            enml += '<div style="background-color: #e8f5e9; padding: 10px; margin: 10px 0; border-radius: 5px;">'
            enml += '<strong>🤖 ChatGPT:</strong><br/>'
        
        # HTMLタグをそのまま使う（Markdownは既にHTMLに変換されている想定）
        enml += content
        enml += '</div>'
    
    enml += '</en-note>'
    
    return enml


def escape_html(text):
    """HTML特殊文字をエスケープ"""
    if not text:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def run_server():
    """Flaskサーバー起動"""
    logger.info("🚀 サーバー起動中...")
    logger.info("📡 Chrome拡張からの接続を待機: http://localhost:8765")
    
    try:
        app.run(host='localhost', port=8765, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ サーバーエラー: {e}", exc_info=True)


def create_tray_icon():
    """システムトレイアイコン作成"""
    # アイコン画像生成
    width = 64
    height = 64
    color1 = (0, 150, 136)  # ティール
    color2 = (255, 255, 255)  # 白
    
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=color2)
    
    # メニュー作成
    menu = pystray.Menu(
        pystray.MenuItem('ChatGPT to Evernote', lambda: None, enabled=False),
        pystray.MenuItem('サーバー稼働中 (http://localhost:8765)', lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Chrome拡張を開く', open_chrome_extension),
        pystray.MenuItem('ログを開く', open_log),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('終了', quit_app)
    )
    
    return pystray.Icon('chatgpt-evernote', image, 'ChatGPT to Evernote', menu)


def open_chrome_extension(icon, item):
    """Chrome拡張管理ページを開く"""
    webbrowser.open('chrome://extensions/')


def open_log(icon, item):
    """ログファイルを開く"""
    log_path = Path(__file__).parent / 'evernote_server.log'
    if log_path.exists():
        webbrowser.open(str(log_path))


def quit_app(icon, item):
    """アプリケーション終了"""
    logger.info("👋 アプリケーション終了")
    icon.stop()
    sys.exit(0)


def main():
    """メイン処理"""
    global server_thread, icon
    
    print("=" * 60)
    print("ChatGPT to Evernote - 自動同期サーバー")
    print("=" * 60)
    print()
    
    # サービス初期化
    if not initialize_services():
        print("❌ 初期化に失敗しました")
        print("詳細はevernote_server.logを確認してください")
        input("Enterキーを押して終了...")
        sys.exit(1)
    
    print("✅ 初期化完了")
    print()
    print("📡 サーバー起動: http://localhost:8765")
    print("🔧 Chrome拡張機能をインストールしてください")
    print("📋 システムトレイアイコンから管理できます")
    print()
    
    # サーバーをバックグラウンドスレッドで起動
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # システムトレイアイコン作成・実行
    icon = create_tray_icon()
    icon.run()


if __name__ == '__main__':
    main()

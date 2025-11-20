"""
ChatGPT公式エクスポート監視モジュール
ユーザーがエクスポートしたJSONファイルを自動検知してEvernoteに同期

使い方:
1. ChatGPT → Settings → Data controls → Export data
2. エクスポートされたZIPファイルをダウンロード
3. 指定フォルダに配置（または自動ダウンロード監視）
4. このスクリプトが自動的に解析してEvernoteに同期
"""
import os
import json
import zipfile
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ChatGPTExportParser:
    """ChatGPT公式エクスポートファイル解析クラス"""
    
    def __init__(self, export_dir: str):
        """
        Args:
            export_dir: エクスポートファイルを配置するディレクトリ
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        logger.info(f"エクスポート監視ディレクトリ: {export_dir}")
    
    def find_export_files(self) -> List[str]:
        """
        エクスポートファイル（ZIP）を検索
        
        Returns:
            ZIPファイルのパスリスト
        """
        zip_files = []
        for file in os.listdir(self.export_dir):
            if file.endswith('.zip') and 'chatgpt' in file.lower():
                full_path = os.path.join(self.export_dir, file)
                zip_files.append(full_path)
        
        zip_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        logger.info(f"検出されたエクスポートファイル: {len(zip_files)}個")
        return zip_files
    
    def extract_zip(self, zip_path: str, extract_dir: Optional[str] = None) -> str:
        """
        ZIPファイルを展開
        
        Args:
            zip_path: ZIPファイルのパス
            extract_dir: 展開先ディレクトリ（Noneの場合は自動生成）
        
        Returns:
            展開先ディレクトリパス
        """
        if extract_dir is None:
            zip_name = os.path.basename(zip_path).replace('.zip', '')
            extract_dir = os.path.join(self.export_dir, f"extracted_{zip_name}")
        
        os.makedirs(extract_dir, exist_ok=True)
        
        logger.info(f"ZIPファイルを展開中: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        logger.info(f"展開完了: {extract_dir}")
        return extract_dir
    
    def parse_conversations_json(self, json_path: str) -> List[Dict]:
        """
        conversations.jsonを解析
        
        Args:
            json_path: JSONファイルのパス
        
        Returns:
            会話データのリスト
        """
        logger.info(f"会話データを解析中: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conversations = []
            
            # ChatGPTエクスポート形式の解析
            # 形式例: [{"id": "...", "title": "...", "create_time": ..., "mapping": {...}}]
            if isinstance(data, list):
                for conv in data:
                    parsed = self._parse_conversation(conv)
                    if parsed:
                        conversations.append(parsed)
            
            logger.info(f"解析完了: {len(conversations)}件の会話")
            return conversations
        
        except Exception as e:
            logger.error(f"JSON解析エラー: {e}")
            return []
    
    def _parse_conversation(self, conv_data: Dict) -> Optional[Dict]:
        """
        個別の会話データを解析
        
        Args:
            conv_data: 会話の生データ
        
        Returns:
            整形された会話データ
        """
        try:
            conversation_id = conv_data.get('id', '')
            title = conv_data.get('title', 'Untitled')
            create_time = conv_data.get('create_time')
            update_time = conv_data.get('update_time')
            
            # メッセージマッピングから実際のメッセージを抽出
            mapping = conv_data.get('mapping', {})
            messages = []
            
            for node_id, node in mapping.items():
                message = node.get('message')
                if message:
                    author_role = message.get('author', {}).get('role')
                    content = message.get('content', {})
                    
                    # テキストコンテンツを抽出
                    if isinstance(content, dict):
                        parts = content.get('parts', [])
                        text = '\n'.join(str(part) for part in parts if part)
                    else:
                        text = str(content)
                    
                    if text:
                        messages.append({
                            'role': author_role,
                            'content': text,
                            'create_time': message.get('create_time')
                        })
            
            # メッセージを時系列でソート
            messages.sort(key=lambda x: x.get('create_time', 0))
            
            return {
                'id': conversation_id,
                'title': title,
                'messages': messages,
                'create_time': create_time,
                'update_time': update_time
            }
        
        except Exception as e:
            logger.error(f"会話解析エラー: {e}")
            return None
    
    def process_export_file(self, zip_path: str) -> List[Dict]:
        """
        エクスポートファイルを処理
        
        Args:
            zip_path: ZIPファイルのパス
        
        Returns:
            全会話データ
        """
        # ZIPを展開
        extract_dir = self.extract_zip(zip_path)
        
        # conversations.jsonを探す
        conversations_file = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file == 'conversations.json':
                    conversations_file = os.path.join(root, file)
                    break
            if conversations_file:
                break
        
        if not conversations_file:
            logger.error("conversations.jsonが見つかりません")
            return []
        
        # 会話データを解析
        return self.parse_conversations_json(conversations_file)
    
    def format_for_evernote(self, conversation: Dict) -> Dict:
        """
        会話データをEvernote用に整形
        
        Args:
            conversation: 会話データ
        
        Returns:
            Evernote用の整形データ
        """
        title = conversation['title']
        create_time = datetime.fromtimestamp(conversation['create_time']) if conversation['create_time'] else None
        
        # メッセージを整形
        content_parts = []
        for msg in conversation['messages']:
            role = msg['role']
            role_label = "👤 User" if role == "user" else "🤖 Assistant"
            content_parts.append(f"**{role_label}:**\n{msg['content']}\n")
        
        content = '\n---\n\n'.join(content_parts)
        
        return {
            'title': title,
            'content': content,
            'create_time': create_time,
            'conversation_id': conversation['id']
        }


def test_export_parser():
    """テスト関数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # エクスポートファイルを配置するディレクトリ
    # Windowsの標準ダウンロードフォルダを監視
    downloads_dir = str(Path.home() / "Downloads")
    export_dir = os.path.join(downloads_dir, "ChatGPT_Exports")
    
    print("=" * 60)
    print("ChatGPT公式エクスポート解析テスト")
    print("=" * 60)
    print(f"\n監視ディレクトリ: {export_dir}")
    print("\nエクスポート手順:")
    print("1. https://chat.openai.com/")
    print("2. Settings → Data controls → Export data")
    print("3. ダウンロードしたZIPファイルを上記ディレクトリに配置")
    print("=" * 60)
    
    parser = ChatGPTExportParser(export_dir)
    
    # エクスポートファイルを検索
    export_files = parser.find_export_files()
    
    if not export_files:
        print("\nエクスポートファイルが見つかりません")
        print(f"ZIPファイルを {export_dir} に配置してください")
        return
    
    print(f"\n検出されたファイル: {len(export_files)}個")
    
    # 最新のエクスポートファイルを処理
    latest_file = export_files[0]
    print(f"\n処理中: {os.path.basename(latest_file)}")
    
    conversations = parser.process_export_file(latest_file)
    print(f"\n✓ 解析完了: {len(conversations)}件の会話")
    
    # サンプル表示
    if conversations:
        print("\n=== 最初の会話サンプル ===")
        sample = conversations[0]
        print(f"タイトル: {sample['title']}")
        print(f"メッセージ数: {len(sample['messages'])}")
        
        formatted = parser.format_for_evernote(sample)
        print(f"\nEvernote用タイトル: {formatted['title']}")
        print(f"コンテンツプレビュー:\n{formatted['content'][:300]}...")


if __name__ == "__main__":
    test_export_parser()

"""
Evernote OAuth認証ヘルパースクリプト
Verification Codeを使って認証トークンを取得
"""
from evernote.api.client import EvernoteClient
import os
from dotenv import load_dotenv

# .envファイル読み込み
load_dotenv()

# 設定読み込み
consumer_key = os.getenv('EVERNOTE_CONSUMER_KEY')
consumer_secret = os.getenv('EVERNOTE_CONSUMER_SECRET')
sandbox = os.getenv('EVERNOTE_ENVIRONMENT', 'production').lower() == 'sandbox'

print("=" * 60)
print("Evernote OAuth認証ヘルパー")
print("=" * 60)
print(f"\nConsumer Key: {consumer_key}")
print(f"Environment: {'Sandbox' if sandbox else 'Production'}")
print()

# EvernoteClient初期化
client = EvernoteClient(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    sandbox=sandbox
)

# リクエストトークン取得
print("リクエストトークンを取得中...")
request_token = client.get_request_token('http://localhost')

print(f"\nOAuth Token: {request_token['oauth_token']}")
print(f"OAuth Token Secret: {request_token['oauth_token_secret']}")

# 認証URL生成
auth_url = client.get_authorize_url(request_token)
print(f"\n認証URL:\n{auth_url}")

print("\n" + "=" * 60)
print("ブラウザでリダイレクトされたlocalhost URLから")
print("oauth_verifier の値をコピーしてください")
print("=" * 60)

# Verification Code入力
oauth_verifier = input("\nVerification Code (oauth_verifier) を入力: ").strip()

# アクセストークン取得
print("\nアクセストークンを取得中...")
try:
    access_token = client.get_access_token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'],
        oauth_verifier
    )
    
    # トークンを保存
    token_file = '.evernote_oauth_token'
    with open(token_file, 'w') as f:
        f.write(access_token)
    
    print(f"\n✅ 認証成功！")
    print(f"トークンを保存しました: {token_file}")
    print(f"\nこれで python main.py を実行できます")
    
    # 接続テスト
    print("\n接続テスト中...")
    test_client = EvernoteClient(token=access_token, sandbox=sandbox)
    user = test_client.get_user_store().getUser()
    print(f"✅ ユーザー: {user.username}")
    
except Exception as e:
    import traceback
    print(f"\n❌ エラー: {e}")
    print("\n詳細:")
    traceback.print_exc()
    print("\nVerification Codeが正しいか確認してください")

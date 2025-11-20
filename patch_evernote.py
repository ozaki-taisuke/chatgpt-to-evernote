"""
Evernote3 SDK の Python 3.11 互換性パッチ
inspect.getargspec を inspect.getfullargspec に置き換える
"""
import os
import fileinput

# evernote SDKのclient.pyパス
client_py = r"C:\Python311\Lib\site-packages\evernote\api\client.py"

print("Evernote SDK Python 3.11 互換性パッチ")
print("=" * 60)
print(f"対象ファイル: {client_py}")

if not os.path.exists(client_py):
    print("❌ ファイルが見つかりません")
    exit(1)

# バックアップ作成
backup_file = client_py + ".backup"
if not os.path.exists(backup_file):
    import shutil
    shutil.copy2(client_py, backup_file)
    print(f"✓ バックアップ作成: {backup_file}")

# ファイル読み込み
with open(client_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 置換
original = "inspect.getargspec"
replacement = "inspect.getfullargspec"

if original in content:
    content = content.replace(original, replacement)
    
    # ファイル書き込み
    with open(client_py, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ パッチ適用完了")
    print(f"  {original} → {replacement}")
    print("\n✅ これで python main.py を実行できます")
else:
    print("✓ 既にパッチ適用済み、または置換対象が見つかりません")

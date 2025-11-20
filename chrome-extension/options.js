// Chrome拡張機能の設定画面

document.addEventListener('DOMContentLoaded', async () => {
  // 既存の設定を読み込み
  await loadSettings();
  
  // フォーム送信イベント
  document.getElementById('settingsForm').addEventListener('submit', handleSave);
});

/**
 * 既存の設定を読み込んで表示
 */
async function loadSettings() {
  try {
    const settings = await chrome.storage.sync.get([
      'evernoteToken',
      'notebookName',
      'tokenCreatedAt'
    ]);
    
    if (settings.evernoteToken) {
      // トークンが既に設定されている場合
      document.getElementById('tokenInfo').style.display = 'block';
      
      // ノートブック名を表示
      if (settings.notebookName) {
        document.getElementById('currentNotebook').textContent = 
          `ノートブック: ${settings.notebookName}`;
        document.getElementById('notebookName').value = settings.notebookName;
      } else {
        document.getElementById('currentNotebook').textContent = 
          'ノートブック: デフォルトノートブック';
      }
      
      // 有効期限を計算して表示
      if (settings.tokenCreatedAt) {
        const createdDate = new Date(settings.tokenCreatedAt);
        const expiryDate = new Date(createdDate);
        expiryDate.setDate(expiryDate.getDate() + 90);
        
        const today = new Date();
        const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        const expiryElement = document.getElementById('tokenExpiry');
        expiryElement.textContent = `有効期限: ${expiryDate.toLocaleDateString('ja-JP')} (残り ${daysLeft} 日)`;
        
        // 30日以内の場合は警告
        if (daysLeft <= 30) {
          expiryElement.classList.add('expiry-warning');
          if (daysLeft <= 0) {
            expiryElement.textContent += ' ⚠️ 期限切れです！新しいトークンを取得してください。';
          } else if (daysLeft <= 7) {
            expiryElement.textContent += ' ⚠️ もうすぐ期限切れです！';
          }
        }
      }
    }
  } catch (error) {
    console.error('設定の読み込みエラー:', error);
  }
}

/**
 * 設定を保存
 */
async function handleSave(event) {
  event.preventDefault();
  
  const saveButton = document.getElementById('saveButton');
  const statusDiv = document.getElementById('status');
  
  // ボタンを無効化
  saveButton.disabled = true;
  saveButton.textContent = '保存中...';
  
  try {
    // 入力値を取得
    const token = document.getElementById('developerToken').value.trim();
    const notebookName = document.getElementById('notebookName').value.trim();
    
    if (!token) {
      throw new Error('Developer Tokenを入力してください');
    }
    
    // トークンの形式を簡易チェック
    if (!token.startsWith('S=s') || !token.includes(':')) {
      throw new Error('Developer Tokenの形式が正しくありません');
    }
    
    // Evernote APIで接続テスト
    const isValid = await testEvernoteConnection(token);
    
    if (!isValid) {
      throw new Error('Evernote APIへの接続に失敗しました。トークンを確認してください。');
    }
    
    // 設定を保存
    await chrome.storage.sync.set({
      evernoteToken: token,
      notebookName: notebookName || '',
      tokenCreatedAt: new Date().toISOString()
    });
    
    // 成功メッセージ
    statusDiv.className = 'status success';
    statusDiv.textContent = '✓ 設定を保存しました！';
    
    // 設定情報を再読み込み
    await loadSettings();
    
    // フォームをクリア（セキュリティのため）
    document.getElementById('developerToken').value = '';
    
    // 3秒後にメッセージを消す
    setTimeout(() => {
      statusDiv.style.display = 'none';
    }, 3000);
    
  } catch (error) {
    // エラーメッセージ
    statusDiv.className = 'status error';
    statusDiv.textContent = `❌ エラー: ${error.message}`;
  } finally {
    // ボタンを再有効化
    saveButton.disabled = false;
    saveButton.textContent = '💾 保存';
  }
}

/**
 * Evernote APIに接続して認証をテスト
 */
async function testEvernoteConnection(token) {
  try {
    // Evernote API エンドポイント（本番環境）
    const apiUrl = 'https://www.evernote.com/shard/s1/notestore';
    
    // ユーザー情報を取得して認証をテスト
    const response = await fetch(`${apiUrl}/listNotebooks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-thrift',
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.ok;
  } catch (error) {
    console.error('Evernote接続テストエラー:', error);
    return false;
  }
}

/**
 * Popup UI Script
 */

const SERVER_URL = 'http://localhost:8765';

// DOM要素
const statusDiv = document.getElementById('status');
const syncCurrentBtn = document.getElementById('syncCurrent');
const loadingDiv = document.getElementById('loading');

// 初期化
document.addEventListener('DOMContentLoaded', async () => {
    await checkServerStatus();
    setupEventListeners();
});

/**
 * サーバー状態チェック
 */
async function checkServerStatus() {
    try {
        const response = await fetch(`${SERVER_URL}/api/health`, {
            signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
            setStatus('ok', '✅ サーバー接続OK');
        } else {
            setStatus('error', '⚠️ サーバーエラー');
        }
    } catch (error) {
        setStatus('error', '❌ サーバー未起動\nevernote_server.exeを起動してください');
    }
}

/**
 * ステータス表示更新
 */
function setStatus(type, message) {
    statusDiv.className = `status ${type}`;
    statusDiv.textContent = message;
}

/**
 * イベントリスナー設定
 */
function setupEventListeners() {
    // 会話保存ボタン（新規作成・更新両対応）
    syncCurrentBtn.addEventListener('click', async () => {
        setLoading(true);
        try {
            // 現在のタブを取得
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            console.log('Current tab:', tab);
            
            if (!tab.url || (!tab.url.includes('chat.openai.com') && !tab.url.includes('chatgpt.com'))) {
                setStatus('error', '⚠️ ChatGPTページで開いてください');
                setLoading(false);
                return;
            }
            
            // Content Scriptから会話抽出
            console.log('Sending message to tab:', tab.id);
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractConversation' });
            console.log('Response from content script:', response);
            
            if (response && response.success && response.data) {
                // サーバーに送信
                console.log('Sending to server:', response.data);
                const saveResponse = await fetch(`${SERVER_URL}/api/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(response.data),
                    signal: AbortSignal.timeout(30000)
                });
                
                if (saveResponse.ok) {
                    const result = await saveResponse.json();
                    const actionText = result.action === 'updated' ? '更新' : '保存';
                    setStatus('ok', `✅ ${actionText}完了\n${result.message}`);
                } else {
                    const errorText = await saveResponse.text();
                    console.error('Server error:', errorText);
                    throw new Error('保存に失敗しました: ' + saveResponse.status);
                }
            } else {
                console.error('No conversation data:', response);
                setStatus('error', '⚠️ 会話データを取得できませんでした');
            }
        } catch (error) {
            console.error('Error details:', error);
            setStatus('error', `❌ ${error.message}`);
        } finally {
            setLoading(false);
        }
    });
}

/**
 * ローディング表示切替
 */
function setLoading(isLoading) {
    loadingDiv.classList.toggle('active', isLoading);
    syncCurrentBtn.disabled = isLoading;
}

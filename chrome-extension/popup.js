/**
 * Popup UI Script
 */

const SERVER_URL = 'http://localhost:8765';

// DOM要素
const statusDiv = document.getElementById('status');
const syncNowBtn = document.getElementById('syncNow');
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
    // 全会話同期ボタン
    syncNowBtn.addEventListener('click', async () => {
        setLoading(true);
        try {
            await chrome.runtime.sendMessage({ action: 'syncAll' });
            setStatus('ok', '✅ 同期完了');
        } catch (error) {
            setStatus('error', `❌ ${error.message}`);
        } finally {
            setLoading(false);
        }
    });
    
    // 現在の会話保存ボタン
    syncCurrentBtn.addEventListener('click', async () => {
        setLoading(true);
        try {
            // 現在のタブを取得
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab.url || (!tab.url.includes('chat.openai.com') && !tab.url.includes('chatgpt.com'))) {
                setStatus('error', '⚠️ ChatGPTページで開いてください');
                return;
            }
            
            // Content Scriptから会話抽出
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractConversation' });
            
            if (response && response.success && response.data) {
                // サーバーに送信
                const saveResponse = await fetch(`${SERVER_URL}/api/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(response.data),
                    signal: AbortSignal.timeout(30000)
                });
                
                if (saveResponse.ok) {
                    const result = await saveResponse.json();
                    setStatus('ok', `✅ 保存完了\n${result.message}`);
                } else {
                    throw new Error('保存に失敗しました');
                }
            } else {
                setStatus('error', '⚠️ 会話データを取得できませんでした');
            }
        } catch (error) {
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
    syncNowBtn.disabled = isLoading;
    syncCurrentBtn.disabled = isLoading;
}

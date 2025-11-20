/**
 * Background Service Worker - 定期同期とサーバー通信
 */

const SERVER_URL = 'http://localhost:8765';
const SYNC_INTERVAL_MINUTES = 60; // 1時間ごと

console.log('🚀 ChatGPT to Evernote: Background service started');

/**
 * 初期化
 */
chrome.runtime.onInstalled.addListener(async () => {
    console.log('✨ Extension installed');
    
    // 定期同期アラーム設定
    await chrome.alarms.create('syncConversations', {
        periodInMinutes: SYNC_INTERVAL_MINUTES
    });
    
    // 初回同期実行
    setTimeout(() => syncAllConversations(), 5000);
});

/**
 * アラームリスナー（定期同期）
 */
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'syncConversations') {
        console.log('⏰ Scheduled sync triggered');
        syncAllConversations();
    }
});

/**
 * 拡張アイコンクリック時（手動同期）
 */
chrome.action.onClicked.addListener(async (tab) => {
    console.log('👆 Extension icon clicked');
    
    // ChatGPTページの場合は現在の会話を同期
    if (tab.url && (tab.url.includes('chat.openai.com') || tab.url.includes('chatgpt.com'))) {
        await syncCurrentTab(tab.id);
    } else {
        // それ以外は全会話同期
        await syncAllConversations();
    }
});

/**
 * サーバーヘルスチェック
 */
async function checkServerHealth() {
    try {
        const response = await fetch(`${SERVER_URL}/api/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            console.log('✅ Server is healthy');
            return true;
        } else {
            console.warn('⚠️ Server returned non-OK status:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ Server health check failed:', error.message);
        showNotification('サーバーに接続できません', 'evernote_server.exeが起動しているか確認してください');
        return false;
    }
}

/**
 * 現在のタブの会話を同期
 */
async function syncCurrentTab(tabId) {
    try {
        console.log(`🔄 Syncing current tab: ${tabId}`);
        
        // サーバーチェック
        if (!await checkServerHealth()) {
            return;
        }
        
        // Content Scriptから会話を抽出
        const response = await chrome.tabs.sendMessage(tabId, { action: 'extractConversation' });
        
        if (response && response.success && response.data) {
            const conversation = response.data;
            console.log(`📝 Extracted conversation: ${conversation.title}`);
            
            // Evernoteに保存
            await saveToEvernote(conversation);
            
            showNotification('保存完了', `「${conversation.title}」をEvernoteに保存しました`);
        } else {
            console.warn('⚠️ No conversation data extracted');
            showNotification('抽出失敗', '会話データを取得できませんでした');
        }
        
    } catch (error) {
        console.error('❌ Error syncing current tab:', error);
        showNotification('同期エラー', error.message);
    }
}

/**
 * 全会話を同期
 */
async function syncAllConversations() {
    try {
        console.log('🔄 Starting full sync...');
        
        // サーバーチェック
        if (!await checkServerHealth()) {
            return;
        }
        
        // ChatGPTタブを探す
        const tabs = await chrome.tabs.query({ 
            url: ['*://chat.openai.com/*', '*://chatgpt.com/*'] 
        });
        
        if (tabs.length === 0) {
            console.log('ℹ️ No ChatGPT tabs open, opening new tab...');
            const newTab = await chrome.tabs.create({ 
                url: 'https://chat.openai.com', 
                active: false 
            });
            
            // ページ読み込み完了を待機
            await waitForTabLoad(newTab.id);
            
            tabs.push(newTab);
        }
        
        // 各タブの会話を同期
        let syncCount = 0;
        for (const tab of tabs) {
            try {
                await syncCurrentTab(tab.id);
                syncCount++;
                
                // 少し待機（レート制限回避）
                await sleep(2000);
            } catch (error) {
                console.error(`❌ Error syncing tab ${tab.id}:`, error);
            }
        }
        
        console.log(`✅ Full sync completed: ${syncCount} conversations`);
        
        if (syncCount > 0) {
            showNotification('同期完了', `${syncCount}件の会話をEvernoteに保存しました`);
        }
        
    } catch (error) {
        console.error('❌ Error in full sync:', error);
        showNotification('同期エラー', error.message);
    }
}

/**
 * Evernoteサーバーに保存
 */
async function saveToEvernote(conversation) {
    try {
        const response = await fetch(`${SERVER_URL}/api/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(conversation),
            signal: AbortSignal.timeout(30000) // 30秒タイムアウト
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        const result = await response.json();
        console.log(`✅ Saved to Evernote: ${result.message}`);
        
        return result;
        
    } catch (error) {
        console.error('❌ Error saving to Evernote:', error);
        throw error;
    }
}

/**
 * 通知表示
 */
function showNotification(title, message) {
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: title,
        message: message,
        priority: 1
    });
}

/**
 * タブの読み込み完了を待機
 */
function waitForTabLoad(tabId) {
    return new Promise((resolve) => {
        const listener = (updatedTabId, changeInfo) => {
            if (updatedTabId === tabId && changeInfo.status === 'complete') {
                chrome.tabs.onUpdated.removeListener(listener);
                setTimeout(resolve, 2000); // 追加待機
            }
        };
        chrome.tabs.onUpdated.addListener(listener);
    });
}

/**
 * スリープ
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

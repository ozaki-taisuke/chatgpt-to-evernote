/**
 * Popup UI Script
 */

const SERVER_URL = 'http://localhost:8765';

// DOM要素
const statusDiv = document.getElementById('status');
const syncCurrentBtn = document.getElementById('syncCurrent');
const importArchiveBtn = document.getElementById('importArchive');
const fileInput = document.getElementById('fileInput');
const loadingDiv = document.getElementById('loading');
const importProgressDiv = document.getElementById('importProgress');
const progressText = document.getElementById('progressText');
const progressCount = document.getElementById('progressCount');

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
    
    // アーカイブインポートボタン
    importArchiveBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    // ファイル選択時の処理
    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            await importArchive(file);
        } catch (error) {
            console.error('Import error:', error);
            setStatus('error', `❌ インポート失敗: ${error.message}`);
        } finally {
            // ファイル選択をリセット
            fileInput.value = '';
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

/**
 * アーカイブファイルをインポート
 */
async function importArchive(file) {
    // UI切替
    importProgressDiv.classList.add('active');
    importArchiveBtn.disabled = true;
    syncCurrentBtn.disabled = true;
    
    try {
        // ファイルを読み込み
        progressText.textContent = '📖 ファイル読み込み中...';
        const fileContent = await readFileAsText(file);
        const archiveData = JSON.parse(fileContent);
        
        // conversations.json の形式確認
        if (!Array.isArray(archiveData)) {
            throw new Error('conversations.jsonの形式が不正です');
        }
        
        const totalConversations = archiveData.length;
        progressText.textContent = '📥 インポート中...';
        progressCount.textContent = `0 / ${totalConversations}件`;
        
        let successCount = 0;
        let errorCount = 0;
        
        // 各会話を順次処理
        for (let i = 0; i < archiveData.length; i++) {
            const conversation = archiveData[i];
            
            try {
                // 会話データを整形
                const formattedData = formatConversationData(conversation);
                
                // サーバーに送信
                const response = await fetch(`${SERVER_URL}/api/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formattedData),
                    signal: AbortSignal.timeout(30000)
                });
                
                if (response.ok) {
                    successCount++;
                } else {
                    console.error(`Failed to import conversation ${i}:`, await response.text());
                    errorCount++;
                }
                
                // 進捗更新
                progressCount.textContent = `${i + 1} / ${totalConversations}件 (成功: ${successCount}, 失敗: ${errorCount})`;
                
                // API制限を考慮して少し待つ
                if (i < archiveData.length - 1) {
                    await sleep(500); // 500msの待機
                }
                
            } catch (error) {
                console.error(`Error importing conversation ${i}:`, error);
                errorCount++;
            }
        }
        
        // 完了メッセージ
        setStatus('ok', `✅ インポート完了\n成功: ${successCount}件, 失敗: ${errorCount}件`);
        progressText.textContent = '✅ 完了！';
        
    } catch (error) {
        throw error;
    } finally {
        // UI復元
        setTimeout(() => {
            importProgressDiv.classList.remove('active');
            importArchiveBtn.disabled = false;
            syncCurrentBtn.disabled = false;
        }, 2000);
    }
}

/**
 * ChatGPTアーカイブの会話データを整形
 */
function formatConversationData(conversation) {
    // conversations.jsonの形式: { id, title, create_time, update_time, mapping, ... }
    const messages = [];
    
    // mapping から会話を抽出
    if (conversation.mapping) {
        for (const nodeId in conversation.mapping) {
            const node = conversation.mapping[nodeId];
            if (node.message && node.message.content) {
                const message = node.message;
                const content = message.content;
                
                // テキストコンテンツを抽出
                if (content.content_type === 'text' && content.parts && content.parts.length > 0) {
                    messages.push({
                        role: message.author.role, // user or assistant
                        content: content.parts.join('\n'),
                        timestamp: message.create_time
                    });
                }
            }
        }
    }
    
    // タイトルがない場合は最初のメッセージから生成
    let title = conversation.title || 'Untitled Conversation';
    if (!title || title === 'Untitled') {
        const firstUserMessage = messages.find(m => m.role === 'user');
        if (firstUserMessage) {
            title = firstUserMessage.content.substring(0, 50) + '...';
        }
    }
    
    return {
        conversation_id: conversation.id,
        title: title,
        messages: messages,
        url: `https://chatgpt.com/c/${conversation.id}`
    };
}

/**
 * ファイルをテキストとして読み込み
 */
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('ファイルの読み込みに失敗しました'));
        reader.readAsText(file);
    });
}

/**
 * スリープ関数
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

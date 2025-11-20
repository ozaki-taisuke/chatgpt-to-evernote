/**
 * Content Script - ChatGPT Webページでの会話抽出
 */

console.log('🔧 ChatGPT to Evernote: Content Script loaded');

/**
 * 現在開いている会話を抽出
 */
function extractCurrentConversation() {
    try {
        // タイトル取得
        const titleElement = document.querySelector('h1, title');
        const title = titleElement?.textContent?.trim() || 'ChatGPT会話';
        
        // 会話IDを取得（URLから）
        const conversationId = window.location.pathname.split('/').pop() || 
                              'conv_' + Date.now();
        
        // メッセージ取得
        const messages = [];
        
        // 複数のセレクタパターンを試行（ChatGPTのUI変更に対応）
        const messageSelectors = [
            '[data-message-author-role]',
            '[data-testid^="conversation-turn"]',
            '.group.w-full'
        ];
        
        let messageElements = [];
        for (const selector of messageSelectors) {
            messageElements = document.querySelectorAll(selector);
            if (messageElements.length > 0) {
                console.log(`✅ Found ${messageElements.length} messages using selector: ${selector}`);
                break;
            }
        }
        
        if (messageElements.length === 0) {
            console.warn('⚠️ No messages found');
            return null;
        }
        
        messageElements.forEach((el, index) => {
            // ロール判定（複数パターン）
            let role = el.getAttribute('data-message-author-role');
            if (!role) {
                // クラス名から判定
                const classes = el.className;
                if (classes.includes('user')) {
                    role = 'user';
                } else if (classes.includes('assistant') || classes.includes('gpt')) {
                    role = 'assistant';
                } else {
                    // 順番から判定（偶数=user, 奇数=assistant）
                    role = index % 2 === 0 ? 'user' : 'assistant';
                }
            }
            
            // コンテンツ取得（複数パターン）
            let contentEl = el.querySelector('.markdown') || 
                           el.querySelector('.whitespace-pre-wrap') ||
                           el.querySelector('[data-message-content]') ||
                           el;
            
            let content = contentEl?.innerHTML || contentEl?.textContent || '';
            
            // 空のメッセージをスキップ
            if (content.trim()) {
                messages.push({
                    role: role,
                    content: content.trim(),
                    timestamp: new Date().toISOString()
                });
            }
        });
        
        console.log(`✅ Extracted ${messages.length} messages from conversation`);
        
        return {
            conversationId: conversationId,
            title: title,
            messages: messages,
            url: window.location.href,
            extractedAt: new Date().toISOString()
        };
        
    } catch (error) {
        console.error('❌ Error extracting conversation:', error);
        return null;
    }
}

/**
 * バックグラウンドスクリプトからのメッセージリスナー
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Received message:', request.action);
    
    if (request.action === 'extractConversation') {
        const conversation = extractCurrentConversation();
        sendResponse({ success: !!conversation, data: conversation });
    }
    
    return true; // 非同期レスポンスを有効化
});

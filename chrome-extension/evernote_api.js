/**
 * Evernote Web API Wrapper (Developer Token方式)
 * 
 * Note: EvernoteはThrift APIを使用しているため、
 * JavaScriptから直接使用するには複雑。
 * ここでは、evernote-sdk-js を使用する代わりに、
 * シンプルなHTTP経由のアクセスを試みる。
 * 
 * 実際には、evernote-sdk-js ライブラリをバンドルして使うのが推奨。
 */

// Evernote SDK (CDN経由で読み込む場合は manifest.json に追加が必要)
// ここでは簡易実装として、XMLHttpRequest経由でThrift APIを叩く

class EvernoteAPI {
  constructor(token, sandbox = false) {
    this.token = token;
    this.sandbox = sandbox;
    
    // Evernote API エンドポイント
    this.baseUrl = sandbox 
      ? 'https://sandbox.evernote.com'
      : 'https://www.evernote.com';
  }

  /**
   * ノートを作成
   */
  async createNote(title, content, tags = [], notebookName = null) {
    try {
      // ENML形式に変換
      const enmlContent = this.convertToENML(content);
      
      // Thrift API呼び出し（簡易版）
      // 注意: 実際の実装では evernote-sdk-js を使用する必要がある
      const note = {
        title: title,
        content: enmlContent,
        tagNames: tags
      };
      
      if (notebookName) {
        // ノートブックGUIDを取得（実装が必要）
        // note.notebookGuid = await this.getNotebookGuid(notebookName);
      }
      
      // TODO: 実際のAPI呼び出し
      console.log('Create note:', note);
      
      return {
        success: true,
        noteGuid: 'dummy-guid-' + Date.now()
      };
      
    } catch (error) {
      console.error('ノート作成エラー:', error);
      throw error;
    }
  }

  /**
   * ノートを更新
   */
  async updateNote(noteGuid, title, content) {
    try {
      const enmlContent = this.convertToENML(content);
      
      // TODO: 実際のAPI呼び出し
      console.log('Update note:', { noteGuid, title });
      
      return {
        success: true,
        noteGuid: noteGuid
      };
      
    } catch (error) {
      console.error('ノート更新エラー:', error);
      throw error;
    }
  }

  /**
   * HTML/テキストをENML形式に変換
   */
  convertToENML(htmlContent) {
    // HTMLタグを除去してプレーンテキストに
    const div = document.createElement('div');
    div.innerHTML = htmlContent;
    const plainText = div.textContent || div.innerText || '';
    
    // ENMLフォーマット
    const enml = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
${plainText.split('\n').map(line => {
  if (line.trim()) {
    return `<div>${this.escapeXML(line)}</div>`;
  }
  return '<div><br/></div>';
}).join('\n')}
</en-note>`;
    
    return enml;
  }

  /**
   * XML特殊文字をエスケープ
   */
  escapeXML(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EvernoteAPI;
}

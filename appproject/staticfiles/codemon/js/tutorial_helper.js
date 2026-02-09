/**
 * TutorialHelper - チュートリアル用のヘルパーユーティリティ
 * 
 * チュートリアルを既存のコードに影響を与えずに実装するためのパターン集
 */

class TutorialHelper {
    constructor() {
        this.observers = [];
        this.eventListeners = [];
    }

    /**
     * 非破壊的なイベントリスナーを追加
     * チュートリアル終了時に自動削除される
     * 
     * @param {HTMLElement} element - イベントを監視する要素
     * @param {string} eventType - イベントタイプ (例: 'click', 'input')
     * @param {Function} handler - イベントハンドラー
     * @param {Object} options - イベントリスナーオプション
     */
    addSafeEventListener(element, eventType, handler, options = {}) {
        if (!element) {
            console.error('❌ TutorialHelper: 要素が見つかりません');
            return null;
        }

        // useCapture: true でチュートリアルのリスナーを先に実行
        const tutorialOptions = { ...options, capture: true };

        element.addEventListener(eventType, handler, tutorialOptions);

        // 削除用に記録
        const listenerInfo = { element, eventType, handler, options: tutorialOptions };
        this.eventListeners.push(listenerInfo);

        console.log(`🔧 TutorialHelper: ${eventType}イベントリスナーを追加`);
        return listenerInfo;
    }

    /**
     * 特定のイベントリスナーを削除
     */
    removeSafeEventListener(listenerInfo) {
        if (!listenerInfo) return;

        const { element, eventType, handler, options } = listenerInfo;
        element.removeEventListener(eventType, handler, options);

        // 記録から削除
        const index = this.eventListeners.indexOf(listenerInfo);
        if (index > -1) {
            this.eventListeners.splice(index, 1);
        }

        console.log(`🗑️ TutorialHelper: ${eventType}イベントリスナーを削除`);
    }

    /**
     * 全ての登録済みイベントリスナーを削除
     */
    removeAllEventListeners() {
        this.eventListeners.forEach(listenerInfo => {
            const { element, eventType, handler, options } = listenerInfo;
            element.removeEventListener(eventType, handler, options);
        });

        console.log(`🗑️ TutorialHelper: ${this.eventListeners.length}個のイベントリスナーを削除`);
        this.eventListeners = [];
    }

    /**
     * DOM変更を監視（MutationObserver）
     * チュートリアルで要素の出現を待つ際に使用
     * 
     * @param {HTMLElement} targetElement - 監視対象の要素
     * @param {Function} callback - 変更時のコールバック
     * @param {Object} options - MutationObserverのオプション
     */
    observeDOM(targetElement, callback, options = {}) {
        if (!targetElement) {
            console.error('❌ TutorialHelper: 監視対象要素が見つかりません');
            return null;
        }

        const defaultOptions = {
            childList: true,
            subtree: true,
            attributes: true,
            attributeOldValue: false,
            characterData: false
        };

        const observer = new MutationObserver((mutations) => {
            callback(mutations, observer);
        });

        observer.observe(targetElement, { ...defaultOptions, ...options });
        this.observers.push(observer);

        console.log('👁️ TutorialHelper: DOM監視を開始');
        return observer;
    }

    /**
     * 要素が出現するまで待つ（Promise版）
     * 
     * @param {string} selector - セレクター
     * @param {number} timeout - タイムアウト（ミリ秒）
     * @param {HTMLElement} parent - 親要素（デフォルトはdocument）
     */
    waitForElement(selector, timeout = 5000, parent = document) {
        return new Promise((resolve, reject) => {
            // 既に存在する場合
            const element = parent.querySelector(selector);
            if (element) {
                console.log(`✅ TutorialHelper: 要素が既に存在 (${selector})`);
                resolve(element);
                return;
            }

            // タイムアウト設定
            const timeoutId = setTimeout(() => {
                observer.disconnect();
                reject(new Error(`⏱️ Timeout: 要素が見つかりませんでした (${selector})`));
            }, timeout);

            // 監視開始
            const observer = this.observeDOM(parent, () => {
                const element = parent.querySelector(selector);
                if (element) {
                    clearTimeout(timeoutId);
                    observer.disconnect();
                    console.log(`✅ TutorialHelper: 要素を検出 (${selector})`);
                    resolve(element);
                }
            });
        });
    }

    /**
     * 全てのMutationObserverを停止
     */
    stopAllObservers() {
        this.observers.forEach(observer => observer.disconnect());
        console.log(`🛑 TutorialHelper: ${this.observers.length}個のオブザーバーを停止`);
        this.observers = [];
    }

    /**
     * チュートリアル終了時のクリーンアップ
     */
    cleanup() {
        this.removeAllEventListeners();
        this.stopAllObservers();
        console.log('🧹 TutorialHelper: クリーンアップ完了');
    }

    /**
     * ボタンクリックを監視（既存の動作を妨げない）
     * 
     * @param {HTMLElement} button - 監視するボタン
     * @param {Function} onBeforeClick - クリック前のコールバック
     * @param {Function} onAfterClick - クリック後のコールバック
     */
    monitorButtonClick(button, onBeforeClick = null, onAfterClick = null) {
        if (!button) return null;

        const handler = (event) => {
            // 既存の動作を止めない（preventDefaultしない）
            console.log('🖱️ TutorialHelper: ボタンクリックを検出');

            if (onBeforeClick) {
                onBeforeClick(event);
            }

            // 既存のイベントが処理された後に実行
            if (onAfterClick) {
                setTimeout(() => {
                    onAfterClick(event);
                }, 0);
            }
        };

        // capture: true で先に実行（ただしpreventDefaultしない）
        return this.addSafeEventListener(button, 'click', handler, { capture: true });
    }

    /**
     * フォーム送信を監視（既存の動作を妨げない）
     */
    monitorFormSubmit(form, onBeforeSubmit = null, onAfterSubmit = null) {
        if (!form) return null;

        const handler = (event) => {
            console.log('📝 TutorialHelper: フォーム送信を検出');

            if (onBeforeSubmit) {
                onBeforeSubmit(event);
            }

            if (onAfterSubmit) {
                setTimeout(() => {
                    onAfterSubmit(event);
                }, 0);
            }
        };

        return this.addSafeEventListener(form, 'submit', handler, { capture: true });
    }
}

// グローバルインスタンスを作成
window.tutorialHelper = new TutorialHelper();

console.log('🔧 TutorialHelper loaded');

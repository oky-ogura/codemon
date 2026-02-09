/**
 * SimpleTutorial - シンプルで堅牢なチュートリアルシステム
 * 
 * 設計方針:
 * - 最小限の機能で最大の安定性
 * - デバッグしやすいシンプルな構造
 * - フラグ管理を排除し、直接起動
 */

(function () {
    'use strict';

    class SimpleTutorial {
        constructor(steps, options = {}) {
            this.steps = steps;
            this.currentStep = 0;
            this.options = options;

            // DOM要素を保持
            this.overlay = null;
            this.highlightBox = null;
            this.messageBox = null;

            console.log(`✨ SimpleTutorial initialized with ${steps.length} steps`);
        }

        /**
         * チュートリアルを開始
         */
        start() {
            console.log('🎬 チュートリアル開始');
            this.createElements();
            this.showStep(0);
        }

        /**
         * DOM要素を作成
         */
        createElements() {
            // オーバーレイ
            this.overlay = document.createElement('div');
            this.overlay.id = 'simple-tutorial-overlay';
            this.overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 150000;
                display: none;
            `;
            document.body.appendChild(this.overlay);

            // ハイライトボックス
            this.highlightBox = document.createElement('div');
            this.highlightBox.id = 'simple-tutorial-highlight';
            this.highlightBox.style.cssText = `
                position: fixed;
                border: 3px solid #4CAF50;
                border-radius: 8px;
                box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
                z-index: 150001;
                pointer-events: none;
                display: none;
            `;
            document.body.appendChild(this.highlightBox);

            // メッセージボックス
            this.messageBox = document.createElement('div');
            this.messageBox.id = 'simple-tutorial-message';
            this.messageBox.style.cssText = `
                position: fixed;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 150002;
                max-width: 400px;
                display: none;
            `;
            document.body.appendChild(this.messageBox);

            console.log('✅ チュートリアル要素を作成しました');
        }

        /**
         * ステップを表示
         */
        showStep(index) {
            if (index < 0 || index >= this.steps.length) {
                console.log('🎉 チュートリアル完了');
                this.complete();
                return;
            }

            this.currentStep = index;
            const step = this.steps[index];

            console.log(`📍 STEP ${index + 1}/${this.steps.length}: ${step.message ? step.message.substring(0, 30) : 'カスタム'}`);

            // 前のステップの表示をクリア
            this.clearDisplay();

            // オーバーレイ表示
            this.overlay.style.display = 'block';

            // ターゲット要素のハイライト
            if (step.target) {
                this.highlightElement(step.target, step);
            } else {
                // ターゲットなし: 画面中央にメッセージ
                this.showCenterMessage(step);
            }

            // カスタムonShowコールバック
            if (step.onShow) {
                console.log('🔧 onShowコールバック実行');
                step.onShow.call(this);
            }
        }

        /**
         * 要素をハイライト
         */
        highlightElement(selector, step) {
            const element = document.querySelector(selector);

            if (!element) {
                console.warn(`⚠️ 要素が見つかりません: ${selector}`);
                this.showCenterMessage(step);
                return;
            }

            const rect = element.getBoundingClientRect();

            // ハイライト位置設定
            this.highlightBox.style.cssText = `
                position: fixed;
                left: ${rect.left - 5}px;
                top: ${rect.top - 5}px;
                width: ${rect.width + 10}px;
                height: ${rect.height + 10}px;
                border: 3px solid #4CAF50;
                border-radius: 8px;
                box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
                z-index: 150001;
                pointer-events: none;
                display: block;
            `;

            // 要素をクリック可能に
            element.style.position = 'relative';
            element.style.zIndex = '150003';
            element.style.pointerEvents = 'auto';

            // メッセージ表示（要素の横）
            this.showMessageNearElement(step, rect);

            // クリック待機
            if (step.requireClick !== false) {
                this.waitForClick(element);
            }
        }

        /**
         * 画面中央にメッセージ表示
         */
        showCenterMessage(step) {
            this.messageBox.innerHTML = `
                <div style="font-size: 18px; line-height: 1.8; margin-bottom: 20px;">
                    ${step.message || ''}
                </div>
                ${step.showNextButton !== false ? `
                    <button id="simple-tutorial-next" style="
                        padding: 10px 30px;
                        background: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 16px;
                        cursor: pointer;
                    ">${step.nextText || 'つぎへ'}</button>
                ` : ''}
                ${step.showSkip ? `
                    <button id="simple-tutorial-skip" style="
                        padding: 10px 20px;
                        background: #999;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                        cursor: pointer;
                        margin-left: 10px;
                    ">スキップ</button>
                ` : ''}
            `;

            // 中央配置
            this.messageBox.style.cssText = `
                position: fixed;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.4);
                z-index: 150002;
                max-width: 500px;
                display: block;
            `;

            // イベントリスナー
            this.setupMessageButtons();
        }

        /**
         * 要素の近くにメッセージ表示
         */
        showMessageNearElement(step, elementRect) {
            this.messageBox.innerHTML = `
                <div style="font-size: 16px; line-height: 1.6;">
                    ${step.message || ''}
                </div>
            `;

            // 要素の左側に配置
            const left = elementRect.left - 420;
            const top = elementRect.top;

            this.messageBox.style.cssText = `
                position: fixed;
                left: ${left > 0 ? left : 20}px;
                top: ${top}px;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 150002;
                max-width: 400px;
                display: block;
            `;
        }

        /**
         * メッセージボタンのイベント設定
         */
        setupMessageButtons() {
            const nextBtn = document.getElementById('simple-tutorial-next');
            if (nextBtn) {
                nextBtn.addEventListener('click', () => this.next());
            }

            const skipBtn = document.getElementById('simple-tutorial-skip');
            if (skipBtn) {
                skipBtn.addEventListener('click', () => this.complete());
            }
        }

        /**
         * 要素のクリックを待機
         */
        waitForClick(element) {
            const clickHandler = () => {
                console.log('✅ 要素がクリックされました');
                element.removeEventListener('click', clickHandler);
                setTimeout(() => this.next(), 300);
            };

            element.addEventListener('click', clickHandler, { once: true });
        }

        /**
         * 次のステップへ
         */
        next() {
            console.log('➡️ 次のステップへ');
            this.showStep(this.currentStep + 1);
        }

        /**
         * 表示をクリア
         */
        clearDisplay() {
            if (this.highlightBox) {
                this.highlightBox.style.display = 'none';
            }
            if (this.messageBox) {
                this.messageBox.style.display = 'none';
            }

            // 全要素のz-indexをリセット
            document.querySelectorAll('[style*="z-index: 150003"]').forEach(el => {
                el.style.zIndex = '';
            });
        }

        /**
         * チュートリアル完了
         */
        complete() {
            console.log('🎊 チュートリアル完了');
            this.clearDisplay();

            if (this.overlay) {
                this.overlay.remove();
            }
            if (this.highlightBox) {
                this.highlightBox.remove();
            }
            if (this.messageBox) {
                this.messageBox.remove();
            }

            if (this.options.onComplete) {
                this.options.onComplete();
            }
        }

        /**
         * 要素の出現を待つヘルパー
         */
        waitForElement(selector, timeout = 5000) {
            return new Promise((resolve, reject) => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    return;
                }

                const observer = new MutationObserver(() => {
                    const element = document.querySelector(selector);
                    if (element) {
                        observer.disconnect();
                        clearTimeout(timer);
                        resolve(element);
                    }
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });

                const timer = setTimeout(() => {
                    observer.disconnect();
                    reject(new Error(`Timeout: ${selector}`));
                }, timeout);
            });
        }
    }

    // グローバルに公開
    window.SimpleTutorial = SimpleTutorial;
    console.log('✅ SimpleTutorial loaded');

})();
